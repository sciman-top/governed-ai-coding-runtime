# Operator UI Visual Refresh

## Goal
- Improve the local operator UI at `http://127.0.0.1:8770/?lang=zh-CN` so it reads as a refined operations workbench instead of a plain report page.
- Preserve existing actions, tabs, history, account/provider status, target settings, and bounded file preview behavior.
- Keep runtime performance stable by avoiding external assets, web fonts, frontend frameworks, heavy animation, and polling changes.

## Risk
- Level: low.
- Reason: the implementation changes the HTML renderer's CSS and presentational labels only; it does not change the action allowlist, API routes, runtime flow commands, persistence, target selection, or account/provider switching semantics.

## Changes
- Added a stronger workbench visual system in `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`.
- Refined the header, metric cards, panels, terminal output, table rows, status markers, and Codex/Claude account/provider cards.
- Kept the UI as server-rendered static HTML with inline CSS and existing JavaScript only.

## Verification
- `python -m unittest tests.runtime.test_operator_ui tests.service.test_operator_api`
  - Result: pass, 7 tests.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - Result: pass, `OK python-bytecode`, `OK python-import`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - Result: pass, 78 runtime/service test files, failures=0.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - Result: pass, including schema, dependency baseline, target governance consistency, agent rule sync, pre-change review, and functional effectiveness checks.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - Result: pass, all doctor checks returned `OK`.

## Visual Evidence
- Baseline: `docs/change-evidence/operator-ui-before.png`
- Runtime view after refresh: `docs/change-evidence/operator-ui-after-runtime-v3.png`
- Codex view after refresh: `docs/change-evidence/operator-ui-after-codex.png`
- Claude view after refresh: `docs/change-evidence/operator-ui-after-claude.png`
- Mobile 390px after refresh: `docs/change-evidence/operator-ui-after-mobile.png`

## Compatibility
- No external network dependency was added.
- No JavaScript runtime dependency was added.
- Browser verification showed no horizontal overflow at 390px mobile width.

## Rollback
- Revert `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py` to the previous CSS block and remove this evidence file plus the related screenshots if the visual direction is rejected.
