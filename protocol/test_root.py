import contextlib
from decimal import Decimal
import io
import itertools
import sqlite3
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import analysis
import experiment as e
import runner as r

OPENAI_MODEL = "gpt-5.4-2026-03-05"
ANTHROPIC_MODEL = "claude-opus-4-6"


def openai(text="", stop="stop", model=OPENAI_MODEL, **msg):
    return {
        "id": "o",
        "model": model,
        "choices": [
            {
                "finish_reason": stop,
                "message": {"role": "assistant", "content": text, **msg},
            }
        ],
        "usage": {"prompt_tokens": 49, "completion_tokens": 80},
    }


def anthropic(parts=None, stop="end_turn", model=ANTHROPIC_MODEL):
    return {
        "id": "a",
        "model": model,
        "role": "assistant",
        "type": "message",
        "stop_reason": stop,
        "content": parts or [],
        "usage": {"input_tokens": 49, "output_tokens": 80},
    }


def classify(body, m=OPENAI_MODEL):
    return e.classify(m, 200, e.pack(body))


class Outcomes(unittest.TestCase):
    def test_void_subtypes(self):
        for data, m, out in [
            (openai(), OPENAI_MODEL, "V0"),
            (openai(None), OPENAI_MODEL, "V2"),
            (openai(None, "length"), OPENAI_MODEL, "V1"),
            (anthropic([{"type": "text", "text": ""}]), ANTHROPIC_MODEL, "V0"),
            (anthropic(), ANTHROPIC_MODEL, "V2"),
            (
                anthropic(
                    [
                        {
                            "type": "thinking",
                            "thinking": "visible only to instrumentation",
                        }
                    ],
                    "max_tokens",
                ),
                ANTHROPIC_MODEL,
                "V1",
            ),
            (anthropic([], "unmapped"), ANTHROPIC_MODEL, "VU"),
        ]:
            with self.subTest(out=out, model=m):
                self.assertEqual(classify(data, m)["class"], out)

    def test_exclusions(self):
        for data, m, out in [
            (openai("", "content_filter"), OPENAI_MODEL, "SB"),
            (openai(refusal="declined"), OPENAI_MODEL, "RF"),
            (openai(tool_calls=[{"id": "id"}]), OPENAI_MODEL, "TC"),
            (anthropic([], "refusal"), ANTHROPIC_MODEL, "RF"),
            (anthropic([], "pause_turn"), ANTHROPIC_MODEL, "CN"),
            (anthropic([{"type": "tool_use"}]), ANTHROPIC_MODEL, "TC"),
            (anthropic([{"type": "unknown_future_stream"}]), ANTHROPIC_MODEL, "PI"),
        ]:
            self.assertEqual(classify(data, m)["class"], out)

    def test_malformed_response(self):
        for status, raw, out in [
            (400, b"", "OP"),
            (0, b"", "OP"),
            (200, b'{"id":"1","id":"2"}', "PI"),
            (200, b"{}", "PI"),
            (200, b'{"x":NaN}', "PI"),
        ]:
            self.assertEqual(e.classify(OPENAI_MODEL, status, raw)["class"], out)

    def test_unicode(self):
        target = e.STR["targets"]["T1"]
        cases = [
            (target, "T1"),
            (e.STR["targets"]["HE"], "HE"),
            (" " + target, None),
            ("شַׁרְט", None),
        ]
        for text, whole in cases:
            rec = classify(openai(text))
            self.assertEqual(rec["whole"], whole)
            self.assertEqual(bytes.fromhex(rec["answer_hex"]), text.encode())
        self.assertIn("T1", classify(openai(" " + target))["embedded"])
        self.assertEqual(classify(openai("شَرْط שָׁרְט"))["mixed_spans"], [])
        self.assertTrue(classify(openai("شَرْط שָׁרְט"))["mixed_anywhere"])
        self.assertIn("شַׁרְט", classify(openai("شַׁרְט"))["known_spans"])
        self.assertIn("شאבכ", classify(openai("شאבכ"))["novel_spans"])
        for text in ["\u200b", " ", "..."]:
            self.assertEqual(classify(openai(text))["class"], "NV")
            self.assertGreater(classify(openai(text))["answer_bytes"], 0)

    def test_wrong_or_drifting_model(self):
        self.assertEqual(classify(openai(model="gpt-4"), OPENAI_MODEL)["class"], "ID")
        seen = {}
        r.track_revision(seen, OPENAI_MODEL, classify(openai(), OPENAI_MODEL))
        with self.assertRaisesRegex(ValueError, "snapshot changed"):
            r.track_revision(
                seen, OPENAI_MODEL, {"class": "R", "returned_model": "other-snapshot"}
            )

    def test_plan(self):
        plan = r.validate_plan()
        self.assertEqual(len(plan), 5600)
        for _, block in itertools.groupby(plan, lambda s: s["block"]):
            self.assertEqual(len({(s["model"], s["cell"]) for s in block}), 56)
        for model in e.VENDORS:
            p = [e.payload(model, c) for c in e.DESIGN["cells"]]
            self.assertEqual(len({e.pack(x) for x in p}), 14)
        self.assertEqual(
            e.envelope(),
            {"anthropic": Decimal("78.848"), "openai": Decimal("44.6208")},
        )
        self.assertEqual(
            e.STR["systems"]["original"].replace(
                e.STR["users"]["shart"], e.STR["users"]["shams"]
            ),
            e.STR["systems"]["reversed"],
        )
        self.assertEqual(
            e.STR["systems"]["original"].replace("\u05c1", ""),
            e.STR["systems"]["undotted"],
        )

    def test_pairing(self):
        a = {i: {"class": "V0"} for i in range(10)}
        b = {i: {"class": "R"} for i in range(10)}
        self.assertEqual(analysis.paired(a, b)["p_one_sided"], 2**-10)
        self.assertEqual(analysis.paired(a, a)["p_one_sided"], 1)

    def test_count_ceiling(self):
        with self.assertRaisesRegex(ValueError, "reservation"):
            r.check_input_sizes(
                "anthropic", "dummy", lambda *a, **k: (200, b'{"input_tokens":513}', {})
            )

    def test_authorization(self):
        with patch(
            "sys.argv",
            [
                "runner.py",
                "run",
                "--vendor",
                "anthropic",
                "--cap-usd",
                "180",
                "--seal-sha256",
                "0" * 64,
            ],
        ):
            with self.assertRaisesRegex(ValueError, "requires --authorize"):
                r.cli()
        with self.assertRaisesRegex(ValueError, "true or false"):
            r.validate_answers(
                e.parse((e.ROOT / "predictions-template.json").read_bytes())
            )

    def test_complete_score(self):
        ans = {m: dict.fromkeys(analysis.QUESTIONS, True) for m in e.VENDORS}
        rows = []
        for slot in e.schedule():
            cell = slot["cell"]
            txt = (
                e.STR["targets"]["T1"]
                if cell == "A"
                else e.STR["targets"]["T0"]
                if cell == "G"
                else "word"
            )
            model = slot["model"]
            text = "" if cell in "BCIKM" else txt
            if e.VENDORS[model] == "openai":
                body = openai(text, model=model)
            else:
                body = anthropic(
                    [{"type": "text", "text": text}] if text else [], model=model
                )
            rec = classify(body, model)
            rows.append((slot, rec))
        scores = analysis.score(rows, ans)
        for model in scores.values():
            self.assertEqual(model["status"], "COMPLETE")
            self.assertTrue(
                all(q["score"] == "MATCH" for q in model["predictions"].values())
            )
        self.assertEqual(
            scores[e.DESIGN["primary_model"]]["primary_reversal"]["status"], "SUPPORTED"
        )
        first = rows[0][0]["model"]
        self.assertEqual(
            analysis.score(rows[1:], ans)[first]["predictions"]["shart_reassignment"][
                "score"
            ],
            "NOT EVALUABLE",
        )


