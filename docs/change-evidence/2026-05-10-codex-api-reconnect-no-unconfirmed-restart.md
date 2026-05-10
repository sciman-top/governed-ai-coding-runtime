# 2026-05-10 Codex API reconnect and no-unconfirmed-restart guard

- rules: R1/R3/R4/R6/R8, E4/E6
- risk: medium, live Codex/Cockpit auth projection plus managed rule sync
- landing: `C:\Users\sciman\.codex`, `C:\Users\sciman\.antigravity_cockpit`, `scripts/codex-interop-check.py`, global/project rule sources
- destination: keep Codex API switching usable across all saved projects, repair API auth/provider projection without process restarts, and enforce explicit user confirmation before restarting Codex/Claude processes

## Superseded Correction

- This file preserves an intermediate 2026-05-10 repair attempt. The `cockpit_http` custom-provider strategy below is superseded and must not be treated as current guidance.
- Current durable rule: keep shared history on the built-in `model_provider = "openai"` bucket, switch API relays with top-level `openai_base_url`, and never define `[model_providers.openai]`.
- Because built-in `openai` cannot be overridden with `supports_websockets = false`, the `35.213.82.91` WebSocket `404` must be fixed in the remote relay/proxy/backend or tolerated as a client fallback warning. Do not split history into a custom provider bucket just to suppress that warning.

## Root Cause

- The API relay at `http://35.213.82.91:8003/v1` was reachable. Direct HTTP probes with the current Cockpit API key returned `/models = 200` and `/responses = 200`.
- The `Reconnecting` symptom was not caused by the remote API being offline. Live logs showed failed target-repo turns using `responses_websocket` against `ws://35.213.82.91:8003/v1/responses`, which returned `404 Not Found`; direct HTTP Responses calls succeeded.
- An intermediate hypothesis treated the built-in `openai` shared-bucket strategy as incomplete because it cannot be given `supports_websockets = false`. That was corrected later: API relay mode still stays on the built-in `openai` bucket, and the relay WebSocket gap is a server-side capability issue rather than a reason to define a custom shared bucket.
- Target repos showed mixed live state: this repo's current thread was still connected through `auth_mode="Chatgpt"` websocket, while `k12-question-graph`, `github-toolkit`, and `ClassroomToolkit` attempted API relay websocket and failed; `vps-ssh-launcher` also showed stale `auth_mode="Chatgpt"` with a `401` against the API relay.
- A config-only API switch was incomplete: `config.toml` could point to API mode while `auth.json` or already-spawned sessions still held stale ChatGPT token shape. That can produce reconnect/auth drift on the next Codex startup or project switch.
- Cockpit fixed account bindings and automatic restart wrappers can relaunch stale account/process state. Process restarts also risk disrupting App session/history visibility, so they require explicit user confirmation in the current task.

## Changes

- Superseded intermediate change, later reverted: temporarily moved live Codex API relay to non-websocket custom bucket semantics:
  - `model_provider = "cockpit_http"`
  - `forced_login_method = "api"`
  - `[model_providers.cockpit_http].base_url = "http://35.213.82.91:8003/v1"`
  - `[model_providers.cockpit_http].requires_openai_auth = false`
  - `[model_providers.cockpit_http].supports_websockets = false`
- Superseded intermediate change, later reverted: migrated `state_5.sqlite.threads.model_provider` from `openai` to `cockpit_http` after backing up the database.
- Projected current Cockpit API account into `C:\Users\sciman\.codex\auth.json` as `auth_mode = "apikey"` with the same base URL.
- Disabled Cockpit automatic Codex App restart wrapper:
  - `codex_restart_specified_app_on_switch = false`
  - `codex_specified_app_path = ""`
- Set Cockpit default Codex instance behavior to follow the current account instead of a fixed `bindAccountId`.
- Added `codex_auth_matches_cockpit_current_account` to `scripts/codex-interop-check.py` so API mode now fails if `auth.json` does not match the current Cockpit account.
- Superseded intermediate change, later reverted: updated `scripts/codex-interop-check.py` and `scripts/Start-CodexShared.ps1` so non-official Cockpit API accounts used `cockpit_http` with `supports_websockets=false`.
- Added tests covering stale/missing API auth projection.
- Added global and project rule text forbidding unconfirmed restart/stop/kill/auto-launch of `Codex App`, `codex`, `Claude Code`, `Claude Desktop`, and `claude` for provider/auth/API repair.
- Applied managed rule sync with `--force` to global user files and all target project files.

## Verification

