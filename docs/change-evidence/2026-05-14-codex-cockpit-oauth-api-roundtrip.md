# Codex/Cockpit OAuth API Roundtrip Evidence

- rule_id: `local-codex-cockpit-auth-interop`
- risk: medium local host state mutation
- landing: `scripts/codex-interop-check.py`, `scripts/operator.ps1`, 8770 operator UI, live `C:\Users\sciman\.codex`, live `C:\Users\sciman\.antigravity_cockpit`
- rollback: restore the timestamped backups created under `C:\Users\sciman\.codex\backups` and `C:\Users\sciman\.antigravity_cockpit\backups`

## Commands

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexApiProjectionRepair`
- `codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -o <temp> "只输出 API_PROBE_OK"`
- `python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexOauthProjectionRepair`
- `codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox -o <temp> "只输出 OAUTH_PROBE_OK"`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Test-CodexGuardAbsence.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexProjectionSmoke`
- `node <inline playwright smoke> http://127.0.0.1:8770/?lang=zh-CN`

## Findings

- API switch target: `codex_apikey_8b8853f15e823dc53bd156163035bc78`, provider bucket `cmp_1778165666417_1`, base URL `http://35.213.82.91:8003/v1`, `supports_websockets=false`.
- OAuth switch target: `codex_bb47feac0a97bc1bfafa026915e79c9c`, provider bucket `openai`.
- Existing API repair worked for OAuth -> API: before repair, config/auth/history were still in `openai`; after repair, `codex_thread_provider_distribution`, `codex_live_provider_bucket`, `codex_auth_matches_cockpit_current_account`, and `codex_history_visibility_metadata` all passed for `cmp_1778165666417_1`.
- Real API connectivity passed: `codex exec` returned `API_PROBE_OK` with provider `cmp_1778165666417_1`.
- OAuth return initially failed before the new repair: config/auth/history remained in API mode, and readonly interop reported mismatched `auth_mode`, provider bucket, and history bucket.
- Added explicit one-shot `--repair-current-cockpit-oauth-projection` / `CodexOauthProjectionRepair`; old generic `--repair-current-cockpit-account-projection` remains blocked.
- After OAuth repair, `codex_thread_provider_distribution=openai:1704`, `visible_user_event_threads=1659`, `codex_live_provider_bucket=pass`, and `codex_auth_matches_cockpit_current_account=pass`.
- Real OAuth connectivity passed: `codex exec` returned `OAUTH_PROBE_OK` with provider `openai`.
- Second API -> OAuth roundtrip passed without reintroducing background guard, trigger, generic repair, or launcher wrapper.
- Guard absence check passed: no `codex-cockpit-switch-guard` scheduled task, startup fallback, worker process, or retired installed wrapper.

## Optimization Follow-up

