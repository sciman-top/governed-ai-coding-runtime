# 2026-05-11 Codex 8770 API Switch Root Cause

## Scope
- 当前落点: `D:\CODE\governed-ai-coding-runtime`
- 目标归宿: 8770 Operator UI 成为 Codex OAuth/API profile 的主切换入口；Cockpit Tools 仅作为可导入来源或兼容排障来源。
- 风险等级: medium。已写入 `~/.codex/auth.json`、`~/.codex/config.toml`，删除一个无效 legacy auth profile 前已自动备份。

## Root Cause
- Cockpit Tools 本机 Codex inventory 只有一个 API account: `35.213.82.91`，base URL 为 `http://35.213.82.91:8003/v1`。
- `~/.codex/auth-profiles/auto-fdb75e04ea.json` 是旧的 legacy API snapshot，只有 `auth_mode=apikey` 与 `OPENAI_API_KEY`，没有 `api_base_url`。
- 旧 8770 切换链允许切换这个 legacy snapshot。切换后会写出:
  - `forced_login_method = "api"`
  - 移除 `openai_base_url`
  - `model_provider = "openai"`
- 这等价于用中转站 API key 去连接默认 OpenAI 官方地址，触发 Codex App `Reconnecting`。

## Fixes
- `scripts/lib/codex_local.py`
  - `switch_auth_profile()` 现在会拒绝切换缺少 `api_base_url` 的 API snapshot。
  - `project_codex_auth_config()` 现在会拒绝把缺少 API endpoint 的 API profile 投影到 `config.toml`。
  - 账号列表对同一 API key 的重复 snapshot 优先显示可切换、带 `api_base_url` 的 profile，并标注 hidden duplicate。
  - OAuth 账号展示按标准化 email 合并，不再把 `auth1..auth5.json` legacy snapshot 与 `auth-profiles/cockpit-*.json` imported snapshot 显示成两个账号。
  - API 账号标签优先使用 `api_provider_name` 或 `api_base_url` 主机名，因此 `cockpit-api-35.213.82.91` 在 UI 中显示为 `35.213.82.91`。
- 8770 UI
  - 正式名称调整为 `治理运行时操作台 / Governed Runtime Operator Console`。
  - 打开 Codex 面板时自动刷新一次本机状态，避免旧浏览器缓存继续展示已合并前的重复账号列表。
  - API 账号卡片精简为 `类型 / 配置 / 地址`，OAuth 卡片保留 `类型 / 配置 / 套餐 / 额度`。
  - 主工具栏保留刷新、同步 Cockpit、探测账号、Usage。
  - 旧 `修复 Cockpit/Codex 互操作`、切换守护等按钮下沉到 `Cockpit 兼容排障`，并明确说明它们只适用于 Cockpit Tools 仍是切号来源的场景。
  - 文案将 `导入到 8770` 改为 `导入`，并精简 `保存 API 账号` 等冗余词。
- 本机现场
  - 已删除 `~/.codex/auth-profiles/auto-fdb75e04ea.json`。
  - 备份路径: `C:\Users\sciman\.codex\auth-backups\auto-fdb75e04ea-20260511-193501.json`

## Live Verification
- 真实本机 profile 重算:
  - active: `cockpit-api-35.213.82.91`, label `35.213.82.91`, `auth_mode=apikey`, `api_base_url=http://35.213.82.91:8003/v1`
  - account count: `8` (`1` API + `7` OAuth email accounts)
  - merged OAuth duplicates: `sciman.top@gmail.com`, `ai.sciman.top@gmail.com`, `sciman.phys@gmail.com`, `agi.sciman@gmail.com`, `agi.phys@gmail.com`
  - hidden legacy sources: `auth1`, `auth2`, `auth3`, `auth4`, `auth5`
- 旧坏 profile 切换 dry-run:
  - target: `auto-fdb75e04ea`
  - result: blocked
  - error: `API auth profile is missing api_base_url; switch blocked to avoid Codex reconnecting against the wrong endpoint`
- 8770 API switch:
  - endpoint: `POST http://127.0.0.1:8770/api/codex/switch`
  - target: `cockpit-api-35.213.82.91`
  - result: `status=ok`
  - active auth: `auth_mode=apikey`, `api_base_url=http://35.213.82.91:8003/v1`
  - config projection: `forced_login_method=api`, `model_provider=openai`, `openai_base_url=http://35.213.82.91:8003/v1`
- API probe:
  - endpoint: `POST http://127.0.0.1:8770/api/codex/probe`
  - target: `cockpit-api-35.213.82.91`
  - result: `ok=1`, `failed=0`, `http_status=200`, `model_count=9`
