# Claude Provider Delete UI

- date: 2026-05-03
- rule_ids: R1, R4, R6, R8, E4
- risk: medium
- current_landing: `scripts/lib/claude_local.py`, `scripts/claude-provider.py`, `scripts/claude-provider.ps1`, `scripts/serve-operator-ui.py`, `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
- target_landing: localhost operator UI `http://127.0.0.1:8770/?lang=zh-CN` and Claude provider CLI
- rollback: revert this change set from git history; deleted provider profile metadata is backed up under Claude home `provider-profiles-backups/` before profile removal

## Change

- Added `delete_provider_profile()` for backing up and deleting non-active local Claude provider profiles.
- Added CLI entrypoint `python scripts/claude-provider.py delete <name> [--dry-run]`.
- Added PowerShell entrypoint `scripts/claude-provider.ps1 delete <name>`.
- Added localhost API `POST /api/claude/delete`.
- Added a `删除` action in the Claude provider panel for inactive providers only.
- Refused deletion of the active Claude provider and refused deletion of the last provider profile.

## Boundary

- This deletes only local provider profile metadata from `provider-profiles.json`.
- It does not delete a Claude/Anthropic cloud account.
- It does not delete credential values from `settings.json` or process environment variables.
- Active provider deletion requires switching to another provider first.
- Deleted default provider profiles remain retired through later default profile refreshes by `retired_profiles`; selecting a retired provider explicitly restores it.
- `delete --dry-run` and `optimize` dry-run paths do not write default provider profiles to disk.

## pre_change_review

- control_repo_manifest_and_rule_sources: compared `rules/manifest.json`, managed global sources under `rules/global/*`, and managed project sources under `rules/projects/*`; source versions converged to `9.50`.
- user_level_deployed_rule_files: synced managed user-level files under `C:\Users\sciman\.codex`, `C:\Users\sciman\.claude`, and `C:\Users\sciman\.gemini`; dry-run after sync reports `changed_count=0`, `blocked_count=0`, all 18 entries `skipped_same_hash`.
- target_repo_deployed_rule_files: synced managed project rule files for `governed-ai-coding-runtime`, `ClassroomToolkit`, `skills-manager`, `github-toolkit`, and `vps-ssh-launcher`; dry-run after sync reports matching source and target sha256 values.
- target_repo_gate_scripts_and_ci: retained the project hard gate sequence `build -> test -> contract/invariant -> hotspot`; no CI or gate entrypoint was changed in this slice.
- target_repo_repo_profile: no `.governed-ai/repo-profile.json` changes were made; rule sync used the existing target catalog/profile facts.
- target_repo_readme_and_operator_docs: no README/operator doc contract changes were required for the delete API because the localhost UI and CLI help expose the action directly.
- current_official_tool_loading_docs: local platform diagnostics ran `codex --version` (`codex-cli 0.128.0`) and `codex --help`; visible commands include `exec`, `review`, `mcp`, `plugin`, `sandbox`, `debug`, and `features`.
- drift-integration decision: rule sync drift was integrated by applying the managed `9.50` sources instead of editing deployed target files by hand; backups were written under `docs/change-evidence/rule-sync-backups/`.

## Rule Sync Evidence

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply`
  - result: pass, `status=applied`, `entry_count=18`, `changed_count=18`, `blocked_count=0`
  - backup roots: `docs/change-evidence/rule-sync-backups/20260503-232713/`, `docs/change-evidence/rule-sync-backups/20260503-232807/`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -FailOnChange`
  - result: pass, `changed_count=0`, `blocked_count=0`, all managed rule targets `skipped_same_hash`

## Verification

- `python -m unittest tests.runtime.test_claude_local tests.runtime.test_codex_local tests.runtime.test_operator_ui tests.runtime.test_operator_entrypoint`
  - result: pass, `Ran 56 tests in 31.515s`
- `python scripts/serve-operator-ui.py --lang zh-CN --output .runtime/artifacts/operator-ui/index.html`
  - result: pass, generated static zh-CN operator UI
- `python scripts/claude-provider.py delete --help`
  - result: pass, delete command help is available
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Restart -UiLanguage zh-CN -Port 8770`
  - result: pass, service restarted
- `Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8770/?lang=zh-CN'`
  - result: HTTP 200, page contains `/api/claude/delete`, delete confirmation copy, `Claude Provider 与配置`, and existing `/api/codex/delete`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - result: pass, `OK python-bytecode`, `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - result: pass, `Completed 103 test files in 172.358s; failures=0`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - result: pass, including `OK dependency-baseline`, `OK target-repo-governance-consistency`, `OK agent-rule-sync`, `OK functional-effectiveness`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - result: pass with existing warning `WARN codex-capability-degraded`; all other checks OK
