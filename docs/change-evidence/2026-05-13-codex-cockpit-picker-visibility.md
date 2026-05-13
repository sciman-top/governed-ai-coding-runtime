# 2026-05-13 Codex/Cockpit Picker Visibility Evidence

## Scope
- Rule ID: `codex-cockpit-api-provider-repair`
- Risk: medium, local Codex auth/config/history projection touches live `~/.codex` state only through the explicit repair path.
- Current landing: `D:\CODE\governed-ai-coding-runtime`
- Target home: `C:\Users\sciman\.codex`

## Cause
The previous check only proved that `state_5.sqlite.threads.model_provider` matched the active Cockpit API provider bucket. Codex App/CLI pickers can still hide rows when picker visibility metadata is not valid, especially `has_user_event` for rows that already have a non-empty `first_user_message`.

## Change
- `scripts/codex-interop-check.py` now reports `codex_history_visibility_metadata`.
- Explicit `--repair-current-cockpit-api-projection` and `--repair-current-cockpit-account-projection` now repair `has_user_event` and missing `thread_source` for active rows in the selected provider bucket when `first_user_message` proves the row is user-visible.
- `docs/runbooks/codex-cockpit-api-provider-repair.md`, `README.md`, and `README.zh-CN.md` now document the provider bucket plus picker visibility invariant.

## Commands
```powershell
python -m unittest tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_flags_hidden_history_visibility_metadata tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_api_projection_repairs_history_visibility_flags
python -m unittest tests.runtime.test_codex_shared_launcher
python scripts/codex-interop-check.py --codex-home C:\Users\sciman\.codex --cc-switch-db C:\Users\sciman\.cc-switch\cc-switch.db --cockpit-home C:\Users\sciman\.antigravity_cockpit --quick-launch --repair-current-cockpit-api-projection --prefer-cockpit-api-account
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
git diff --check
codex exec "Reply exactly: CODEX_API_PICKER_VISIBILITY_OK"
```

## Key Output
- Focused tests: `Ran 2 tests ... OK`
- Shared launcher tests: `Ran 23 tests ... OK`
- Live repair status: `pass`
- Active provider: `cmp_1778165666417_1`
- Thread provider distribution after API smoke: `cmp_1778165666417_1: 1701`
- Picker visibility after API smoke: `active_threads=1701`, `user_message_threads=1656`, `visible_user_event_threads=1656`
- Live repair changed rows this run: `history_rows_changed=0`, `history_visibility_rows_changed=0`
- Build gate: `OK python-bytecode`, `OK python-import`
- Runtime gate: `Completed 113 test files ... failures=0`
- Contract gate: passed schema, dependency baseline, target governance, shell-risk, agent-rule-sync, pre-change-review, and functional-effectiveness checks.
- Hotspot gate: passed with pre-existing `WARN codex-capability-degraded`; this warning is unrelated to the API provider/history picker repair and points at native attach/status handshake support.
- `git diff --check`: exit code `0`; only CRLF normalization warnings were printed.
- API smoke: `codex exec` returned `CODEX_API_PICKER_VISIBILITY_OK` with provider `cmp_1778165666417_1`.

## Backups
The live repair created timestamped backups:
- `C:\Users\sciman\.codex\backups\config.toml.20260513_233631_cockpit-api-projection.bak`
- `C:\Users\sciman\.codex\backups\auth.json.20260513_233631_cockpit-api-projection.bak`
- `C:\Users\sciman\.codex\backups\state_5.sqlite.20260513_233631_cockpit-api-projection.bak`

## Rollback
Restore the three backup files together, then rerun:

```powershell
python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch
```
