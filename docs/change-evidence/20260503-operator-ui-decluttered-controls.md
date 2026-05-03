# 2026-05-03 Operator UI Decluttered Controls

- Rule ID: `R1/R2/R6/R8`
- Risk: `low`
- Scope:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
  - `tests/runtime/test_operator_ui.py`

## Goal

Keep the expanded operator functions available at `http://127.0.0.1:8770/?lang=zh-CN` without making the page feel overloaded.

## Changes

1. Merged the previous standalone recommended-entry panel into the unified operator bench.
2. Kept only two first-screen recommendations:
   - daily fast feedback,
   - delivery readiness.
3. Left repo verification expanded by default.
4. Collapsed lower-frequency or higher-risk groups by default:
   - target governance,
   - rules and evolution,
   - advanced run parameters.
5. Kept all previously integrated actions available through the same page and `/api/run` path.

## Commands

```powershell
python -m unittest tests.runtime.test_operator_ui tests.runtime.test_operator_entrypoint
python scripts/serve-operator-ui.py --lang zh-CN --output .runtime/artifacts/operator-ui/index.html
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Restart -UiLanguage zh-CN -Port 8770
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

## Evidence

- UI regression tests: `Ran 34 tests ... OK`
- Static render: `.runtime/artifacts/operator-ui/index.html`
- Live URL: `http://127.0.0.1:8770/?lang=zh-CN`
- Build: `OK python-bytecode`, `OK python-import`
- Runtime: `Completed 103 test files ... failures=0`
- Contract: `OK functional-effectiveness`, `OK agent-rule-sync`, `OK target-repo-governance-consistency`
- Hotspot: `WARN codex-capability-degraded` only; no new operator UI or gate-command warning
- Desktop browser screenshot: `docs/change-evidence/operator-ui-8770-decluttered-desktop.png`
- Mobile browser screenshot: `docs/change-evidence/operator-ui-8770-decluttered-mobile.png`

## Compatibility

- No action identifiers were removed.
- No API routes changed.
- Existing high-risk actions remain available but no longer occupy the default first screen.

## Rollback

Use git history to revert the touched files and remove this evidence/screenshots if the compact control layout needs to be backed out.
