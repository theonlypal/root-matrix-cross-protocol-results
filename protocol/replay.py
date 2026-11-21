"""Read archived provider bodies from pinned checkouts; compare to the original classifiers."""

from collections import Counter
from pathlib import Path
import sys
from experiment import AR, HE, SPAN, STR, classify, digest, pack, parse

STUDIES = {
    "gpt-5.4-shrt-prerequisite-gate-analysis/raw": 800,
    "gpt-5.4-shrt-prerequisite-reassignment-analysis/raw": 800,
    "opus45-opus46-matched-results/exp3": 1200,
}


def replay(sources):
    result = {}
    for study, expected in STUDIES.items():
        counts = Counter()
        files = sorted((sources / study / "attempts").rglob("response.bin"))
        if len(files) != expected:
            raise ValueError("Archived attempt count differs for " + study)
        for response in files:

            def read(name):
                return parse((response.parent / name).read_bytes())

            old = read("classification.json")
            attempt = read("attempt.json")
            raw = response.read_bytes()
            r = classify(old["returned_model"], attempt["http_status"], raw)
            if (
                digest(raw) != attempt["response_sha256"]
                or r["answer_hex"] != old["content_utf8_hex"]
                or r["present"]
                != old.get("text_container_present", old.get("content_present"))
                or r["stop"] != old.get("stop_reason", old.get("finish_reason"))
                or r["response_id"] != old["response_id"]
                or (
                    old["class"] in {"V0", "V1", "V2", "VU", "NV"}
                    and old["class"] != r["class"]
                )
                or (old["class"] in {"T1", "T0", "HE"} and old["class"] != r["whole"])
            ):
                raise ValueError("Historical receipt mismatch: " + str(response))
            counts[(old["returned_model"], r["class"], r["whole"] or "")] += 1
        result[study] = {
            "compared": expected,
            "outcomes": [[*k, n] for k, n in sorted(counts.items())],
        }
    return result


PILOTS = {
    "gemini3-crossscript-prerequisite-replication/runs/pilot-20261012-paid": "gemini-3-flash-preview",
    "gemini36-crossscript-prerequisite-replication/runs/pilot-20261012-paid": "gemini-3.6-flash",
    "kimi-k3-crossscript-prerequisite-replication/data/pilot-20261012": "kimi-k3",
}


def pilot_replay(sources):
    result = {}
    for rel, model in PILOTS.items():
        folder = sources / rel
        rows = parse((folder / "verification.json").read_bytes())["rows"]
        totals = Counter()
        seen = set()
        groups = {}
        for row in rows:
            slot = row.get("slot_id") or row["slot"]
            raw = parse((folder / slot / "response.bin").read_bytes())
            if model == "kimi-k3":
                choice = raw["choices"][0]
                text = choice["message"].get("content")
                present = text is not None
                stop = choice["finish_reason"]
                actual = raw["model"]
                ident = raw["id"]
            else:
                choice = raw["candidates"][0]
                pieces = [
                    p["text"]
                    for p in choice.get("content", {}).get("parts", [])
                    if "text" in p and not p.get("thought")
                ]
                present = bool(pieces)
                text = "".join(pieces)
                stop = choice["finishReason"]
                actual = raw["modelVersion"]
                ident = raw["responseId"]
            text = text or ""
            if (
                actual != model
                or ident in seen
                or stop.lower() != "stop"
                or text != (row["answer"] or "")
                or len(text.encode()) != row["answer_bytes"]
            ):
                raise ValueError("Pilot receipt differs at " + rel + "/" + slot)
            seen.add(ident)
            kind = "nonempty" if text else "V0" if present else "V2"
            if kind != "nonempty" and row["class"] != kind:
                raise ValueError("Historical Void subtype mismatch")
            totals[kind] += 1
            totals["T1"] += text == STR["targets"]["T1"]
            totals["T0"] += text == STR["targets"]["T0"]
            totals["PATAH_whole"] += text == "شַׁרְט"
            totals["ZWSP_whole"] += text == "\u200b"
            totals["scripts_anywhere"] += bool(AR.search(text) and HE.search(text))
            totals["same_word"] += any(
                AR.search(w) and HE.search(w) for w in SPAN.findall(text)
            )
            group = (
                "match"
                if row["cell"] in ("A", "E", "H")
                else "mismatch"
                if row["cell"] in ("B", "F", "G")
                else "removed"
            )
            c = groups.setdefault(group, Counter())
            c[kind] += 1
        if len(seen) != 40:
            raise ValueError("Expected 40 distinct pilot responses")
        result[model] = {
            "receipts": len(seen),
            "counts": dict(totals),
            "groups": groups,
        }
    return result


if __name__ == "__main__":
    sources = Path(sys.argv[1])
    print(
        pack(
            {
                "primary_replay": replay(sources),
                "historical_pilots": pilot_replay(sources),
            }
        ).decode()
    )
