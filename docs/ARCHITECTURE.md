# RepoGuard Architecture

## Layer 1: Task intake
Receives a natural-language software issue and repository location.

## Layer 2: Repository intelligence
Provides bounded tools for file enumeration, text/symbol search, file reads, and later code-graph enrichment.

## Layer 3: Gemma 4 reasoning agent
Uses a post-trained Gemma 4 model to identify likely files, plan investigation, request tool calls, draft candidate changes, and interpret test feedback.

## Layer 4: Verification
Runs tests and checks patch scope.

## Layer 5: Governance
Assigns risk based on touched components. High-risk edits require human approval.

## Layer 6: Evidence
Records model actions, tool calls, test results, risks and approval decisions.

## Target differentiator
Most coding-agent benchmarks reward whether a bug is fixed. RepoGuard additionally studies whether small local agents can be made more trustworthy through structured navigation, bounded tools, verification and auditable human governance.
