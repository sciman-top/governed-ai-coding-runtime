# 20260501 Core Principle Change Artifact Contract

## Goal
Add machine-verifiable contracts for core-principle change proposal, manifest, and optional dry-run report artifacts while preserving the proposal-first safety boundary.

## pre_change_review
- control_repo_manifest_and_rule_sources: checked `schemas/catalog/schema-catalog.yaml`, `docs/specs/*`, `scripts/verify-repo.ps1`, and current materializer/operator flow before changing the contract gate.
- user_level_deployed_rule_files: not changed; no user-level `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` sync is performed by this task.
- target_repo_deployed_rule_files: not changed; no target-repo rule sync is performed by this task.
- target_repo_gate_scripts_and_ci: not changed; only this control repo's local `scripts/verify-repo.ps1` contract gate is extended.
- target_repo_repo_profile: not changed.
- target_repo_readme_and_operator_docs: README files are updated only to describe the new audit-only dry-run report switch.
- current_official_tool_loading_docs: no tool loading model change; the task stays inside repository-local schema, operator, and gate behavior.
- drift-integration decision: no drift integration required because this change does not alter distributed rules, target repo gates, target repo profiles, or host loading semantics.

## Changes
- Added schema/spec/example coverage for:
  - core-principle change proposals
  - core-principle change manifests
  - core-principle change dry-run reports
- Added contract-gate validation for existing core-principle change artifacts under `docs/change-evidence/core-principle-change-*`.
- Added explicit `overwrite_same_candidate` semantics and SHA-256 operation hashes to materializer output.
- Added `-WriteCorePrincipleDryRunReport` as an audit-only path that writes only a dry-run report, not proposal/manifest or active policy files.

## Verification
- `python -m unittest tests.runtime.test_core_principle_change_materialization`
  - Result: pass. `Ran 9 tests`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - First run reached new artifact schema checks and then correctly failed at `pre-change-review` because this evidence file did not yet exist.

## Rollback
- Revert the schema/spec/example additions.
- Revert `scripts/materialize-core-principle-change.py`, `scripts/materialize-core-principle-change.ps1`, `scripts/operator.ps1`, `scripts/verify-repo.ps1`, and README changes.
- Delete any generated dry-run report under `docs/change-evidence/core-principle-change-reports/`; active core-principle policy/spec/verifier files are not changed by this task.
