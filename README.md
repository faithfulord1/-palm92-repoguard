# Palm92 RepoGuard

**Offline-first, human-governed software engineering agent for the Google Gemma 4 Developer Agent Competition**

RepoGuard is designed to turn a compact Gemma 4 model into a repository-aware coding agent that can inspect a codebase, reason about an issue, propose a patch, run tests, assess risk, and produce an auditable evidence trail before a human approves changes.

## Core workflow

Issue → Repository Scan → File Selection → Fix Plan → Patch → Tests → Risk Review → Human Approval → Evidence Report

## Competition hypothesis

A smaller local coding model can become more reliable when it is given:

1. structured repository navigation tools,
2. explicit plan-before-edit behavior,
3. test feedback loops,
4. risk-aware human approval gates,
5. an evidence ledger that records actions and tool outputs.

## MVP v0.1

- Read a local repository
- Search files and symbols
- Inspect relevant source files
- Produce a structured fix plan
- Draft a patch
- Run a controlled test command
- Generate a JSON evidence report
- Require human approval before high-risk changes

## Research questions

1. Does structured repository navigation improve task success compared with plain prompt-only context?
2. Does a plan-before-edit stage reduce unnecessary file modifications?
3. Does test-feedback iteration improve bug-fix success?
4. Does adding a risk gate reduce unsafe or overly broad changes?
5. What is the performance/cost trade-off across Gemma 4 variants?

## Status

Foundation scaffold created September 2026.
