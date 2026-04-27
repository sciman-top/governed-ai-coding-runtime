# 20260427 Claude Code Settings Hooks Template

## Goal
- Execute `GAP-116` by adding a managed Claude Code settings/hooks surface for target repos.
- Keep `CLAUDE.md` as context rules and `.claude/settings.json` plus hooks as enforceable host-control inputs.
- Avoid touching unrelated local Claude configuration such as `.claude/settings.local.json`.

## Changed Files
- `docs/targets/templates/claude-code/settings.json`
- `docs/targets/templates/claude-code/governed-pre-tool-use.py`
- `.claude/settings.json`
- `.claude/hooks/governed-pre-tool-use.py`
- `docs/targets/target-repo-governance-baseline.json`
- `tests/runtime/test_claude_code_governance_template.py`
- `tests/runtime/test_target_repo_governance_consistency.py`
- `docs/plans/claude-code-first-class-entrypoint-plan.md`
- target repos received managed `.claude/settings.json` and `.claude/hooks/governed-pre-tool-use.py` through governance baseline sync

## Decision
Claude Code first-class support uses separate surfaces:
- `CLAUDE.md` carries human-readable context, repo facts, gates, rollback, and N/A semantics.
- `.claude/settings.json` carries shared permissions and hook wiring.
- `.claude/hooks/governed-pre-tool-use.py` fail-closes direct Windows PowerShell usage and sensitive local file reads through hook exit code `2`.

The managed baseline writes only shared project settings and hook files. It does not write `.claude/settings.local.json`.

## Verification
- `python -m unittest tests.runtime.test_claude_code_governance_template tests.runtime.test_target_repo_governance_consistency.TargetRepoGovernanceConsistencyTests.test_default_baseline_requires_windows_process_environment_policy tests.runtime.test_target_repo_governance_consistency.TargetRepoGovernanceConsistencyTests.test_apply_target_repo_governance_check_only_fails_on_managed_file_drift`
  - status: pass
  - key_output: `Ran 6 tests`; `OK`
- `python -m py_compile docs/targets/templates/claude-code/governed-pre-tool-use.py`
  - status: pass
- `python -c "import json, pathlib; json.load(open('docs/targets/templates/claude-code/settings.json', encoding='utf-8')); print('settings-json-ok')"`
  - status: pass
  - key_output: `settings-json-ok`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json`
  - status: pass
  - key_output: `target_count=5`, `failure_count=0`
- `python scripts/verify-target-repo-governance-consistency.py`
  - status: pass
  - key_output: `sync_revision=2026-04-27.2`, `target_count=5`, `drift_count=0`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -FailOnChange`
  - status: pass
  - key_output: `entry_count=18`, `changed_count=0`, `blocked_count=0`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - status: pass
  - key_output: `OK target-repo-governance-consistency`, `OK target-repo-powershell-policy`, `OK agent-rule-sync`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - status: pass
  - key_output: `OK current-source-compatibility`, `OK post-closeout-queue-sync`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
  - status: pass
  - key_output: `OK powershell-parse`, `OK issue-seeding-render`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
  - status: pass
  - key_output: `Running 73 test files`, `failures=0`, `OK target-repo-governance-consistency`, `OK current-source-compatibility`, `OK issue-seeding-render`

## Residual Risks
- This does not certify Claude Code adapter conformance; that remains `GAP-117`.
- This does not certify all-target first-class support end to end; that remains `GAP-118` and `GAP-119`.
- Permission pattern behavior still depends on Claude Code host semantics; the Python hook provides fail-closed defense for the highest-risk checks.

## Rollback
Remove the managed Claude Code settings/hooks entries from `docs/targets/target-repo-governance-baseline.json`, delete the template files, rerun governance baseline sync, and revert target-repo `.claude/settings.json` / `.claude/hooks/governed-pre-tool-use.py` managed files if needed. Leave `CLAUDE.md` rule sync intact unless rolling back the broader `GAP-115..119` queue.
