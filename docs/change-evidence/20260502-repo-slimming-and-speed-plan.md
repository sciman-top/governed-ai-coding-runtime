# 2026-05-02 Repo Slimming And Coding Speed Plan

## Rule
- `R1`: current landing point is planning only; target home is a bounded repo-slimming and coding-speed optimization lane.
- `R4`: file deletion, evidence movement, and gate behavior changes are deferred until a task has dry-run proof, rollback, and focused verification.
- `R8`: this entry records the basis, commands, evidence, compatibility, and rollback for creating the plan.

## Basis
- A read-only repository inventory showed that active work surfaces and historical evidence are mixed together.
- The largest surface is `docs/change-evidence/`, which should remain traceable but should not be part of default agent exploration.
- The largest maintenance hotspots include `scripts/runtime-flow-preset.ps1`, `scripts/verify-repo.ps1`, and `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`.
- Existing repo-map context shaping already targets a bounded token budget, so the right next step is separation and routing rather than blanket deletion.

## Commands
- `git status --short`
- `rg --files`
- PowerShell read-only inventory over `rg --files`, excluding `.git`, `.pytest_cache`, `.tmp`, `.runtime`, `.worktrees`, and `.playwright-mcp`.
- `Get-Content docs/change-evidence/repo-map-context-artifact.json`
- `Get-Content .governed-ai/repo-map-context-shaping.json`
- `Get-Content docs/change-evidence/runtime-test-speed-latest.json`
- `Get-Content docs/change-evidence/target-repo-runs/kpi-latest.json`

## Key Output
- Approximate visible repository surface: `1110` files and `15.03 MB`.
- Approximate text surface: `1078` files and `160900` lines.
- `docs/`: about `734` files, `10.10 MB`, and `82020` text lines.
- `docs/change-evidence/`: about `543` files, `8.75 MB`, and `55793` text lines.
- PNG evidence and root screenshots: about `26` files and `6.44 MB`.
- Repo-map artifact: `selected_file_count=31`, `estimated_token_cost=5988`, `max_tokens=6000`, `decision=keep`.
- Current worktree already had unrelated uncommitted managed-asset cleanup changes, so this slice is restricted to planning artifacts.

## Changes
- Added `docs/plans/repo-slimming-and-speed-plan.md`.
- Updated `docs/plans/README.md` to list the new active planning lane.

## Compatibility
- No runtime behavior changed.
- No evidence files were moved or deleted.
- No rule source or distributed rule file changed.
- No gate command changed.

## Verification
- Documentation-only planning slice.
- Alternative verification: confirm new plan and evidence are present and reviewable.

## Rollback
- Delete `docs/plans/repo-slimming-and-speed-plan.md`.
- Delete this evidence file.
- Revert the `docs/plans/README.md` index entry.
