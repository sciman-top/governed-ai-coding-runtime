# 20260419 GAP-062 Trace Grading And Improvement Baseline

## Change Basis
- `GAP-062` is the first active task in the governance-optimization lane after completed `GAP-060` closeout and `GAP-061` lane canonicalization.
- The previous trace-grading contract only captured a minimal field list and coarse phase language; it did not normalize replay-readiness, policy visibility, outcome-quality separation, or postmortem-ready inputs.
- Landing point:
  - `docs/specs/eval-and-trace-grading-spec.md`
  - `schemas/jsonschema/eval-trace-policy.schema.json`
  - `schemas/examples/eval-trace-policy/governed-runtime-improvement-baseline.example.json`
  - `docs/architecture/minimum-viable-governance-loop.md`
  - queue and activation wording in docs entrypoints
- Target destination: traces can be graded across explicit dimensions, failed runs and reviewer feedback can produce structured postmortem inputs, and later controlled-improvement work consumes evidence-backed signals instead of anecdotal summaries.
- Active rule path: `D:\OneDrive\CODE\governed-ai-coding-runtime\AGENTS.md`, carrying `GlobalUser/AGENTS.md v9.39`.
- Clarification trace: `issue_id=gap-062-trace-grading-improvement-baseline`, `attempt_count=1`, `clarification_mode=direct_fix`, `clarification_scenario=n/a`, `clarification_questions=[]`, `clarification_answers=[]`.

## Files Changed
- Updated `docs/specs/eval-and-trace-grading-spec.md`
- Updated `schemas/jsonschema/eval-trace-policy.schema.json`
- Added `schemas/examples/eval-trace-policy/governed-runtime-improvement-baseline.example.json`
- Updated `docs/architecture/minimum-viable-governance-loop.md`
- Updated `docs/backlog/issue-ready-backlog.md`
- Updated `docs/README.md`
- Updated `docs/backlog/README.md`
- Updated `docs/roadmap/governance-optimization-lane-roadmap.md`
- Added `docs/change-evidence/20260419-gap-062-trace-grading-improvement-baseline.md`

## Summary
- Expanded the trace-grading spec from a minimal baseline into a four-dimension policy covering `evidence_completeness`, `workflow_correctness`, `replay_readiness`, and `outcome_quality`.
- Added explicit failure classifications and a normalized postmortem-input model so failed runs, reviewer disagreement, and repeated failure signatures can feed later governance tasks without rewriting runtime truth.
- Extended the eval-trace policy schema with machine-readable sections for trace grading, postmortem inputs, and improvement-signal flow, plus one valid example for contract verification.
- Updated the minimum governance loop so trace grading and postmortem capture occur after evidence persistence and before any later controlled-improvement proposal stage.
- Realigned docs entrypoints and backlog posture so the governance-optimization lane is described as active through `GAP-062` instead of still being a future planned queue.

## Verification
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

- Exit code: `0`
- Key output: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
```

- Exit code: `0`
- Key output: `OK active-markdown-links`, `OK backlog-yaml-ids`, `OK old-project-name-historical-only`

## Risks
- This change only defines the governance contract and queue posture; it does not yet add runtime-side trace graders or postmortem generators, so later GAPs must keep implementation claims narrower than the new contract surface.
- Some top-level project entry docs outside `docs/` may still need future wording alignment if they summarize lane activation in different language.

## Rollback
- Revert the expanded trace-grading spec and schema to the earlier minimal baseline.
- Remove the eval-trace policy example directory if the contract is simplified again.
- Revert the governance loop and docs entrypoint wording to the prior “planned follow-on” posture if the governance lane is re-baselined.
- Remove this evidence file if the `GAP-062` contract slice is withdrawn.
