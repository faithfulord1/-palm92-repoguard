# Palm92 RepoGuard — Gemma 4 Developer Agent Competition: Locked Planning Reference

Recorded: 2026-09-25. Preserve this as a planning reference for future project sessions. **The competition organiser may amend requirements and deadlines. Recheck the official page before registering or submitting.**

## Official competition

- Competition: Google — The Gemma 4 Developer Agent Competition
- Organiser: Google DeepMind; hosted on Kaggle
- Official page: https://www.kaggle.com/competitions/gemma-4-developer-agent
- Goal: post-train / configure a Gemma 4 software-engineering agent that can navigate code repositories, draft fixes, and submit patches for validation.
- Entry: sign in to Kaggle, click **Join Competition** and accept the rules. **The user has not yet confirmed that registration is complete.** A GitHub repository or working Colab experiment does not constitute entry.
- Paper track: optional, with separate sign-up / submission.
- Rules reviewed on 2026-09-25.

## Official milestones (11:59 p.m. UTC, unless the organiser changes them)

- 2026-09-23: competition opened.
- 2026-11-12: optional research-paper deadline (paper track requires separate registration).
- 2026-11-25: entry deadline and team-merger deadline; accept competition rules before this date.
- 2026-12-02: final agent submission deadline.

**Internal target, not an organiser deadline or delivery guarantee:** prepare a submission-ready RepoGuard by **2026-10-31**, leaving November for validation, revisions and final submission.

## Submission requirements verified from official Kaggle overview (as of 2026-09-25)

- Submission must be a `submission.zip` containing an ADK-compatible agent configuration with root-level **`agent.yaml`**. System prompts, skills, custom subagents, and PEFT LoRA adapters are optional components subject to organiser rules.
- At present, the ONLY supported base model for all agents and subagents is **`gemma-4-31b-it-qat-w4a16-ct`**.
- The competition harness exposes specified tools including `run_command`, `read_file`, `edit_file`, `write_file`, `submit_patch`, `get_status`, `get_code_neighbors`, `search_similar_code`, and `get_code_subgraph`; custom tools outside the supported harness or permitted agent_tool configuration cannot simply be copied from RepoGuard's current Python runtime.
- The scoring metric is patch validation on issue repositories (PASS/FAIL); the agent has a combined **12-hour budget** for all issue patches, including sandbox setup, excluding validation time.
- Submission format, model requirements, sandbox restrictions, testing harness, and timeline must be rechecked against the official Kaggle rules and HARNESS_README before final packaging.

## RepoGuard project and evidence status

- GitHub repository: https://github.com/faithfulord1/palm92-repoguard
- Development branch: `v0.9-hard-benchmarks`
- v0.7 Lite is a locked initial **four-easy-task** baseline: 1/4 fixed (25%), 50% test pass, 11.75 mean steps, 193.2126 seconds mean latency.
- v0.8 verification uses the SAME original four easy tasks with `google/gemma-4-E4B-it` (4-bit) on a Colab T4, and measured 4/4 fixed, 100% test pass, 4.75 mean steps, 133.1837 seconds mean latency. A single small run; do not generalise the rates to difficult tasks.
- v0.9 uses a DIFFERENT three-medium-task pack (invoice rounding, pagination, hierarchical permissions). Initial `medium-v001`: 0/3 fixed, all reached 12 steps, no proposals, no test results. Keep this archive unchanged.
- The one-task `diagnostic-v001` exposed repeated reads of `invoice.py`, rather than invalid JSON. The agent was modified on the development branch to discourage and block redundant unchanged-file reads, and the branch gained regression tests.
- The one-task `diagnostic-v002` fixed invoice rounding in four model actions: read `invoice.py`, `tests/test_invoice.py`, `pricing.py`, then proposed and automatically verified a fix; 3 tests passed. One successful run does not establish overall medium-pack reliability or isolate which code change caused the improvement.
- **CURRENT RUN TO COMPLETE:** `medium-v002`, the three-medium-task follow-up. Notebook: https://colab.research.google.com/github/faithfulord1/palm92-repoguard/blob/v0.9-hard-benchmarks/notebooks/RepoGuard_v0_9_Medium_v002_Followup.ipynb
- This notebook has been adjusted to `%cd /content/palm92-repoguard` before the run and evidence-export cells to avoid the previously observed `/content/scripts/... not found` error.
- Do **not** claim medium-v002 has completed unless its actual JSONL/summary evidence has been collected.
- Evidence is intentionally separated by experiment ID. Keep prior raw evidence unchanged, use new IDs for fresh runs, and do not directly compare success percentages from the four-easy-task and three-medium-task sets.
- Current E4B/T4 prototyping is **not** sufficient to establish compliance with the required 31B competition model and ADK harness.

## Work plan with checkpoints

1. **2026-09-25 to 2026-09-30 — Finish the current experiment.** Run medium-v002 in Colab with T4 after installation and CPU fixture checks; save and inspect `artifacts/v0.9/medium-v002/tasks.jsonl` and `summary.json`, and archive the original ZIP. Diagnose failures before further changes.
2. **2026-10-01 to 2026-10-10 — Competition compatibility.** Read the official Kaggle dataset and HARNESS_README, design a root `agent.yaml`, map RepoGuard's tools and governance into allowed ADK/harness features, and plan validation with required `gemma-4-31b-it-qat-w4a16-ct`.
3. **2026-10-11 to 2026-10-20 — Integration and reliability.** Validate code editing, patch submission, test execution, sandbox boundaries, tool interfaces, human governance where supported, and evidence logging within time and compute limits. Separate reproducible local trials from official evaluation.
4. **2026-10-21 to 2026-10-31 — Submission-ready candidate.** Assemble `submission.zip` with root `agent.yaml`, run available compatibility validation, write documentation and instructions, record reproducibility and remaining limitations.
5. **November — Recheck the rules, register if not yet done, iterate, optionally submit research paper by November 12, accept rules by November 25, and submit the final valid agent by December 2.** Aim to complete registration well ahead of the deadline.

## Open decisions / action items

- **Registration status unconfirmed:** ask the user to join Kaggle and verify acceptance of competition rules; do not claim entry occurred.
- **medium-v002 results pending:** the user will run the corrected notebook or use a future Work session after the usage-limit reset; inspect actual collected evidence.
- **31B compute strategy pending:** the Colab T4 experiments use smaller E4B and do not prove that the required 31B competition model will run in the same environment.
- **Official harness inspection pending:** obtain and read the competition's HARNESS_README/data and verify actual submission schema/tools before creating final package.
- **Submission status:** not submitted. Internal October 31 date is a milestone, not a promise.

This record captures the user's request to keep all relevant project milestones, deadlines, requirements, links, and next steps in one durable, versioned GitHub document.
