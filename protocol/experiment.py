"""Exact request bytes, structural provider decoding and outcome measurements."""

import csv
import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path

import regex
from classification_helpers import explicit_block, near_void

ROOT = Path(__file__).resolve().parent


def parse(raw):
    def unique(pairs):
        d = dict(pairs)
        if len(d) != len(pairs):
            raise ValueError("Duplicate JSON field")
        return d

    def invalid(value):
        raise ValueError("Nonfinite JSON")

    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid)


def pack(data):
    return json.dumps(
        data, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":")
    ).encode("utf-8")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


DESIGN = parse((ROOT / "design.json").read_bytes())
STR = parse((ROOT / "strings.json").read_bytes())
VENDORS = {
    m: v for v, prices in DESIGN["rates_usd_per_million"].items() for m in prices
}
KNOWN = {v["text"] for v in parse((ROOT / "variants.json").read_bytes())}
NORMAL = {"openai": "stop", "anthropic": "end_turn"}
LENGTH = {"openai": "length", "anthropic": "max_tokens"}
AR = regex.compile(r"\p{Script=Arabic}")
HE = regex.compile(r"\p{Script=Hebrew}")
SPAN = regex.compile(r"[\p{L}\p{M}]+")
ANSI = regex.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def schedule():
    with (ROOT / "schedule.tsv").open() as f:
        return list(csv.DictReader(f, delimiter="\t"))


def payload(model, cell):
    system, user = DESIGN["cells"][cell]
    sys_text = STR["systems"][system]
    msg = {"role": "user", "content": STR["users"][user]}
    if VENDORS[model] == "openai":
        return {
            "model": model,
            "messages": [{"role": "system", "content": sys_text}, msg],
            "max_completion_tokens": DESIGN["max_output"],
            "service_tier": "default",
        }
    return {
        "model": model,
        "system": sys_text,
        "messages": [msg],
        "max_tokens": DESIGN["max_output"],
        "service_tier": "standard_only",
    }


def cost(model, n_in, n_out):
    prices = DESIGN["rates_usd_per_million"][VENDORS[model]][model]
    return (
        Decimal(str(prices[0])) * n_in + Decimal(str(prices[1])) * n_out
    ) / 1_000_000


def envelope():
    return {
        v: sum(
            cost(m, DESIGN["input_reserve"], DESIGN["max_output"])
            * DESIGN["repeat"]
            * len(DESIGN["cells"])
            for m in rates
        )
        for v, rates in DESIGN["rates_usd_per_million"].items()
    }


def decoded(vendor, body):
    """Return final text, container status, stop and any explicit excluded channel."""
    if not isinstance(body.get("id"), str) or not body["id"] or not body.get("model"):
        raise ValueError("Missing response identity")
    if vendor == "openai":
        choices = body["choices"]
        if not isinstance(choices, list) or len(choices) != 1:
            raise ValueError("Expected one choice")
        choice = choices[0]
        msg = choice["message"]
        if msg["role"] != "assistant":
            raise ValueError("Wrong message role")
        stop = choice["finish_reason"]
        text = msg.get("content")
        present = text is not None
        if present and not isinstance(text, str):
            raise ValueError("Unexpected content envelope")
        excluded = None
        if stop == "content_filter" or any(
            explicit_block(x) for x in [body, choice, msg]
        ):
            excluded = "SB"
        elif msg.get("refusal") or stop == "refusal":
            excluded = "RF"
        elif (
            msg.get("function_call")
            or msg.get("tool_calls")
            or stop in ("tool_calls", "function_call")
        ):
            excluded = "TC"
    else:
        if (
            body.get("type") != "message"
            or body.get("role") != "assistant"
            or not isinstance(body.get("content"), list)
        ):
            raise ValueError("Unexpected Messages envelope")
        stop = body["stop_reason"]
        parts = body["content"]
        text_parts = []
        kinds = set()
        for part in parts:
            kind = part["type"]
            kinds.add(kind)
            if kind == "text":
                if not isinstance(part["text"], str):
                    raise ValueError("Invalid text block")
                text_parts.append(part["text"])
        present = bool(text_parts)
        text = "".join(text_parts)
        excluded = None
        if explicit_block(body) or stop == "content_filter":
            excluded = "SB"
        elif stop == "refusal" or "refusal" in kinds:
            excluded = "RF"
        elif stop == "tool_use" or any("tool" in k for k in kinds):
            excluded = "TC"
        elif stop == "pause_turn":
            excluded = "CN"
        elif kinds - {"text", "thinking", "redacted_thinking"}:
            excluded = "PI"
    if not isinstance(stop, str) or not stop:
        raise ValueError("Missing termination")
    return text or "", present, stop, excluded


def classify(model, status, raw):
    """Malformed/error bodies can never contribute to a Void or a target hit."""
    if not 200 <= status < 300:
        return {"class": "OP", "http_status": status}
    try:
        b = parse(raw)
        vendor = VENDORS[model]
        text, present, stop, excluded = decoded(vendor, b)
        buf = text.encode("utf-8")
        dated_alias = (
            vendor == "openai"
            and not re.search(r"-\d{4}-\d{2}-\d{2}$", model)
            and re.fullmatch(re.escape(model) + r"-\d{4}-\d{2}-\d{2}", b["model"])
        )
        if b["model"] != model and not dated_alias:
            excluded = "ID"
        if excluded:
            outcome = excluded
        elif buf:
            outcome = "NV" if near_void(text) else "R"
        elif stop == NORMAL[vendor]:
            outcome = "V0" if present else "V2"
        elif stop == LENGTH[vendor]:
            outcome = "V1"
        else:
            outcome = "VU"
        # Extract spans before any display normalization. Escape sequences create boundaries.
        words = set(SPAN.findall(ANSI.sub(" ", text)))
        spans = sorted(s for s in words if AR.search(s) and HE.search(s))
        targets = STR["targets"] | {
            "SHART": STR["users"]["shart"],
            "SHAMS": STR["users"]["shams"],
        }
        return {
            "class": outcome,
            "returned_model": b["model"],
            "response_id": b["id"],
            "stop": stop,
            "present": present,
            "answer_bytes": len(buf),
            "answer_sha256": digest(buf),
            "answer_hex": buf.hex(),
            "whole": next((k for k, x in targets.items() if x == text), None),
            "embedded": [k for k, x in targets.items() if x in text and x != text],
            "mixed_anywhere": bool(AR.search(text) and HE.search(text)),
            "mixed_spans": spans,
            "whole_span": text if text in spans else None,
            "known_whole": text if text in KNOWN else None,
            "known_spans": sorted(words & KNOWN),
            "novel_spans": sorted(set(spans) - KNOWN),
            "usage": b.get("usage"),
            "fingerprint": b.get("system_fingerprint"),
        }
    except (KeyError, TypeError, IndexError, AttributeError, ValueError, UnicodeError):
        return {"class": "PI", "http_status": status}
