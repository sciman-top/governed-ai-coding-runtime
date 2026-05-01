# 2026-05-01 Operator UI Entrypoint Integration

- Rule ID: `R1/R2/R6/R8`
- Risk: `low`
- Scope:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
  - `scripts/serve-operator-ui.py`
  - `tests/runtime/test_operator_ui.py`

## Goal

Keep more of the project's operator-facing entrypoints inside `http://127.0.0.1:8770/?lang=zh-CN`, and make the first screen read like a workbench instead of a loose collection of panels.

## Changes

1. Added a `控制台总览 / Workbench Overview` section under the tab strip so `Runtime / Codex / Claude / 反馈` can be opened from the main page directly.
2. Reworked the `Runtime` panel layout into `runtime-shell`:
   - left side for execution output, history, and next-work recommendation,
   - right side for maintenance and attachment state,
   - tasks remain full width below.
3. Promoted the injected `next-work` block into a first-class panel so its recommendation is aligned with the main operator flow.
4. Converted the new overview cards into summary cards:
   - first screen keeps only decision-grade signals,
   - detailed Codex / Claude / Feedback content stays in each tab,
   - cards hydrate from cached or live panel data instead of duplicating whole panels.
5. Grouped sidebar actions into page actions, common actions, and governance changes to reduce scan noise.
6. Added UI regression assertions for the overview cards, runtime shell structure, and overview panel switching.

## Commands

```powershell
python -m unittest tests.runtime.test_operator_ui
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Restart -UiLanguage zh-CN -Port 8770
```

## Evidence

- Build: `OK python-bytecode`, `OK python-import`
- Runtime: `Completed 94 test files ... failures=0`
- Contract: `OK functional-effectiveness`
- Hotspot: `WARN codex-capability-degraded` only; no new UI regression signal
- Browser verification:
  - before: `docs/change-evidence/operator-ui-before-entrypoint-integration.png`
  - after: `docs/change-evidence/operator-ui-after-entrypoint-integration.png`
  - summary-card final: `docs/change-evidence/operator-ui-after-summary-cards.png`
  - live URL: `http://127.0.0.1:8770/?lang=zh-CN`

## Compatibility

- No API route changes.
- No operator action identifier changes.
- Existing `Runtime / Codex / Claude / 反馈` tabs remain intact; this change only improves discoverability and layout.

## Rollback

Use git history to revert the touched files once the commit SHA is known:

```powershell
git restore --source=<known-good-commit> -- packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py scripts/serve-operator-ui.py tests/runtime/test_operator_ui.py docs/change-evidence/20260501-operator-ui-entrypoint-integration.md
```
