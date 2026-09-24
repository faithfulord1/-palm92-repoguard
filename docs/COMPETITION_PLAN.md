# Competition Plan

## Track A: Developer Agent Competition
Goal: maximize real software issue resolution while keeping the agent runnable on practical hardware.

### Experiments
1. Baseline: Gemma 4 + issue + repository listing.
2. Structured repository-search tools.
3. Plan-before-edit versus immediate editing.
4. Single-pass patch versus test-feedback repair loop.
5. Ungoverned patching versus risk gate + human approval.

### Metrics
- task success / tests passed
- files inspected
- files modified
- unnecessary edits
- tool calls
- wall-clock latency
- context usage
- human intervention rate
- high-risk actions blocked

## Track B: Paper
Working title:

**RepoGuard: Improving Small Local Software Engineering Agents with Structured Repository Navigation, Verification, and Human-Governed Risk Gates**

### Paper structure
1. Abstract
2. Introduction
3. Related work
4. Method
5. Experimental setup
6. Results
7. Ablations
8. Limitations
9. Conclusion

### Evidence rule
Every experiment preserves model/checkpoint, prompt version, task ID, tool trace, patch, test result, risk decision, latency and final outcome.
