# Root Run Entrypoint And Operator UI UX

## Goal
- Reduce first-use and daily-use friction for `governed-ai-coding-runtime` operators.
- Keep `scripts/operator.ps1` as the real implementation while adding a shorter repository-root path.
- Surface the same short entrypoints directly in the localhost operator UI at `http://127.0.0.1:8770/?lang=zh-CN`.

## Changes
- Added `run.ps1` at the repository root as a scenario-based shortcut.
- Added aliases for the most common operator workflows:
  - `readiness`
  - `ui`
  - `targets`
  - `rules-check`
  - `rules-apply`
  - `daily`
  - `apply-all`
  - `feedback`
- Updated root Chinese/English usage docs and `docs/README.md` to make the shortest path visible before the longer implementation commands.
- Added runtime tests proving the root shortcut help text and `readiness` forwarding behavior.
- Updated the operator UI so the left-side operator bench starts with a recommended-entrypoint section that shows the exact `.\run.ps1 ...` commands and executes through the same allowlisted API.
- Changed localhost UI action execution to call `run.ps1` aliases instead of directly invoking `scripts/operator.ps1`, while keeping `scripts/operator.ps1` as the delegated implementation.
- Added visible blocked-action notes under shortcut cards when the next-work selector blocks a higher-impact action.
- Captured browser verification screenshots:
  - `docs/change-evidence/operator-ui-run-entry-desktop-20260502.png`
  - `docs/change-evidence/operator-ui-run-entry-mobile-20260502.png`

## Risk
- Low. The shortcut delegates to the existing operator script and does not change runtime policy, target catalog, rule sync semantics, or target-repo write behavior.

## Verification
- `python -m unittest tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_root_run_entrypoint_help_succeeds tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_root_run_entrypoint_forwards_aliases`
- `python -m unittest tests.runtime.test_operator_ui tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_ui_server_dry_run_supports_single_target`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\run.ps1 governance-baseline -DryRun`
- Browser check on `http://127.0.0.1:8770/?lang=zh-CN`
  - desktop viewport `1280x900`: no console errors
  - mobile viewport `390x844`: shortcut cards and blocked-action note fit without overlap
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

## Rollback
- Revert `run.ps1`, the README/doc updates, `scripts/serve-operator-ui.py`, `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`, this evidence file, the screenshot artifacts, and the tests updated in `tests/runtime/test_operator_entrypoint.py` / `tests/runtime/test_operator_ui.py`.
