# Cockpit Runtime Mode History Projection Evidence

- rule_id: `LocalCodexCockpit`
- risk: `medium`
- landing: `D:\CODE\external\cockpit-tools` self-use Cockpit source and installed `Cockpit Tools Local`
- target: Cockpit owns `direct_projection` / `gateway_litellm` projection, including Codex auth/config/history bucket visibility.
- rollback:
  - restore installed exe from `C:\Users\sciman\AppData\Local\Cockpit Tools Local\backups\cockpit-tools-local.exe.20260516_112131.pre-history-projection.bak`
  - latest installed exe backup: `C:\Users\sciman\AppData\Local\Cockpit Tools Local\backups\cockpit-tools-local.exe.20260516_114650.pre-gateway-fallback.bak`
  - restore Codex projection files from `C:\Users\sciman\.codex\backups\*.20260516_112208_cockpit-oauth-projection.bak` if needed

## Commands

- `npm run typecheck`
- `cargo fmt`
- `cargo test config_toml -- --nocapture`
- `cargo test local_access -- --nocapture`
- `cargo check`
- `python -m unittest tests.runtime.test_codex_cockpit_policy_contract tests.runtime.test_litellm_gateway_contract tests.runtime.test_operator_entrypoint`
- `npm run tauri -- build`
- `python scripts\codex-interop-check.py --codex-home C:\Users\sciman\.codex --cc-switch-db C:\Users\sciman\.cc-switch\cc-switch.db --cockpit-home C:\Users\sciman\.antigravity_cockpit --quick-launch`

## Evidence

- pre_change_review:
  - control_repo_manifest_and_rule_sources: checked `rules/manifest.json`, `AGENTS.md`, and `tests/runtime/test_codex_cockpit_policy_contract.py` before removing the old sync-mode entrypoint and tightening the allowed Cockpit repair commands.
  - user_level_deployed_rule_files: checked live `C:\Users\sciman\.codex\config.toml`, `C:\Users\sciman\.codex\auth.json`, and `C:\Users\sciman\.codex\state_5.sqlite` projection state through `codex-interop-check.py --quick-launch`.
  - target_repo_deployed_rule_files: checked the self-use Cockpit source tree at `D:\CODE\external\cockpit-tools` and kept the durable fix in Cockpit source rather than an external projection script.
  - target_repo_gate_scripts_and_ci: ran Cockpit `npm run typecheck`, `cargo test`, `cargo check`, `npm run tauri -- build`, and control-repo runtime tests listed above.
  - target_repo_repo_profile: no target repo profile expansion was needed; this was a local Cockpit/Codex interoperability repair bounded by `LocalCodexCockpit`.
  - target_repo_readme_and_operator_docs: updated README/runbook/operator references so the removed `Sync-CodexCockpitMode.ps1` path is not advertised as the active entrypoint.
  - current_official_tool_loading_docs: verified current behavior from live Codex config, local CLI probes, Cockpit logs, and the installed app path rather than relying on old projection assumptions.
  - drift-integration decision: integrate by deleting the old generic mode sync script, keeping explicit `CodexOauthProjectionRepair` / `CodexApiProjectionRepair` / `CodexLaunchBindingRepair` entrypoints, and documenting LiteLLM Gateway as a Cockpit-owned source fix.
- Cockpit desktop shortcut target: `C:\Users\sciman\AppData\Local\Cockpit Tools Local\cockpit-tools-local.exe`.
- Installed exe replaced from `D:\CODE\external\cockpit-tools\target\release\cockpit-tools.exe`; latest installed exe timestamp `2026-05-16 11:46:23`.
- Direct/OAuth projection fresh check: `status=pass`.
- Picker visibility evidence in `C:\Users\sciman\.codex\state_5.sqlite`: `openai=1742`, `visible_user_event_threads=1696`.
- Saved API provider profile check: `cockpit_saved_api_provider_profiles_projectable=pass`.
- LiteLLM listener: `127.0.0.1:4000`, `/v1/models` returned `cockpit-current` with the local API key.
- Temporary Cockpit local access listener: `127.0.0.1:2876` started when `codex_local_access.enabled=true`.
- Earlier gateway generation probe reached Cockpit through LiteLLM but returned `429`: current account `gpt-5.5` cooldown around `603705` seconds. This was an upstream/account availability block, not provider/history projection.
- After Cockpit source update and reinstall, direct Cockpit API service probe passed: `POST http://127.0.0.1:2876/v1/responses` with `model=gpt-5.5`, `store=false`, `stream=true` returned HTTP `200`.
- After Cockpit source update and reinstall, LiteLLM gateway probe passed: `POST http://127.0.0.1:4000/v1/responses` with `model=cockpit-current`, `store=false`, `stream=true` returned HTTP `200`; response stream showed upstream `model=gpt-5.5`.
- `npm run tauri -- build` produced the release exe successfully; MSI bundling failed on WiX download with `protocol: http response missing version`.

## Compatibility

- `direct_projection` now writes the old OAuth/API projection shape and runs history visibility repair after materialization.
- `gateway_litellm` now writes custom provider `litellm_gateway` and runs history visibility repair after materialization.
- `gateway_litellm` now sets Codex top-level `model = "cockpit-current"` so Codex App/CLI sends a model listed by LiteLLM `/v1/models`; returning to `direct_projection` removes that LiteLLM-only model if present.
- Shared profiles `shared-current-provider`, `shared-cockpit-api`, and `shared-cockpit-auth` are preserved so old direct API/OAuth picker/provider behavior remains available.
- Cockpit API service routing now uses `followCurrentAccount` plus eligible quota fallback candidates, so a cooled current account can be bypassed without changing the global current Cockpit account.
- The Codex account page quota sorts no longer let API-service/current-account priority override `weekly`, `hourly`, `weekly_reset`, or `hourly_reset` ordering.
