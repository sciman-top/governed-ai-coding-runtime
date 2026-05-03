# 2026-05-03 Operator UI Expanded Entrypoints

- Rule ID: `R1/R2/R6/R8`
- Risk: `low`
- Scope:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
  - `scripts/serve-operator-ui.py`
  - `tests/runtime/test_operator_ui.py`
  - `tests/runtime/test_operator_entrypoint.py`

## Goal

Keep more project operator functions inside `http://127.0.0.1:8770/?lang=zh-CN`, and make the page structure easier to scan from routine verification to target governance and runtime evolution.

## Changes

1. Added UI/API action coverage for `fast_feedback` and `core_principle_materialize`.
2. Surfaced existing evolution actions in the left operator bench:
   - `evolution_review`
   - `experience_review`
   - `evolution_materialize`
   - `core_principle_materialize`
3. Reorganized action groups into:
   - repo verification,
   - target governance,
   - rules and evolution.
4. Updated shortcut copy so quick feedback is clearly separated from delivery readiness.
5. Refined overview copy so the page reads as a unified operator console rather than a set of unrelated panels.

## Commands

```powershell
python -m unittest tests.runtime.test_operator_ui tests.runtime.test_operator_entrypoint
python scripts/serve-operator-ui.py --lang zh-CN --output .runtime/artifacts/operator-ui/index.html
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Restart -UiLanguage zh-CN -Port 8770
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Status -UiLanguage zh-CN -Port 8770
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

## Evidence

- UI regression tests: `Ran 34 tests ... OK`
- Static render: `.runtime/artifacts/operator-ui/index.html`
- Live service: `status=running`, `ready=true`, `stale=false`, `url=http://127.0.0.1:8770/?lang=zh-CN`
- Build: `OK python-bytecode`, `OK python-import`
- Runtime: `Completed 103 test files ... failures=0`
- Contract: `OK functional-effectiveness`, `OK agent-rule-sync`, `OK target-repo-governance-consistency`
- Hotspot: `WARN codex-capability-degraded` only; no new operator UI or gate-command warning
- Desktop browser screenshot: `docs/change-evidence/operator-ui-8770-integrated-entrypoints.png`
- Mobile browser screenshot: `docs/change-evidence/operator-ui-8770-integrated-entrypoints-mobile.png`

## Compatibility

- Existing action IDs remain unchanged.
- New UI action IDs delegate to existing `run.ps1` aliases or `scripts/operator.ps1` actions.
- No target-repo mutation was performed during validation.

## Rollback

Use git history to revert the touched files and remove the evidence/screenshots if the expanded entrypoint layout needs to be backed out.