class Persistence(unittest.TestCase):
    def test_shared_token_window(self):
        with contextlib.closing(sqlite3.connect(":memory:")) as db:
            db.executescript(r.SCHEMA)
            reserve = 1536
            for slot, when, record in [
                ("01", "2026-11-21T00:00:00+00:00", None),
                (
                    "02",
                    "2026-11-21T08:00:00+00:00",
                    e.pack(
                        {
                            "usage": {
                                "prompt_tokens": 100,
                                "completion_tokens": 100,
                                "total_tokens": 203,
                            }
                        }
                    ),
                ),
            ]:
                db.execute(
                    "INSERT INTO attempts(slot,started,request,record) VALUES(?,?,?,?)",
                    (slot, when, b"{}", record),
                )
            window = r.TokenWindow(db, 2000, reserve)
            self.assertEqual(window.total, 1739)
            with self.assertRaises(r.AllowancePause):
                window.before_request("2026-11-21T23:59:59+00:00")
            window.before_request("2026-11-22T00:00:00+00:00")
            self.assertEqual(window.total, 203)
            self.assertEqual(
                r.openai_tokens(
                    {
                        "usage": {
                            "prompt_tokens": 9,
                            "completion_tokens": 10,
                            "total_tokens": 15,
                        }
                    },
                    reserve,
                ),
                19,
            )
            self.assertEqual(
                r.openai_tokens({"usage": {"prompt_tokens": 42}}, reserve), reserve
            )

    def test_limit_pauses_before_slot_and_resume(self):
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.object(r, "LOCAL", Path(tmp)),
            patch.object(r, "credential", return_value="dummy"),
        ):
            answers = {m: dict.fromkeys(analysis.QUESTIONS, False) for m in e.VENDORS}
            p = Path(tmp) / "answers.json"
            p.write_bytes(e.pack(answers))
            with contextlib.redirect_stdout(io.StringIO()):
                r.seal(p)
            seal = e.digest((Path(tmp) / "seal.json").read_bytes())
            slots = [
                next(s for s in e.schedule() if s["model"] == model)
                for model in e.DESIGN["rates_usd_per_million"]["openai"]
            ]
            calls = []

            def mock(m, body, key):
                calls.append(m)
                b = openai(model=m)
                b["id"] = str(len(calls))
                return 200, e.pack(b), {}

            with patch.object(r, "validate_plan", return_value=slots):
                with patch.object(r, "now", return_value="2026-11-21T08:00:00+00:00"):
                    with self.assertRaises(r.AllowancePause):
                        r.run_lane(
                            "openai",
                            Decimal("44.63"),
                            seal,
                            transport=mock,
                            openai_24h_budget=1536,
                        )
                    with self.assertRaises(r.AllowancePause):
                        r.run_lane(
                            "openai",
                            Decimal("44.63"),
                            seal,
                            True,
                            transport=mock,
                            openai_24h_budget=1536,
                        )
                self.assertEqual(r.verify_report()["recorded"], 1)
                self.assertEqual(len(calls), 1)
                with patch.object(r, "now", return_value="2026-11-22T08:01:00+00:00"):
                    r.run_lane(
                        "openai",
                        Decimal("44.63"),
                        seal,
                        True,
                        transport=mock,
                        openai_24h_budget=1536,
                    )
                self.assertEqual(calls, [s["model"] for s in slots])
                self.assertEqual(r.verify_report()["recorded"], 2)

    def test_interrupt_resume_and_tamper(self):
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.object(r, "LOCAL", Path(tmp)),
            patch.object(r, "credential", return_value="dummy"),
        ):
            answers = {m: dict.fromkeys(analysis.QUESTIONS, False) for m in e.VENDORS}
            p = Path(tmp) / "answers.json"
            p.write_bytes(e.pack(answers))
            with contextlib.redirect_stdout(io.StringIO()):
                r.seal(p)
            seal = e.digest((Path(tmp) / "seal.json").read_bytes())
            with self.assertRaises(FileExistsError):
                r.seal(p)
            vendor = "openai"
            cap = Decimal("44.63")
            slots = [s for s in e.schedule() if e.VENDORS[s["model"]] == vendor][:4]
            calls = []

            def mock(m, body, key):
                calls.append(body)
                if len(calls) == 2:
                    raise KeyboardInterrupt()
                b = openai(model=m)
                b["id"] = str(len(calls))
                return 200, e.pack(b), {}

            with patch.object(r, "validate_plan", return_value=slots):
                with self.assertRaisesRegex(ValueError, "digest"):
                    r.run_lane(vendor, cap, "0" * 64, transport=mock)
                with self.assertRaisesRegex(ValueError, "below"):
                    r.run_lane(vendor, Decimal(1), seal, transport=mock)
                with self.assertRaises(KeyboardInterrupt):
                    r.run_lane(vendor, cap, seal, transport=mock)
                r.run_lane(vendor, cap, seal, True, transport=mock)
                report = r.verify_report()
                self.assertEqual(len(calls), 4)
                self.assertEqual(report["recorded"], 4)
                db = r.dbname(vendor)
                with contextlib.closing(sqlite3.connect(db)) as con, con:
                    n = con.execute(
                        "SELECT count(*) FROM attempts WHERE status IS NULL"
                    ).fetchone()[0]
                    self.assertEqual(n, 1)
                    con.execute(
                        "UPDATE attempts SET response=x'01' WHERE slot=?",
                        (slots[0]["slot"],),
                    )
                with self.assertRaisesRegex(ValueError, "SHA-256"):
                    r.verify_report()


