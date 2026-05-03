# Codex Account Delete UI

- date: 2026-05-03
- rule_ids: R1, R4, R6, R8, E4
- risk: medium
- current_landing: `scripts/lib/codex_local.py`, `scripts/codex-account.py`, `scripts/codex-account.ps1`, `scripts/serve-operator-ui.py`, `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
- target_landing: localhost operator UI `http://127.0.0.1:8770/?lang=zh-CN` and Codex account CLI
- rollback: revert this change set from git history; deleted local auth snapshots are backed up under Codex home `auth-backups/` before removal

## Change

- Added `delete_auth_profile()` for backing up and deleting non-active local Codex auth snapshots.
- Added CLI entrypoint `python scripts/codex-account.py delete <name> [--dry-run]`.
- Added PowerShell entrypoint `scripts/codex-account.ps1 delete <name>`.
- Added localhost API `POST /api/codex/delete`.
- Added a `删除` action in the Codex account panel for inactive snapshots only.
- Refused deletion of `auth.json` and any snapshot whose content matches the currently active `auth.json`.

## Verification

- `python -m unittest tests.runtime.test_codex_local tests.runtime.test_operator_ui tests.runtime.test_operator_entrypoint`
  - result: pass, `Ran 47 tests in 23.730s`
- `python scripts/serve-operator-ui.py --lang zh-CN --output .runtime/artifacts/operator-ui/index.html`
  - result: pass, generated static zh-CN operator UI
- `python scripts/codex-account.py delete --help`
  - result: pass, delete command help is available
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Restart -UiLanguage zh-CN -Port 8770`
  - result: pass, service restarted
- `Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8770/?lang=zh-CN'`
  - result: HTTP 200, page contains `/api/codex/delete`, delete confirmation copy, and `Codex 账号与配置`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - result: pass, `OK python-bytecode`, `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - result: pass, `Completed 103 test files in 111.964s; failures=0`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - result: pass, including `OK dependency-baseline`, `OK target-repo-governance-consistency`, `OK agent-rule-sync`, `OK functional-effectiveness`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - result: pass with existing warning `WARN codex-capability-degraded`; all other checks OK

## Compatibility

- This deletes only local Codex auth snapshot files; it does not delete an OpenAI or ChatGPT cloud account.
- Active credentials remain protected. To delete a currently active saved snapshot, switch to another account first.
- Deletion creates a backup before removing the snapshot file.
