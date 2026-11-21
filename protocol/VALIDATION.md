# Offline validation

The regression suite exercises native-format synthetic responses across the frozen schedule, prediction entry, seal binding, same-input contrasts, exact byte identity, error handling, paired tests, spend and token guards, interrupted dispatch, and evidence tampering. The end-to-end test supplies a mock transport, denies socket connections, stores synthetic receipts in a temporary directory, and re-verifies them from SQLite. For the historical response replay run replay.py with the pinned research-source checkout directory. No fixture answers are author predictions.

The full fixture run covers 2,800 OpenAI completions, 2,800 Anthropic completions and 28 Anthropic input-count fixtures. The primary regression distinguishes the fixed-input contrasts C>A and B>D from the between-word contrasts B>A and C>D.
