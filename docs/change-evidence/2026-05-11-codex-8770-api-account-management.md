# 2026-05-11 Codex 8770 API Account Management Evidence

## Scope
- 当前落点: `D:\CODE\governed-ai-coding-runtime`
- 目标归宿: 由 `http://127.0.0.1:8770/?lang=zh-CN` 提供 Codex API 账号保存、探测与切换入口，避免继续依赖 Cockpit Tools 的进程管理和自定义 provider 覆盖行为。
- 风险等级: medium，本次改动会写入本机 Codex `auth-profiles/*.json` 和 `config.toml` 投影，但不会重启、停止、杀掉或自动拉起 Codex App / `codex` 进程。

## Root-Cause Contract
- API 账号必须使用 `auth_mode = "apikey"`，并把 API key 保存为命名 auth profile。
- API/OAuth 切换统一投影到内置 `model_provider = "openai"` 历史桶。
- API 账号切换时设置 `forced_login_method = "api"`；OAuth/ChatGPT 切换时设置 `forced_login_method = "chatgpt"` 并移除 `openai_base_url`。
- 禁止在 `config.toml` 写入 `[model_providers.openai]` 自定义表，避免覆盖 Codex 内置 provider 定义。
- 8770 只做文件级保存、备份、配置投影和可选 `/models` 探测，不做 Codex App 进程管理。

## Changes
- `scripts/lib/codex_local.py`
  - 新增 `save_api_auth_profile()`、`probe_codex_api_account()`、`project_codex_auth_config()`。
  - `switch_auth_profile()` 在 API/OAuth 切换时同步投影 `config.toml`。
  - `codex_status()` 增加 `config.auth_projection`，用于显示当前历史桶和登录方法投影。
- `scripts/serve-operator-ui.py`
  - 新增 `POST /api/codex/save-api`，调用受控 API profile 保存逻辑。
- `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui*.py`
  - 在 Codex 页增加 API 账号表单、探测开关、保存后切换开关和前端提交逻辑。
- `tests/runtime/*`
  - 覆盖 API profile 写入、共享 `openai` 历史桶投影、OAuth 切回清理、探测失败不落盘、8770 endpoint 和交互 UI。

## Verification
- `python -m py_compile scripts\lib\codex_local.py scripts\serve-operator-ui.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_script.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_text.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_style.py`
  - status: pass
- `python -m unittest tests.runtime.test_codex_local.CodexLocalTests.test_save_api_auth_profile_projects_shared_openai_history_bucket tests.runtime.test_codex_local.CodexLocalTests.test_switch_auth_profile_to_chatgpt_clears_api_projection tests.runtime.test_codex_local.CodexLocalTests.test_save_api_auth_profile_probe_failure_does_not_write_profile tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_ui_can_save_codex_api_profile_without_exposing_key tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_ui_action_generates_html tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_ui_action_generates_english_html tests.runtime.test_operator_ui.OperatorUiTests.test_operator_ui_interactive_mode_renders_actions_and_ref_buttons`
  - status: pass
  - key_output: `Ran 7 tests ... OK`
- `python -m unittest tests.runtime.test_codex_local tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui`
  - status: pass
  - key_output: `Ran 75 tests ... OK`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Start -UiLanguage zh-CN -Port 8770`
  - status: pass
  - key_output: `ready: true`, `stale: false`, `url: http://127.0.0.1:8770/?lang=zh-CN`
- Browser check: `http://127.0.0.1:8770/?lang=zh-CN`
  - status: pass
  - key_output: Codex tab shows `API 账号`, `账号名`, `Base URL`, `API Key`, `保存前探测 /models`, `保存后立即切换`, `保存 API 账号`
- `Invoke-RestMethod -Uri 'http://127.0.0.1:8770/api/ui-process'`
  - status: pass
  - key_output: `status: ok`, `stale: false`

## Gate Results
- build: pass
  - cmd: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - key_output: `OK python-bytecode`, `OK python-import`
- runtime: pass
  - cmd: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - key_output: `Completed 111 test files ... failures=0`, `OK runtime-unittest`
- contract/invariant: pass
  - cmd: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - key_output: `OK schema-json-parse`, `OK dependency-baseline`, `OK functional-effectiveness`
- hotspot: pass with existing warning
  - cmd: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - key_output: `OK gate-command-doctor`, `WARN codex-capability-degraded`
  - warning_scope: native attach/status handshake capability remains degraded and is unrelated to API account profile projection.

## Rollback
- 代码回滚: 使用 git 回滚本文件列出的源码、测试和证据文件。
- 本机配置回滚: `save_api_auth_profile()` 和 `switch_auth_profile()` 修改真实 `config.toml` 前会写入 `backups/config-*.toml`；需要时恢复最近一次备份。
- 账号快照回滚: 覆盖已有 API profile 前会写入 `auth-backups/*.json`；需要时恢复对应 profile 或重新切换回 OAuth profile。