- Browser:
  - url: `http://127.0.0.1:8770/?lang=zh-CN`
  - page title: `治理运行时操作台`
  - opening Codex tab auto-refreshed status to `Codex 状态: 已刷新`
  - visible main controls: `刷新 Codex 状态`, `强制在线刷新`, `同步 Cockpit`, `探测账号`, `打开官方 Usage`
  - after Codex panel refresh, visible API account label: `35.213.82.91`
  - visible API address: `http://35.213.82.91:8003/v1`
  - visible account labels: `35.213.82.91` plus `7` unique OAuth email labels, no duplicate account-card labels
  - legacy tools are folded under `Cockpit 兼容排障`

## Cockpit Tools Source Review
- Source: `https://github.com/jlcodes99/cockpit-tools`, inspected at commit `38e7a94`.
- Relevant files:
  - `src/utils/codexExportFormats.ts`
  - `src/utils/externalProviderImport.ts`
  - `src-tauri/src/modules/codex_account.rs`
  - `src/components/codex/CodexModelProviderManager.tsx`
- Supported import/export shapes:
  - Cockpit Tools portable JSON supports OAuth and API key accounts.
  - `cpa` is portable Codex token storage and is OAuth-oriented.
  - `sub2api` uses `{ type: "sub2api-data", accounts: [{ credentials: ... }] }` and is OAuth-oriented.
- Functions suitable for 8770:
  - local Cockpit account import
  - API key account save/probe/switch
  - cpa/sub2api/Cockpit JSON import
  - provider/base URL presets as UI convenience only
- Functions intentionally not promoted into 8770 main flow:
  - Codex App instance launch/restart
  - Cockpit-owned switch guard/repair as the main switching path
  - model provider custom bucket projection that hides Codex App history

## Compatibility Finding
- After 8770 switches to API, Cockpit Tools current account can still be OAuth.
- Running `codex-interop-check.py --quick-launch` then fails by design because that checker assumes Cockpit Tools owns the current Codex account projection.
- Therefore `修复 Cockpit 接管` can overwrite a 8770 API selection if used in the wrong mode; it is now labeled and placed as compatibility diagnostics, not part of the 8770 API switching path.

## Verification Commands
- `python -m unittest tests.runtime.test_codex_local.CodexLocalTests.test_codex_status_prefers_switchable_api_duplicate_over_legacy_auto_snapshot tests.runtime.test_codex_local.CodexLocalTests.test_codex_status_collapses_oauth_profiles_by_email_across_sources`
  - status: pass
  - key_output: `Ran 2 tests ... OK`
- `python -m unittest tests.runtime.test_operator_ui.OperatorUiTests.test_operator_ui_renders_empty_state_html tests.runtime.test_operator_ui.OperatorUiTests.test_operator_ui_renders_non_empty_snapshot tests.runtime.test_operator_ui.OperatorUiTests.test_operator_ui_renders_english_html_when_requested tests.runtime.test_operator_ui.OperatorUiTests.test_operator_ui_interactive_mode_renders_actions_and_ref_buttons`
  - status: pass
  - key_output: `Ran 4 tests ... OK`
- `python -m unittest tests.runtime.test_codex_local tests.runtime.test_operator_ui`
  - status: pass
  - key_output: `Ran 44 tests ... OK`
- `python -m py_compile scripts\lib\codex_local.py scripts\serve-operator-ui.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_script.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_text.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_style.py`
  - status: pass
- `python -m unittest tests.runtime.test_codex_local tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui`
  - status: pass
  - key_output: `Ran 81 tests ... OK`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - status: pass
  - key_output: `OK python-bytecode`, `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - status: pass
  - key_output: `Completed 111 test files ... failures=0`, `OK runtime-unittest`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - status: pass
  - key_output: `OK dependency-baseline`, `OK agent-rule-sync`, `OK functional-effectiveness`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - status: pass with existing warning
  - key_output: `OK gate-command-doctor`, `WARN codex-capability-degraded`

## Rollback
- Restore deleted legacy snapshot from `C:\Users\sciman\.codex\auth-backups\auto-fdb75e04ea-20260511-193501.json` if needed.
- Restore active auth from `C:\Users\sciman\.codex\auth-backups\auth-20260511-193527.json` if API active profile must be reverted.
- Restore config from `C:\Users\sciman\.codex\config-backups\config-20260511-193527.toml` if the API projection must be reverted.
- Code rollback: revert the modified files in this change.
