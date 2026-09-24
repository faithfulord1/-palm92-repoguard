# Palm92 RepoGuard

**Offline-first, human-governed software engineering agent for the Google Gemma 4 Developer Agent Competition**

RepoGuard is designed to turn Gemma 4 into a repository-aware coding agent that can inspect a codebase, reason about an issue, propose a patch, run tests, assess risk, and produce an auditable evidence trail with human governance.

## Open the first real Gemma experiment

[Open RepoGuard v0.7.1 adaptive baseline directly in Google Colab](https://colab.research.google.com/github/faithfulord1/palm92-repoguard/blob/main/notebooks/RepoGuard_v0_7_1_Adaptive_Gemma_Baseline.ipynb)

After Colab opens:

1. Choose a GPU runtime.
2. Run the notebook cells from top to bottom.
3. Keep the generated JSONL and summary evidence files unchanged.
4. Use the results for the next RepoGuard experiment.

## Current workflow

Issue → Repository Scan → File Selection → Fix Plan → Patch Preview → Risk Review → Human Approval / Isolated Benchmark Policy → Tests → Evidence Report

## Current project stage: v0.7.1

RepoGuard now includes:

- Gemma 4 Transformers adapter
- bounded autonomous repository tool loop
- repository reading and search
- patch proposals and unified diff previews
- human approval and rejection queue
- isolated benchmark copies
- low-risk benchmark auto-approval only inside isolated copies
- experiment JSONL logging
- automatic CSV and Markdown comparisons
- four controlled Python benchmark tasks
- cloud GPU preflight
- first real Gemma baseline runner
- Colab-ready baseline notebook

## Competition hypothesis

A smaller local coding model can become more reliable when it is given:

1. structured repository navigation tools,
2. explicit plan-before-edit behavior,
3. test feedback loops,
4. risk-aware human approval gates,
5. an evidence ledger that records actions and tool outputs.

## Experiment sequence

1. baseline-v001
2. tools-v001
3. planning-v001
4. verification-v001
5. governance-v001
6. full-repoguard-v001

The same task pack should be used across experiments so architecture changes can be measured rather than guessed.

## Research questions

1. Does structured repository navigation improve task success compared with plain prompt-only context?
2. Does a plan-before-edit stage reduce unnecessary file modifications?
3. Does test-feedback iteration improve bug-fix success?
4. Does adding a risk gate reduce unsafe or overly broad changes?
5. What is the performance/cost trade-off across Gemma 4 variants?

## Evidence

Raw experiment outputs are stored under `artifacts/` during execution. Raw JSONL experiment evidence should be preserved unchanged after each measured run.

## Status

v0.7.1 prepared September 2026. E4B is preferred when sufficient GPU memory is available, with E2B as the lower-memory fallback.
