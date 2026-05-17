# 2026-05-17 network research policy target sync

- rule_id: network_research_policy_target_sync
- risk_level: medium
- current_landing: `docs/targets/target-repo-governance-baseline.json`, `docs/targets/templates/claude-code/settings.json`, `scripts/apply-target-repo-governance.py`, `scripts/verify-target-repo-governance-consistency.py`, `schemas/jsonschema/repo-profile.schema.json`, `docs/architecture/control-pack-inheritance-matrix.json`, `docs/targets/target-repo-rollout-contract.json`
- target_destination: target repo `.governed-ai/repo-profile.json` plus `.claude/settings.json`; local Codex config gets only `web_search = "cached"`
- rollback: revert the listed control-repo files from git; restore `C:\Users\sciman\.codex\config.toml` from `C:\Users\sciman\.codex\config-backups\config-20260517-222824-before-web-search-enable.toml`; rerun `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json`

## Pre-change review

- pre_change_review: required because this changes governance baseline, rollout contract, repo-profile schema, target `.claude/settings.json` template, and target repo profile projections.
- control_repo_manifest_and_rule_sources: reviewed `rules/manifest.json`, loaded `AGENTS.md`, `docs/targets/target-repo-governance-baseline.json`, `docs/targets/target-repo-rollout-contract.json`, `docs/architecture/control-pack-inheritance-matrix.json`, and `schemas/jsonschema/repo-profile.schema.json`.
- user_level_deployed_rule_files: `python scripts\sync-agent-rules.py --scope All --fail-on-change` passed with `changed_count=0`, proving global/project rule files stayed in sync.
- target_repo_deployed_rule_files: same `sync-agent-rules.py --scope All --fail-on-change` checked 21 entries and reported no managed rule drift.
- target_repo_gate_scripts_and_ci: reviewed target catalog gate commands through `docs/targets/target-repos-catalog.json`; no build/test/contract command was changed.
- target_repo_repo_profile: `python scripts\verify-target-repo-governance-consistency.py` passed with `target_count=6`, `drift_count=0`, and `sync_revision=2026-05-17.1`.
- target_repo_readme_and_operator_docs: no operator entrypoint or user workflow command changed; this slice adds capability policy and settings/profile projection only.
- current_official_tool_loading_docs: local `codex --help` shows `--search` enables native Responses `web_search` without per-call approval; live `codex mcp list` still reports no MCP servers, so Codex is claimed as native-search-capable, not MCP-backed-search-capable.
- drift-integration decision: `json_merge` for `.claude/settings.json` now merges `permissions.allow` and `permissions.deny` string arrays without dropping target-local entries.

## Changes

- Added `network_research_policy` as a typed repo-profile baseline override with `network_posture=read_only`, `side_effect_class=network_read`, and `default_mode=autonomous_when_needed`.
- Added Claude Code project settings allow entries for `WebSearch`, `WebFetch`, and known read-only/search MCP tool patterns.
- Preserved target-local `.claude/settings.json` keys and allow/deny entries by changing JSON merge behavior to de-duplicate string arrays under `permissions.allow` and `permissions.deny`.
- Registered the new policy in the control-pack inheritance matrix, rollout contract, and repo-profile JSON schema.
- Applied the governance baseline to all 6 target repos: `classroomtoolkit`, `github-toolkit`, `k12-question-graph`, `self-runtime`, `skills-manager`, and `vps-ssh-launcher`.
- Added `web_search = "cached"` to live `C:\Users\sciman\.codex\config.toml` after creating the backup listed above.

## Verification

