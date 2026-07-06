# Multi-Repo Trial Loop

## Status
Retired.

## Why It Is Retired
This repository no longer manages target-repo rollout, attachment posture, session-bridge flows, or batch apply-all governance. The older multi-repo trial loop is preserved only as historical context for archived evidence under `docs/change-evidence/target-repo-runs/**`.

## What Replaced It
- repo-local verification through `scripts/verify-repo.ps1`
- host-only feedback through `scripts/operator.ps1 -Action FeedbackReport`
- repo-local task/evidence generation through `scripts/run-governed-task.py`

## Historical Boundary
Historical trial artifacts may still exist for traceability, but they must not be used as proof that multi-repo rollout remains a current supported capability.

## Related
- [Host Feedback Loop](./host-feedback-loop.md)
- [AI Coding Usage Guide](../quickstart/ai-coding-usage-guide.md)
