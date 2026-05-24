# 2026-05-23 Token-Efficient Search Ignore

- rules: R1/R6/R8, context_budget_and_instruction_minimalism
- risk: low
- current_location: `D:\CODE\governed-ai-coding-runtime`
- target_destination: repo-local search/context hygiene for daily coding

## Basis
- pre_change_review:
  - control_repo_manifest_and_rule_sources: compared `rules/manifest.json`, rule source files under `rules/global/**` and `rules/projects/**`, plus the target governance baseline and rollout contract before integrating `.ignore`.
  - user_level_deployed_rule_files: inspected drift through `python scripts/sync-agent-rules.py --scope All --fail-on-change`; deployed global Codex/Claude/Gemini rule files were behind source version `9.53` and were synchronized with backups.
  - target_repo_deployed_rule_files: the same drift check covered the six target repo rule projections; all were synchronized from control repo sources to version `9.53`.
  - target_repo_gate_scripts_and_ci: target rollout used `scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json`, then `scripts/verify-target-repo-rollout-contract.py`, `scripts/verify-target-repo-governance-consistency.py`, and runtime preset unit tests.
  - target_repo_repo_profile: target catalog/baseline contract remained repo-profile driven; `.ignore` was added as a managed file with `block_on_drift`, not as a repo-specific ad hoc copy.
  - target_repo_readme_and_operator_docs: no README/operator workflow semantics changed; the new file only narrows default search context and remains bypassable with explicit paths or `rg -u`.
  - current_official_tool_loading_docs: Codex loading semantics were treated as rule-file context only; live Codex config token-efficiency changes were kept outside `ApplyAllFeatures` because this repo must not write auth/provider/profile/runtime switching state.
  - drift-integration decision: integrate `.ignore` into the one-click governance baseline, synchronize existing rule drift through the canonical rule-sync entrypoint, and leave live Codex config as backed-up local state rather than a managed target baseline file.
- Live Codex config inspected read-only:
  - `model_context_window = 516000`
  - `model_auto_compact_token_limit = 460000`
  - `model_reasoning_effort = "xhigh"`
- Repo-owned recommended defaults remain:
  - `scripts/lib/codex_local.py`: `272000 / 220000 / medium`
  - `tests.runtime.test_codex_local`: verifies the same recommended context and compact values
- One broad `rg ... .` search produced an original tool-output estimate over `553000` tokens because historical evidence and archive-heavy paths were included before the search surface was narrowed.

## Change
- Added root `.ignore` so daily `rg` searches skip archive-heavy and binary-heavy context by default:
  - `docs/change-evidence/**`
  - `docs/archive/**`
  - long backlog history files
  - operator UI screenshots and generated/local runtime caches
- Integrated `.ignore` into the one-click target governance baseline:
  - template: `docs/targets/templates/search-context.ignore`
  - baseline: `docs/targets/target-repo-governance-baseline.json`
  - rollout contract: `docs/targets/target-repo-rollout-contract.json`
  - mode: `block_on_drift`
- Archived evidence remains available with explicit paths or `rg -u`.
- Adjusted live Codex user config after backup:
  - backup: `C:\Users\sciman\.codex\config.toml.bak-token-efficiency-20260523-162106`
  - `model_context_window`: `516000 -> 272000`
  - `model_auto_compact_token_limit`: `460000 -> 220000`
  - `model_reasoning_effort`: `xhigh -> medium`
  - unchanged fields verified in readback: `model_provider = "openai"`, `model = "gpt-5.3-codex"`, `sandbox_mode = "workspace-write"`, `approval_policy = "never"`

## Verification
- `rg -l <token/context pattern> .` after the change:
  - matched files: `310`
  - `docs/change-evidence` matches: `0`
  - `docs/archive` matches: `0`
  - heavy backlog matches: `0`
- `rg --files` after the change: `596` default files.
- `git diff --check -- .ignore`: pass.
- `python -m unittest tests.runtime.test_codex_local tests.runtime.test_policy_tool_credential_audit`: pass, `31` tests.
- Fresh readback of `C:\Users\sciman\.codex\config.toml` showed `272000 / 220000 / medium`.
- Backup diff showed only the intended three token-efficiency lines changed.
- `python -m unittest tests.runtime.test_target_repo_governance_consistency tests.runtime.test_runtime_flow_preset`: pass, `59` tests.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json`: pass, `target_count = 6`, `failure_count = 0`.
- `python scripts/verify-target-repo-rollout-contract.py`: pass, `sync_revision = 2026-05-23.1`.
- `python scripts/verify-target-repo-governance-consistency.py`: pass, `drift_count = 0`.
- `python -m unittest tests.runtime.test_target_repo_rollout_contract tests.runtime.test_target_repo_governance_consistency tests.runtime.test_runtime_flow_preset`: pass, `71` tests.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply`: pass, `changed_count = 21`, `blocked_count = 0`; backups written under `docs/change-evidence/rule-sync-backups/20260523-175451/`.
- `python scripts/sync-agent-rules.py --scope All --fail-on-change`: pass after sync, `changed_count = 0`, `blocked_count = 0`.

## Rollback
- Remove `.ignore`.
- Remove `docs/targets/templates/search-context.ignore` and the matching `.ignore` entries from:
  - `docs/targets/target-repo-governance-baseline.json`
  - `docs/targets/target-repo-rollout-contract.json`
- Restore live config from `C:\Users\sciman\.codex\config.toml.bak-token-efficiency-20260523-162106` if the lower context profile causes a concrete regression.
- Re-run:
  - `rg --files`
  - `python -m unittest tests.runtime.test_codex_local tests.runtime.test_policy_tool_credential_audit`
