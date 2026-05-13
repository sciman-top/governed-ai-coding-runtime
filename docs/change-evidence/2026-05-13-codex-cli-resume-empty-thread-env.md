# 2026-05-13 Codex CLI Resume Empty Picker From Parent Thread Env

## Scope
- Landing: live user wrapper `C:\Users\sciman\.local\bin\codex.ps1`, `C:\Users\sciman\.codex\state_5.sqlite`.
- Target: make `codex resume` launched from an existing Codex-controlled shell use the active Cockpit/API provider bucket instead of inheriting the parent App thread.

## Root Cause
- The user-visible `codex resume` picker was empty even though `state_5.sqlite` contained hundreds of current-project rows.
- The active shell had `CODEX_THREAD_ID=019e1dc9-db0c-73c3-8630-8b666a94b564`.
- New nested CLI launches inherited that parent thread id and updated/read the stale `codex_local_access` bucket instead of the active Cockpit API bucket `cmp_1778165666417_1`.
- A second mismatch came from Windows extended cwd strings such as `\\?\D:\CODE\governed-ai-coding-runtime`, while the interactive CLI starts from normal cwd strings such as `D:\CODE\governed-ai-coding-runtime`.

## Changes
- Backed up the live wrapper and SQLite state to:
  - `C:\Users\sciman\.codex\backups\codex-wrapper-thread-env-20260513-043124`
  - `C:\Users\sciman\.codex\backups\history-cwd-normalize-20260513-042743`
- Updated `C:\Users\sciman\.local\bin\codex.ps1` to remove `Env:CODEX_THREAD_ID` before running the preflight repair and native Codex binary.
- Normalized `threads.cwd` values by removing the Windows extended path prefix.
- Verified no active rows remain in the stale `codex_local_access` bucket after the current preflight/state repair.

## Verification
- `codex --version` with a synthetic inherited `CODEX_THREAD_ID` returned `codex-cli 0.130.0` and left the shell with `CODEX_THREAD_ID` cleared.
- `python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch` returned `status=pass`.
- Current active provider distribution in `state_5.sqlite` is under `cmp_1778165666417_1`, including `cli`, `vscode`, and `exec` rows for `D:\CODE\governed-ai-coding-runtime`.

## Rollback
- Restore `C:\Users\sciman\.local\bin\codex.ps1` and `state_5.sqlite` from `C:\Users\sciman\.codex\backups\codex-wrapper-thread-env-20260513-043124`.
- If only cwd normalization must be undone, restore `state_5.sqlite` from `C:\Users\sciman\.codex\backups\history-cwd-normalize-20260513-042743`.
