# v0.9 diagnostic-v002: successful loop-guard follow-up

**Source:** user-uploaded `repoguard-v0.9-diagnostic-v002.zip`, recorded 2026-09-25 UTC. This archive is separate from original unsuccessful `medium-v001` and `diagnostic-v001` experiments.

## Original upload contents

| File | SHA-256 of user-uploaded file |
| --- | --- |
| `event-counts.json` | `e4f9f1b4ec60091ea02ce1d846b88e86a48851d2ce621296b6edfd1170cb83f9` |
| `audit.json` | `df08baa141a99c5d209427683f53cc0683e7cd7ae2dc5a465103790dc6361036` |
| `result.json` | `1f591d41931c579359f53ad348d73229dd02ea2e97790e7118eb1299fcd50f55` |

The three JSON files in this GitHub folder reproduce the structured user-supplied evidence using JSON serialization through the connector. Before asserting byte-identical copies, download and compare their SHA-256 values with the original upload hashes above.

## Directly observed diagnostic

The isolated invoice-rounding task reached `fixed` in **four model actions**:

1. Read `invoice.py`.
2. Read `tests/test_invoice.py`.
3. Read `pricing.py`.
4. Proposed a write to `invoice.py`, multiplying each discounted unit price by quantity **before** calling `round_currency`.

The normal-risk change was automatically approved under `auto_low_risk` and its post-write pytest run passed **3 tests** (`returncode: 0`). The audit recorded one proposal, one approval, one automatic verification and no duplicate read, invalid-model-JSON or approval-required event.

## Interpretation and limits

This confirms a **single successful diagnostic** after introducing repeated-read protection and progression guidance. The diagnostic did not actually encounter or block a duplicate read: the model chose a write on step four. The output therefore does **not** establish whether the blocker itself, the revised instructions, or normal generation variability caused this improved outcome. Nor does success on the one invoice task establish performance on the separate pagination and permissions tasks.

## Next

Keep all earlier evidence unchanged. Run a new `medium-v002` three-task benchmark using the current v0.9 branch, inspect per-task statuses and test output, then archive its raw JSONL and summary under a new folder. Never mix easy v0.7/v0.8 results into medium-task percentages.
