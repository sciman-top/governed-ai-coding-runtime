# 2026-05-01 GAP-137 Repo Map And Context Shaping Integration

## Goal
Close `GAP-137` by generating a governed repo-map context artifact from a repo-local strategy override, preserving required governance files, and emitting effect metrics that decide whether the artifact should be kept or adjusted.

## Risk
- risk_tier: medium
- primary_risk: repo-local include/exclude overrides could hide governance-critical files or create noisy artifacts that do not reduce clarification work
- compatibility_boundary: this change adds a repo-local strategy file, artifact builder, verifier, and runtime test, but it does not mutate target repos, push, merge, or replace host context systems

## Changes
- added repo-local strategy override [repo-map-context-shaping.json](/D:/CODE/governed-ai-coding-runtime/.governed-ai/repo-map-context-shaping.json)
- added [Repo Map Context Artifact Builder](/D:/CODE/governed-ai-coding-runtime/scripts/build-repo-map-context-artifact.py)
- added [Repo Map Context Artifact Verifier](/D:/CODE/governed-ai-coding-runtime/scripts/verify-repo-map-context-artifact.py)
- added [Repo Map Context Artifact Tests](/D:/CODE/governed-ai-coding-runtime/tests/runtime/test_repo_map_context_artifact.py)
- generated [Repo Map Context Artifact](/D:/CODE/governed-ai-coding-runtime/docs/change-evidence/repo-map-context-artifact.json)
- updated [Repo Map And Context Shaping Spec](/D:/CODE/governed-ai-coding-runtime/docs/specs/repo-map-context-shaping-spec.md) so required governance files and effect metrics are explicit invariants
- wired [scripts/verify-repo.ps1](/D:/CODE/governed-ai-coding-runtime/scripts/verify-repo.ps1) `-Check Contract` to require the repo-map context artifact verifier

## Pre-Change Review
pre_change_review: required because this change updates `scripts/verify-repo.ps1`, adds a repo-local strategy file, and introduces a generated evidence artifact.

control_repo_manifest_and_rule_sources: checked against `docs/backlog/issue-ready-backlog.md`, `docs/specs/repo-map-context-shaping-spec.md`, `schemas/examples/repo-map-context-shaping/hybrid-default.example.json`, and the existing attachment context-pack baseline before editing.

user_level_deployed_rule_files: not changed by this implementation.

target_repo_deployed_rule_files: not changed by this implementation; the override is repo-local to this control repo.

target_repo_gate_scripts_and_ci: not changed directly; the artifact is verified through this control repo's `Contract` gate.

target_repo_repo_profile: not changed by this implementation.

target_repo_readme_and_operator_docs: checked by updating queue status docs so the repo-map artifact is not left implicit.

current_official_tool_loading_docs: not changed by this implementation; the artifact shapes repo context only.

drift-integration decision: integrate by using a repo-local strategy override under `.governed-ai/` and a generated artifact under `docs/change-evidence/`, keeping host context systems untouched.

## Verification
```powershell
python scripts/build-repo-map-context-artifact.py
```

Result: pass. Key output: `decision=keep`, `estimated_token_cost=5986`, `file_selection_accuracy=1.0`, `clarification_reduction_proxy=1.0`.

```powershell
python scripts/verify-repo-map-context-artifact.py
```

Result: pass. Key output: required governance files all present in `selected_files`, `decision=keep`.

```powershell
python -m unittest tests.runtime.test_repo_map_context_artifact
```

Result: pass. Key output: `Ran 2 tests`, `OK`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

Result: pass. Key output includes `OK repo-map-context-artifact`, `OK promotion-lifecycle`, and `OK knowledge-memory-lifecycle`.

## Outcome
- context artifacts are now generated, not manually copied
- repo-local include/exclude overrides cannot hide `README.md`, `docs/README.md`, `docs/backlog/issue-ready-backlog.md`, or `scripts/verify-repo.ps1`
- effect metrics now decide whether the artifact is `keep` or `adjust`

## Rollback
- remove `.governed-ai/repo-map-context-shaping.json`
- remove `scripts/build-repo-map-context-artifact.py`, `scripts/verify-repo-map-context-artifact.py`, and `tests/runtime/test_repo_map_context_artifact.py`
- remove `docs/change-evidence/repo-map-context-artifact.json`
- remove the `repo-map-context-artifact` hook from `scripts/verify-repo.ps1`