- Consolidated API/OAuth projection JSON writes, backup collection, and `codex_instances.json` follow-current repair into shared helpers.
- Added unique backup path collision handling so repeated repairs in the same second cannot overwrite the earlier backup.
- Added explicit OAuth projection internals; the exposed OAuth path no longer depends on the deprecated generic projection entrypoint.
- Kept deprecated generic write repair blocked and kept old guard/trigger names only in absence checks, cleanup, docs, and tests.
- Replaced broad process enumeration in `scripts\Test-CodexGuardAbsence.ps1` with a WMI `CommandLine LIKE` filter plus fallback; measured check time improved from about `2576 ms` to about `1720 ms` on this host.
- Secret scan only matched test dummy strings and leak-prevention assertions; no live secret was found in the changed scripts, docs, packages, or focused tests.
- Focused tests after refactor: `python -m unittest tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui tests.runtime.test_codex_guard_absence tests.runtime.test_codex_launch_binding_repair tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_blocks_generic_current_account_projection` -> `55 tests OK`.
- Syntax check after refactor: `python -m py_compile scripts\codex-interop-check.py scripts\serve-operator-ui.py` -> pass.
- Guard absence live check after refactor: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Test-CodexGuardAbsence.ps1` -> pass.
- Final optimization roundtrip API repair passed: after `CodexApiProjectionRepair`, `codex_thread_provider_distribution=cmp_1778165666417_1:1704`, `visible_user_event_threads=1659`, `codex_live_provider_bucket=pass`, and `codex_auth_matches_cockpit_current_account=pass`.
- Final optimization API connectivity passed: `codex exec` returned `API_PROBE_OK_OPTIMIZED` with provider `cmp_1778165666417_1`; the known startup noise `ERROR: The process "<pid>" not found.` was still present but did not affect exit code or output.
- Final optimization OAuth repair passed: after `CodexOauthProjectionRepair`, `codex_thread_provider_distribution=openai:1705`, `visible_user_event_threads=1660`, `codex_live_provider_bucket=pass`, and `codex_auth_matches_cockpit_current_account=pass`.
- Final optimization OAuth `codex exec` reached provider `openai` but was blocked by account usage limit, not local projection: `You've hit your usage limit ... try again at May 21st, 2026 2:09 AM`.
- Final readonly state is OAuth: `current_account_id=codex_bb47feac0a97bc1bfafa026915e79c9c`, provider bucket `openai`, `active_threads=1706`, `visible_user_event_threads=1660`, and interop `status=pass`.
- Full project gates after fixes: `scripts\build-runtime.ps1` -> pass; `scripts\verify-repo.ps1 -Check Runtime` -> `114 test files`, `failures=0`; `scripts\verify-repo.ps1 -Check Contract` -> pass; `scripts\doctor-runtime.ps1` -> pass with existing `WARN codex-capability-degraded`.
- During full Runtime gate, `Test-CodexGuardAbsence.ps1` exposed and fixed a process-scan false positive under parallel tests; production default task process scan remains enabled, custom isolated task names skip global process scanning.
- During full Runtime gate, governance hub certification exposed and fixed a concurrent report write race by writing through a unique temporary file before replacement.
- Fresh post-refactor live quick check at `2026-05-14 21:10 +08:00` initially failed only on stale local projection details: `cockpit_saved_api_provider_profiles_projectable` and `cockpit_codex_instances_follow_current_account`. Running `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexOauthProjectionRepair` created backups, did not restart Codex, changed `history_visibility_rows_changed=6`, and the after-state returned `status=pass` with `codex_live_provider_bucket=pass`, `codex_auth_matches_cockpit_current_account=pass`, `cockpit_saved_api_provider_profiles_projectable=pass`, and `cockpit_codex_instances_follow_current_account=pass`.
- Projection repair now treats malformed existing `config.toml` as unsafe to preserve: it keeps a timestamped backup and rebuilds a parseable minimal projection instead of splicing new provider/auth settings into invalid TOML.
- Added focused malformed TOML regression coverage: `test_projection_rebuilds_malformed_toml_into_parseable_config` verifies the repaired config parses through `tomllib`, restores `model_provider=openai`, `forced_login_method=chatgpt`, and writes saved API providers as no-WebSocket custom providers.
- Added `CodexProjectionSmoke` as a read-only operator action and `/api/actions` entry. The action runs `codex-interop-check.py --quick-launch` plus `Test-CodexGuardAbsence.ps1`; it does not pass repair flags, `--apply`, or `--migrate-provider-bucket`.
- Live `CodexProjectionSmoke` passed at `2026-05-14 21:25 +08:00`: interop `status=pass`, `codex_live_provider_bucket=pass`, `codex_auth_matches_cockpit_current_account=pass`, `cockpit_saved_api_provider_profiles_projectable=pass`, `cockpit_codex_instances_follow_current_account=pass`, and guard absence `status=pass`.
- The 8770 operator UI was refreshed after source changes; Playwright verified the Chinese Codex panel exposes the main-toolbar `投影 smoke` button with nonzero geometry and no text overflow. Screenshot evidence: `.runtime/artifacts/operator-ui/codex-projection-smoke-zh.png`.
- Focused tests after projection smoke additions: `python -m unittest tests.runtime.test_codex_launch_binding_repair tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui` -> `54 tests OK`.
- Script checks after projection smoke additions: `python -m py_compile scripts\codex-interop-check.py scripts\serve-operator-ui.py` -> pass; `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Scripts` -> pass.
- Fresh full gates after projection smoke/UI visibility changes: `scripts\build-runtime.ps1` -> pass; `scripts\verify-repo.ps1 -Check Runtime` -> `114 test files`, `failures=0`; `scripts\verify-repo.ps1 -Check Contract` -> pass; `scripts\doctor-runtime.ps1` -> pass with existing `WARN codex-capability-degraded`; `git diff --check` -> pass with line-ending warnings only.

## Backups

- `C:\Users\sciman\.antigravity_cockpit\backups\codex_accounts.json.20260514_022150.live-roundtrip-before-api.bak`
- `C:\Users\sciman\.antigravity_cockpit\backups\codex_accounts.json.20260514_022255.live-roundtrip-before-oauth.bak`
- `C:\Users\sciman\.codex\backups\config.toml.20260514_022201_cockpit-api-projection.bak`
- `C:\Users\sciman\.codex\backups\auth.json.20260514_022201_cockpit-api-projection.bak`
- `C:\Users\sciman\.codex\backups\state_5.sqlite.20260514_022201_cockpit-api-projection.bak`
- `C:\Users\sciman\.codex\backups\config.toml.20260514_022650_cockpit-account-projection.bak`
- `C:\Users\sciman\.codex\backups\auth.json.20260514_022650_cockpit-account-projection.bak`
- `C:\Users\sciman\.codex\backups\state_5.sqlite.20260514_022650_cockpit-account-projection.bak`
- Later second-round backups also exist for the final API -> OAuth verification pass.
- `C:\Users\sciman\.codex\backups\config.toml.20260514_211044_cockpit-oauth-projection.bak`
- `C:\Users\sciman\.codex\backups\auth.json.20260514_211044_cockpit-oauth-projection.bak`
- `C:\Users\sciman\.codex\backups\state_5.sqlite.20260514_211044_cockpit-oauth-projection.bak`
- `C:\Users\sciman\.antigravity_cockpit\backups\codex_instances.json.20260514_211044_cockpit-oauth-projection.bak`
- `C:\Users\sciman\.codex\backups\config.toml.20260514_212341_cockpit-oauth-projection.bak`
- `C:\Users\sciman\.codex\backups\auth.json.20260514_212341_cockpit-oauth-projection.bak`
- `C:\Users\sciman\.codex\backups\state_5.sqlite.20260514_212341_cockpit-oauth-projection.bak`
- `C:\Users\sciman\.antigravity_cockpit\backups\codex_instances.json.20260514_212341_cockpit-oauth-projection.bak`
