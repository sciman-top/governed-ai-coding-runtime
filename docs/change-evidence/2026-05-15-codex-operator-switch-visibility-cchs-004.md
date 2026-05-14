# CCHS-004 Codex Operator Switch Visibility Evidence

## Scope
- Rule ID: CCHS-004
- Risk: low; read-only UI/API projection
- Landing: `scripts/serve-operator-ui.py`, `scripts/operator-ui-service.ps1`, `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui*.py`, `tests/runtime/test_operator_ui.py`
- Target: expose native CLI segmented continuity versus Codex App restart-required status in the operator Codex panel
- Rollback: revert this evidence file and the operator UI/API changes

## Commands
- `python -m unittest tests.runtime.test_operator_ui tests.runtime.test_codex_cockpit_switch_health`
- `python -m py_compile scripts/serve-operator-ui.py scripts/codex-cockpit-switch-health.py`
- `python scripts/serve-operator-ui.py --output .runtime/artifacts/operator-ui/cchs-004-smoke.html --lang zh-CN`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Status`
- `git diff --check`

## Key Output
- UI tests: `Ran 9 tests ... OK`
- Static render: `.runtime/artifacts/operator-ui/cchs-004-smoke.html`
- 8770 service status: `status=running`, `ready=true`, `stale=true`, `url=http://127.0.0.1:8770/?lang=zh-CN`
- Live service refresh/restart: not performed in this slice

## Compatibility
- The `/api/codex/status` payload is enriched with `switch_health` from the read-only CCHS-002 checker.
- The Codex panel renders the switch health as text only: `CLI 分段连续` / `App 需重启落地`, selected account counts, selected plan types, and recent 401/token count.
- No automatic restart button or action was added.
- No Cockpit or Codex config/auth files are written.

## Result
- `pass`: code-level operator visibility and static UI rendering are implemented and verified.
- `pending_live_refresh`: existing 8770 process is stale and needs an explicit operator-approved service refresh before the live page shows this new UI.