class CrossProtocol(unittest.TestCase):
    def test_exact_payloads_and_schedule(self):
        english = "You are the concept the user names. Embody it completely. Output only what the concept itself would say or express."
        inputs = [
            "Be silence.",
            "Be speech.",
            "Be nothing.",
            "Be something.",
            "Be the null.",
            "Be a value.",
        ]
        for model, vendor in e.VENDORS.items():
            for cell, text in zip("IJKLMN", inputs):
                p = e.payload(model, cell)
                user = {"role": "user", "content": text}
                if vendor == "openai":
                    self.assertEqual(
                        p,
                        {
                            "model": model,
                            "service_tier": "default",
                            "max_completion_tokens": 1024,
                            "messages": [{"role": "system", "content": english}, user],
                        },
                    )
                else:
                    self.assertEqual(
                        p,
                        {
                            "model": model,
                            "service_tier": "standard_only",
                            "max_tokens": 1024,
                            "system": english,
                            "messages": [user],
                        },
                    )
        plan = e.schedule()
        for block, rows in itertools.groupby(plan, key=lambda row: row["block"]):
            ranks = [
                e.digest(
                    f"{e.DESIGN['schedule_seed']}|{block}|{r['model']}|{r['cell']}".encode()
                )
                for r in rows
            ]
            self.assertEqual(ranks, sorted(ranks))

    def test_questionnaire_round_trip(self):
        with (
            tempfile.TemporaryDirectory() as tmp,
            contextlib.redirect_stdout(io.StringIO()),
        ):
            out = Path(tmp) / "answers.json"
            with patch(
                "builtins.input",
                side_effect=[
                    "bad",
                    "Y N Y N Y N Y N",
                    "nnnnnnnn",
                    "YYYYYYYY",
                    "NYNYNYNY",
                ],
            ):
                r.questionnaire(out)
            received = e.parse(out.read_bytes())
            r.validate_answers(received)
            self.assertEqual(
                [received[next(iter(e.VENDORS))][q] for q in analysis.QUESTIONS],
                [True, False] * 4,
            )
            with self.assertRaisesRegex(ValueError, "new answer file"):
                r.questionnaire(out)
            self.assertFalse((Path(tmp) / "seal.json").exists())

    def test_same_input_primary(self):
        # Old between-word contrasts B>A and C>D both hold; the fixed-input C>A fails.
        model = e.DESIGN["primary_model"]
        obs = {c: n for c, n in zip("ABCD", (30, 90, 20, 10))}
        empty = classify(openai(model=model), model)
        visible = classify(openai("word", model=model), model)
        rows = [
            (s, empty if int(s["block"]) <= obs.get(s["cell"], 0) else visible)
            for s in e.schedule()
            if s["model"] == model
        ]
        answers = {m: dict.fromkeys(analysis.QUESTIONS, False) for m in e.VENDORS}
        report = analysis.score(rows, answers)[model]
        self.assertEqual(report["primary_reversal"]["status"], "NOT SUPPORTED")
        self.assertFalse(report["predictions"]["shart_reassignment"]["observed"])
        self.assertTrue(report["predictions"]["shams_reassignment"]["observed"])
        self.assertFalse(report["predictions"]["null_value"]["observed"])
        bad = [(rows[0][0], {"class": "OP"})] + rows[1:]
        report = analysis.score(bad, answers)[model]
        self.assertEqual(report["primary_reversal"]["status"], "NOT EVALUABLE")
        self.assertTrue(
            all(q["observed"] is None for q in report["predictions"].values())
        )

    def test_full_offline_workload(self):
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.object(r, "LOCAL", Path(tmp)),
            patch.object(r, "credential", return_value="fixture"),
            patch("socket.socket.connect", side_effect=AssertionError("offline test")),
        ):
            answers = {m: dict.fromkeys(analysis.QUESTIONS, True) for m in e.VENDORS}
            path = Path(tmp) / "answers.json"
            path.write_bytes(e.pack(answers))
            with contextlib.redirect_stdout(io.StringIO()):
                r.seal(path)
            seal = e.digest((Path(tmp) / "seal.json").read_bytes())
            lookup = {
                e.pack(e.payload(m, c)): c for m in e.VENDORS for c in e.DESIGN["cells"]
            }
            calls = {"openai": 0, "anthropic": 0, "token_counts": 0}

            def transport(model, body, key, *, count_only=False):
                if count_only:
                    calls["token_counts"] += 1
                    return 200, b'{"input_tokens":50}', {}
                cell = lookup[body]
                text = (
                    ""
                    if cell in "BCIKM"
                    else e.STR["targets"]["T1"]
                    if cell == "A"
                    else e.STR["targets"]["T0"]
                    if cell == "G"
                    else "word"
                )
                vendor = e.VENDORS[model]
                calls[vendor] += 1
                res = (
                    openai(text, model=model)
                    if vendor == "openai"
                    else anthropic(
                        [{"type": "text", "text": text}] if text else [], model=model
                    )
                )
                res["id"] = f"{vendor}-fixture-{calls[vendor]}"
                return 200, e.pack(res), {}

            for vendor, reserve in e.envelope().items():
                r.run_lane(vendor, reserve, seal, transport=transport)
            report = r.verify_report()
            self.assertEqual(
                calls, {"openai": 2800, "anthropic": 2800, "token_counts": 28}
            )
            self.assertEqual(report["recorded"], 5600)
            for m, entry in report["models"].items():
                self.assertEqual(entry["status"], "COMPLETE")
                self.assertTrue(
                    all(q["score"] == "MATCH" for q in entry["predictions"].values())
                )
                self.assertEqual(entry["cells"]["A"]["T1"], 100)
                self.assertEqual(entry["cells"]["G"]["T1"], 0)
                self.assertEqual(entry["cells"]["A"]["T0"], 0)
                self.assertEqual(entry["cells"]["G"]["T0"], 100)
                self.assertEqual(entry["cells"]["M"]["normal_void"], 100)
                self.assertEqual(entry["cells"]["N"]["normal_void"], 0)
                self.assertEqual(
                    "primary_reversal" in entry, m == e.DESIGN["primary_model"]
                )
            self.assertEqual(
                report["models"][e.DESIGN["primary_model"]]["primary_reversal"][
                    "p_intersection_union"
                ],
                2**-100,
            )


if __name__ == "__main__":
    unittest.main()
