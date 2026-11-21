"""Local Root Matrix commands. Only run/resume with --authorize can contact a model."""

import argparse
import http.client
from importlib.metadata import version
from collections import deque
from contextlib import closing, contextmanager
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import fcntl
import hmac
import os
from pathlib import Path
import re
import sqlite3
import sys
import urllib.error
import urllib.request

from experiment import (
    ROOT,
    DESIGN,
    STR,
    VENDORS,
    parse,
    pack,
    digest,
    classify,
    payload,
    schedule,
    cost,
    envelope,
)
from analysis import QUESTIONS, score

LOCAL = ROOT / "local"
ENDPOINTS = {
    "anthropic": "https://api.anthropic.com/v1/messages",
    "openai": "https://api.openai.com/v1/chat/completions",
}


def now():
    return datetime.now(timezone.utc).isoformat()


def require(condition, msg):
    if not condition:
        raise ValueError(msg)


def write_new(path, data):
    with path.open("xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())


def inventory():
    manifest = (ROOT / "SHA256SUMS").read_bytes()
    names = set()
    for line in manifest.decode().splitlines():
        expected, name = line.split("  ", 1)
        require(
            Path(name).name == name and name not in names,
            "Invalid study manifest entry.",
        )
        names.add(name)
        require(
            digest((ROOT / name).read_bytes()) == expected,
            "Study file changed: " + name,
        )
    require(
        names
        == {p.name for p in ROOT.iterdir() if p.is_file() and p.name != "SHA256SUMS"},
        "Study inventory mismatch.",
    )
    return digest(manifest)


def validate_answers(answers):
    require(
        isinstance(answers, dict) and set(answers) == set(VENDORS),
        "Supply predictions for every selected model.",
    )
    for m, a in answers.items():
        require(
            isinstance(a, dict)
            and set(a) == set(QUESTIONS)
            and all(type(v) is bool for v in a.values()),
            "Every prediction must be true or false: " + m,
        )


def read_seal():
    raw = (LOCAL / "seal.json").read_bytes()
    obj = parse(raw)
    require(
        obj["study_sha256"] == inventory(), "Prediction seal belongs to another study."
    )
    validate_answers(obj["answers"])
    return raw, obj


def validate_plan():
    require(
        "regex==" + version("regex") == (ROOT / "requirements.txt").read_text().strip(),
        "Install the pinned regex version.",
    )
    rows = schedule()
    expected = {
        (str(b), m, c)
        for b in range(1, DESIGN["repeat"] + 1)
        for m in VENDORS
        for c in DESIGN["cells"]
    }
    require(
        len(rows) == len(expected)
        and {(r["block"], r["model"], r["cell"]) for r in rows} == expected,
        "Invalid frozen schedule.",
    )
    require(
        all(
            r["slot"] == str(i).zfill(5)
            and int(r["block"]) == 1 + (i - 1) // (len(VENDORS) * len(DESIGN["cells"]))
            for i, r in enumerate(rows, 1)
        ),
        "Slot order invalid.",
    )
    return rows


def seal(path):
    answers = parse(path.read_bytes())
    validate_answers(answers)
    LOCAL.mkdir(mode=0o700, exist_ok=True)
    raw = pack({"study_sha256": inventory(), "sealed_utc": now(), "answers": answers})
    write_new(LOCAL / "seal.json", raw)
    print("Prediction seal SHA-256", digest(raw))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


def send(model, body, key, *, count_only=False):
    vendor = VENDORS[model]
    headers = {"Content-Type": "application/json", "Accept-Encoding": "identity"}
    if vendor == "openai":
        headers["Authorization"] = "Bearer " + key
    else:
        headers.update({"x-api-key": key, "anthropic-version": "2023-06-01"})
    url = ENDPOINTS[vendor] + ("/count_tokens" if count_only else "")
    request = urllib.request.Request(url, body, headers=headers, method="POST")
    try:
        reply = urllib.request.build_opener(NoRedirect).open(request, timeout=240)
    except urllib.error.HTTPError as e:
        reply = e
    except (OSError, http.client.HTTPException):
        return 0, b"", {}
    try:
        with reply:
            raw = reply.read()
            safe = {
                k.lower(): v
                for k, v in reply.headers.items()
                if k.lower()
                in {
                    "request-id",
                    "x-request-id",
                    "date",
                    "content-type",
                    "openai-processing-ms",
                }
            }
            if key.encode() in raw + pack(safe) or re.search(
                rb"sk-(?:ant-|proj-|[A-Za-z0-9_-]{16})", raw + pack(safe)
            ):
                return 0, b"", {"capture": "credential-like string withheld"}
            return reply.status, raw, safe
    except (OSError, http.client.HTTPException):
        return 0, b"", {}


def credential(vendor):
    label = "OpenAI" if vendor == "openai" else "Anthropic"
    key = os.getenv(vendor.upper() + "_API_KEY")
    if not key:
        key = (
            (Path.home() / "void-matrix-api-keys" / (label + " API Key.txt"))
            .read_text()
            .strip()
        )
    require(
        key and not any(c.isspace() for c in key), "Credential must be a single value."
    )
    return key


SCHEMA = """
CREATE TABLE meta(data BLOB NOT NULL);
CREATE TABLE attempts(slot TEXT PRIMARY KEY,started TEXT NOT NULL,request BLOB NOT NULL,
 status INTEGER,headers BLOB,response BLOB,finished TEXT,record BLOB,receipt_hash TEXT);
"""


def receipt_hash(slot, started, req, status, headers, raw, finished, record):
    return digest(
        pack(
            [
                slot,
                started,
                digest(req),
                status,
                digest(headers),
                digest(raw),
                finished,
                digest(record),
            ]
        )
    )


def create_db(path, metadata):
    write_new(path, b"")
    db = sqlite3.connect(path)
    try:
        db.executescript(SCHEMA)
        with db:
            db.execute("INSERT INTO meta VALUES (?)", (pack(metadata),))
    finally:
        db.close()


@contextmanager
def lock_lane(path):
    with path.open("a+b") as f:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def dbname(v):
    return LOCAL / (v + ".sqlite")


def track_revision(seen, requested, record):
    if "returned_model" in record and record["class"] != "ID":
        received = record["returned_model"]
        require(
            seen.setdefault(requested, received) == received,
            "Returned snapshot changed within a model. Lane halted.",
        )


def read_rows(db, slots, metadata):
    rowdata = db.execute("SELECT data FROM meta").fetchall()
    require(
        len(rowdata) == 1 and parse(rowdata[0][0]) == metadata,
        "Run identity or cap mismatch.",
    )
    result = []
    ids = set()
    open_slots = set()
    revisions = {}
    for slot, started, req, status, headers, raw, finished, record, h in db.execute(
        "SELECT * FROM attempts ORDER BY slot"
    ):
        s = slots[slot]
        require(
            VENDORS[s["model"]] == metadata["vendor"]
            and req == pack(payload(s["model"], s["cell"])),
            "Request does not match schedule.",
        )
        if status is None:
            require(
                all(v is None for v in (headers, raw, finished, record, h)),
                "Incomplete slot corrupt.",
            )
            result.append((s, {"class": "UNKNOWN"}))
            open_slots.add(slot)
            continue
        require(
            receipt_hash(slot, started, req, status, headers, raw, finished, record)
            == h,
            "Receipt SHA-256 mismatch.",
        )
        r = classify(s["model"], status, raw)
        require(record == pack(r), "Reclassification mismatch.")
        if r.get("response_id"):
            require(r["response_id"] not in ids, "Duplicate provider response ID.")
            ids.add(r["response_id"])
        track_revision(revisions, s["model"], r)
        result.append((s, r))
    return result, open_slots


def compute_usage(model, r):
    usage = r.get("usage")
    if not isinstance(usage, dict):
        return None
    if VENDORS[model] == "openai":
        a, b = usage.get("prompt_tokens"), usage.get("completion_tokens")
    else:
        a, b = usage.get("input_tokens"), usage.get("output_tokens")
        if usage.get("cache_creation_input_tokens") or usage.get(
            "cache_read_input_tokens"
        ):
            return None
    if not all(type(x) is int and x >= 0 for x in (a, b)):
        return None
    return a, b


def check_input_sizes(vendor, key, transport):
    if vendor != "anthropic":
        return
    for model in DESIGN["rates_usd_per_million"][vendor]:
        for cell in DESIGN["cells"]:
            request = payload(model, cell)
            count_request = {k: request[k] for k in ("model", "messages", "system")}
            status, body, _ = transport(
                model, pack(count_request), key, count_only=True
            )
            require(status == 200, "Input count unavailable for " + model + " " + cell)
            n = parse(body).get("input_tokens")
            require(
                type(n) is int and 0 < n <= DESIGN["input_reserve"],
                "Input token reservation insufficient for " + model + " " + cell,
            )


class AllowancePause(ValueError):
    """The next OpenAI slot remains unstarted until token capacity is available."""


def openai_tokens(record, reserve):
    usage = record.get("usage")
    if isinstance(usage, dict):
        reported = usage.get("total_tokens")
        counts = [usage.get("prompt_tokens"), usage.get("completion_tokens")]
        candidates = []
        if type(reported) is int and reported >= 0:
            candidates.append(reported)
        if all(type(n) is int and n >= 0 for n in counts):
            candidates.append(sum(counts))
        if candidates:
            return max(candidates)
    return reserve


class TokenWindow:
    def __init__(self, db, limit, reserve):
        self.limit = limit
        self.reserve = reserve
        self.events = deque()
        self.total = 0
        for when, record in db.execute(
            "SELECT coalesce(finished, started), record FROM attempts "
            "ORDER BY coalesce(finished, started), slot"
        ):
            self.add(when, parse(record) if record else {})

    def add(self, when, record):
        tokens = openai_tokens(record, self.reserve)
        self.events.append((datetime.fromisoformat(when), tokens))
        self.total += tokens

    def before_request(self, when):
        cutoff = datetime.fromisoformat(when) - timedelta(hours=24)
        while self.events and self.events[0][0] <= cutoff:
            self.total -= self.events.popleft()[1]
        if self.total + self.reserve > self.limit:
            raise AllowancePause(
                f"OpenAI paused before dispatch: {self.total} recent tokens, "
                f"{self.reserve} needed for the next slot, rolling limit {self.limit}."
            )


def run_lane(
    v, cap, expected_seal, resume=False, transport=send, openai_24h_budget=None
):
    raw, _ = read_seal()
    require(
        hmac.compare_digest(digest(raw), expected_seal),
        "Prediction seal digest mismatch.",
    )
    require(cap.is_finite() and cap >= envelope()[v], "Cap below full-lane reserve.")
    if v == "anthropic":
        require(cap <= Decimal("180"), "Anthropic ceiling is $180.")
    reserve_tokens = DESIGN["input_reserve"] + DESIGN["max_output"]
    limit = (
        DESIGN["openai_rolling_24h_token_cap"]
        if openai_24h_budget is None
        else openai_24h_budget
    )
    if v == "openai":
        require(
            type(limit) is int
            and reserve_tokens <= limit <= DESIGN["openai_rolling_24h_token_cap"],
            "OpenAI rolling token budget outside permitted range.",
        )
    else:
        require(
            openai_24h_budget is None,
            "OpenAI token budget applies only to the OpenAI lane.",
        )
    slots = {s["slot"]: s for s in validate_plan()}
    meta = {
        "vendor": v,
        "seal_sha256": expected_seal,
        "study_sha256": inventory(),
        "cap_usd": str(cap.normalize()),
    }
    with lock_lane(LOCAL / (v + ".lock")):
        dbfile = dbname(v)
        if not resume:
            create_db(dbfile, meta)
        require(dbfile.is_file(), "No existing lane to resume.")
        db = sqlite3.connect(dbfile)
        try:
            prior, _ = read_rows(db, slots, meta)
            done = {s["slot"] for s, r in prior}
            ids = {r["response_id"] for _, r in prior if r.get("response_id")}
            reserve_total = envelope()[v] + sum_overage(prior)
            revisions = {}
            for previous, record in prior:
                track_revision(revisions, previous["model"], record)
            window = TokenWindow(db, limit, reserve_tokens) if v == "openai" else None
            key = credential(v)
            check_input_sizes(v, key, transport)
            for s in slots.values():
                m = s["model"]
                n = s["slot"]
                if VENDORS[m] != v or n in done:
                    continue
                reserved = cost(m, DESIGN["input_reserve"], DESIGN["max_output"])
                # Pre-reserve all remaining calls; charge the larger of actual cost or
                # the frozen reservation when prior usage is incomplete or exceeds it.
                if cap < reserve_total:
                    raise ValueError("Remaining run exceeds approved spend envelope.")
                body = pack(payload(m, s["cell"]))
                started = now()
                if window is not None:
                    window.before_request(started)
                with db:
                    db.execute(
                        "INSERT INTO attempts(slot,started,request) VALUES (?,?,?)",
                        (n, started, body),
                    )
                status, raw_reply, headers = transport(m, body, key)
                r = classify(m, status, raw_reply)
                record = pack(r)
                head = pack(headers)
                finished = now()
                h = receipt_hash(
                    n, started, body, status, head, raw_reply, finished, record
                )
                with db:
                    db.execute(
                        "UPDATE attempts SET status=?,headers=?,response=?,finished=?,record=?,receipt_hash=? WHERE slot=?",
                        (status, head, raw_reply, finished, record, h, n),
                    )
                if window is not None:
                    window.add(finished, r)
                reserve_total += sum_overage([(s, r)])
                track_revision(revisions, m, r)
                if r.get("response_id"):
                    require(
                        r["response_id"] not in ids,
                        "Duplicate provider response ID; lane halted.",
                    )
                    ids.add(r["response_id"])
                require(
                    r["class"] not in {"OP", "PI", "ID"},
                    "Lane paused; inspect preserved slot " + n + ".",
                )
                usage = compute_usage(m, r)
                require(
                    usage is not None and cost(m, *usage) <= reserved,
                    "Usage requires inspection at " + n + ".",
                )
        finally:
            db.close()


def sum_overage(prior):
    total = Decimal(0)
    for s, r in prior:
        m = s["model"]
        usage = compute_usage(m, r)
        if usage:
            total += max(
                Decimal(0),
                cost(m, *usage)
                - cost(m, DESIGN["input_reserve"], DESIGN["max_output"]),
            )
    return total


def verify_report():
    seal_bytes, sealdata = read_seal()
    slots = {s["slot"]: s for s in validate_plan()}
    rows = []
    chains = {}
    for v in DESIGN["rates_usd_per_million"]:
        f = dbname(v)
        if not f.exists():
            continue
        with closing(sqlite3.connect(f.as_uri() + "?mode=ro", uri=True)) as db:
            db.execute("BEGIN")
            meta = parse(db.execute("SELECT data FROM meta").fetchone()[0])
            require(
                meta["vendor"] == v
                and meta["seal_sha256"] == digest(seal_bytes)
                and meta["study_sha256"] == inventory(),
                "Seal mismatch.",
            )
            new, _ = read_rows(db, slots, meta)
            rows += new
            chains[v] = digest(
                pack(
                    db.execute(
                        "SELECT slot,receipt_hash FROM attempts ORDER BY slot"
                    ).fetchall()
                )
            )
    return {
        "study_sha256": inventory(),
        "prediction_seal_sha256": digest(seal_bytes),
        "receipt_set_sha256": chains,
        "recorded": len(rows),
        "scheduled": len(slots),
        "models": score(rows, sealdata["answers"]),
    }


def questionnaire(path=None):
    print(
        "Answer Q1–Q8 separately for each model. Each cell has 100 trials. A tie means No."
    )
    print("Empty = zero visible UTF-8 bytes with normal stop (V0 or V2).")
    print(
        "Exact dotted = "
        + STR["targets"]["T1"]
        + ". Exact undotted = "
        + STR["targets"]["T0"]
        + ". Both compare the whole answer."
    )
    for number, question in enumerate(QUESTIONS.values(), 1):
        print(f"Q{number}. {question.text} ({question.high} > {question.low})")
    for model in VENDORS:
        print(model)
    if path is None:
        return
    require(
        path.resolve().parent != ROOT,
        "Save personal answers outside the frozen study file set.",
    )
    require(not path.exists(), "Choose a new answer file.")
    answers = {}
    for model in VENDORS:
        while True:
            line = input(f"{model} Q1–Q8 (eight Y/N letters): ")
            tokens = "".join(line.split()).upper()
            if len(tokens) == len(QUESTIONS) and set(tokens) <= {"Y", "N"}:
                answers[model] = dict(zip(QUESTIONS, (t == "Y" for t in tokens)))
                break
            print("Enter exactly eight Y/N letters.")
    validate_answers(answers)
    write_new(path, pack(answers) + b"\n")
    print("Saved responses to", path)


def cli():
    p = argparse.ArgumentParser(description=__doc__)
    subs = p.add_subparsers(dest="cmd", required=True)
    subs.add_parser("check")
    subs.add_parser("questions").add_argument(
        "--save", type=Path, metavar="ANSWERS_JSON"
    )
    subs.add_parser("verify")
    subs.add_parser("seal").add_argument("answers", type=Path)
    for action in ("run", "resume"):
        sub = subs.add_parser(action)
        sub.add_argument("--vendor", choices=["openai", "anthropic"], required=True)
        sub.add_argument("--authorize", action="store_true")
        sub.add_argument(
            "--openai-24h-budget",
            type=int,
            help="Rolling token ceiling shared by both OpenAI models (default 1000000)",
        )
        sub.add_argument("--seal-sha256", required=True)
        sub.add_argument("--confirm-rates", action="store_true")
        sub.add_argument("--cap-usd", type=Decimal, required=True)
    args = p.parse_args()
    if args.cmd == "check":
        print(
            "Study SHA-256",
            inventory(),
            "slots",
            len(validate_plan()),
            "USD envelopes",
            {k: str(v) for k, v in envelope().items()},
        )
    elif args.cmd == "questions":
        questionnaire(args.save)
    elif args.cmd == "seal":
        seal(args.answers)
    elif args.cmd == "verify":
        print(pack(verify_report()).decode())
    else:
        require(args.authorize, "Execution requires --authorize.")
        require(
            args.confirm_rates,
            "Verify current provider rates before authorizing the lane.",
        )
        run_lane(
            args.vendor,
            args.cap_usd,
            args.seal_sha256,
            args.cmd == "resume",
            openai_24h_budget=args.openai_24h_budget,
        )


if __name__ == "__main__":
    try:
        cli()
    except AllowancePause as e:
        print(e, file=sys.stderr)
        sys.exit(75)
    except (ValueError, OSError, sqlite3.Error) as e:
        sys.exit(str(e))
