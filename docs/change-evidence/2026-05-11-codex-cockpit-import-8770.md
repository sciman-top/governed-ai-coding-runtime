# 2026-05-11 Codex Cockpit Import Into 8770 Evidence

## Scope
- 当前落点: `D:\CODE\governed-ai-coding-runtime`
- 目标归宿: 8770 Operator UI 作为 Codex OAuth/API 账号管理入口，支持从 Cockpit Tools 当前本机配置只读导入，也支持粘贴 Cockpit Tools / cpa / sub2api JSON。
- 风险等级: medium。导入会写入 `~/.codex/auth-profiles/*.json`，但不会启动、停止、重启或杀掉 Codex App / `codex` 进程。

## Source Findings
- Cockpit Tools 本机 Codex 真源:
  - `C:\Users\sciman\.antigravity_cockpit\codex_accounts.json`
  - `C:\Users\sciman\.antigravity_cockpit\codex_accounts\*.json`
- 当前读取到账户:
  - total: 8
  - OAuth: 7
  - API Key: 1
  - current_account_id: `codex_c641df4d56baceca12b3ffcd597061b3`
- API Key account:
  - provider: `35.213.82.91`
  - base_url: `http://35.213.82.91:8003/v1`
  - secret handling: only redacted hash is emitted in command/UI output.

## Cockpit Source Reference
- `src-tauri/src/modules/codex_account.rs`
  - API key portable account accepts `auth_mode=apikey`, `OPENAI_API_KEY`, `api_base_url`, `api_provider_id`, `api_provider_name`.
  - Built-in OpenAI mode writes top-level `openai_base_url`; custom provider mode writes `model_provider` plus `[model_providers.<id>]`.
- `src/utils/codexExportFormats.ts`
  - `cpa` exports portable token storage.
  - `sub2api` exports `{ type: "sub2api-data", accounts: [{ credentials: ... }] }`.
- 8770 intentionally does not copy Cockpit's custom provider projection. Imported API profiles are projected through the shared `model_provider = "openai"` bucket to preserve Codex App history visibility.

## Changes
- `scripts/lib/codex_local.py`
  - Added Cockpit source discovery and import.
  - Added generic payload import for Cockpit Tools / cpa / sub2api / refresh-token lines.
  - Added API and OAuth online probes with redacted output.
- `scripts/serve-operator-ui.py`
  - Added `/api/codex/cockpit`, `/api/codex/import-cockpit`, `/api/codex/import-payload`, `/api/codex/probe`.
- `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui*.py`
  - Added Cockpit import button, saved-profile probe button, and JSON/cpa/sub2api import form.
- `tests/runtime/*`
  - Added coverage for Cockpit import, cpa/sub2api parsing, backend endpoints, and interactive UI rendering.

## Live Sync And Probe
- Dry-run import:
  - status: pass
  - result: `imported=8`, `api_key=1`, `oauth=7`
  - secret leak check: pass; no `sk-`, `rt_`, or JWT prefix appears in returned JSON.
- Real import with probe:
  - status: pass
  - imported: 8
  - OAuth probe: 7/7 HTTP 200 from `https://chatgpt.com/backend-api/wham/accounts/check`
  - API probe: HTTP 200 from `http://35.213.82.91:8003/v1/models`
  - API model_count: 77
- Live 8770 service refresh:
  - cmd: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Start -UiLanguage zh-CN -Port 8770`
  - status: pass
  - key_output: `ready=True`, `stale=False`
- Live 8770 Cockpit source API:
  - endpoint: `GET http://127.0.0.1:8770/api/codex/cockpit`
  - status: pass
  - result: `total=8`, `api_key_count=1`, `oauth_count=7`, `current_account_id=codex_c641df4d56baceca12b3ffcd597061b3`
- Live 8770 saved-profile probe:
  - endpoint: `POST http://127.0.0.1:8770/api/codex/probe`
  - profile: `cockpit-api-35.213.82.91`
  - status: pass
  - result: `ok=1`, `failed=0`, `http_status=200`, `model_count=77`, `url=http://35.213.82.91:8003/v1/models`
- Browser UI check:
  - url: `http://127.0.0.1:8770/?lang=zh-CN`
  - status: pass
  - visible controls: `导入 Cockpit 账号`, `探测已保存账号`, `导入 JSON / cpa / sub2api`, `导入到 8770`
  - action check: clicked `探测已保存账号` from the Codex tab without switching the active account or launching Codex App instances.

## Verification
- `python -m py_compile scripts\lib\codex_local.py scripts\serve-operator-ui.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_script.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_text.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_style.py`
  - status: pass
- `python -m unittest tests.runtime.test_codex_local.CodexLocalTests.test_import_cockpit_codex_accounts_imports_oauth_and_api_without_secret_output tests.runtime.test_codex_local.CodexLocalTests.test_import_codex_accounts_from_payload_accepts_cpa_and_sub2api_shapes tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_ui_can_import_cockpit_and_probe_codex_profiles tests.runtime.test_operator_ui.OperatorUiTests.test_operator_ui_interactive_mode_renders_actions_and_ref_buttons`
  - status: pass
  - key_output: `Ran 4 tests ... OK`
- `python -m unittest tests.runtime.test_codex_local tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui`
  - status: pass
  - key_output: `Ran 78 tests ... OK`

## Gate Results
- build: pass
  - cmd: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - key_output: `OK python-bytecode`, `OK python-import`
- runtime: pass
  - cmd: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - key_output: `Completed 111 test files ... failures=0`, `OK runtime-unittest`
- contract/invariant: pass
  - cmd: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - key_output: `OK dependency-baseline`, `OK agent-rule-sync`, `OK functional-effectiveness`
- hotspot: pass with existing warning
  - cmd: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - key_output: `OK gate-command-doctor`, `WARN codex-capability-degraded`
  - warning_scope: native attach/status handshake capability remains degraded and is unrelated to Cockpit account import or API probing.

## Rollback
- Code rollback: revert the files listed in `Changes`.
- Profile rollback: imported files are under `~/.codex/auth-profiles/cockpit-*.json`; delete those imported profiles or restore from `~/.codex/auth-backups/*.json`.
- Config rollback: this import path does not switch active accounts. If a later switch projects `config.toml`, restore from `~/.codex/config-backups/config-*.toml`.
