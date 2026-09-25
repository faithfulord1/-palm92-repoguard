# v0.9 medium-v001: archived unsuccessful first run

Source: user-uploaded `repoguard-v0.9-medium-v001.zip` from completed
Colab run, collected 2026-09-25 (UTC).

| Original file | SHA-256 |
| --- | --- |
| `summary.json` | `aac3d1ff1babb01bb380fe0902438b24d568a8b78af1c58b324f50f2e2c5e484` |
| `tasks.jsonl` | `74d35e983e71336a88f2463090a71730fcd170de34376f24dab9a3735c2ed8da` |

Reported results: 3 attempted, 0 fixed, all hit 12-step limit,
no proposals, no test results (`null`), and no recorded human interventions.
These outcomes are from the new medium task pack, so they must not be
compared as a controlled measure of the architectural change from v0.8.

**Diagnostic limitation:** Neither original file contains model-generated
actions or the agent audit event stream. It is impossible to conclude from
this archive alone whether the model returned invalid JSON, read files
repeatedly, failed to navigate, or took some other action. A *separate*
instrumented run is required. Never overwrite medium-v001.
