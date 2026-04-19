# 20260419 GAP-063 Repo Admission And Compatibility Signal Hardening

## Change Basis
- `GAP-063` follows the completed `GAP-062` trace-grading baseline and is the next active governance-lane task on the current branch baseline.
- The previous repo-admission contract only expressed coarse blocking checks. It did not make compatibility warnings machine-readable for knowledge readiness, eval readiness, attachment hygiene, or stricter-only override safety.
- Landing point:
  - `docs/specs/repo-admission-minimums-spec.md`
  - `schemas/jsonschema/repo-admission-minimums.schema.json`
  - `schemas/examples/repo-admission-minimums/attached-repo-warning-compatible.example.json`
  - `docs/architecture/governance-boundary-matrix.md`
  - queue and activation wording in docs entrypoints
- Target destination: repo reuse admission can emit explicit `accept`, `warn`, or `block` signals, while preserving the kernel rule that repo overrides may only tighten behavior.
- Active rule path: `D:\OneDrive\CODE\governed-ai-coding-runtime\AGENTS.md`, carrying `GlobalUser/AGENTS.md v9.39`.
- Clarification trace: `issue_id=gap-063-repo-admission-compatibility-hardening`, `attempt_count=1`, `clarification_mode=direct_fix`, `clarification_scenario=n/a`, `clarification_questions=[]`, `clarification_answers=[]`.

## Files Changed
- Updated `docs/specs/repo-admission-minimums-spec.md`
- Updated `schemas/jsonschema/repo-admission-minimums.schema.json`
- Added `schemas/examples/repo-admission-minimums/attached-repo-warning-compatible.example.json`
- Updated `docs/architecture/governance-boundary-matrix.md`
- Updated `docs/backlog/issue-ready-backlog.md`
- Updated `docs/README.md`
- Updated `docs/backlog/README.md`
- Updated `docs/roadmap/governance-optimization-lane-roadmap.md`
- Added `docs/change-evidence/20260419-gap-063-repo-admission-compatibility-hardening.md`

## Summary
- Expanded repo-admission minimums so the contract now requires knowledge readiness, eval readiness, attachment posture, and override summaries to be expressed explicitly rather than inferred.
- Added a machine-readable compatibility-signal model with `signal_kind`, `status`, `reason`, `blocking`, and `evidence_refs`, enabling `accept`, `warn`, and `block` outputs.
- Hardened failure behavior so missing or stale attachment posture blocks admission, while missing knowledge or eval readiness declarations remain visible `warn` states instead of hidden defaults.
- Updated the governance-boundary matrix so repo admission semantics are owned by unified governance, while repos may only add stricter warning or blocking rules.
- Advanced queue wording so the governance lane is now described as completed through `GAP-063`, with `GAP-064` as the next active task.

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
- This is still an admission contract slice, not runtime enforcement code. Future implementation work must ensure adapter selection, attachment probing, and operator tooling actually emit the declared compatibility signals.
- `warn` semantics are now explicit, so later tasks must avoid reintroducing hidden defaults in repo-level config loaders or CLI surfaces.

## Rollback
- Revert the repo-admission spec and schema to the earlier blocking-only baseline.
- Remove the new repo-admission example if the compatibility-signal surface is simplified.
- Revert governance-boundary and docs entrypoint wording if the governance lane is re-sequenced.
- Remove this evidence file if the `GAP-063` contract slice is withdrawn.
