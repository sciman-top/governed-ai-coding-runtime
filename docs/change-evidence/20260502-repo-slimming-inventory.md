# 2026-05-02 Repo Slimming Inventory

## Rule
- `R1`: current landing point is Task 1 inventory and safety fence for the repo-slimming lane.
- `R4`: this slice is inventory-only and does not authorize deletion, archive movement, or gate weakening.
- `R8`: the inventory output, commands, compatibility, and rollback are recorded here.

## Basis
- The repo-slimming plan requires a machine-readable baseline before any archive or deletion work starts.
- The repository already had unrelated uncommitted slimming-plan files, so this slice stays limited to inventory, test coverage, and evidence output.
- The default repo-map token budget already exists; the missing piece was a durable surface audit that can be compared over time.

## Changes
- Added [audit-repo-slimming-surface.py](/D:/CODE/governed-ai-coding-runtime/scripts/audit-repo-slimming-surface.py) to emit a machine-readable repository surface audit.
- Added [test_repo_slimming_surface.py](/D:/CODE/governed-ai-coding-runtime/tests/runtime/test_repo_slimming_surface.py) to verify script output and CLI behavior.
- Generated [repo-slimming-surface-audit.json](/D:/CODE/governed-ai-coding-runtime/docs/change-evidence/repo-slimming-surface-audit.json).
- Updated [repo-slimming-and-speed-plan.md](/D:/CODE/governed-ai-coding-runtime/docs/plans/repo-slimming-and-speed-plan.md) with exact Task 1 outputs and completion state.

## Commands
- `python -m unittest tests.runtime.test_repo_slimming_surface`
- `python scripts/audit-repo-slimming-surface.py`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

## Key Output
- Visible work surface excluding transient/runtime/cache directories: `1154` files, `16097152` bytes, `15.35 MB`.
- Text surface: `1123` files, `184362` lines.
- `docs/`: `764` files, `10879267` bytes, `10.38 MB`, `96022` text lines.
- `docs/change-evidence/`: `572` files, `9455870` bytes, `9.02 MB`, `66505` text lines.
- `scripts/`: `90` files, `1136851` bytes, `1.08 MB`, `28959` text lines.
- `tests/`: `102` files, `1064141` bytes, `1.01 MB`, `23739` text lines.
- `packages/`: `51` files, `691838` bytes, `0.66 MB`, `17309` text lines.
- `schemas/`: `89` files, `362184` bytes, `0.35 MB`, `13224` text lines.
- PNG files dominate binary weight: `26` files, `6750541` bytes, `6.44 MB`.
- Top maintained hotspots by line count:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`: `3382` lines
  - `scripts/runtime-flow-preset.ps1`: `2749` lines
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`: `2465` lines
  - `tests/runtime/test_runtime_flow_preset.py`: `2170` lines
  - `tests/runtime/test_target_repo_governance_consistency.py`: `1957` lines
- Transient surfaces are also substantial but already excluded from the active visible baseline:
  - `.runtime`: `5304` files, `20.81 MB`
  - `dist`: `1180` files, `13.54 MB`
  - `.git`: `3980` files, `22.59 MB`
  - `__pycache__`: `237` files, `3.08 MB`

## Safety Fence
- `delete_mode = forbidden_by_default`
- `archive_move_mode = forbidden_by_default`
- Override condition: Task 2 or later must add dry-run proof, rollback, focused verification, and change evidence before archive movement.
- Existing dirty worktree entries remain out of scope unless explicitly adopted by a later slimming task.

## Verification
- Focused test passed: `Ran 2 tests in 10.711s`, `OK`.
- Docs gate passed:
  - `OK active-markdown-links`
  - `OK claim-drift-sentinel`
  - `OK post-closeout-queue-sync`
  - no docs contract failures

## Compatibility
- No runtime behavior changed.
- No file movement or deletion occurred.
- No rule source or hard-gate command changed.
- The audit artifact is additive and can be compared in future slices.

## Rollback
- Delete [audit-repo-slimming-surface.py](/D:/CODE/governed-ai-coding-runtime/scripts/audit-repo-slimming-surface.py).
- Delete [test_repo_slimming_surface.py](/D:/CODE/governed-ai-coding-runtime/tests/runtime/test_repo_slimming_surface.py).
- Delete [repo-slimming-surface-audit.json](/D:/CODE/governed-ai-coding-runtime/docs/change-evidence/repo-slimming-surface-audit.json).
- Revert the Task 1 status updates in [repo-slimming-and-speed-plan.md](/D:/CODE/governed-ai-coding-runtime/docs/plans/repo-slimming-and-speed-plan.md).