- pre_change_review: this change touches rule files, live auth projection code, and target-deployed `AGENTS.md`; review scope is limited to provider/auth/API repair and no-unconfirmed process restart policy.
- control_repo_manifest_and_rule_sources: managed source files were updated under `rules/global/codex/AGENTS.md`, `rules/global/claude/CLAUDE.md`, and `rules/projects/*/codex/AGENTS.md`; sync used `rules/manifest.json`.
- user_level_deployed_rule_files: `C:\Users\sciman\.codex\AGENTS.md` and `C:\Users\sciman\.claude\CLAUDE.md` were updated by managed sync.
- target_repo_deployed_rule_files: target Codex `AGENTS.md` files were updated for `D:\CODE\ClassroomToolkit`, `D:\CODE\skills-manager`, `D:\CODE\github-toolkit`, `D:\CODE\k12-question-graph`, and `D:\CODE\vps-ssh-launcher`.
- target_repo_gate_scripts_and_ci: target repo gate scripts and CI were not changed; this update only strengthens agent process-restart policy in deployed rule files.
- target_repo_repo_profile: target repo profiles were not changed; no repository execution profile or runtime target catalog value was modified.
- target_repo_readme_and_operator_docs: target README/operator docs were not changed because the operational rule belongs in global/project agent rules and the local change evidence file.
- current_official_tool_loading_docs: no external loading model change was made; Codex still reads `AGENTS.md`, and Claude global wrapper remains `CLAUDE.md`.
- drift-integration decision: same-version drift was force-synced only after source rule files were updated in the control repo; post-sync dry-run showed `changed_count=0` and `blocked_count=0`.
- `python scripts\codex-interop-check.py --codex-home C:\Users\sciman\.codex --cc-switch-db C:\Users\sciman\.cc-switch\cc-switch.db --cockpit-home C:\Users\sciman\.antigravity_cockpit --quick-launch`
  - result: `pass`
  - key checks: `codex_thread_provider_distribution=cockpit_http:1623`, `codex_live_provider_bucket=pass`, `codex_auth_matches_cockpit_current_account=pass`, `cockpit_codex_app_restart_semantics=pass`
- Live migration command:
  - command: `python scripts\codex-interop-check.py --codex-home C:\Users\sciman\.codex --cc-switch-db C:\Users\sciman\.cc-switch\cc-switch.db --cockpit-home C:\Users\sciman\.antigravity_cockpit --apply --migrate-provider-bucket --quick-launch`
  - result: `pass`
  - changed: `config.toml` provider bucket to `cockpit_http`, recreated SQLite bucket triggers, backed up `state_5.sqlite`, migrated `updated_rows=1624`
- Full session metadata migration:
  - command: `python scripts\codex-interop-check.py --codex-home C:\Users\sciman\.codex --cc-switch-db C:\Users\sciman\.cc-switch\cc-switch.db --cockpit-home C:\Users\sciman\.antigravity_cockpit --apply --migrate-provider-bucket`
  - result: `fail` only for locked live session JSONL files
  - changed: `files_changed=1614`, `provider_updates=1735`
  - residual: 9 live session files returned Windows `Access denied`; no process was stopped or restarted to unlock them
- Direct HTTP API probe using the projected API key:
  - base URL: `http://35.213.82.91:8003/v1`
  - `/models = 200`
  - `/responses = 200`
- `python scripts\sync-agent-rules.py --scope All --apply --force`
  - result: `applied`
  - `changed_count=8`
  - updated: global Codex, global Claude, current repo `AGENTS.md`, and target Codex `AGENTS.md` files for ClassroomToolkit, skills-manager, github-toolkit, k12-question-graph, and vps-ssh-launcher
- `python scripts\sync-agent-rules.py --scope All --fail-on-change`
  - result: `pass`
  - `changed_count=0`
  - `blocked_count=0`
- `python -m unittest tests.runtime.test_codex_shared_launcher`
  - result: `Ran 10 tests in 2.192s, OK`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - result: `OK python-bytecode`, `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - result: `Completed 109 test files in 124.131s; failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - result: all listed contract checks passed, including `agent-rule-sync`, `pre-change-review`, and `functional-effectiveness`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - result: all hard checks passed; residual `WARN codex-capability-degraded` is an existing Codex native attach capability warning, not a failure for this API/auth/rule repair

## Backups

