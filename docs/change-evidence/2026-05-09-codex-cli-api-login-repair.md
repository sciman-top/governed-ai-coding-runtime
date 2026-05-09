# 2026-05-09 Codex CLI API login repair

## Scope
- rule_id: `local-codex-cockpit-auth-interop`
- risk: medium, user-local Codex and Cockpit Tools auth/provider state was changed with backups.
- landing: live `C:\Users\sciman\.codex` and `C:\Users\sciman\.antigravity_cockpit`
- destination: direct `codex` / `codex exec` startup should match the current Cockpit Tools Codex API account instead of forcing ChatGPT login.

## Root Cause
- `C:\Users\sciman\.codex\config.toml` had `forced_login_method = "chatgpt"` while Cockpit Tools current Codex account was API-key mode.
- `C:\Users\sciman\.codex\auth.json` was missing after Codex logged out on the mismatch.
- History rows were still bucketed under `cmp_1778165666417_1` while the shared-history strategy expects the built-in `openai` bucket with `openai_base_url` for API relays.

## Actions
- Ran `python scripts\codex-interop-check.py --codex-home C:\Users\sciman\.codex --cc-switch-db C:\Users\sciman\.cc-switch\cc-switch.db --cockpit-home C:\Users\sciman\.antigravity_cockpit --apply`.
- Ran `python scripts\codex-interop-check.py --codex-home C:\Users\sciman\.codex --cc-switch-db C:\Users\sciman\.cc-switch\cc-switch.db --cockpit-home C:\Users\sciman\.antigravity_cockpit --apply --migrate-provider-bucket`.
- Restored Cockpit Tools current API account provider metadata in the per-account detail file without logging secret values; `codex_accounts.json` remains a summary/index and is not the durable provider metadata store.
- Temporarily stopped `cockpit-tools.exe` because restarting Cockpit Tools rewrote the current API account back to `openai_builtin` and removed `api_base_url`.
- Follow-up root cause: Cockpit Tools can import/sync the current API-key account from `C:\Users\sciman\.codex\auth.json`. The governed projection previously wrote only `OPENAI_API_KEY`, so the same account was re-upserted without Base URL/provider metadata.
- Updated `scripts/codex-interop-check.py` and `scripts/Start-CodexShared.ps1` so API-key auth projection includes `base_url`, `api_base_url`, `api_provider_mode`, `api_provider_id`, and `api_provider_name`.
- Added `cockpit_current_api_provider_metadata_restored` repair so `codex-interop-check --apply` can restore a wiped Cockpit API account from matching Codex API key plus live `openai_base_url`.

## Evidence
- `codex login status` reported API-key login.
- `codex exec --skip-git-repo-check "Reply with OK only."` returned `OK`.
- `python scripts\codex-interop-check.py --codex-home C:\Users\sciman\.codex --cc-switch-db C:\Users\sciman\.cc-switch\cc-switch.db --cockpit-home C:\Users\sciman\.antigravity_cockpit` returned `status=pass` after Cockpit Tools was stopped and the account metadata was restored.
- After restarting `cockpit-tools.exe`, the same interop check still returned `status=pass`; the current API account kept `api_provider_mode=custom`, `api_provider_id=cmp_1778165666417_1`, `api_provider_name=35.213.82.91`, and `api_base_url=http://35.213.82.91:8003/v1`.
- Targeted unit tests: `python -m unittest tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_repairs_cc_switch_shared_history_blockers tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_restores_cockpit_api_provider_metadata_from_codex_state tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_refuses_api_account_without_base_url`
- Full gate: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` returned `OK python-bytecode` and `OK python-import`.
- Full gate: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` completed 106 test files with `failures=0`.
- Full gate: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` returned all listed contract checks as `OK`.
- Full gate: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` returned `OK` checks with existing `WARN codex-capability-degraded`.
- History bucket distribution after repair: `openai` for existing shared history plus one current `cmp_1778165666417_1` API account row.
- Live login mode after repair: `forced_login_method=api`, `model_provider=openai`, `openai_base_url=http://35.213.82.91:8003/v1`.

## Backups
- `C:\Users\sciman\.codex\backups\config.toml.20260509_231421_cockpit_provider.bak`
- `C:\Users\sciman\.codex\backups\state_5.sqlite.20260509_231432_provider_bucket.bak`
- `C:\Users\sciman\.antigravity_cockpit\codex_accounts\backups\codex_apikey_8b8853f15e823dc53bd156163035bc78.json.pre-final-provider-restore-*.bak`
- `C:\Users\sciman\.antigravity_cockpit\backups\codex_accounts.json.pre-index-provider-restore-*.bak`

## Residual Risk
- Earlier in the incident, restarting `cockpit-tools.exe` reproduced metadata loss for the current API account. After the auth projection fix, restart verification stayed `pass`.
- The API relay reports websocket `404 Not Found` on `ws://35.213.82.91:8003/v1/responses`, but `codex exec` falls back and completed the test request.

## Rollback
- Restore the listed `config.toml` and `state_5.sqlite` backups to revert Codex live provider/history changes.
- Restore the listed Cockpit account/index backups to revert the current API account metadata edits.
