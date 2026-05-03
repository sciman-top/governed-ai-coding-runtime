# 2026-05-03 Refresh Evidence First After GAP-151

## Rule
- `R1`: current landing point is post-`GAP-151` evidence freshness; target home is the selector-controlled `refresh_evidence_first` recovery posture.
- `R4`: low-risk evidence refresh; target-repo runs are quick daily verification runs and do not request write/apply actions.
- `R8`: record commands, key output, compatibility, rollback, and remaining recovery condition.

## Basis
- `GAP-151` closed the managed-asset queue and rendered `active_task_count=0`.
- `python scripts/select-next-work.py` still returned `next_action=refresh_evidence_first`, `evidence_state=stale`, and `ltp_decision=defer_all` because latest target runs were fresh but still degraded for Codex host posture.
- The correct next action is to refresh target-run evidence and host feedback, not to implement an `LTP-01..06` package.

## Commands And Key Output
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action DailyAll -Mode quick -TargetParallelism 5`: pass; preflight showed `next_action=refresh_evidence_first`, `gate=pass`, `source=fresh`, `evidence=stale`.
- `DailyAll` exported fresh target runs at stamp `20260503191935`: `target_count=5`, `failure_count=0`, `batch_timed_out=false`, `batch_elapsed_seconds=104`.
- Exported target-run evidence:
  - `docs/change-evidence/target-repo-runs/classroomtoolkit-daily-20260503191935.json`
  - `docs/change-evidence/target-repo-runs/github-toolkit-daily-20260503191935.json`
  - `docs/change-evidence/target-repo-runs/self-runtime-daily-20260503191935.json`
  - `docs/change-evidence/target-repo-runs/skills-manager-daily-20260503191935.json`
  - `docs/change-evidence/target-repo-runs/vps-ssh-launcher-daily-20260503191935.json`
- `python scripts/host-feedback-summary.py --assert-minimum --max-target-runs 5`: pass minimum surface; overall `status=attention`, `dimensions_ok=4`, `dimensions_attention=2`, `dimensions_fail=0`, `target_run_freshness=fresh`.
- Latest target-run posture remains degraded for all five target repos: `codex_capability_status=degraded`, `adapter_tier=process_bridge`, `flow_kind=process_bridge`, `unsupported_capabilities=["native_attach"]`.
- `python scripts/verify-evidence-recovery-posture.py --as-of 2026-05-03`: pass; selector remains `next_action=refresh_evidence_first`, `evidence_state=stale`, `ltp_decision=defer_all`; target runs are `fresh` with `degraded_latest_run_count=5`.
- Target repo mutation check after refresh: `D:\CODE\ClassroomToolkit`, `D:\CODE\github-toolkit`, `D:\CODE\skills-manager`, and `D:\CODE\vps-ssh-launcher` remained clean. The control repo only received generated evidence files under `docs/change-evidence/target-repo-runs/`.

## Codex Diagnostics
- `codex --version`: pass; `codex-cli 0.125.0`.
- `codex --help`: pass; command list includes `exec`, `resume`, `debug`, `features`, `mcp`, `plugin`, and no top-level `status` subcommand.
- `codex status`: `platform_na`; exit code `1`, key output `Error: stdin is not a terminal`.
- `codex exec resume --help`: pass as supporting evidence; resume exists but does not prove the native attach status handshake required by this repo.

## Compatibility
- This refresh does not modify target repos and does not change runtime policy, rule files, provider config, MCP config, auth, or login chain.
- The selector is intentionally still conservative: fresh target runs alone do not authorize native attach recovery claims.
- No `LTP-01..06` package is selected or implemented; the selector still returns `ltp_decision=defer_all`.

## Recovery Condition
- The recovery rule remains: a fresh target run must show `codex_capability_status=ready` and `adapter_tier=native_attach`.
- Until that evidence exists, the correct completion statement is: backlog/issue work is complete, but host capability recovery remains attention/degraded and keeps `refresh_evidence_first` active.

## Rollback
- Revert this evidence file and the generated `20260503191935` target-run JSON files.
- Revert regenerated `docs/change-evidence/target-repo-runs/kpi-latest.json`, `docs/change-evidence/target-repo-runs/kpi-rolling.json`, and `docs/change-evidence/target-repo-runs/effect-report-classroomtoolkit.json` if the refresh batch is rejected.
