# Preserved cross-script executions

The GitHub inventory on November 21, 2026 covers 152 owner-visible repositories. The November 7 synthesis has its own DOI and source manifest. The three 40-response cross-vendor pilots are separate GitHub evidence sets. Their repositories are absent as primary source pins from that manifest. A search for a DOI explicitly synthesizing these three pilots found no match. That search cannot establish absence from every publication. [Synthesis](https://doi.org/10.5281/zenodo.24044104) · [Manifest](https://github.com/theonlypal/shart-identity-condition-continuation/blob/289301f49c5e3087735825ced4adacaa34633153/source-manifest.json)

## The three pilots

Each pilot has 15 matched, 15 mismatched and 10 rule-removed trials. Every response below has a normal provider stop. A row counts the entire decoded final-answer text in UTF-8. Google thought parts and Kimi reasoning fields are separate provider channels.

| Returned identifier | Matched normal-stop Voids | Mismatched normal-stop Voids | Removed normal-stop Voids | Entire dotted hybrid T1 | Other evidence |
|---|---:|---:|---:|---:|---|
| gemini-3-flash-preview | 0/15 | 0/15 | 0/10 | 1/40 | 11 answers contain both scripts, one contains a same-word hybrid. [Raw pilot](https://github.com/theonlypal/gemini3-crossscript-prerequisite-replication/tree/65bb67b9b535282345e0f73bae95bcee55f2ed5c/runs/pilot-20261012-paid) |
| gemini-3.6-flash | 0/15 | 12/15 V2 | 0/10 | 0/40 | Slot 37 returns a whole hybrid with U+05B7 PATAH; exact T1 uses U+05B8 QAMATS. [Raw pilot](https://github.com/theonlypal/gemini36-crossscript-prerequisite-replication/tree/4c91342383d42dc8eb453b84ef7ca73c99633142/runs/pilot-20261012-paid) |
| kimi-k3 | 0/15 | 1/15 V0 | 0/10 | 0/40 | Slot 29 returns an empty string and reports 353 reasoning tokens. Eight answers contain both scripts in separate words. Three whole answers consist of the three UTF-8 bytes for U+200B. [Raw pilot](https://github.com/theonlypal/kimi-k3-crossscript-prerequisite-replication/tree/43466666e35d0925a164eb1e4ea94dd40d48a51c/data/pilot-20261012) |

## GPT and Claude

| Study | Measured result | Evidence |
|---|---|---|
| GPT-5.4 original condition and rule removal | Exact T1 on 185/200 matched trials. Wrong input with the rule gives 200/200 V0. Removing the rule gives 0/200 V0 for each input. | [800-trial record](https://github.com/theonlypal/gpt-5.4-shrt-prerequisite-gate-analysis/tree/82bdbfb690db7c714d21a8b80f0eb3a1fe25f7a6) |
| GPT-5.4 reassignment | V0 on 200/200 original mismatches and 198/200 reassigned mismatches. Matched cells each give 0/200 V0. | [800-trial record](https://github.com/theonlypal/gpt-5.4-shrt-prerequisite-reassignment-analysis/tree/eb8e39e070c3f4e2b00c5288efe008e2d737b4c3) |
| GPT-5.4 confirmed formation | Dotted T1 4,830/5,120; undotted T0 2,423/5,120 on corresponding primary arms. | [12,160-slot study](https://github.com/theonlypal/gpt-5.4-shrt-cross-script-evidence/tree/76442445abc39d7b4224ad89d4ae5fa5dafc0e39/evidence/study/run/attempts) |
| GPT-5.2 replication | Dotted T1 909/5,120; undotted T0 1,501/5,120. The opposite-direction hybrid (Hebrew initial SHIN in Arabic text) occurs as the whole answer 602 times across this study. | [12,160-slot study](https://github.com/theonlypal/gpt-5.2-shrt-cross-script-replication/tree/ad563eeea8fb18255d76e494a05f394d189282e5/evidence/records/attempts) |
| Opus 4.5 / 4.6 matched Experiment 3 | Whole T1 in 9/600 and 69/600. T1 anywhere, including whole answers, in 197/600 and 115/600. Both models returned nonempty text on all 600 trials. | [1,200 raw responses](https://github.com/theonlypal/opus45-opus46-matched-results/tree/582d3a781510697916498f0189ed22f7d3e9e2b6/exp3/attempts) |

Each 12,160-slot GPT study has 11,820 successful answer envelopes and 340 operational errors; the denominators above include the ten operational errors per primary arm. The exploratory lineage ledger separately lists 61 requested identifiers, including sparse and alias rows. Dense mixed-output counts include 3,171/10,240 for dated GPT-5.2, 2,273/10,240 for GPT-5.3 Chat, 9,092/10,240 for dated GPT-5.4, 37/5,130 for the partial GPT-5.6 Luna sweep and 78/8,660 for partial Terra. Six selected discovery receipts are public; the complete raw exploratory corpus is outside that repository. [Lineage ledger](https://github.com/theonlypal/gpt-5.4-cross-script-artifact/tree/5220e3b10ad75f09a7f4335985c7a52d4c65e70a/results)

## Provenance and coverage

- archive-inventory.json preserves all 61 discovery rows, the requested-to-returned identifier mapping, the source links and per-model tallies in 13 relevant archives, and the outputs of the local 2,920-response replay. The archive tables include primary, preflight, secondary and mirrored records. Adding their denominators would count some responses more than once.
- variants.json identifies 42 distinct historical letter/mark spans and their source examples. Forty-one combine Arabic and Hebrew. One combines Arabic, Latin and Myanmar. Whole answers, embedded spans, words alongside each other and different combining marks have separate measurements.
- The older historical Gemini medial-REH form and the later Antigravity UI return differ from initial-SHEEN T1. The UI transcript contains the medial-REH form in earlier user messages before its return. [UI transcript](https://github.com/theonlypal/antigravity-true-mark-render-20261103/tree/6667bce82e467c183f4878ae28dadc76abf38495)
- The October 29 Void and the Mark repository freezes a four-vendor design including Gemini 4 Argon. Its default tree and releases exposed no completed Study B receipts at inspection. The alignment-and-binding repository exposes 24 preflight envelopes. Counts requiring its missing full-run archives are unavailable. [Frozen four-vendor protocol](https://github.com/theonlypal/void-mark-matrix/tree/34b6bec66875be9e3a4fc0a91985d210ebcb840c) · [Preflight evidence](https://github.com/theonlypal/alignment-and-binding-condition-evidence)
- The inspected raw-source audit independently compared 24,960 extracted final-answer strings across the two main OpenAI studies, Opus Experiment 3 and the pilots. This Root Matrix additionally replays 2,800 historical GPT/Opus receipts through its own classifier and decodes all 120 other-vendor pilot bodies. Historical comparisons retain their original output ceilings, sampling settings, conditions and denominators.
