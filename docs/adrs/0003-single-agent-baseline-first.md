# ADR-0003: Single-Agent Baseline First

## Status
Accepted

## Date
2026-04-17

## Context
The temptation for an AI coding platform is to start with multi-agent orchestration. The reviewed governance assets show that policy, evidence, risk, and replayability are already hard problems before parallel autonomy is added.

## Decision
Phase 1 will implement a governed single-agent baseline with:
- bounded tool use
- explicit approval pauses
- verification gates
- evidence capture
- rollback references

Subagents, if later introduced, will only run behind hard guards and evidence requirements.

## Alternatives Considered
### Multi-agent from day one
- Pros: stronger demo of autonomy and scale
- Cons: higher coordination complexity, weaker accountability, harder rollback paths
- Rejected: wrong order of complexity

### Human-only workflow without agent execution
- Pros: simplest control model
- Cons: does not validate the product thesis
- Rejected: insufficient to prove governed AI coding value

## Consequences
- faster validation of core runtime loop
- clearer debugging and evidence model
- better base for later parallelism and subagent policy
