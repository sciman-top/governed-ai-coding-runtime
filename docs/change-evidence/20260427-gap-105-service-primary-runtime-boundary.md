# 20260427 GAP-105 Service-Primary Runtime Boundary Batch 1

## Goal
Close `GAP-105` by making execution-like CLI wrapper output carry visible service-boundary evidence while preserving existing control-plane dispatch, API/CLI parity, persistence tests, and wrapper drift guards.

## Scope
- Preserve the existing service-primary route: CLI wrappers dispatch through the control-plane application instead of directly calling the session bridge.
- Project `service_boundary=control-plane` from control-plane responses into wrapper payloads.
- Cover execution-like wrapper paths for attached write governance and attached verification.
- Keep service-primary claims bounded to the current local control-plane facade, not a network service rollout.

## Changed Files
- `scripts/run-governed-task.py`
- `tests/runtime/test_run_governed_task_service_wrapper.py`
- `docs/README.md`
- `docs/backlog/README.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/change-evidence/README.md`
- `docs/change-evidence/20260427-gap-105-service-primary-runtime-boundary.md`
- `docs/plans/README.md`
- `docs/plans/optimized-hybrid-final-state-long-term-implementation-plan.md`

## Closeout Result
- `run-governed-task.py` now preserves the top-level control-plane `service_boundary` field in wrapper payloads.
- `run_attachment_verification` includes the preserved `service_boundary` in its returned payload.
- Service wrapper tests now assert `service_boundary=control-plane` for attached write governance and attached verification paths.
- Existing runtime gates still enforce:
  - service/API parity tests
  - service wrapper drift guard against direct `build_session_bridge_command(` and `handle_session_bridge_command(` calls in `run-governed-task.py`
  - local fallback and service metadata persistence tests

## Verification
Commands:
- `python -m unittest tests.runtime.test_run_governed_task_service_wrapper`
- `python -m unittest tests.service.test_session_api tests.service.test_operator_api tests.service.test_control_plane_cli`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- `git diff --check`

Key output:
- service wrapper tests: `Ran 9 tests ... OK`
- service API tests: `Ran 8 tests ... OK`
- runtime gate: `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`, `Ran 422 tests ... OK (skipped=5)`, `Ran 10 tests ... OK`
- issue rendering: `issue_seed_version=4.4`, `rendered_tasks=89`, `completed_task_count=83`, `active_task_count=6`
- docs gate: `OK active-markdown-links`, `OK backlog-yaml-ids`, `OK gap-evidence-slo`, `OK claim-drift-sentinel`, `OK claim-evidence-freshness`, `OK post-closeout-queue-sync`
- full gate: `OK runtime-build`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`, `OK schema-catalog-pairing`, `OK dependency-baseline`, `OK transition-stack-convergence`, `OK target-repo-governance-consistency`, `OK runtime-doctor`, `OK issue-seeding-render`
- full tests: `Ran 422 tests ... OK (skipped=5)`, `Ran 10 tests ... OK`
- `git diff --check`: no whitespace errors; Git reported CRLF normalization warnings for existing text files

## Residual Risks
- This completes the local service-primary boundary batch, not `GAP-106` live Codex attach continuity.
- The service boundary remains local facade/control-plane shaped; broader HTTP/network deployment remains trigger-based.
- `GAP-106..111` still block complete hybrid final-state certification.

## Rollback
Revert the wrapper payload projection, related tests, and the `GAP-105` status/evidence updates. Runtime wrapper drift guard should remain active.
