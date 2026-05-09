# 2026-05-10 Codex CLI history and warning repair

- landing: `scripts/Optimize-CodexLocal.ps1`, `scripts/codex-interop-check.py`, `tests/runtime/test_codex_shared_launcher.py`, `README.md`, `README.zh-CN.md`, `docs/quickstart/ai-coding-usage-guide.zh-CN.md`
- risk: low; changes normalize local Codex config/history metadata and reduce duplicate skill metadata, without deleting skill files or changing the Codex login source boundary
- command: `python scripts/codex-interop-check.py --codex-home C:\Users\sciman\.codex --cc-switch-db C:\Users\sciman\.cc-switch\cc-switch.db --cockpit-home C:\Users\sciman\.antigravity_cockpit`
- evidence: `status=pass`; `codex_thread_provider_distribution.distribution={"openai":1609}`; `unexpected_providers={}`
- command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Optimize-CodexLocal.ps1 -Apply`
- evidence: wrote `C:\Users\sciman\.codex\config.toml`; backup `C:\Users\sciman\.codex\config-backups\config-20260510-002911.toml`; interop status remained `pass`; provider bucket migration updated `0` rows because all active history was already normalized
- command: config inspection
- evidence: live `C:\Users\sciman\.codex\config.toml` now has 78 `[[skills.config]]` entries with `enabled = false` for duplicate `C:\Users\sciman\.agents\skills\*` paths that also exist under canonical `D:\CODE\skills-manager\agent`
- command: `codex debug prompt-input "noop" 2>&1 | Select-String -Pattern 'Skill descriptions were shortened|truncated skill metadata|Falling back from WebSockets|Error:'`
- evidence: no matching warning/error output after duplicate skill disable overrides
- command: `python -m unittest tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_optimizer_apply_writes_shared_history_config_without_fixed_relay_id tests.runtime.test_codex_shared_launcher.CodexSharedLauncherTests.test_interop_checker_fails_when_any_active_thread_uses_non_shared_provider`
- evidence: `Ran 2 tests ... OK`
- compatibility: CLI history picker is `codex resume`; use `codex resume --all --include-non-interactive` or the installed `codex-cockpit-resume` / `codex-shared-resume` shortcuts when App, API and non-interactive sessions must be visible together
- compatibility: the current relay `http://35.213.82.91:8003/v1` returned 404 for Responses WebSocket upgrade; Codex can fall back to HTTPS Responses. Official Codex config supports `model_providers.<id>.supports_websockets`, but built-in `openai` cannot be overridden, so disabling WebSocket for the shared `openai` bucket is not currently applied without splitting history into a custom provider bucket
- rollback: restore `C:\Users\sciman\.codex\config-backups\config-20260510-002911.toml` or the git versions of the changed repo files if the duplicate skill disable strategy needs to be undone
