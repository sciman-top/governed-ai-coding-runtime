# 20260430 Claude Code Local Provider Console

## Goal
- Optimize local Claude Code settings for third-party Anthropic-compatible providers instead of official Claude subscription login.
- Keep the default provider as BigModel GLM, add a DeepSeek v4 profile, and expose provider/config health in the existing localhost Operator UI.
- Preserve secrets only in user-owned local settings/env; repository provider profiles must not store API keys or tokens.

## Sources
- Anthropic Claude Code settings/env docs: `https://code.claude.com/docs/en/settings`, `https://code.claude.com/docs/en/env-vars`
- Anthropic permission modes docs: `https://code.claude.com/docs/en/permission-modes`
- BigModel Claude API compatibility docs: `https://docs.bigmodel.cn/cn/guide/develop/claude/introduction`, `https://docs.bigmodel.cn/cn/guide/develop/claude`
- DeepSeek Anthropic API docs: `https://api-docs.deepseek.com/guides/anthropic_api`

## Changed Files
- `scripts/lib/claude_local.py`
- `scripts/claude-provider.py`
- `scripts/claude-provider.ps1`
- `scripts/Optimize-ClaudeLocal.ps1`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
- `scripts/serve-operator-ui.py`
- `tests/runtime/test_claude_local.py`
- `tests/runtime/test_operator_ui.py`
- `tests/runtime/test_operator_entrypoint.py`
- `README.md`
- `README.zh-CN.md`
- `docs/README.md`

## Local User Changes
- Updated `C:\Users\sciman\.claude\settings.json` after creating backup:
  - backup: `C:\Users\sciman\.claude\settings-backups\settings-20260430-030024.json`
  - active provider: `bigmodel-glm`
  - `model`: `opus` instead of `opus[1m]`
  - `permissions.defaultMode`: `dontAsk`
  - `permissions.disableBypassPermissionsMode`: `disable`
  - `skipDangerousModePermissionPrompt`: `false`
  - BigModel env retained with `ANTHROPIC_AUTH_TOKEN` redacted and provider URL `https://open.bigmodel.cn/api/anthropic`
  - compatibility/performance env added: `CLAUDE_CODE_MAX_OUTPUT_TOKENS=8192`, `CLAUDE_CODE_MAX_RETRIES=6`, `BASH_DEFAULT_TIMEOUT_MS=300000`, `BASH_MAX_TIMEOUT_MS=1200000`, `BASH_MAX_OUTPUT_LENGTH=30000`
  - nonessential/login/upgrade traffic disabled for third-party provider flow
- Added `C:\Users\sciman\.claude\provider-profiles.json` without secrets.
- Installed provider switcher:
  - `C:\Users\sciman\.claude\scripts\Switch-ClaudeProvider.ps1`
  - `C:\Users\sciman\.claude\scripts\claude-provider.py`
  - `C:\Users\sciman\.claude\scripts\lib\claude_local.py`
  - `C:\Users\sciman\.local\bin\claude-provider.cmd`

## Decision
- Use `permissions.defaultMode="dontAsk"` plus explicit allow/deny rules instead of `bypassPermissions`.
- Keep BigModel as the default because the current local credential already exists and BigModel documents Claude Code support through `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_BASE_URL`.
- Add DeepSeek as a fail-closed profile. Switching requires `ANTHROPIC_API_KEY`; without it, the switch returns an error and does not remove the active GLM credential.
- Do not expose third-party quota numbers in UI; no stable local API was found for provider quota windows.

## Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Optimize-ClaudeLocal.ps1`
  - status: pass after UTF-8 output fix
  - key_output: current config initially `attention`; planned changes did not print token values
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Optimize-ClaudeLocal.ps1 -Apply`
  - status: pass
  - key_output: `status=ok`, `config.status=ok`, backup created, switcher installed
- `python scripts/claude-provider.py status`
  - status: pass
  - key_output: `active_provider=bigmodel-glm`, `config.status=ok`, `claude --version=2.1.114`, all listed MCP servers connected
- `python scripts/claude-provider.py install`
  - status: pass
  - key_output: installed standalone `Switch-ClaudeProvider.ps1`, `claude-provider.py`, `lib/claude_local.py`, and `claude-provider.cmd`
- `C:\Users\sciman\.local\bin\claude-provider.cmd status`
  - status: pass
  - key_output: installed user-level shim resolves its local Python implementation and reports `config.status=ok`
- `python scripts/claude-provider.py switch deepseek-v4 --dry-run`
  - status: expected fail-closed
  - key_output: `missing credential: ANTHROPIC_API_KEY`
- `python -m unittest tests.runtime.test_claude_local`
  - status: pass
  - key_output: `Ran 3 tests`; `OK`
- `python -m unittest tests.runtime.test_operator_ui tests.runtime.test_operator_entrypoint`
  - status: pass
  - key_output: `Ran 13 tests`; `OK`
- `python -m py_compile scripts/lib/claude_local.py scripts/claude-provider.py packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py scripts/serve-operator-ui.py`
  - status: pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Restart -UiLanguage zh-CN`
  - status: pass
  - key_output: service ready at `http://127.0.0.1:8770/?lang=zh-CN`
- `Invoke-RestMethod http://127.0.0.1:8770/api/claude/status`
  - status: pass
  - key_output: `status=ok`, `active_provider=bigmodel-glm`, `config.status=ok`
- Browser check at `http://127.0.0.1:8770/?lang=zh-CN`
  - status: pass
  - key_output: same-page tabs `Runtime / Codex / Claude`; Claude tab shows BigModel active, DeepSeek missing credential, config `ok`
  - screenshot: `docs/change-evidence/claude-operator-ui-tabs.png`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - status: pass
  - key_output: `OK python-bytecode`, `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - status: pass
  - key_output: `Running 78 test files`; `failures=0`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - status: pass
  - key_output: `OK dependency-baseline`, `OK agent-rule-sync`, `OK functional-effectiveness`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - status: pass
  - key_output: all checks `OK`, including `codex-capability-ready` and `adapter-posture-visible`
- Secret scan over changed text files
  - status: pass
  - key_output: no real key/hash pattern hits; only pre-existing test fixture string `ANTHROPIC_AUTH_TOKEN = "must-not-propagate"`
- `README.zh-CN.md` sync check
  - status: pass
  - key_output: Chinese README now documents `Optimize-CodexLocal.ps1`, `Optimize-ClaudeLocal.ps1`, and the same-page Codex/Claude Operator UI tabs

## Residual Risks
- DeepSeek switching is configured but blocked until a valid `ANTHROPIC_API_KEY` exists locally.
- Provider usage/quota remains provider-side; the Operator UI intentionally reports it as unknown instead of scraping unstable account pages.
- `dontAsk` reduces prompts by design. Safety depends on deny rules, hooks, git review, and runtime gates.

## Rollback
- Restore the backup `C:\Users\sciman\.claude\settings-backups\settings-20260430-030024.json` to `C:\Users\sciman\.claude\settings.json`.
- Remove `C:\Users\sciman\.claude\provider-profiles.json`, `C:\Users\sciman\.claude\scripts\Switch-ClaudeProvider.ps1`, and `C:\Users\sciman\.local\bin\claude-provider.cmd` if provider switching should be removed.
- Revert the repository files listed above and rerun the full gate sequence.
