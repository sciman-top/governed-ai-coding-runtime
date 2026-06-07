# 2026-06-07 GAP-166..168 host capability claim contract closeout

- rule_id: gap_166_168_host_capability_claim_contract_closeout
- risk_level: medium
- current_landing: `docs/specs/agent-adapter-contract-spec.md`, `schemas/jsonschema/agent-adapter-contract.schema.json`, `schemas/examples/agent-adapter-contract/*`, `docs/architecture/host-capability-claim-upgrade-policy.json`, `scripts/verify-host-capability-claim-upgrade-policy.py`, `scripts/verify-repo.ps1`, `docs/architecture/host-family-capability-surface-blueprint.md`, `docs/strategy/current-best-end-state-blueprint.md`, `docs/product/interaction-model.md`, `docs/plans/host-family-capability-operationalization-plan.md`, `docs/backlog/issue-ready-backlog.md`, `docs/backlog/README.md`, `docs/plans/README.md`, `docs/README.md`, `tests/runtime/test_adapter_registry.py`, `tests/runtime/test_host_capability_claim_upgrade_policy.py`
- target_destination: complete `GAP-166..168` as an owner-directed conditional planning package while preserving `docs/architecture/planning-status.json` as the source of the current active queue and current decision gate
- rollback: revert the listed files from git and rerun the verification commands below

## Goal

- Current landing point: `GAP-165` had already fenced the host-family operationalization follow-on queue, but `GAP-166..168` still lacked a canonical machine-readable host-capability declaration, a claim-upgrade gate, and a full queue closeout package.
- Target home: finish those three tasks as a bounded planning/contract slice without claiming that Codex recovery is already complete or that the current active queue has changed.

## Owner-Directed Boundary

- Promotion basis: explicit owner direction in the current session to continue autonomous execution after `GAP-165` closeout.
- Promotion scope: docs/spec/schema/example/verifier/closeout work only.
- Non-goal of this slice: changing `planning-status.json`, declaring Codex `native_attach` recovery, or reopening a new active implementation queue.

## Pre-change review

- pre_change_review: required because this slice changes a contract spec, its paired JSON schema and examples, the docs gate verifier set in `scripts/verify-repo.ps1`, and multiple planning/claim docs that govern what the repository is allowed to say about live host posture.
- control_repo_manifest_and_rule_sources: reviewed `rules/manifest.json`, `AGENTS.md`, `docs/architecture/planning-status.json`, `docs/architecture/host-family-capability-surface-blueprint.md`, `docs/strategy/current-best-end-state-blueprint.md`, `docs/product/interaction-model.md`, `docs/specs/agent-adapter-contract-spec.md`, `schemas/jsonschema/agent-adapter-contract.schema.json`, and `docs/backlog/issue-ready-backlog.md`.
- user_level_deployed_rule_files: `python scripts\sync-agent-rules.py --scope All --fail-on-change` was not required to change any deployed rule copy for this slice because no user-level or target-repo rule body changed; the authoritative source review remained in the control repo.
- target_repo_deployed_rule_files: no target repo managed rule file, wrapper, or baseline projection changed in this slice; target-repo deployed copies remain unaffected because the work stays inside control-repo docs/spec/schema/verifier surfaces.
- target_repo_gate_scripts_and_ci: reviewed `scripts/verify-repo.ps1`, `scripts/build-runtime.ps1`, `scripts/doctor-runtime.ps1`, and the current `verify.yml` contract expectations; this slice only adds a docs-gate verifier and does not alter target-repo build/test/contract commands.
- target_repo_repo_profile: reviewed current repo-profile and adapter-facing contract surfaces to confirm the new canonical host-capability declaration is additive and claim-facing; no target repo `.governed-ai/repo-profile.json` projection was changed.
- target_repo_readme_and_operator_docs: reviewed `docs/README.md`, `docs/backlog/README.md`, `docs/plans/README.md`, and `docs/product/interaction-model.md` to ensure the new wording distinguishes `planning package complete` from `active queue promoted`.
- current_official_tool_loading_docs: current Codex project-doc layering and host-claim wording continue to be grounded by the existing local load model and host posture evidence; this slice tightens claim requirements rather than changing any host auth/provider/runtime ownership boundary.
- drift-integration decision: extend the existing `agent-adapter-contract` surface instead of creating a parallel host-capability spec, so the human-readable spec, JSON schema, examples, runtime tests, and docs-gate verifier all share one contract family.

## Change Summary

- Extended the existing `agent-adapter-contract` spec/schema/examples with a canonical `capability_surface` declaration that includes `host_family`, `surface_class`, `attach_mode`, `adapter_tier`, `degrade_reason`, `verification_refs`, and `evidence_refs`.
- Added a machine-readable `host-capability-claim-upgrade-policy.json` plus a docs-gate verifier so stronger live-host claims now fail closed when canonical fields or fresh recovery evidence are missing.
- Updated host-family blueprint, best-end-state blueprint, and interaction-model docs so claim-surface wording matches the new contract and recovery gate.
- Closed `GAP-166`, `GAP-167`, and `GAP-168` in the plan/backlog/index surfaces while keeping the queue inactive as current active work until a later promotion explicitly changes `planning-status.json`.

## Verification

- build:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - result: pass
- focused tests:
  - `python -m unittest tests.runtime.test_adapter_registry tests.runtime.test_host_capability_claim_upgrade_policy tests.runtime.test_issue_seeding`
  - result: pass
- contract/invariant:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - result: pass
- docs:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - result: pass
  - key output includes `OK host-capability-claim-upgrade-policy`
- scripts:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
  - result: pass
- renderability:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
  - result: pass
- hotspot:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - result: pass with the existing `WARN codex-capability-degraded` hint only

## Risks

- The main risk is turning a completed planning package into an implied claim that the live host posture has recovered.
- The mitigation is explicit fail-closed policy language, a dedicated docs verifier, and unchanged `planning-status.json`.

## Rollback

1. Revert the listed files from git.
2. Re-run:
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - `python -m unittest tests.runtime.test_adapter_registry tests.runtime.test_host_capability_claim_upgrade_policy tests.runtime.test_issue_seeding`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
   - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
3. Confirm that `planning-status.json` still remains unchanged and that no stronger live-host claim survives without the policy/verifier pair.
