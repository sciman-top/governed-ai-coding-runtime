# 2026-05-12 Agent switching ownership boundary

- rule_id: `R1/R4/R6/R8`
- risk: `medium`
- current_landing: local Codex/Cockpit and Claude/CC Switch integration surfaces
- target_landing: this repository becomes read-only diagnostics only for account/API switching concerns
- rollback: revert this change set from git history if the repository must temporarily resume managed local switching

## Boundary

- `Cockpit Tools` owns Codex App/CLI account and API switching.
- `CC Switch` owns Claude Code / Claude Desktop account and API switching.
- This repository must not write, repair, intercept, install, delete, optimize, or restart-wrap either switching surface.

## Changes

- Disabled project-managed Claude provider management entrypoints in `scripts/lib/claude_local.py`.
- Kept `claude-provider status|continuity` read-only and removed implicit provider-profile writes from `status` and `list`.
- Left deprecated `claude-provider switch|install|optimize|delete` commands in place only to fail closed with `project_managed_claude_switching_disabled`.
- Updated the 8770 Claude panel copy and controls so it no longer presents switch/delete/optimize actions.
- Updated README and quickstart docs to make Cockpit Tools and CC Switch the exclusive switching owners.

## Verification

- `python -m unittest tests.runtime.test_claude_local`
- `python -m unittest tests.runtime.test_operator_ui tests.runtime.test_operator_entrypoint`
- `python -m py_compile scripts\lib\claude_local.py scripts\claude-provider.py scripts\serve-operator-ui.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_script.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_text.py`

## Rollback

- Revert this change set from git history.
- Do not manually restore project-managed Claude or Codex switching shims unless the ownership boundary is explicitly changed again.
