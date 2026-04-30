## Summary

- Integrated Claude local-provider actions into the existing localhost operator UI at `http://127.0.0.1:8770/?lang=zh-CN` instead of keeping `claude-provider` as a separate terminal-first entrypoint.
- Added same-page Claude actions for recommended-config preview/apply plus safe previews of local `settings.json`, `provider-profiles.json`, and `Switch-ClaudeProvider.ps1`.
- Reworked the Claude tab layout into a clearer split between active-provider summary, provider cards, and local entrypoints so GLM/DeepSeek choices and compact strategy are visible without opening files first.

## Changed Files

- `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
- `scripts/serve-operator-ui.py`
- `scripts/lib/claude_local.py`
- `tests/runtime/test_operator_ui.py`
- `tests/runtime/test_claude_local.py`
- `README.md`
- `README.zh-CN.md`
- `README.en.md`

## Verification

- `python -m py_compile packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py scripts/serve-operator-ui.py scripts/lib/claude_local.py`
  - key_output: success
- `python -m unittest tests/runtime/test_operator_ui.py tests/runtime/test_claude_local.py`
  - key_output: `Ran 9 tests ... OK`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Restart`
  - key_output: localhost operator UI restarted
- Browser verification at `http://127.0.0.1:8770/?lang=zh-CN`
  - key_output: Claude tab shows `预演推荐配置` / `应用推荐配置`, local file preview buttons, active-provider summary cards, GLM/DeepSeek provider cards
  - key_output: `预演推荐配置` writes dry-run optimize JSON to the output panel
  - key_output: `查看 provider-profiles.json` previews `C:\Users\sciman\.claude\provider-profiles.json` in the output panel
- Full repo gates:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - key_output: all passed

## Compatibility / Risk

- No new arbitrary filesystem read path was added to the browser UI. The new file-preview surface is allowlisted to Claude-local config files only.
- Existing `/api/claude/status` and `/api/claude/switch` behavior remains intact; the new `/api/claude/optimize` and `/api/claude/file` routes are additive.

## Rollback

- Revert the changed files above.
- Restart the operator UI service:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Restart`
