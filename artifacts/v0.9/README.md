# v0.9 exploratory experiment

This folder is reserved for **new** medium-difficulty multi-file task evidence.
Never edit the archived v0.7 Lite and v0.8 verification evidence.

Each run gets a new folder such as `medium-v001/` containing `tasks.jsonl`
and `summary.json`. If interrupted, keep the partial output and use a
*different* experiment ID for the next run.

Task pack: `benchmarks/v0.9_tasks.json`. The three authored tasks have public
tests inside each isolated fixture and are development experiments, not held-out
evaluation. Do not compare percentages directly with the four easy v0.7/v0.8
tasks. Run checks and manually inspect per-task JSONL, patches and test output
before reporting a verified repair.
