"""Frozen prediction questions and block-paired analysis for the Root Matrix."""

from collections import Counter
from math import comb
from typing import NamedTuple

from experiment import DESIGN, VENDORS


class Comparison(NamedTuple):
    text: str
    high: str
    low: str
    metric: str


# The same definitions drive the questionnaire, seal validation, and scorer.
QUESTIONS = {
    "shart_reassignment": Comparison(
        "With شَرْط as input, will it return empty more often when the rule requires شَمْس than when it requires شَرْط?",
        "C",
        "A",
        "normal_void",
    ),
    "shams_reassignment": Comparison(
        "With شَمْس as input, will it return empty more often when the rule requires شَرْط than when it requires شَمْس?",
        "B",
        "D",
        "normal_void",
    ),
    "rule_removal": Comparison(
        "With شَمْس as input, will the original rule produce more empty answers than removing the rule?",
        "B",
        "F",
        "normal_void",
    ),
    "dotted_output": Comparison(
        "With شَرْط as input, will the exact dotted answer occur more often under the dotted system than under the undotted system?",
        "A",
        "G",
        "T1",
    ),
    "undotted_output": Comparison(
        "With شَرْط as input, will the exact undotted answer occur more often under the undotted system than under the dotted system?",
        "G",
        "A",
        "T0",
    ),
    "silence_speech": Comparison(
        "Will “Be silence.” produce more empty answers than “Be speech.”?",
        "I",
        "J",
        "normal_void",
    ),
    "nothing_something": Comparison(
        "Will “Be nothing.” produce more empty answers than “Be something.”?",
        "K",
        "L",
        "normal_void",
    ),
    "null_value": Comparison(
        "Will “Be the null.” produce more empty answers than “Be a value.”?",
        "M",
        "N",
        "normal_void",
    ),
}
VALID = {"V0", "V1", "V2", "VU", "R", "NV", "RF", "SB", "TC", "CN"}


def normal(record):
    return record["class"] in {"V0", "V2"}


def paired(high, low):
    """One-sided exact sign test of more normal-stop Voids in the high arm."""
    up = sum(normal(r) and not normal(low[b]) for b, r in high.items())
    down = sum(not normal(r) and normal(low[b]) for b, r in high.items())
    discordant = up + down
    probability = (
        sum(comb(discordant, i) for i in range(up, discordant + 1)) / 2**discordant
    )
    return {"high_only": up, "low_only": down, "p_one_sided": probability}


def summarize(records):
    rows = list(records.values())
    visible = [r for r in rows if r["class"] in {"R", "NV"}]
    whole = Counter(r["whole"] for r in visible if r["whole"])
    return {
        "scheduled": DESIGN["repeat"],
        "recorded": len(rows),
        "classes": dict(Counter(r["class"] for r in rows)),
        "returned_models": dict(
            Counter(r["returned_model"] for r in rows if "returned_model" in r)
        ),
        "normal_void": sum(map(normal, rows)),
        "T1": whole["T1"],
        "T0": whole["T0"],
        "whole": dict(whole),
        "embedded_only": dict(Counter(k for r in visible for k in r["embedded"])),
        "mixed_anywhere": sum(r["mixed_anywhere"] for r in visible),
        "mixed_spans": dict(Counter(s for r in visible for s in r["mixed_spans"])),
        "known_whole": dict(
            Counter(r["known_whole"] for r in visible if r["known_whole"])
        ),
        "stop_reasons": dict(Counter(r["stop"] for r in rows if "stop" in r)),
    }


def score(rows, predictions):
    groups = {m: {c: {} for c in DESIGN["cells"]} for m in VENDORS}
    for slot, record in rows:
        group = groups[slot["model"]][slot["cell"]]
        block = int(slot["block"])
        if block in group or not 1 <= block <= DESIGN["repeat"]:
            raise ValueError("Invalid or duplicate block for model and cell.")
        group[block] = record
    results = {}
    for model, cells in groups.items():
        counts = {c: summarize(records) for c, records in cells.items()}
        ready = all(
            len(records) == DESIGN["repeat"]
            and all(r["class"] in VALID for r in records.values())
            for records in cells.values()
        )
        answers = {}
        for key, question in QUESTIONS.items():
            high = counts[question.high][question.metric]
            low = counts[question.low][question.metric]
            expected = predictions[model][key]
            observed = high > low if ready else None
            answers[key] = {
                "predicted": expected,
                "observed": observed,
                "high_cell": question.high,
                "low_cell": question.low,
                "high_count": high,
                "low_count": low,
                "score": "NOT EVALUABLE"
                if not ready
                else "MATCH"
                if observed == expected
                else "MISMATCH",
            }
        entry = {
            "status": "COMPLETE" if ready else "INCOMPLETE",
            "cells": counts,
            "predictions": answers,
        }
        if model == DESIGN["primary_model"]:
            primary = {"status": "NOT EVALUABLE"}
            if ready:
                tests = {}
                for key in ("shart_reassignment", "shams_reassignment"):
                    q = QUESTIONS[key]
                    tests[key] = paired(cells[q.high], cells[q.low])
                p = max(t["p_one_sided"] for t in tests.values())
                primary = {
                    "status": "SUPPORTED"
                    if p <= DESIGN["primary_family_alpha"]
                    else "NOT SUPPORTED",
                    "directions": tests,
                    "p_intersection_union": p,
                }
            entry["primary_reversal"] = primary
        results[model] = entry
    return results
