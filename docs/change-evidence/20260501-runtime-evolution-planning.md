# 2026-05-01 Runtime Evolution Planning

## Goal
Add a governed self-evolution queue and dry-run implementation before enabling any automatic mutation.

## Changes
- Added draft policy: `docs/architecture/runtime-evolution-policy.json`
- Added plan: `docs/plans/runtime-evolution-review-plan.md`
- Added backlog and issue seed tasks for `GAP-120..124`
- Updated documentation indexes so the planning queue is discoverable
- Added dry-run evaluator, operator entrypoint, Docs gate coverage, scheduled workflow, and tests
- Added internal AI coding experience as a source category when captured as reviewable evidence, controlled improvement proposals, knowledge-source records, or skill-manifest candidates
- Added dry-run AI coding experience extraction through `scripts/extract-ai-coding-experience.py` and `scripts/operator.ps1 -Action ExperienceReview`
- Added extractor quality checks for source refs, recomputable scores, promotion thresholds, non-mutating proposals, mandatory human review, and disabled skill candidates
- Added controlled materialization through `scripts/materialize-runtime-evolution.py` and `scripts/operator.ps1 -Action EvolutionMaterialize`
- Added `GAP-125..129` for auto-apply boundary, low-risk patch generation, skill candidate materialization, branch/PR preparation, and retire/delete follow-up
- Added review-gated PR preparation through `scripts/prepare-runtime-evolution-pr.py`
- Added dry-run retire/delete proposal review through `scripts/review-runtime-evolution-retirements.py`

## Risk
Low to medium. This change adds dry-run execution scripts, operator actions, a scheduled freshness workflow, controlled materialization, and tests. It can write proposal and disabled skill candidate files, but it does not permit direct policy auto-apply, skill enablement, target repo sync, push, or merge.

## Verification
pre_change_review:
- control_repo_manifest_and_rule_sources: checked current `rules/manifest.json`, project `AGENTS.md`, and existing docs/index conventions before adding this queue; no manifest-managed rule source was changed.
- user_level_deployed_rule_files: no user-level deployed rule files were changed by this runtime-evolution slice.
- target_repo_deployed_rule_files: no target-repo deployed rule files were changed by this runtime-evolution slice.
- target_repo_gate_scripts_and_ci: added `.github/workflows/runtime-evolution.yml` as a self-runtime scheduled dry-run freshness check only; target repo gates and target CI are not changed.
- target_repo_repo_profile: target repo profiles were not changed.
- target_repo_readme_and_operator_docs: docs indexes and backlog were updated to describe the new dry-run status without claiming automatic mutation.
- current_official_tool_loading_docs: official tool-loading assumptions stay covered by the existing current-source compatibility policy; this slice does not change Codex/Claude loading semantics.
- drift-integration decision: integrate the new queue into existing operator, Docs gate, issue rendering, and evidence paths instead of creating a parallel governance lane.

Executed verification:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
```

```powershell
python -m unittest tests.runtime.test_runtime_evolution
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action EvolutionReview
```

```powershell
python -m unittest tests.runtime.test_runtime_evolution tests.runtime.test_learning_efficiency_metrics
```

```powershell
python -m unittest tests.runtime.test_ai_coding_experience_extraction
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action ExperienceReview
```

```powershell
python scripts/extract-ai-coding-experience.py --as-of 2026-05-01
```

```powershell
python -m unittest tests.runtime.test_runtime_evolution_materialization
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action EvolutionMaterialize
```

```powershell
python scripts/prepare-runtime-evolution-pr.py --as-of 2026-05-01
```

```powershell
python scripts/review-runtime-evolution-retirements.py --as-of 2026-09-01 --stale-after-days 30
```

## Rollback
Use git history to revert:
- `docs/architecture/runtime-evolution-policy.json`
- `docs/plans/runtime-evolution-review-plan.md`
- `.github/workflows/runtime-evolution.yml`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/README.md`
- `docs/architecture/README.md`
- `docs/plans/README.md`
- `docs/change-evidence/runtime-evolution-patches/`
- `docs/change-evidence/runtime-evolution-proposals/`
- `skills/candidates/`
- this evidence file
