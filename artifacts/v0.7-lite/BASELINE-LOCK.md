# Locked Baseline Evidence: v0.7 Lite

These files are the raw, unedited evidence from the first real Palm92 RepoGuard Gemma 4 benchmark run.

## Run identity

- Experiment: `baseline-lite-v001`
- Model: `google/gemma-4-E4B-it`
- Variant: `e4b-4bit`
- Prompt version: `v0.7-lite`
- GPU used: Tesla T4, 14.6 GB visible VRAM
- Tasks: 4

## Frozen baseline metrics

- Fixed: 1/4
- Fix rate: 25%
- Test pass rate: 50%
- Average steps: 11.75
- Average latency: 193.2126 seconds
- Human intervention rate: 0%
- Proposals created: 5
- Proposals approved: 5
- Proposals rejected: 0

## Evidence policy

The JSONL and summary files in this folder are treated as immutable raw evidence.
Future experiments must use new filenames and experiment IDs rather than modifying these files.

## v0.8 hypothesis

The first baseline shows a verification/stopping weakness:
- one task passed tests but still ended at the maximum step count
- one task edited code but still failed tests
- one task never produced a patch
- one task completed successfully

v0.8 therefore focuses first on automatic post-write verification and verified stopping before adding broader capabilities.
