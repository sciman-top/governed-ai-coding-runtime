# 2026-05-01 Governance Hub Reuse Plan Evidence

## Goal
Record the scope correction and executable planning work for the next queue:

- Codex and Claude Code are primary cooperation hosts.
- Claude Code is treated as local third-party Anthropic-compatible provider usage, including GLM or DeepSeek-style provider profiles, not as an official subscription dependency.
- Hermes Agent, OpenHands, SWE-agent, Letta, Mem0, LangGraph, Aider, Cline, OPA, MCP gateways, and similar projects are selective mechanism sources.
- The project should advance the `Governance Hub + Reusable Contract + Controlled Evolution` mainline only through executable tasks, evidence, rollback, and effect feedback.
- Controlled evolution must evaluate the existing capability portfolio too. It must be able to add, keep, improve, merge, deprecate, retire, or delete candidates based on evidence instead of only proposing additions.

## Risk
- Level: low to medium.
- Scope: docs, backlog seeds, and issue-rendering metadata.
- No runtime policy is auto-applied.
- No skill is auto-enabled.
- No target repository is synced.
- No branch, push, merge, or PR action is performed.

## Changes
- Added `docs/plans/governance-hub-reuse-and-controlled-evolution-plan.md`.
- Added the `GAP-130..139` queue to `docs/backlog/issue-ready-backlog.md`.
- Added `GAP-130..139` to `docs/backlog/issue-seeds.yaml` and advanced `issue_seed_version` to `5.1`.
- Added `phase:governance-hub-reuse` issue labels to `scripts/github/create-roadmap-issues.ps1`.
- Updated `docs/plans/README.md`, `docs/backlog/README.md`, `docs/README.md`, and `README.md` to reference the new queue and preserve claim discipline.
- Updated `docs/research/runtime-governance-borrowing-matrix.md` with the clarified host-vs-mechanism boundary and additional source rows.
- Strengthened the post-`GAP-130` queue to require third-party Claude Code provider assumptions and capability portfolio cleanup outcomes.
- Added `docs/architecture/core-principles-policy.json`, `schemas/jsonschema/core-principles.schema.json`, `docs/specs/core-principles-spec.md`, `schemas/examples/core-principles/default-runtime.example.json`, `scripts/verify-core-principles.py`, and `tests/runtime/test_core_principles.py`.
- Wired `scripts/verify-repo.ps1 -Check Docs` to fail when core principles drift.
- Strengthened the core principles with `automation_first_outer_ai_intelligent_evolution` and `outer_ai_evolution_controls`, covering automatic outer AI triggers, allowed advisory actions, forbidden automatic effective actions, and required structured-candidate/risk/evidence/rollback controls.
- Added the explicit `governance_hub_reusable_contract_final_state` core principle and a dedicated core-principle change materializer/operator flow that defaults to dry-run reporting, requires `-ConfirmCorePrincipleProposalWrite` to write reviewable proposal and manifest files, and never changes active policy.
- Executed the confirmed write path, producing `docs/change-evidence/core-principle-change-proposals/20260501-governance-hub-reusable-contract-final-state.json` and `docs/change-evidence/core-principle-change-patches/20260501-core-principle-change-materialization.json`.

## Pre-Change Review
pre_change_review: required because `scripts/verify-repo.ps1` is part of the self-repo hard gate.

control_repo_manifest_and_rule_sources: checked through the current control repository files before editing; this change adds a verifier instead of changing distributed rule sources.

user_level_deployed_rule_files: not changed by this implementation; the new gate protects repository docs and policy before later rule sync work.

target_repo_deployed_rule_files: not changed by this implementation; target-repo sync remains disabled.

target_repo_gate_scripts_and_ci: not changed by this implementation; the new verifier is local to this control repo's Docs gate.

target_repo_repo_profile: not changed by this implementation.

target_repo_readme_and_operator_docs: README and docs index were already updated in this evidence batch and are now checked by `verify-core-principles.py`.

current_official_tool_loading_docs: current host-loading assumptions remain bounded by Codex/Claude cooperation-host posture and do not change official loading behavior.

drift-integration decision: integrate by adding a machine verifier and Docs gate wiring; do not rely on natural-language principle reminders alone.

## Claim Discipline
This change closes `GAP-130` as the scope rebaseline. It does not claim that `GAP-131..139` implementation capabilities are live. It makes the next executable queue machine-renderable and verifiable.

Future implementation claims require:

- runnable command or contract
- target-repo feedback where applicable
- effect metric
- evidence reference
- rollback or retirement path
- successful verification gate

## Verification Results
Completed verification for this change:

```powershell
python scripts/verify-core-principles.py
```

Result: pass. Key output: `status=pass`, no missing principles, no missing doc refs, no missing evidence refs, no missing portfolio outcomes, and no forbidden active patterns.

The same verifier now also checks `automation_first_outer_ai_intelligent_evolution`, `outer_ai_evolution_controls.automatic_trigger_allowed`, required outer AI allowed actions, forbidden automatic effective actions, and required controls.

It also checks `governance_hub_reusable_contract_final_state`, which makes `Governance Hub + Reusable Contract + Controlled Evolution loop + outer AI intelligent review/generation capability` an explicit core principle.

```powershell
python -m unittest tests.runtime.test_core_principle_change_materialization tests.runtime.test_operator_entrypoint.OperatorEntrypointTests.test_operator_entrypoint_help_succeeds tests.runtime.test_core_principles
```

Result: pass. Key output: `Ran 10 tests`, `OK`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action CorePrincipleMaterialize
```

Result: pass. Key output: `mode=dry_run`, `operation_count=2`, `active_policy_auto_apply=false`, `written_files=[]`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action CorePrincipleMaterialize -ConfirmCorePrincipleProposalWrite
```

Result: pass. Key output: `mode=apply`, `operation_count=2`, `active_policy_auto_apply=false`, written proposal and manifest paths under `docs/change-evidence/core-principle-change-*`.

```powershell
python -m unittest tests.runtime.test_core_principles
```

Result: pass. Key output: `Ran 5 tests`, `OK`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll
```

Result: pass. Key output: `issue_seed_version=5.1`, `rendered_tasks=117`, `rendered_issue_creation_tasks=12`, `completed_task_count=105`, `active_task_count=12`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
```

Result: pass. Key output includes `OK core-principles`, `OK backlog-yaml-ids`, `OK runtime-evolution-materialization`, `OK gap-evidence-slo`, and `OK post-closeout-queue-sync`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts
```

Result: pass. Key output: `OK powershell-parse`, `OK issue-seeding-render`.

Full hard-gate order also completed:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

Result: pass. Key output: `OK python-bytecode`, `OK python-import`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

Result: pass. Key output: `Completed 83 test files`, `failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

Result: pass. Key output includes `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`, `OK dependency-baseline`, `OK target-repo-governance-consistency`, `OK agent-rule-sync`, `OK pre-change-review`, and `OK functional-effectiveness`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

Result: pass with existing host capability warning. Key output includes `OK runtime-status-surface`, `OK adapter-posture-visible`, and `WARN codex-capability-degraded`.

## Rollback
Use git to revert the files listed in `Changes` if the new queue is rejected or superseded.

Additional rollback action:

- remove `GAP-130..139` from `issue-seeds.yaml`
- remove the `Governance Hub Reuse And Controlled Evolution Queue` section from `issue-ready-backlog.md`
- remove the `phase:governance-hub-reuse` label mapping from `create-roadmap-issues.ps1`
- remove the new plan and this evidence file
