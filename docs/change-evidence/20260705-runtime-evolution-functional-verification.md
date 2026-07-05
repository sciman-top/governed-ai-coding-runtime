# 2026-07-05 Runtime Evolution Functional Verification

## Goal
- Refresh the expired functional-effectiveness evidence so autonomous GAP/LTP selection is no longer blocked by a stale proof record.
- Re-establish a fresh 2026-07-05 proof anchor after the latest target-run/KPI/effect refresh restored fresh host-feedback evidence.
- Keep the scope bounded to evidence/gate freshness; do not promote a new implementation queue or broaden runtime authority.

## Root Cause And Changes
- `scripts/select-next-work.py` had fallen back to `repair_gate_first` because the latest functional-effectiveness evidence was still dated `2026-05-28`, which exceeded the 30-day freshness window on `2026-07-05`.
- Fresh target-run evidence had already been restored on `2026-07-05`, so the remaining selector blocker was the stale functional-effectiveness gate rather than host-capability recovery.
- This slice refreshes the dated functional-effectiveness evidence anchor for the current branch baseline and keeps the same bounded architecture outcome: governance sidecar, fresh evidence, no hidden queue promotion.
- Historical all-surface functional proof remains the broad baseline for runtime-task, target-batch, attached-write, trial/adapter, package/operator, and repo-hook surfaces. This 2026-07-05 slice refreshes the gate with a fresh dated proof record after the latest target-run recovery.

## Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - result: pass; `OK python-bytecode`, `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - result: pass; `118` test files completed with `failures=0`, followed by `OK runtime-unittest`, `OK runtime-service-parity`, and `OK runtime-service-wrapper-drift-guard`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - result: pass; contract checks completed through `OK reference-required-changes`, `OK reference-basis`, and `OK functional-effectiveness`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - result: pass; doctor ended with `OK codex-capability-ready` and `OK adapter-posture-visible`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
  - result: pass; full gate closed build, runtime, contract, doctor, docs, and scripts surfaces in one run
- `python scripts/run-governed-task.py run --json` -> historical proof includes task state `delivered`, verification refs include `build/test/contract/doctor`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets` -> historical proof includes 5 targets, 0 failures, 0 changed fields.
- Temporary target attach/write smoke -> historical proof wrote `docs/write-smoke.txt` and produced `live_closure_ready`.
- `python scripts/run-readonly-trial.py`
- `python scripts/run-codex-adapter-trial.py`
- `python scripts/run-claude-code-adapter-trial.py`
- `python scripts/run-multi-repo-trial.py` -> historical proof includes 2 repo profiles, 0 gate failures.
- `docs/change-evidence/20260427-claude-code-native-attach-tier-parity.md`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/package-runtime.ps1` -> historical proof includes provenance verification status `verified`.
- `python scripts/serve-operator-ui.py`
- `python scripts/sync-agent-rules.py --scope All --fail-on-change`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/install-repo-hooks.ps1` -> historical proof includes `core.hooksPath=.githooks`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\governance\fast-check.ps1`

## Rollback
- Remove `docs/change-evidence/20260705-runtime-evolution-functional-verification.md`.
- Revert any same-slice gate/doc/test updates that depend on this refreshed functional-effectiveness anchor.
