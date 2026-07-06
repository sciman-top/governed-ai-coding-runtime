# Contracts

Repo-owned runtime contracts and domain models live here.

## Source Root
```text
packages/contracts/src/governed_ai_coding_runtime_contracts/
```

## Current Surface
The current package exposes pure-Python contract primitives for:
- task intake, task storage, workflow, and worker coordination
- repo profiles, runtime roots, runtime status, and entrypoint-policy enforcement
- tool governance, subprocess guardrails, write policy, approval, and verification planning
- evidence, replay, delivery handoff, eval traces, and learning-efficiency metrics
- operator queries, operator UI models, control-console read models, and workflow-effect metrics
- host and adapter surfaces for Codex, Claude Code, adapter registry, compatibility, continuity, and clarification governance

## Current Consumers
- `scripts/run-governed-task.py`
- `scripts/host-feedback-summary.py`
- `scripts/serve-operator-ui.py`
- `apps/control-plane/`
- runtime and service tests under `tests/`

## Boundaries
- These models are runtime-only contracts and helper primitives.
- They do not imply ownership of host login, provider switching, or upstream UI state.
- They are kept repo-local first; promotion to a separately versioned package needs explicit dependency, rollout, and compatibility evidence.

## Verification
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

```powershell
python -m unittest discover -s tests/runtime -p "test_*.py"
```
