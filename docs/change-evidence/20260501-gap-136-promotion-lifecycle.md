# 2026-05-01 GAP-136 Skill Hook Gate Eval Promotion Lifecycle

## Goal
Close `GAP-136` by making generated skill, hook, gate, eval, policy, and workflow candidates move through one staged promotion lifecycle with explicit disable-by-default posture, promotion evidence, gate refs, effect metrics, rollback refs, and candidate-only retirement cleanup.

## Risk
- risk_tier: medium
- primary_risk: generated candidates could look governed while still lacking explicit promotion gates, or cleanup logic could overreach into reviewed assets or evidence history
- compatibility_boundary: this change extends controlled materialization and retirement review, but it does not auto-enable skills, auto-apply policy, sync target repos, push, or merge

## Changes
- added [Promotion Lifecycle Spec](/D:/CODE/governed-ai-coding-runtime/docs/specs/promotion-lifecycle-spec.md)
- added [Promotion Lifecycle Schema](/D:/CODE/governed-ai-coding-runtime/schemas/jsonschema/promotion-lifecycle.schema.json)
- added [Promotion Lifecycle Example](/D:/CODE/governed-ai-coding-runtime/schemas/examples/promotion-lifecycle/default-runtime-evolution.example.json)
- added [Promotion Lifecycle Runtime Asset](/D:/CODE/governed-ai-coding-runtime/docs/architecture/promotion-lifecycle.json)
- added [Promotion Lifecycle Verifier](/D:/CODE/governed-ai-coding-runtime/scripts/verify-promotion-lifecycle.py)
- added [Promotion Lifecycle Tests](/D:/CODE/governed-ai-coding-runtime/tests/runtime/test_promotion_lifecycle.py)
- extended [Runtime Evolution Materializer](/D:/CODE/governed-ai-coding-runtime/scripts/materialize-runtime-evolution.py) to write [Promotion Lifecycle Manifest](/D:/CODE/governed-ai-coding-runtime/docs/change-evidence/runtime-evolution-promotions/20260501-runtime-evolution-promotion-lifecycle.json) alongside proposal and disabled skill candidate files
- extended [Runtime Evolution Retirement Review](/D:/CODE/governed-ai-coding-runtime/scripts/review-runtime-evolution-retirements.py) so stale proposal candidates, duplicate lifecycle entries, and replaced candidates stay candidate-only cleanup work and never delete reviewed assets or evidence history
- updated [scripts/verify-repo.ps1](/D:/CODE/governed-ai-coding-runtime/scripts/verify-repo.ps1) `-Check Contract` to require promotion lifecycle verification

## Pre-Change Review
pre_change_review: required because this change updates `scripts/verify-repo.ps1`, `scripts/materialize-runtime-evolution.py`, and `scripts/review-runtime-evolution-retirements.py`.

control_repo_manifest_and_rule_sources: checked against `docs/backlog/issue-ready-backlog.md`, `docs/plans/governance-hub-reuse-and-controlled-evolution-plan.md`, `docs/specs/control-registry-spec.md`, `docs/specs/skill-manifest-spec.md`, and the existing runtime evolution materialization flow before editing.

user_level_deployed_rule_files: not changed by this implementation.

target_repo_deployed_rule_files: not changed by this implementation.

target_repo_gate_scripts_and_ci: not changed directly; promotion evidence references the existing `Runtime` and `Contract` gates rather than introducing a parallel gate stack.

target_repo_repo_profile: not changed by this implementation.

target_repo_readme_and_operator_docs: checked by updating repository status docs and generated asset descriptions so the promotion lifecycle is visible to operators.

current_official_tool_loading_docs: not changed by this implementation; the new lifecycle governs repository-generated candidates only.

drift-integration decision: integrate by upgrading the existing `EvolutionMaterialize` and retirement-review path rather than inventing a second candidate promotion subsystem.

## Verification
```powershell
python scripts/verify-promotion-lifecycle.py
```

Result: pass. Key output: `lifecycle_entry_count=2`, `retire_proposal_count=2`, `status=pass`.

```powershell
python -m unittest tests.runtime.test_runtime_evolution_materialization tests.runtime.test_promotion_lifecycle
```

Result: pass. Key output: `Ran 8 tests`, `OK`.

```powershell
Get-Content -Raw 'schemas/examples/promotion-lifecycle/default-runtime-evolution.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/promotion-lifecycle.schema.json'
```

Result: pass. Key output: `True`.

```powershell
python scripts/materialize-runtime-evolution.py --apply --as-of 2026-05-01
```

Result: pass. Key output: wrote proposal, disabled skill candidate, materialization manifest, and promotion lifecycle manifest.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

Result: pass. Key output includes `OK promotion-lifecycle`, `OK knowledge-memory-lifecycle`, `OK target-repo-reuse-effect-feedback`, `OK pre-change-review`, and `OK functional-effectiveness`.

## Outcome
- generated skill candidates remain `default_enabled=false`
- promotion records now carry gate references, effect-metric refs, and rollback refs before any candidate can move beyond disabled or review state
- retirement review remains candidate-scoped and explicitly blocks reviewed-asset deletion and evidence-history deletion
- the repository now materializes a promotion lifecycle manifest instead of leaving promotion state implicit in scattered files

## Rollback
- revert `scripts/materialize-runtime-evolution.py` and `scripts/review-runtime-evolution-retirements.py` to the prior candidate-only behavior
- remove `docs/specs/promotion-lifecycle-spec.md`, `schemas/jsonschema/promotion-lifecycle.schema.json`, `schemas/examples/promotion-lifecycle/default-runtime-evolution.example.json`, `docs/architecture/promotion-lifecycle.json`, `scripts/verify-promotion-lifecycle.py`, and `tests/runtime/test_promotion_lifecycle.py`
- remove `docs/change-evidence/runtime-evolution-promotions/20260501-runtime-evolution-promotion-lifecycle.json`
- remove the `promotion-lifecycle` hook from `scripts/verify-repo.ps1`
