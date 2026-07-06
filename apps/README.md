# Apps

Service-shaped runtime entrypoints and worker scaffolds live here.

## Current Surface
- `control-plane/`
  - `main.py` exposes `/health` and `/operator` routes through `app.py`
  - uses `packages/agent-runtime/service_facade.py` instead of owning a separate policy model
- `workflow-worker/`
  - persists workflow heartbeat metadata through `packages/agent-runtime/persistence.py`
- `agent-worker/`
  - persists worker-ready metadata through the same SQLite-backed metadata store contract
- `tool-runner/`
  - executes governed commands through `governed_ai_coding_runtime_contracts.tool_runner`

## Current Status
- `apps/` is no longer future-only; checked-in service-shaped scaffolds exist today.
- The current active queue is `Continuous-Execution`, but these entrypoints still support boundary extraction, packaging, and local compose experiments rather than replacing the default CLI/operator path.
- Day-to-day operator flow still starts from `run.ps1`, `scripts/operator.ps1`, `scripts/verify-repo.ps1`, and `scripts/governance/preflight.ps1`.

## Boundaries
- These entrypoints are repo-owned scaffolds, not proof that production service deployment is the primary runtime posture.
- Host login/provider switching and adapter-tier claims remain governed by the same repo-local contracts, gates, and evidence model as the CLI path.
- Pair this directory with `infra/local-runtime/` when you need a local compose-backed service-shape experiment.

## Verification
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

```powershell
python apps/control-plane/main.py --route /health
```
