# 20260615 Workflow Governance Pre-Change Review

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_profile.py`
  - `schemas/jsonschema/repo-profile.schema.json`
  - `schemas/examples/repo-profile/governed-ai-coding-runtime.example.json`
  - `docs/specs/repo-profile-spec.md`
  - `scripts/runtime-flow-preset.ps1`
  - `tests/runtime/test_repo_profile.py`
  - `tests/runtime/test_runtime_flow_preset.py`
- verification path: add a bounded workflow-governance slice to repo-profile and `runtime-flow-preset`, then prove it with runtime tests and the existing contract/docs gates without changing `planning-status.json`

## Pre-Change Review
pre_change_review

- changed_surface_paths:
  - `docs/specs/repo-profile-spec.md`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_profile.py`
  - `schemas/examples/repo-profile/governed-ai-coding-runtime.example.json`
  - `schemas/jsonschema/repo-profile.schema.json`
  - `scripts/runtime-flow-preset.ps1`
  - `tests/runtime/test_repo_profile.py`
  - `tests/runtime/test_runtime_flow_preset.py`

- control_repo_manifest_and_rule_sources:
  - reviewed `AGENTS.md`
  - reviewed `rules/manifest.json`
  - confirmed this slice stays inside the control repo and does not mutate rule sync sources

- user_level_deployed_rule_files:
  - reviewed requirement boundary from project and global `AGENTS.md`
  - no user-level deployed rule file mutation in this slice

- target_repo_deployed_rule_files:
  - reviewed `docs/targets/target-repo-governance-baseline.json`
  - confirmed this slice does not directly mutate target deployed rule files

- target_repo_gate_scripts_and_ci:
  - reviewed `scripts/runtime-flow-preset.ps1`
  - reviewed `scripts/verify-repo.ps1`
  - confirmed the gate chain remains `build -> test -> contract/invariant -> hotspot`

- target_repo_repo_profile:
  - reviewed `schemas/jsonschema/repo-profile.schema.json`
  - reviewed `schemas/examples/repo-profile/governed-ai-coding-runtime.example.json`
  - reviewed `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_profile.py`
  - decision: add a bounded `workflow_governance_policy` surface so workflow selection becomes repo-owned, machine-readable, and explicitly degradable

- target_repo_readme_and_operator_docs:
  - reviewed `README.md`
  - reviewed `docs/README.md`
  - current slice does not yet tighten those product/value claims; that remains a follow-on doc/evidence task

- current_official_tool_loading_docs:
  - reviewed current Codex loading semantics from repo `AGENTS.md`
  - kept `planning-status.json` untouched and did not introduce host capability claims beyond explicit degrade behavior

- drift-integration decision:
  - accept a minimal vertical slice now:
    - repo-profile contract supports workflow governance policy
    - `runtime-flow-preset` projects `workflow_mode_selected`, `workflow_mode_source`, `workflow_mode_reason`, `workflow_degrade_reason`, `workflow_required_artifacts`, and `workflow_metrics`
    - advanced modes degrade explicitly instead of being silently claimed
  - defer the wider queue/reference/value-audit package until the repo-owned files actually exist in the worktree

## Verification
- `python -m unittest tests.runtime.test_repo_profile tests.runtime.test_runtime_flow_preset -v`
  - result: pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - result: pass

## Risk
- risk_level: `medium`
- reason: touches repo-profile contract/schema/example and the canonical target orchestration script, but stays additive and keeps advanced workflow claims behind explicit degrade behavior

## Rollback
- revert:
  - `docs/specs/repo-profile-spec.md`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_profile.py`
  - `schemas/examples/repo-profile/governed-ai-coding-runtime.example.json`
  - `schemas/jsonschema/repo-profile.schema.json`
  - `scripts/runtime-flow-preset.ps1`
  - `tests/runtime/test_repo_profile.py`
  - `tests/runtime/test_runtime_flow_preset.py`
