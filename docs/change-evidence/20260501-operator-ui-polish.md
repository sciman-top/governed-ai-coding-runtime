# Operator UI Polish

## Goal
- Improve the local operator UI so it feels like a refined runtime control console instead of a plain report surface.
- Preserve the existing server-rendered UI model, action allowlist, API routes, status loading, history, target selection, evidence preview, and provider/account switching behavior.
- Keep performance stable by avoiding external assets, web fonts, frontend frameworks, heavy JavaScript, polling changes, or image-based chrome.

## Risk
- Level: low.
- Reason: the change is limited to the operator HTML renderer's visual system and short operator-facing labels, plus matching renderer tests. It does not change runtime commands, persistence, target governance behavior, auth/profile switching semantics, or localhost API routing.

## Changes
- Updated `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`.
- Rebalanced the UI from a one-note teal report style into a neutral operations console with a darker header, refined card elevation, gold/accent detail lines, clearer section hierarchy, and denser but more readable control copy.
- Kept the implementation as inline CSS and existing JavaScript only.
- Updated `tests/runtime/test_operator_ui.py` for the revised bilingual title.

## Visual Evidence
- Runtime view: `docs/change-evidence/operator-ui-after-runtime-polish.png`
- Codex view: `docs/change-evidence/operator-ui-after-codex-polish.png`
- Claude view: `docs/change-evidence/operator-ui-after-claude-polish.png`
- Feedback view: `docs/change-evidence/operator-ui-after-feedback-polish.png`
- Mobile 390px: `docs/change-evidence/operator-ui-after-mobile-polish.png`

## Verification
- Browser inspection at `http://127.0.0.1:8790/?lang=zh-CN`.
- Checked Runtime, Codex, Claude, Feedback, and 390px mobile layouts.
- Browser metric check: `clientWidth=390`, `scrollWidth=390`, `overflow=false`, `cssBytes=16363`.
- `python -m unittest tests.runtime.test_operator_ui tests.service.test_operator_api`
  - Result: pass, 7 tests.

## Compatibility
- No external network dependency was added.
- No image, web font, or JavaScript package dependency was added.
- Existing action ids, API endpoints, local storage keys, and file preview safety boundaries are unchanged.

## Rollback
- Revert `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py` and `tests/runtime/test_operator_ui.py`.
- Remove this evidence file and the `operator-ui-after-*-polish.png` screenshots if the visual direction is rejected.