- `C:\Users\sciman\.codex\backups\config.toml.20260510_182332_cockpit_provider.bak`
- `C:\Users\sciman\.codex\backups\config.toml.20260510_184917_cockpit_provider.bak`
- `C:\Users\sciman\.codex\backups\auth.json.20260510_182332_cockpit_auth.bak`
- `C:\Users\sciman\.codex\backups\state_5.sqlite.20260510_184917_provider_bucket.bak`
- `C:\Users\sciman\.codex\backups\session_provider_bucket_20260510_184939\changed-lines.jsonl`
- `D:\CODE\governed-ai-coding-runtime\docs\change-evidence\rule-sync-backups\20260510-182004\`
- `C:\Users\sciman\.antigravity_cockpit\backups\api-current-no-restart-20260510-181829`

## Rollback

- Restore `config.toml`, `auth.json`, and `state_5.sqlite` from the listed backups if API account projection and provider bucket migration must be undone.
- Restore synced global/project rules from `docs/change-evidence/rule-sync-backups/20260510-182004/` if the managed rule update must be rolled back.
- Do not use process restart as rollback unless the user explicitly confirms it in the current task.

## Residual Risk

- The currently running Codex App may not hot-reload every file-level change. This repair intentionally did not restart the App or CLI after the user correction.
- Superseded intermediate residual: at this point in the investigation, 9 live session JSONL files were locked and SQLite state had been moved to `cockpit_http`. Later repair restored the shared `openai` bucket; use the current restart-guard evidence file for present state.

## 2026-05-10 OAuth follow-up

- Trigger: after switching away from the `35.213.82.91` API relay to OAuth, the App again showed repository histories as empty.
- Fresh root cause:
  - `state_5.sqlite` still contained the histories, but all active rows had been migrated to `threads.model_provider = "cockpit_http"` for the API relay.
  - The current Cockpit account was `auth_mode = "oauth"`, which maps to Codex `forced_login_method = "chatgpt"` and provider bucket `openai`.
  - Live `config.toml` had drifted to `forced_login_method = "api"` with active provider `openai`, while `auth.json` had tokens but no explicit `auth_mode`.
  - `scripts/codex-interop-check.py` treated Cockpit `oauth` as unsupported instead of normalizing it to Codex `chatgpt`; therefore the checker could identify the mismatch but could not repair it.
  - Cockpit default settings also kept `followLocalAccount = false` and a fixed `bindAccountId`, so account switching could relaunch stale account state.
- Code fix:
  - `scripts/codex-interop-check.py` now normalizes Cockpit `auth_mode = "oauth"` to Codex login/auth mode `chatgpt`.
  - The auth projection check now reports both `cockpit_auth_mode` and expected Codex `auth_mode`.
  - Unsupported auth modes fail closed instead of being projected through the ChatGPT path by accident.
  - `tests/runtime/test_codex_shared_launcher.py` adds a regression test for OAuth after API relay bucket migration.
- Live repair:
  - command: `python scripts\codex-interop-check.py --codex-home C:\Users\sciman\.codex --cc-switch-db C:\Users\sciman\.cc-switch\cc-switch.db --cockpit-home C:\Users\sciman\.antigravity_cockpit --apply --migrate-provider-bucket --quick-launch`
  - result: `pass`
  - changed: `codex_threads_provider_bucket_migrated updated_rows=1626`, target provider `openai`
  - changed: `codex_live_config_cockpit_provider` to `model_provider = "openai"` and `forced_login_method = "chatgpt"`
  - changed: `codex_auth_cockpit_projected` from Cockpit `oauth` to Codex `auth_mode = "chatgpt"`
  - changed: `cockpit_codex_instances_follow_current_account_repaired`
  - unchanged: no Codex App, CLI, Claude, or Claude Desktop process was stopped or restarted.
- Fresh verification:
  - `python scripts\codex-interop-check.py --codex-home C:\Users\sciman\.codex --cc-switch-db C:\Users\sciman\.cc-switch\cc-switch.db --cockpit-home C:\Users\sciman\.antigravity_cockpit --quick-launch`
    - result: `pass`
    - key checks: `codex_thread_provider_distribution=openai:1625`, `codex_live_provider_bucket=pass`, `codex_auth_matches_cockpit_current_account=pass`, `cockpit_live_login_mode_matches_current_account=pass`
  - `python scripts\codex-history-view-diagnose.py --codex-home C:\Users\sciman\.codex --target-cwd D:\CODE\governed-ai-coding-runtime --target-cwd D:\CODE\k12-question-graph --target-cwd D:\CODE\skills-manager --target-cwd D:\CODE\ClassroomToolkit --target-cwd D:\CODE\github-toolkit --target-cwd D:\CODE\vps-ssh-launcher`
    - result: `pass`
    - loaded `337` non-archived App-source rows
    - all six target repos were visible in the default first page.
  - `python -m unittest tests.runtime.test_codex_shared_launcher -v`
    - result: `Ran 11 tests`, `OK`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1`
    - result: `OK python-bytecode`, `OK python-import`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime`
    - result: `Completed 109 test files in 128.801s; failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Contract`
    - result: all listed contract checks passed, including `agent-rule-sync`, `pre-change-review`, and `functional-effectiveness`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\doctor-runtime.ps1`
    - result: hard checks passed; residual `WARN codex-capability-degraded` is the existing native attach warning, not a failure for this auth/history repair
- New backups:
  - `C:\Users\sciman\.codex\backups\config.toml.20260510_190513_cockpit_provider.bak`
  - `C:\Users\sciman\.codex\backups\state_5.sqlite.20260510_190513_provider_bucket.bak`
  - `C:\Users\sciman\.antigravity_cockpit\backups\codex_instances.json.20260510_190513_cockpit_follow_current_account.bak`
- Rollback:
  - restore the listed `config.toml`, `state_5.sqlite`, and `codex_instances.json` backups if OAuth projection must be undone.
  - do not restore stale fixed `bindAccountId` unless the intent is account isolation rather than shared history.
