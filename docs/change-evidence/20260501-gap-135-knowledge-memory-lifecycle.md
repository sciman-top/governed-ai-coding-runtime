# 2026-05-01 GAP-135 Governed Knowledge Memory Lifecycle

## Goal
Close `GAP-135` by turning AI coding experience extraction into a governed lifecycle that produces reviewable knowledge candidates, pattern candidates, memory records, and retirement records with explicit source evidence, verification references, expiry, and rollback posture.

## Risk
- risk_tier: medium
- primary_risk: AI coding lessons could drift into hidden memory authority or stale notes unless promotion, retrieval, expiry, and retirement are all explicit and verifiable
- compatibility_boundary: this change extends dry-run experience extraction and contract verification, but it does not auto-enable skills, mutate policy, sync target repos, push, or merge

## Changes
- added [Knowledge Memory Lifecycle Spec](/D:/CODE/governed-ai-coding-runtime/docs/specs/knowledge-memory-lifecycle-spec.md)
- added [Knowledge Memory Lifecycle Schema](/D:/CODE/governed-ai-coding-runtime/schemas/jsonschema/knowledge-memory-lifecycle.schema.json)
- added [Knowledge Memory Lifecycle Example](/D:/CODE/governed-ai-coding-runtime/schemas/examples/knowledge-memory-lifecycle/default-governed-lifecycle.example.json)
- added [Knowledge Memory Lifecycle Runtime Asset](/D:/CODE/governed-ai-coding-runtime/docs/architecture/knowledge-memory-lifecycle.json)
- added [Knowledge Memory Lifecycle Verifier](/D:/CODE/governed-ai-coding-runtime/scripts/verify-knowledge-memory-lifecycle.py)
- added [Knowledge Memory Lifecycle Tests](/D:/CODE/governed-ai-coding-runtime/tests/runtime/test_knowledge_memory_lifecycle.py)
- extended [AI Coding Experience Extractor](/D:/CODE/governed-ai-coding-runtime/scripts/extract-ai-coding-experience.py) so `ExperienceReview` now emits governed knowledge candidates, pattern candidates, memory records, and retirement records in addition to proposals and disabled skill candidates
- updated [scripts/verify-repo.ps1](/D:/CODE/governed-ai-coding-runtime/scripts/verify-repo.ps1) `-Check Contract` to fail closed when knowledge-memory lifecycle invariants drift
- added archived retirement example [one-off-note.json](/D:/CODE/governed-ai-coding-runtime/docs/change-evidence/runtime-evolution-knowledge/archive/one-off-note.json) to show retirement preserves audit history instead of deleting evidence

## Pre-Change Review
pre_change_review: required because this change updates `scripts/verify-repo.ps1`, extends `scripts/extract-ai-coding-experience.py`, and adds a new schema-backed lifecycle contract.

control_repo_manifest_and_rule_sources: checked against `docs/backlog/issue-ready-backlog.md`, `docs/plans/governance-hub-reuse-and-controlled-evolution-plan.md`, `docs/specs/knowledge-source-spec.md`, `docs/specs/controlled-improvement-proposal-spec.md`, and `docs/architecture/runtime-evolution-policy.json` before editing.

user_level_deployed_rule_files: not changed by this implementation; the lifecycle stays inside repository-owned dry-run extraction and contract verification.

target_repo_deployed_rule_files: not changed by this implementation; `GAP-135` governs local experience review output rather than target-repo sync.

target_repo_gate_scripts_and_ci: not changed directly; the new lifecycle is consumed through this control repo's `Contract` gate.

target_repo_repo_profile: not changed by this implementation.

target_repo_readme_and_operator_docs: checked by updating status docs and `ExperienceReview` help text so the new lifecycle is not left implicit.

current_official_tool_loading_docs: not changed by this implementation; the lifecycle governs repository-owned evidence and does not alter host loading semantics.

drift-integration decision: integrate by extending the existing `ExperienceReview` path instead of creating a parallel memory subsystem, and fail closed through `verify-repo.ps1 -Check Contract`.

## Verification
```powershell
python scripts/verify-knowledge-memory-lifecycle.py
```

Result: pass. Key output: `knowledge_candidate_count=1`, `pattern_candidate_count=1`, `memory_record_count=1`, `retirement_record_count=0`, `status=pass`.

```powershell
python -m unittest tests.runtime.test_ai_coding_experience_extraction tests.runtime.test_knowledge_memory_lifecycle
```

Result: pass. Key output: `Ran 11 tests`, `OK`.

```powershell
Get-Content -Raw 'schemas/examples/knowledge-memory-lifecycle/default-governed-lifecycle.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/knowledge-memory-lifecycle.schema.json'
```

Result: pass. Key output: `True`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

Result: pass. Key output includes `OK knowledge-memory-lifecycle`, `OK target-repo-reuse-effect-feedback`, `OK pre-change-review`, and `OK functional-effectiveness`.

## Outcome
- promotion guard: governed knowledge and pattern candidates only count as promotion-ready when both `source_refs` and `verification_refs` are attached
- memory guard: generated memory records now include `scope`, `provenance`, `confidence`, `expires_at`, and `retrieval_evidence`
- retirement guard: low-value knowledge can move to a retired record with `archive_ref`, `audit_history_retained=true`, and `delete_active_evidence=false`
- operator path: `scripts/operator.ps1 -Action ExperienceReview` stays dry-run and non-mutating while exposing the richer lifecycle output

## Rollback
- revert `scripts/extract-ai-coding-experience.py` lifecycle additions
- remove `docs/specs/knowledge-memory-lifecycle-spec.md`, `schemas/jsonschema/knowledge-memory-lifecycle.schema.json`, `schemas/examples/knowledge-memory-lifecycle/default-governed-lifecycle.example.json`, `docs/architecture/knowledge-memory-lifecycle.json`, `scripts/verify-knowledge-memory-lifecycle.py`, and `tests/runtime/test_knowledge_memory_lifecycle.py`
- remove `docs/change-evidence/runtime-evolution-knowledge/archive/one-off-note.json`
- remove the `knowledge-memory-lifecycle` hook from `scripts/verify-repo.ps1`
