# 2026-05-01 GAP-131 Capability Portfolio Classifier

## Goal
Close `GAP-131` by turning the refreshed borrowing review and the existing repository capability set into a machine-checkable portfolio classifier with lifecycle outcomes, effect hypotheses, evidence linkage, and rollback wording.

## Risk
- risk_tier: medium
- primary_risk: narrative-only borrowing conclusions drift away from executable implementation planning
- compatibility_boundary: classifier introduces a new planning and verification artifact but does not mutate active policy, enable skills, sync target repos, push, or merge

## Changes
- added [Capability Portfolio Classifier Spec](/D:/CODE/governed-ai-coding-runtime/docs/specs/capability-portfolio-classifier-spec.md)
- added [Capability Portfolio Classifier Schema](/D:/CODE/governed-ai-coding-runtime/schemas/jsonschema/capability-portfolio-classifier.schema.json)
- added [Capability Portfolio Classifier Example](/D:/CODE/governed-ai-coding-runtime/schemas/examples/capability-portfolio-classifier/default-governance-hub.example.json)
- added [Capability Portfolio Classifier Runtime Artifact](/D:/CODE/governed-ai-coding-runtime/docs/architecture/capability-portfolio-classifier.json)
- added [Capability Portfolio Verifier](/D:/CODE/governed-ai-coding-runtime/scripts/verify-capability-portfolio.py)
- added [Capability Portfolio Tests](/D:/CODE/governed-ai-coding-runtime/tests/runtime/test_capability_portfolio_classifier.py)
- updated queue status, spec and schema indexes, docs index, schema catalog, and `verify-repo.ps1` integration

## Pre-Change Review
pre_change_review: required because this change updates `scripts/verify-repo.ps1`, which is part of the self-repo hard gate.

control_repo_manifest_and_rule_sources: checked against `schemas/catalog/schema-catalog.yaml`, the new spec and schema pair, and the active `docs/plans/governance-hub-reuse-and-controlled-evolution-plan.md` queue before editing.

user_level_deployed_rule_files: not changed by this implementation; `GAP-131` adds local classifier and verifier coverage only.

target_repo_deployed_rule_files: not changed by this implementation; target-repo sync remains disabled.

target_repo_gate_scripts_and_ci: not changed by this implementation; the new verifier is wired only into this control repo's Docs gate.

target_repo_repo_profile: not changed by this implementation.

target_repo_readme_and_operator_docs: checked by updating `README.md`, `README.en.md`, `README.zh-CN.md`, `docs/README.md`, `docs/plans/README.md`, and `docs/backlog/README.md` so the queue status does not drift.

current_official_tool_loading_docs: not changed by this implementation; host-loading assumptions stay under the existing Codex and Claude cooperation-host boundary.

drift-integration decision: integrate by adding a machine-checkable portfolio artifact, schema, example, verifier, tests, and evidence rather than leaving `GAP-131` as research-only narrative.

## Verification
```powershell
python scripts/verify-capability-portfolio.py
```

Result: pass. Key output: `status=pass`, `entry_count=26`, `errors=[]`.

```powershell
python -m unittest discover -s tests/runtime -p "test_capability_portfolio_classifier.py"
```

Result: pass. Key output: `Ran 3 tests`, `OK`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll
```

Result: pass. Key output: `issue_seed_version=5.1`, `rendered_tasks=117`, `completed_task_count=106`, `active_task_count=11`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
```

Result: pass. Key output includes `OK capability-portfolio`, `OK current-source-compatibility`, `OK claim-drift-sentinel`, and `OK post-closeout-queue-sync`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

Result: pass. Key output: `OK python-bytecode`, `OK python-import`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

Result: pass. Key output includes `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`, `OK dependency-baseline`, `OK target-repo-governance-consistency`, `OK agent-rule-sync`, `OK pre-change-review`, and `OK functional-effectiveness`.

Note: the first replay failed closed on `pre_change_review` because this evidence file did not yet include the required drift-review tokens. That evidence gap is now closed in this file and the final replay passed.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

Result: pass. Key output: `Running 85 test files with 4 workers`, `Completed 85 test files in 136.691s; failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

Result: pass with host warning. Key output includes `OK runtime-status-surface`, `OK adapter-posture-visible`, and `WARN codex-capability-degraded`.

## Rollback
- revert the `GAP-131` classifier files and the related status/index updates
- remove the `verify-repo.ps1` hook if later planning decides to keep this queue narrative-only
