# 2026-05-10 Codex history cwd alias repair

- rules: R1/R4/R6/R8, E4/E6
- risk: medium, local Codex App visibility metadata changed after SQLite backup
- landing: `scripts/codex-history-cwd-alias.py`, `tests/runtime/test_codex_history_cwd_alias.py`, live `C:\Users\sciman\.codex\state_5.sqlite`
- destination: keep one shared Codex history database while preventing old repo path buckets from splitting repository history

## Findings

- `C:\Users\sciman\.codex\sessions` and `state_5.sqlite.threads` were not missing history; `threads` contained 1616 rows.
- `codex-interop-check.py --quick-launch` passed: all active `threads.model_provider` rows were already in the shared `openai` provider bucket.
- A real `threads.cwd` path alias bucket drift was found and repaired. Current Codex App workspaces use `\\?\D:\CODE\...`, while older rows used `D:\CODE\...`, `D:\OneDrive\CODE\...`, `E:\CODE\...`, and `E:\PythonProject\...` for the same repo names.
- Post-restart user verification showed the native sidebar still looked sparse, so cwd alias drift was not the final root cause of the visible App sidebar issue. The final visible-sidebar root cause is documented in `docs/change-evidence/2026-05-10-codex-history-view-pagination-root-cause.md`.

## Commands

- `python -m unittest tests.runtime.test_codex_history_cwd_alias -v`
- `python scripts/codex-interop-check.py --codex-home "$env:USERPROFILE\.codex" --cc-switch-db "$env:USERPROFILE\.cc-switch\cc-switch.db" --cockpit-home "$env:USERPROFILE\.antigravity_cockpit" --quick-launch`
- `python scripts/codex-history-cwd-alias.py --codex-home "$env:USERPROFILE\.codex" --alias "<old-cwd>=>\\?\D:\CODE\<repo>" ...`
- `python scripts/codex-history-cwd-alias.py --codex-home "$env:USERPROFILE\.codex" --alias "<old-cwd>=>\\?\D:\CODE\<repo>" ... --apply`

## Evidence

- Unit test result: 2 tests passed.
- Provider-bucket check result: `status = "pass"`, distribution `{ "openai": 1615 }`.
- Live repair backed up SQLite state to `C:\Users\sciman\.codex\backups\state_5.sqlite.20260510_150729_cwd_alias.bak`.
- Live repair updated `783` `threads.cwd` rows and did not rewrite transcript JSONL, messages, accounts, provider config, or auth.
- Post-repair canonical current-workspace counts:
  - `\\?\D:\CODE\governed-ai-coding-runtime`: `368`
  - `\\?\D:\CODE\skills-manager`: `244`
  - `\\?\D:\CODE\ClassroomToolkit`: `535`
  - `\\?\D:\CODE\vps-ssh-launcher`: `36`
  - `\\?\D:\CODE\github-toolkit`: `22`
- `D:\CODE\k12-question-graph` already had only the current canonical bucket and remained unchanged.
- Native App sidebar persistence was not claimed as fixed by this evidence after the restart failed to change the visible grouped list.

## Rollback

- Close Codex App and restore `C:\Users\sciman\.codex\backups\state_5.sqlite.20260510_150729_cwd_alias.bak` to `C:\Users\sciman\.codex\state_5.sqlite`.
- Revert `scripts/codex-history-cwd-alias.py`, `tests/runtime/test_codex_history_cwd_alias.py`, and this evidence file from git history if the cwd alias repair workflow is removed.