- `python -m py_compile scripts\apply-target-repo-governance.py scripts\verify-target-repo-governance-consistency.py scripts\lib\codex_local.py scripts\lib\claude_local.py`: pass.
- `python -m unittest tests.runtime.test_target_repo_governance_consistency.TargetRepoGovernanceConsistencyTests.test_default_baseline_requires_windows_process_environment_policy tests.runtime.test_target_repo_governance_consistency.TargetRepoGovernanceConsistencyTests.test_apply_target_repo_governance_json_merge_managed_file_preserves_local_keys tests.runtime.test_target_repo_governance_consistency.TargetRepoGovernanceConsistencyTests.test_verify_target_repo_governance_consistency_allows_json_merge_managed_file_local_keys`: pass.
- `python -m unittest tests.runtime.test_control_pack_inheritance tests.runtime.test_target_repo_rollout_contract`: pass.
- `python scripts\verify-control-pack-inheritance.py`: pass; `inherited_field_count=7`.
- `python scripts\verify-target-repo-rollout-contract.py`: pass; `capability_count=15`, `feature_count=7`.
- `python scripts\verify-target-repo-governance-consistency.py`: pass; `target_count=6`, `drift_count=0`.
- `python scripts\sync-agent-rules.py --scope All --fail-on-change`: pass; `entry_count=21`, `changed_count=0`, `blocked_count=0`.
- `git diff --check`: pass with line-ending warnings only.
- Target projection probe: all 6 targets had `.claude/settings.json` containing `WebSearch=true`, `WebFetch=true`, and `.governed-ai/repo-profile.json` containing `network_research_policy.network_posture=read_only`.
- Codex live probe: `C:\Users\sciman\.codex\config.toml` contains `web_search = "cached"`; `codex --help` exposes `--search`; `codex mcp list` reports no MCP servers configured; `codex --search exec ...` started with native search mode but the model call was blocked by the current Codex usage limit until `May 24th, 2026 10:30 PM`.
- Claude live probe: `C:\Users\sciman\.claude\settings.json` contains `WebSearch` and `WebFetch`; `claude mcp list` reported connected search/fetch/documentation MCP servers earlier in this run.
- Runtime timing follow-up: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime` exposed the pre-existing `test_runtime_flow_preset_all_targets_json_supports_target_parallelism` fixed wall-clock threshold under full-suite load (`elapsed=8.710816s`, threshold `<8.0s`). The test now verifies parallel execution against measured per-target duration instead of a host-dependent absolute threshold. Focused command `python -m unittest tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_all_targets_json_supports_target_parallelism`: pass, `Ran 1 test in 4.901s`.
- Final hard gates after the timing fix:
  - build: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1`: pass; `OK python-bytecode`, `OK python-import`.
  - test: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime`: pass; `Completed 111 test files in 189.374s; failures=0`, `OK runtime-unittest`.
  - contract/invariant: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Contract`: pass; includes `OK target-repo-governance-consistency`, `OK agent-rule-sync`, `OK functional-effectiveness`.
  - hotspot: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\doctor-runtime.ps1`: pass; exit code 0 with existing `WARN codex-capability-degraded`.
- `git diff --check`: pass with line-ending warnings only.
- Contract/runtime gates refreshed generated evidence files including `docs/change-evidence/runtime-test-speed-latest.json`, `docs/change-evidence/governance-hub-certification-report.json`, `docs/change-evidence/policy-tool-credential-audit-report.json`, and current-date guarded core-principle candidate artifacts under `docs/change-evidence/core-principle-change-*`; active core-principle policy files were not changed.
- Post-sync idempotence: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json`: pass; `target_count=6`, `failure_count=0`; all target `governance_sync_changed`, `governance_sync_blocked`, `governance_sync_managed_changed`, and `governance_sync_managed_blocked` arrays were empty.
- Fresh target content probe: all 6 targets have `network_research_policy.default_mode=autonomous_when_needed`, `network_research_policy.network_posture=read_only`, and Claude `permissions.allow` includes `WebSearch` and `WebFetch`.
- Target diff scope check: changed target repos only contain expected governance projection files (`.claude/settings.json`, `.governed-ai/repo-profile.json`, and `.governed-ai/managed-files/**.provenance.json`); `D:\CODE\ClassroomToolkit` had no new diff.
- Target diff whitespace check: `git diff --check` passed for changed target repos; `k12-question-graph` and `vps-ssh-launcher` reported line-ending warnings only.
- Unrelated target repo warning: `git -C D:\CODE\vps-ssh-launcher status --short --untracked-files=all` reports `warning: could not open directory 'port/' /': No such file or directory`; inspection found an untracked empty-looking abnormal directory under `D:\CODE\vps-ssh-launcher\port`. Governance checks still pass and tracked diff scope is limited to expected projection files. No cleanup was applied in this slice.

## Compatibility and N/A

- compatibility: additive profile field plus additive Claude allow entries; no gate command, auth provider, token, or target source code changes.
- platform_na: Codex MCP-backed search remains platform_na for this host because `codex mcp list` reports no MCP servers configured. Codex live exec search is also temporarily platform_na because `codex --search exec ...` reached the Codex usage limit; alternative verification is native `web_search` config plus `codex --help --search` support.
- gate_na: none.
