# Root Matrix cross-protocol results

**The preregistered GPT-5.2 primary bidirectional prerequisite-reversal test passed. Secondary model studies remained incomplete where required by the frozen protocol.**

Sharthok Rayan Pal

Results for the [registered protocol](https://doi.org/10.5281/zenodo.24427738) at [v1.0.0](https://github.com/theonlypal/root-matrix-cross-protocol-preregistration/tree/633898463c02b249698bc1bb08711e29ab1d99a5). The design fixes 14 cells in 100 blocks for each of four hosted model identifiers. Each scheduled slot receives at most one dispatch.

The first dispatch starts at 2026-11-21T21:10:51.623031+00:00 and the last recorded slot finishes at 2026-11-21T22:58:49.653271+00:00. Of 5,600 scheduled slots, 4,112 have verified records, including 4,109 HTTP 200 responses and three operational outcomes. The other 1,488 slots have no dispatch or response.

## Findings

The registered GPT-5.2 bidirectional reversal verdict is **SUPPORTED**. The intersection–union p-value is 3.1554436208840472e-30 at α = 0.05.

| Fixed input | Unmatched-condition-only normal Voids | Matched-condition-only normal Voids | One-sided paired p |
|---|---:|---:|---:|
| شَرْط | 98 | 0 | 3.1554436208840472e-30 |
| شَمْس | 100 | 0 | 7.8886090522101181e-31 |

On `gpt-5.2-2025-12-11`, the fixed input `شَرْط` returned zero visible bytes with a normal stop in 100/100 requests when the rule required `شَمْس` and 2/100 when the rule required `شَرْط`. With `شَمْس` as input, the counts were 100/100 when the rule required `شَرْط` and 0/100 when it required `شَمْس`.

## Coverage and observed classes

| Requested model | Scheduled | Recorded | HTTP 200 | Untouched | Observed classes | Frozen model status |
|---|---:|---:|---:|---:|---|---|
| `gpt-5.2-2025-12-11` | 1,400 | 1,400 | 1,400 | 0 | NV 2, R 788, V0 610 | COMPLETE |
| `gpt-5.4-2026-03-05` | 1,400 | 1,400 | 1,399 | 0 | NV 6, OP 1, R 902, V0 491 | INCOMPLETE |
| `claude-opus-4-5-20251101` | 1,400 | 656 | 655 | 744 | NV 76, OP 1, R 574, RF 1, V2 4 | INCOMPLETE |
| `claude-opus-4-6` | 1,400 | 656 | 655 | 744 | OP 1, R 514, V2 141 | INCOMPLETE |

OpenAI addressed 2,800/2,800 slots. GPT-5.4 slot `04671` has transport status 0. Anthropic recorded 1,312/2,800 slots. Opus 4.6 slot `00947` has transport status 0. Opus 4.5 slot `02624` records HTTP 400 for insufficient API credit. Both transport records preserve an empty body and no returned headers. The Anthropic schedule ends at this checkpoint with 744 untouched slots on each identifier.

V0 and V2 denote normal-stop, zero-visible-byte responses with a present or absent text container, respectively. R denotes a visible response, NV a near-Void, RF an explicit refusal and OP an operational outcome. The evidence measures responses at the hosted API boundary under the specified instructions. Internal token selection and its mechanism are outside the observation.

## Normal-stop outcomes

Each fraction gives normal-stop Voids divided by recorded slots, including operational outcomes in the denominator. Each Arabic cell has 100 scheduled requests. The English comparison pools three null inputs and their three paired controls. The preregistration makes all eight predictions for a model unevaluable if any slot has an operational or invalid record.

| Requested model | شَرْط mismatch, match (C, A) | شَمْس mismatch, match (B, D) | English nulls, controls (I+K+M, J+L+N) | Predictions |
|---|---|---|---|---|
| `gpt-5.2-2025-12-11` | 100/100, 2/100 | 100/100, 0/100 | 298/300, 0/300 | 8/8 MATCH |
| `gpt-5.4-2026-03-05` | 99/100, 0/100 | 100/100, 0/100 | 192/300, 0/300 | 8/8 NOT EVALUABLE |
| `claude-opus-4-5-20251101` | 0/47, 0/47 | 0/47, 0/47 | 4/141, 0/140 | 8/8 NOT EVALUABLE |
| `claude-opus-4-6` | 0/47, 0/46 | 0/47, 0/47 | 141/141, 0/141 | 8/8 NOT EVALUABLE |

## Cell counts

[Cell definitions, output coding and analysis](https://github.com/theonlypal/root-matrix-cross-protocol-preregistration/blob/633898463c02b249698bc1bb08711e29ab1d99a5/study/PROTOCOL.md). The recorded outcomes describe the provider API response, including its termination metadata.

| Identifier | Cell | Recorded / scheduled | V0 | V2 | V1 | VU | Whole dotted T1 | Whole undotted T0 | Other classes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| `gpt-5.2-2025-12-11` | A | 100/100 | 2 | 0 | 0 | 0 | 40 | 0 | R 98 |
| `gpt-5.2-2025-12-11` | B | 100/100 | 100 | 0 | 0 | 0 | 0 | 0 | 0 |
| `gpt-5.2-2025-12-11` | C | 100/100 | 100 | 0 | 0 | 0 | 0 | 0 | 0 |
| `gpt-5.2-2025-12-11` | D | 100/100 | 0 | 0 | 0 | 0 | 3 | 0 | R 100 |
| `gpt-5.2-2025-12-11` | E | 100/100 | 0 | 0 | 0 | 0 | 18 | 0 | R 100 |
| `gpt-5.2-2025-12-11` | F | 100/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 100 |
| `gpt-5.2-2025-12-11` | G | 100/100 | 10 | 0 | 0 | 0 | 0 | 24 | R 90 |
| `gpt-5.2-2025-12-11` | H | 100/100 | 100 | 0 | 0 | 0 | 0 | 0 | 0 |
| `gpt-5.2-2025-12-11` | I | 100/100 | 98 | 0 | 0 | 0 | 0 | 0 | NV 2 |
| `gpt-5.2-2025-12-11` | J | 100/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 100 |
| `gpt-5.2-2025-12-11` | K | 100/100 | 100 | 0 | 0 | 0 | 0 | 0 | 0 |
| `gpt-5.2-2025-12-11` | L | 100/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 100 |
| `gpt-5.2-2025-12-11` | M | 100/100 | 100 | 0 | 0 | 0 | 0 | 0 | 0 |
| `gpt-5.2-2025-12-11` | N | 100/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 100 |
| `gpt-5.4-2026-03-05` | A | 100/100 | 0 | 0 | 0 | 0 | 88 | 0 | R 100 |
| `gpt-5.4-2026-03-05` | B | 100/100 | 100 | 0 | 0 | 0 | 0 | 0 | 0 |
| `gpt-5.4-2026-03-05` | C | 100/100 | 99 | 0 | 0 | 0 | 0 | 0 | OP 1 |
| `gpt-5.4-2026-03-05` | D | 100/100 | 0 | 0 | 0 | 0 | 15 | 0 | R 100 |
| `gpt-5.4-2026-03-05` | E | 100/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 100 |
| `gpt-5.4-2026-03-05` | F | 100/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 100 |
| `gpt-5.4-2026-03-05` | G | 100/100 | 0 | 0 | 0 | 0 | 0 | 26 | R 100 |
| `gpt-5.4-2026-03-05` | H | 100/100 | 100 | 0 | 0 | 0 | 0 | 0 | 0 |
| `gpt-5.4-2026-03-05` | I | 100/100 | 92 | 0 | 0 | 0 | 0 | 0 | NV 6, R 2 |
| `gpt-5.4-2026-03-05` | J | 100/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 100 |
| `gpt-5.4-2026-03-05` | K | 100/100 | 100 | 0 | 0 | 0 | 0 | 0 | 0 |
| `gpt-5.4-2026-03-05` | L | 100/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 100 |
| `gpt-5.4-2026-03-05` | M | 100/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 100 |
| `gpt-5.4-2026-03-05` | N | 100/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 100 |
| `claude-opus-4-5-20251101` | A | 47/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 47 |
| `claude-opus-4-5-20251101` | B | 47/100 | 0 | 0 | 0 | 0 | 1 | 0 | R 47 |
| `claude-opus-4-5-20251101` | C | 47/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 46, RF 1 |
| `claude-opus-4-5-20251101` | D | 47/100 | 0 | 0 | 0 | 0 | 2 | 0 | OP 1, R 46 |
| `claude-opus-4-5-20251101` | E | 46/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 46 |
| `claude-opus-4-5-20251101` | F | 47/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 47 |
| `claude-opus-4-5-20251101` | G | 47/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 47 |
| `claude-opus-4-5-20251101` | H | 47/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 47 |
| `claude-opus-4-5-20251101` | I | 47/100 | 0 | 3 | 0 | 0 | 0 | 0 | NV 15, R 29 |
| `claude-opus-4-5-20251101` | J | 47/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 47 |
| `claude-opus-4-5-20251101` | K | 47/100 | 0 | 1 | 0 | 0 | 0 | 0 | NV 45, R 1 |
| `claude-opus-4-5-20251101` | L | 46/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 46 |
| `claude-opus-4-5-20251101` | M | 47/100 | 0 | 0 | 0 | 0 | 0 | 0 | NV 16, R 31 |
| `claude-opus-4-5-20251101` | N | 47/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 47 |
| `claude-opus-4-6` | A | 46/100 | 0 | 0 | 0 | 0 | 28 | 0 | R 46 |
| `claude-opus-4-6` | B | 47/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 47 |
| `claude-opus-4-6` | C | 47/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 47 |
| `claude-opus-4-6` | D | 47/100 | 0 | 0 | 0 | 0 | 0 | 0 | OP 1, R 46 |
| `claude-opus-4-6` | E | 47/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 47 |
| `claude-opus-4-6` | F | 46/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 46 |
| `claude-opus-4-6` | G | 47/100 | 0 | 0 | 0 | 0 | 0 | 42 | R 47 |
| `claude-opus-4-6` | H | 47/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 47 |
| `claude-opus-4-6` | I | 47/100 | 0 | 47 | 0 | 0 | 0 | 0 | 0 |
| `claude-opus-4-6` | J | 47/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 47 |
| `claude-opus-4-6` | K | 47/100 | 0 | 47 | 0 | 0 | 0 | 0 | 0 |
| `claude-opus-4-6` | L | 47/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 47 |
| `claude-opus-4-6` | M | 47/100 | 0 | 47 | 0 | 0 | 0 | 0 | 0 |
| `claude-opus-4-6` | N | 47/100 | 0 | 0 | 0 | 0 | 0 | 0 | R 47 |

## Author predictions

Each question compares counts strictly. The registered directional significance test applies to GPT-5.2 alone.

| Identifier | Question | Metric | Cells | Counts | Prediction | Observed | Score |
|---|---|---|---|---|---|---|---|
| `gpt-5.2-2025-12-11` | Q1 | normal_void | C > A | 100 / 2 | Yes | Yes | MATCH |
| `gpt-5.2-2025-12-11` | Q2 | normal_void | B > D | 100 / 0 | Yes | Yes | MATCH |
| `gpt-5.2-2025-12-11` | Q3 | normal_void | B > F | 100 / 0 | Yes | Yes | MATCH |
| `gpt-5.2-2025-12-11` | Q4 | T1 | A > G | 40 / 0 | Yes | Yes | MATCH |
| `gpt-5.2-2025-12-11` | Q5 | T0 | G > A | 24 / 0 | Yes | Yes | MATCH |
| `gpt-5.2-2025-12-11` | Q6 | normal_void | I > J | 98 / 0 | Yes | Yes | MATCH |
| `gpt-5.2-2025-12-11` | Q7 | normal_void | K > L | 100 / 0 | Yes | Yes | MATCH |
| `gpt-5.2-2025-12-11` | Q8 | normal_void | M > N | 100 / 0 | Yes | Yes | MATCH |
| `gpt-5.4-2026-03-05` | Q1 | normal_void | C > A | 99 / 0 | Yes | — | NOT EVALUABLE |
| `gpt-5.4-2026-03-05` | Q2 | normal_void | B > D | 100 / 0 | Yes | — | NOT EVALUABLE |
| `gpt-5.4-2026-03-05` | Q3 | normal_void | B > F | 100 / 0 | Yes | — | NOT EVALUABLE |
| `gpt-5.4-2026-03-05` | Q4 | T1 | A > G | 88 / 0 | Yes | — | NOT EVALUABLE |
| `gpt-5.4-2026-03-05` | Q5 | T0 | G > A | 26 / 0 | Yes | — | NOT EVALUABLE |
| `gpt-5.4-2026-03-05` | Q6 | normal_void | I > J | 92 / 0 | Yes | — | NOT EVALUABLE |
| `gpt-5.4-2026-03-05` | Q7 | normal_void | K > L | 100 / 0 | Yes | — | NOT EVALUABLE |
| `gpt-5.4-2026-03-05` | Q8 | normal_void | M > N | 0 / 0 | Yes | — | NOT EVALUABLE |
| `claude-opus-4-5-20251101` | Q1 | normal_void | C > A | 0 / 0 | No | — | NOT EVALUABLE |
| `claude-opus-4-5-20251101` | Q2 | normal_void | B > D | 0 / 0 | No | — | NOT EVALUABLE |
| `claude-opus-4-5-20251101` | Q3 | normal_void | B > F | 0 / 0 | No | — | NOT EVALUABLE |
| `claude-opus-4-5-20251101` | Q4 | T1 | A > G | 0 / 0 | Yes | — | NOT EVALUABLE |
| `claude-opus-4-5-20251101` | Q5 | T0 | G > A | 0 / 0 | Yes | — | NOT EVALUABLE |
| `claude-opus-4-5-20251101` | Q6 | normal_void | I > J | 3 / 0 | No | — | NOT EVALUABLE |
| `claude-opus-4-5-20251101` | Q7 | normal_void | K > L | 1 / 0 | No | — | NOT EVALUABLE |
| `claude-opus-4-5-20251101` | Q8 | normal_void | M > N | 0 / 0 | No | — | NOT EVALUABLE |
| `claude-opus-4-6` | Q1 | normal_void | C > A | 0 / 0 | No | — | NOT EVALUABLE |
| `claude-opus-4-6` | Q2 | normal_void | B > D | 0 / 0 | No | — | NOT EVALUABLE |
| `claude-opus-4-6` | Q3 | normal_void | B > F | 0 / 0 | No | — | NOT EVALUABLE |
| `claude-opus-4-6` | Q4 | T1 | A > G | 28 / 0 | Yes | — | NOT EVALUABLE |
| `claude-opus-4-6` | Q5 | T0 | G > A | 42 / 0 | Yes | — | NOT EVALUABLE |
| `claude-opus-4-6` | Q6 | normal_void | I > J | 47 / 0 | Yes | — | NOT EVALUABLE |
| `claude-opus-4-6` | Q7 | normal_void | K > L | 47 / 0 | Yes | — | NOT EVALUABLE |
| `claude-opus-4-6` | Q8 | normal_void | M > N | 47 / 0 | Yes | — | NOT EVALUABLE |

## Raw evidence

[receipts.tsv](receipts.tsv) maps each of the 4,112 recorded slots to its exact request bytes, response body where captured, timestamps, provider response ID, HTTP status, classification and hashes. [outstanding-slots.tsv](outstanding-slots.tsv) enumerates the 1,488 untouched slots from the frozen schedule. [ledgers/](ledgers/) contains the two original SQLite ledgers with the captured response headers and per-slot evidence. [results.json](results.json) contains the frozen classifier and scorer output.

## Verification

[Verification output](VERIFICATION.txt) includes both exact paired probabilities.

From the root of the results archive, use Python 3.10 or later. The bundled verifier checks the file hashes, replays the frozen classifier and scorer in a temporary directory, matches the raw exports to the ledgers, and recomputes both exact paired tests. Dependency installation requires access to the package or a local wheel. Verification itself runs offline.

```sh
work=$(mktemp -d)
python3 -m venv "$work/venv"
"$work/venv/bin/python" -m pip install -r protocol/requirements.txt
"$work/venv/bin/python" -B verify.py
```

Runtime note. Python 3.9.6 handled the first 64 OpenAI calls and 38 Anthropic calls, and Python 3.14.7 handled subsequent calls and replayed all saved receipts under the registered verifier.
