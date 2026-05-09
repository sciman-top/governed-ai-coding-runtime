# 2026-05-09 Codex openai history bucket and CLI resume

## Scope

- landing: `scripts/Start-CodexShared.ps1`, `scripts/codex-interop-check.py`, `scripts/Optimize-CodexLocal.ps1`, `tests/runtime/test_codex_shared_launcher.py`
- destination: Cockpit Tools Codex auth/API switches share one `C:\Users\sciman\.codex` history database through the built-in `openai` provider bucket; relay/API switches use `openai_base_url` instead of a custom ChatGPT-incompatible provider bucket.
- risk: medium local host config mutation, limited to `C:\Users\sciman\.codex` and Cockpit Tools Codex restart settings, with timestamped backups.

## Commands

- `python -m unittest tests.runtime.test_codex_shared_launcher`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\Optimize-CodexLocal.ps1 -Apply`
- `codex-cockpit-resume --help`
- `codex-cockpit-exec "Reply with OK only."`
- SQLite query-plan probe against `C:\Users\sciman\.codex\state_5.sqlite`

## Evidence

- Root cause: `model_provider=cockpit` was a custom provider bucket. It could show App history, but ChatGPT auth through that custom provider failed on `https://api.openai.com/v1/responses` with missing `api.responses.write` scope. A direct probe with built-in `model_provider=openai` returned `OK`.
- Live repair migrated `threads.model_provider` from `{ "cockpit": 1592, "openai": 1 }` to `{ "openai": 1593 }`.
- Live `codex-cockpit-exec "Reply with OK only."` returned `OK` with `provider: openai`, `profile=shared-cockpit-auth`, and `model_provider=openai`.
- `codex-cockpit-resume --help` now reaches native `codex resume` and the installed resume launchers default to `--all --include-non-interactive` so CLI history includes App/API/non-interactive sessions.
- Live history list query now uses `idx_threads_archived_provider_updated_at_ms` with no temporary sort; probe returned 50 rows in `0.394 ms`.
- Live interop repair created these indexes: `idx_threads_archived_provider_updated_at_ms`, `idx_threads_archived_provider_updated_at`, `idx_threads_archived_updated_at_ms`, `idx_threads_archived_updated_at`.
- Live interop repair rotated `C:\Users\sciman\.codex\log\codex-tui.log` from `791552029` bytes to `139` bytes and moved the old log to `C:\Users\sciman\.codex\log\backups\codex-tui.20260509_163510.log`.
- Repeat live apply is stable: interop actions were only `codex_history_indexes_ensured=ok`, `codex_tui_log_rotation=ok`, and `codex_threads_provider_bucket_migrated=ok updated_rows=0`.
- The native Codex CLI still prints transient Windows process cleanup lines such as `ERROR: The process "<pid>" not found.` during successful runs. The managed launcher now avoids emitting its own stale PID stop errors, but this native CLI message is upstream process cleanup noise, not a history/provider failure.

## Verification

- `python -m unittest tests.runtime.test_codex_shared_launcher` passed.
- `python -m unittest tests.runtime.test_shell_risk_contract` passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\build-runtime.ps1` passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify-repo.ps1 -Check Runtime` passed: 106 test files, failures=0.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\verify-repo.ps1 -Check Contract` passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\doctor-runtime.ps1` passed with existing `WARN codex-capability-degraded`.

## Backups

- `C:\Users\sciman\.codex\config-backups\config-20260509-164223.toml`
- `C:\Users\sciman\.codex\backups\config.toml.20260509_164223_cockpit_provider.bak`
- `C:\Users\sciman\.codex\backups\auth.json.20260509_164223_cockpit_auth.bak`
- `C:\Users\sciman\.codex\backups\state_5.sqlite.20260509_164223_provider_bucket.bak`
- `C:\Users\sciman\.codex\log\backups\codex-tui.20260509_163510.log`

## Rollback

- Restore `config.toml`, `auth.json`, and `state_5.sqlite` from the listed backups to undo the live provider/history migration.
- Re-run `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\Optimize-CodexLocal.ps1 -Apply` after reverting this repo change if the managed launchers need to be restored to the previous behavior.
