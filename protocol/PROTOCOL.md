# Root Matrix: semantic nulls, prerequisite reversal, and exact rendering

Four provider identifiers, 100 randomized complete blocks, 14 cells per model, 5,600 single-turn requests. The primary model is gpt-5.2-2025-12-11. The other identifiers are gpt-5.4-2026-03-05, claude-opus-4-5-20251101, and claude-opus-4-6. Each block orders all 56 model/cell pairs by SHA-256 of the UTF-8 string seed|block|model|cell, in ascending digest order, using the seed in design.json and decimal block numbers 1–100. Each vendor executes its schedule subsequence in order. Blocks pair observations for analysis. They need not be simultaneous across providers.

## Conditions

strings.json holds every complete system and user message. unicode.json lists the exact bytes and code points. Each request starts a fresh conversation and contains one system instruction and one user message, with the original punctuation, no final newline and no tools. Sampling and reasoning parameters are omitted. Chat Completions uses max_completion_tokens=1024 and service_tier=default. Anthropic Messages uses max_tokens=1024 and service_tier=standard_only. Raw returned identifiers must match the four requested identifiers. The OpenAI ceiling includes reasoning tokens. [Official OpenAI documentation](https://developers.openai.com/api/reference/resources/chat/subresources/completions/methods/create)

| Cells | System | First input | Second input |
|---|---|---|---|
| A, B | Dotted identity, require شَرْط | شَرْط | شَمْس |
| C, D | Dotted identity, require شَمْس | شَرْط | شَمْس |
| E, F | Dotted identity, remove prerequisite clause | شَرْط | شَمْس |
| G, H | Undotted identity, require شَرْط | شَرْط | شَمْس |
| I, J | English embodiment | Be silence. | Be speech. |
| K, L | English embodiment | Be nothing. | Be something. |
| M, N | English embodiment | Be the null. | Be a value. |

The English system is “You are the concept the user names. Embody it completely. Output only what the concept itself would say or express.” Nothing in this system instructs silence.

## Outcomes and analysis

A Void is a model execution returning a successful provider response with exactly zero visible UTF-8 output bytes. Provider termination metadata determines its subtype. Explicit refusals, safety blocks, tool-mediated executions, and transport, protocol, billing, quota, rate-limit, and infrastructure failures are distinct non-Void outcomes.

A normal-stop Void is V0 (empty text container present) or V2 (text container absent). V1 indicates a budget stop and VU an unmapped termination. Nonempty near-Voids, visible answers and excluded outcomes retain their own classes. The classifier receives the requested model, HTTP status and raw response bytes. It has no cell, user input or prediction argument. The scorer joins classified records to the schedule. Each cell reports scheduled slots, observed classes, normal-stop Void counts, whole-answer T1 and T0, embedded occurrences and stop reasons. Complete exact targets in nonexcluded text count independently of termination. No trimming or Unicode normalization occurs. T1 starts with Arabic SHEEN; T0 drops Hebrew U+05C1. English pairs have separate outcomes.

The single primary test is bidirectional reversal in GPT-5.2. C>A holds the user input شَرْط fixed. B>D holds the input شَمْس fixed. Each direction uses a one-sided exact paired sign test across the 100 blocks with ties discarded. Zero discordant pairs gives p=1. The conjunction uses the larger directional p at alpha 0.05. The other models and contrasts are descriptive. Author prediction scoring compares counts strictly: equal counts answer No. A directional prediction can match even if the primary statistical test lacks support. Operational, malformed, identity or ambiguous dispatch records and absent slots retain their scheduled places. Any such slot makes the corresponding model verdicts not evaluable. No outcome-dependent replacements or stopping.

## Local commands

Use Python 3.10 or later with requirements.txt installed. From this directory:

    python3 -B runner.py check
    python3 -B -m unittest -v test_root
    python3 -B runner.py questions
    python3 -B runner.py questions --save ../root-matrix-answers.json
    python3 -B runner.py seal ../root-matrix-answers.json

The fourth command asks the eight code-defined questions for each model and saves the 32 answers to a new file. The fifth creates an exclusive seal binding those answers to SHA256SUMS. Keep the seal digest separately. The local seal records a local UTC time. The intended prospective study requires an independently timestamped public protocol and prediction commitment before live execution.

For a subsequently authorized run, use runner.py run with --vendor, --cap-usd, --confirm-rates, --seal-sha256 and --authorize. Each vendor has 2,800 slots. At the design's frozen rates the full reservations are USD 78.848 for Anthropic and USD 44.6208 for OpenAI before credits. Confirm current rates and allowance before live dispatch. Anthropic checks all 28 input sizes before inference. OpenAI shares one 1,000,000-token rolling 24-hour limit across both identifiers. A smaller --openai-24h-budget reserves capacity for outside usage. Exhausting headroom pauses before dispatch with exit 75. An authorized resume uses the existing ledger and skips every reserved slot including ambiguous dispatches. Byte-preserved request/response evidence and a recomputable per-slot SHA-256 are stored in local/. Only a live run or resume accesses provider credentials. The verify command checks the seal, plan, stored evidence hashes and reclassification, then prints the per-model scoreboard. EVIDENCE.md describes the historical cross-script records.
