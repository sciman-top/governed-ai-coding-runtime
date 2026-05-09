# 2026-05-09 Codex switcher interop hardening

- rules: R1/R6/R8, E4/E6
- risk: medium, user-local Codex config and CC Switch sqlite state are persisted but backed up before write
- landing: `scripts/codex-interop-check.py`, `scripts/Optimize-CodexLocal.ps1`, `tests/runtime/test_codex_shared_launcher.py`
- destination: keep `CC Switch` and `Cockpit Tools` responsible for accounts/providers while enforcing the shared Codex history root invariants

## Commands

- `python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit"`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Optimize-CodexLocal.ps1 -Apply`
- `python -m unittest tests.runtime.test_codex_shared_launcher`

## Evidence

- Pre-apply interop check failed on `cc_switch_common_sqlite_home`, `cc_switch_common_log_dir`, and `cc_switch_provider_storage_a2398ca2-ed8f-4219-9d66-24db0cfd8e8e`.
- Apply backed up Codex config to `C:\Users\sciman\.codex\config-backups\config-20260509-123447.toml`.
- Apply backed up CC Switch sqlite state to `C:\Users\sciman\.cc-switch\backups\db_backup_20260509_123447_codex_interop.db`.
- Apply added CC Switch `common_config_codex` `sqlite_home = "C:\\Users\\sciman\\.codex"`, `log_dir = "C:\\Users\\sciman\\.codex\\log"`, and `history.persistence = "save-all"` / `max_bytes = 104857600`.
- Apply removed `disable_response_storage` from the current CC Switch Codex provider config for `RightCode`.
- Post-apply interop check returned `status = "pass"` for CC Switch shared config, CC Switch provider storage, Cockpit account inventory, Cockpit provider inventory, and Cockpit instance shared-state checks.
- Unit test `tests.runtime.test_codex_shared_launcher` passed with temporary CC Switch sqlite repair coverage.

## Rollback

- Restore `C:\Users\sciman\.codex\config-backups\config-20260509-123447.toml` to `C:\Users\sciman\.codex\config.toml`.
- Restore `C:\Users\sciman\.cc-switch\backups\db_backup_20260509_123447_codex_interop.db` to `C:\Users\sciman\.cc-switch\cc-switch.db` if the CC Switch interop repair must be undone.
- Revert `scripts/codex-interop-check.py`, `scripts/Optimize-CodexLocal.ps1`, tests, and docs from git history.
