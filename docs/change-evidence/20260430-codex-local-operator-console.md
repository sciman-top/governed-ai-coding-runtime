# 2026-04-30 Codex Local Operator Console

## Scope
- Added a repository-owned Codex local account/config helper.
- Extended the localhost operator UI with a Codex account and configuration panel.
- Added a dry-run-first new-machine optimizer for user-level Codex defaults.
- Cleaned the local user config by removing the stale non-ChatGPT token line.

## Risk
- Risk tier: medium.
- Sensitive boundary: ChatGPT auth JSON files remain user-owned. UI and scripts expose only file names, short hashes, auth mode, and refresh timestamps. Tokens are never printed.
- Usage limits: 5h/7d windows are shown as `unknown` until a stable official local API is available.

## Commands
- `python -m py_compile scripts/serve-operator-ui.py scripts/codex-account.py scripts/lib/codex_local.py packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
- `python scripts/codex-account.py status`
- `python scripts/codex-account.py list`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Optimize-CodexLocal.ps1`
- `python -m unittest tests.runtime.test_codex_local tests.runtime.test_operator_entrypoint -v`
- `python scripts/serve-operator-ui.py --output .runtime/artifacts/operator-ui/index.html --lang zh-CN`
- Browser verification: `http://127.0.0.1:8781/?lang=zh-CN`
- Browser verification after tab integration: `http://127.0.0.1:8770/?lang=zh-CN`

## Evidence
- Unit tests passed: `tests.runtime.test_codex_local`, `tests.runtime.test_operator_entrypoint`.
- Static operator UI generated `.runtime/artifacts/operator-ui/index.html`.
- Browser snapshot showed the Codex panel with auth profiles, login status, usage unknown state, and config health.
- Screenshot artifact: `docs/change-evidence/codex-operator-ui.png`.
- The Codex panel is integrated into the normal operator UI through in-page `Runtime / Codex` tabs on port `8770`.
- Tab screenshot artifact: `docs/change-evidence/codex-operator-ui-tabs.png`.

## Rollback
- Revert:
  - `scripts/lib/codex_local.py`
  - `scripts/codex-account.py`
  - `scripts/codex-account.ps1`
  - `scripts/Optimize-CodexLocal.ps1`
  - `scripts/serve-operator-ui.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
  - `tests/runtime/test_codex_local.py`
  - `tests/runtime/test_operator_entrypoint.py`
  - README updates
- Restore user-level Codex config from `C:\Users\sciman\.codex\config-backups\` if `Optimize-CodexLocal.ps1 -Apply` was used.
