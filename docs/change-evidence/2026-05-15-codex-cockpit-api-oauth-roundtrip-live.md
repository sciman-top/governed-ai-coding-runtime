# 2026-05-15 Codex Cockpit API OAuth Roundtrip Live

- rule_id: `local-codex-cockpit-auth-interop`
- risk: medium live host state mutation
- landing: `scripts/codex-interop-check.py`, `tests/runtime/test_codex_shared_launcher.py`, live `C:\Users\sciman\.codex`, live `C:\Users\sciman\.antigravity_cockpit`
- destination: prove Cockpit API and OAuth projections can roundtrip without restarting Codex, while preserving provider buckets, picker visibility, and repair boundaries
- rollback: restore the timestamped backups listed below, then rerun `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexProjectionSmoke`

## Commands

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexApiProjectionRepair`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexProjectionSmoke`
- `codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox --output-last-message .runtime\codex-api-roundtrip-probe-20260515.txt "只输出 API_ROUNDTRIP_OK"`
- `python scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit" --quick-launch --repair-current-cockpit-oauth-projection --cockpit-account-id codex_3797bc603c01b0dd72e9181fe9aad25d`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action CodexProjectionSmoke`
- `codex exec --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox --output-last-message .runtime\codex-oauth-roundtrip-probe-20260515.txt "只输出 OAUTH_ROUNDTRIP_OK"`

## API Projection Result

- `CodexApiProjectionRepair`: `status=changed`
- API account: `codex_apikey_8b8853f15e823dc53bd156163035bc78`
- provider bucket: `cmp_1778165666417_1`
- base URL: `http://35.213.82.91:8003/v1`
- previous Cockpit current account: `codex_3797bc603c01b0dd72e9181fe9aad25d`
- `cockpit_current_account_changed`: `true`
- `history_rows_changed`: `1727`
- `codex_thread_provider_distribution`: `cmp_1778165666417_1=1726`, `status=pass`
- `codex_history_visibility_metadata`: `active_threads=1726`, `user_message_threads=1680`, `visible_user_event_threads=1680`, `status=pass`
- `CodexProjectionSmoke`: `status=pass`
- API `codex exec`: `API_ROUNDTRIP_OK`, provider `cmp_1778165666417_1`, session `019e27e6-5b8d-79b1-a275-eb1a62975f21`

## OAuth Projection Result

- Initial explicit OAuth projection exposed a real gap: Codex auth/config/history were repaired for the requested OAuth account, but `codex_accounts.json.current_account_id` stayed on the previous API account, causing ordinary `CodexProjectionSmoke` to fail.
- Fixed `_repair_cockpit_oauth_projection` to update `codex_accounts.json.current_account_id` with a backup, mirroring API projection semantics.
- Added `tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_explicit_oauth_projection_updates_cockpit_current_account`.
- Final explicit OAuth projection: `status=changed`
- OAuth account: `codex_3797bc603c01b0dd72e9181fe9aad25d`
- provider bucket: `openai`
- previous Cockpit current account: `codex_apikey_8b8853f15e823dc53bd156163035bc78`
- `cockpit_current_account_changed`: `true`
- `history_rows_changed`: `0`
- `history_visibility_rows_changed`: `0`
- `CodexProjectionSmoke`: `status=pass`
- `codex_thread_provider_distribution`: `openai=1727`, `status=pass`
- `codex_history_visibility_metadata`: `active_threads=1727`, `user_message_threads=1681`, `visible_user_event_threads=1681`, `status=pass`
- OAuth `codex exec`: `OAUTH_ROUNDTRIP_OK`, provider `openai`, session `019e27eb-eca9-7472-9cc7-84d4b5afd5d5`

## Backups

- `C:\Users\sciman\.codex\backups\config.toml.20260515_031045_cockpit-api-projection.bak`
- `C:\Users\sciman\.codex\backups\auth.json.20260515_031045_cockpit-api-projection.bak`
- `C:\Users\sciman\.codex\backups\state_5.sqlite.20260515_031045_cockpit-api-projection.bak`
- `C:\Users\sciman\.antigravity_cockpit\backups\codex_accounts.json.20260515_031045_cockpit-api-projection.bak`
- `C:\Users\sciman\.codex\backups\config.toml.20260515_031650_cockpit-oauth-projection.bak`
- `C:\Users\sciman\.codex\backups\auth.json.20260515_031650_cockpit-oauth-projection.bak`
- `C:\Users\sciman\.codex\backups\state_5.sqlite.20260515_031650_cockpit-oauth-projection.bak`
- `C:\Users\sciman\.antigravity_cockpit\backups\codex_accounts.json.20260515_031650_cockpit-oauth-projection.bak`

## Boundary

- No Codex App, Codex CLI, Cockpit Tools, or background guard process was restarted, stopped, killed, or auto-launched by the repair flow.
- The repeated `ERROR: The process "<pid>" not found.` message appeared during `codex exec`, but both probes exited `0` and returned the expected final messages. It remains classified as startup noise, not connectivity failure.

## Pre-Change Review

- `pre_change_review`: required because this change touches managed project rule files, local Codex/Cockpit projection code, and live auth/provider/history projection behavior. Scope was constrained to OAuth/API roundtrip, provider bucket alignment, picker visibility, and no-restart repair boundaries.
- `control_repo_manifest_and_rule_sources`: checked `rules/manifest.json`, root `AGENTS.md`, and `rules/projects/governed-ai-coding-runtime/codex/AGENTS.md`; source and deployed self-runtime rule files were brought back to same-hash before rerunning sync checks.
- `user_level_deployed_rule_files`: checked by `python scripts\sync-agent-rules.py --scope All --fail-on-change`; global user-level Codex/Claude/Gemini rule files were same-hash and not changed by this task.
- `target_repo_deployed_rule_files`: checked by the same all-scope dry-run; target repo deployed rule files were same-hash and did not require propagation.
- `target_repo_gate_scripts_and_ci`: no target repo gate script or CI file was changed; verification stayed inside this control repo with focused tests and the standard runtime gate.
- `target_repo_repo_profile`: no `.governed-ai/repo-profile.json` or target repo profile was changed.
- `target_repo_readme_and_operator_docs`: README files and `docs/runbooks/codex-cockpit-api-provider-repair.md` were updated to reflect the stricter Codex/Cockpit repair contract; no unrelated target README/operator docs were changed.
- `current_official_tool_loading_docs`: no Codex loading model change was introduced; this task only strengthened the existing project rule source/target pair and verified the manifest-managed sync path.
- `drift-integration decision`: integrate by updating the control repo rule source first, preserving Cockpit-native no-restart semantics, and adding a regression test for explicit OAuth current-account projection rather than reintroducing generic repair, provider bucket migration, background guard, or restart wrapper behavior.
