# 2026-05-12 Claude CC Switch provider live probe

## 2026-05-12 Boundary Update

This earlier probe proved Claude Code connectivity through Zhipu GLM and DeepSeek, but the ownership boundary was corrected afterward:

- `CC Switch` owns all Claude Code / Claude Desktop account, API, and provider switching.
- This repository no longer switches, installs, optimizes, deletes, or imports Claude provider state.
- `claude-provider status|continuity` remain read-only diagnostics only.
- `claude-provider switch|install|optimize|delete` now return `project_managed_claude_switching_disabled`.

The live connectivity findings below remain historical evidence only; they are no longer a contract that this repository should perform switching.

- rule_id: `R1/R6/R8/E4`
- risk: `medium`
- current_landing: local Claude Code provider settings and CC Switch SQLite provider state
- target_landing: `scripts/lib/claude_local.py`, `scripts/claude-provider.py`, `scripts/claude-provider.ps1`, `tests/runtime/test_claude_local.py`
- rollback: restore the latest `C:\Users\sciman\.claude\settings-backups\settings-*.json` for local state, or revert this change set from git history

## Root Cause

- `cc-switch` is installed as a desktop app and stores provider rows in `C:\Users\sciman\.cc-switch\cc-switch.db`; no `cc-switch` CLI shim is on PATH.
- CC Switch stores both Zhipu GLM and DeepSeek Claude provider credentials under `ANTHROPIC_AUTH_TOKEN`.
- The previous repo `deepseek-v4` profile expected `ANTHROPIC_API_KEY`, so repo switching could not use the existing local CC Switch DeepSeek credential.
- CC Switch common/provider config also contained drift such as `model=opus[1m]` and Zhipu `ANTHROPIC_DEFAULT_SONNET_MODEL=glm-5.1`; importing those values directly caused `claude-provider status` to report `attention`.

## Changes

- Added optional `--cc-switch-db` / `-CcSwitchDb` support to `claude-provider status` and `switch`.
- `switch` can now import the matching CC Switch Claude provider env from local SQLite, with secret values redacted in command output.
- Provider profile defaults now keep DeepSeek aligned with the observed local Anthropic-compatible shape: `ANTHROPIC_AUTH_TOKEN`, `deepseek-v4-pro`, and `deepseek-v4-flash`.
- CC Switch provides local secrets and endpoint values, while repo provider profiles remain authoritative for recommended non-secret model mapping.

## Verification

- `python -m unittest tests.runtime.test_claude_local` -> `Ran 12 tests ... OK`
- `python -m py_compile scripts\lib\claude_local.py scripts\claude-provider.py` -> exit `0`
- `claude-provider status -CcSwitchDb C:\Users\sciman\.cc-switch\cc-switch.db` -> `active=bigmodel-glm`, `config_status=ok`, `continuity=ok`, `cc_switch_current=Zhipu GLM`
- `claude --bare -p --output-format json --model haiku "Reply exactly: GLM_OK"` -> `GLM_OK`, model `glm-4.5-air`
- `claude --bare -p --output-format json --model haiku "Reply exactly: DEEPSEEK_OK"` after switching through CC Switch DB -> `DEEPSEEK_OK`, model `deepseek-v4-flash`
- Target repo probes, Zhipu GLM: `classroomtoolkit`, `github-toolkit`, `k12-question-graph`, `self-runtime`, `skills-manager`, `vps-ssh-launcher` all returned `TARGET_OK <repo>` with exit `0`
- Target repo probes, DeepSeek: the same six target repos all returned `TARGET_OK <repo>` with exit `0`

## Desktop History Findings

- Claude Code CLI continuity is healthy and still anchored in `C:\Users\sciman\.claude`: `projects_jsonl=258`, `history.jsonl=true`, `provider_switch_policy=preserve_claude_home`.
- Claude Desktop official profile and Claude Desktop 3p profile are separate Electron app data roots:
  - `C:\Users\sciman\AppData\Roaming\Claude`: `localAgentFiles=629`
  - `C:\Users\sciman\AppData\Local\Claude-3p`: `deploymentMode=3p`, `localAgentFiles=12`, `claudeCodeSessionFiles=1`
- Therefore the file-level evidence does not support claiming that both Claude Desktop profiles show all local-agent history. No symlink/copy repair was applied because merging Electron/VM session stores is a higher-risk state migration and was not needed for Claude Code provider connectivity.
