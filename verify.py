"""Reproduce the final Root Matrix checkpoint offline from the two preserved ledgers."""
import csv
import hashlib
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from collections import Counter
from contextlib import closing
from fractions import Fraction
from math import comb
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PRIMARY = "gpt-5.2-2025-12-11"
CHECKPOINT = "7b9e5a331934cf1d3ae4b037a6760eaab9b3ce3d367f327a892da0c2bc4662d3"
STUDY = "0543a6d92658e857e31b9e3c8f9c95ed5328f1eb39aa20bd75f086399663360e"
SEAL = "21af0f5ff1ca1d9d79f009ad8a708d445b763379b92b9daebe8fe81e8cc1e6ae"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, label):
    if not condition:
        raise ValueError(label)


def tsv(path):
    with (ROOT / path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main():
    for line in (ROOT / "SHA256SUMS").read_text().splitlines():
        digest, filename = line.split("  ", 1)
        require(sha((ROOT / filename).read_bytes()) == digest, filename)
    require(sha((ROOT / "results.json").read_bytes()) == CHECKPOINT, "Checkpoint hash")
    require(sha((ROOT / "protocol/SHA256SUMS").read_bytes()) == STUDY, "Study manifest")
    require(sha((ROOT / "prediction-seal.json").read_bytes()) == SEAL, "Sealed predictions")
    with tempfile.TemporaryDirectory() as tmp:
        replica = Path(tmp) / "protocol"
        shutil.copytree(ROOT / "protocol", replica)
        local = replica / "local"
        local.mkdir()
        shutil.copyfile(ROOT / "prediction-seal.json", local / "seal.json")
        for vendor in ("openai", "anthropic"):
            shutil.copyfile(ROOT / "ledgers" / (vendor + ".sqlite"), local / (vendor + ".sqlite"))
        output = subprocess.check_output([sys.executable, "-B", str(replica / "runner.py"), "verify"])
    report = json.loads(output)
    require(report == json.loads((ROOT / "results.json").read_bytes()), "Frozen verifier replay")
    schedule = {r["slot"]: r for r in tsv("schedule.tsv")}
    records = tsv("receipts.tsv")
    receipts = {r["slot"]: r for r in records}
    require(len(records) == len(receipts) == report["recorded"] == 4112, "Recorded slots")
    require(len(schedule) == report["scheduled"] == 5600, "Scheduled slots")
    outstanding = tsv("outstanding-slots.tsv")
    require(len(outstanding) == 1488 and outstanding == [s for k,s in schedule.items() if k not in receipts], "Outstanding slots")
    seen = set()
    response_ids = set()
    pairs = {}
    for vendor in ("openai", "anthropic"):
        uri = (ROOT / "ledgers" / (vendor + ".sqlite")).as_uri() + "?mode=ro"
        with closing(sqlite3.connect(uri, uri=True)) as db:
            require(db.execute("pragma integrity_check").fetchone() == ("ok",), "Ledger integrity")
            for slot, start, finish, req, res, status, classified, receipt_hash in db.execute(
                "select slot, started, finished, request, response, status, record, receipt_hash from attempts"
            ):
                r, s, c = receipts[slot], schedule[slot], json.loads(classified)
                require(slot not in seen, "Duplicate dispatch")
                seen.add(slot)
                require(r["block"] == str(s["block"]) and r["cell"] == s["cell"]
                        and r["requested_model"] == s["model"] and r["vendor"] == vendor, slot)
                require((ROOT/r["request_file"]).read_bytes() == req and sha(req) == r["request_sha256"], slot)
                require((ROOT/r["response_file"]).read_bytes() == res and sha(res) == r["response_sha256"], slot)
                require(r["receipt_sha256"] == receipt_hash and r["class"] == c["class"] and r["http_status"] == str(status), slot)
                require(r["started_utc"] == start and r["finished_utc"] == finish, slot)
                for field, key in (("returned_model","returned_model"),("response_id","response_id"),("output_bytes","answer_bytes"),("stop_reason","stop")):
                    require(r[field] == str(c.get(key, "")), slot)
                if status == 200:
                    response_id = json.loads(res)["id"]
                    require(response_id == r["response_id"] and response_id not in response_ids, slot)
                    response_ids.add(response_id)
                if s["model"] == PRIMARY and s["cell"] in "ABCD":
                    pairs[int(s["block"]), s["cell"]] = c["class"] in {"V0","V2"}
    require(seen == set(receipts) and len(response_ids) == 4109, "Receipt inventory")
    primary = report["models"][PRIMARY]["primary_reversal"]
    probabilities = []
    for direction, high, low in (("shart_reassignment","C","A"),("shams_reassignment","B","D")):
        cells = [(pairs[b,high],pairs[b,low]) for b in range(1,101)]
        counts = Counter(cells)
        up, down = counts[True, False], counts[False, True]
        n = up + down
        p = Fraction(sum(comb(n,i) for i in range(up,n+1)), 2**n)
        probabilities.append(p)
        require(primary["directions"][direction] == {"high_only": up,"low_only": down,"p_one_sided": float(p)}, direction)
        print(f"{direction}: mismatch {sum(h for h,l in cells)}/100, match {sum(l for h,l in cells)}/100, discordant {up}:{down}, exact p = {p}")
    joint = max(probabilities)
    require(float(joint) == primary["p_intersection_union"] and joint <= Fraction(1,20) and primary["status"] == "SUPPORTED", "Primary verdict")
    print(f"PASS: GPT-5.2 bidirectional primary, intersection-union p = {float(joint):.17g}.")
    print("VERIFIED: 4112/5600 slots recorded, 4109 distinct HTTP 200 response IDs, 3 operational outcomes, 1488 untouched.")


if __name__ == "__main__":
    main()
