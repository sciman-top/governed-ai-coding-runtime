# 20260419 GAP-067 Controlled Improvement Proposal Pipeline

## Change Basis
- `GAP-067` follows completed `GAP-066` provenance hardening and is the final implementation task before governance-lane closeout.
- Existing trace and postmortem contracts produced proposal-ready signals, but there was no dedicated controlled-proposal contract that enforced human review and non-mutation boundaries.
- Landing point:
  - `docs/specs/controlled-improvement-proposal-spec.md`
  - `schemas/jsonschema/controlled-improvement-proposal.schema.json`
  - `schemas/examples/controlled-improvement-proposal/policy-rollout-review-proposal.example.json`
  - catalog/index wiring and architecture boundary updates
  - queue posture sync to make `GAP-068` the active closeout item
- Target destination: runtime can emit structured improvement proposals from evidence-backed inputs, while proposal outputs stay separated from autonomous policy or kernel mutation.
- Active rule path: `D:\OneDrive\CODE\governed-ai-coding-runtime\AGENTS.md`, carrying `GlobalUser/AGENTS.md v9.39`.
- Clarification trace: `issue_id=gap-067-controlled-improvement-proposal-pipeline`, `attempt_count=1`, `clarification_mode=direct_fix`, `clarification_scenario=n/a`, `clarification_questions=[]`, `clarification_answers=[]`.

## Files Changed
- Added `docs/specs/controlled-improvement-proposal-spec.md`
- Added `schemas/jsonschema/controlled-improvement-proposal.schema.json`
- Added `schemas/examples/controlled-improvement-proposal/policy-rollout-review-proposal.example.json`
- Updated `schemas/catalog/schema-catalog.yaml`
- Updated `docs/specs/README.md`
- Updated `schemas/examples/README.md`
- Updated `docs/architecture/minimum-viable-governance-loop.md`
- Updated `docs/architecture/governance-boundary-matrix.md`
- Updated `docs/backlog/issue-ready-backlog.md`
- Updated `docs/README.md`
- Updated `docs/backlog/README.md`
- Updated `docs/roadmap/governance-optimization-lane-roadmap.md`
- Added `docs/change-evidence/20260419-gap-067-controlled-improvement-proposal-pipeline.md`

## Summary
- Introduced a machine-readable controlled proposal contract with proposal categories (`skill`, `hook`, `policy`, `control`, `knowledge`, `repo_followup`) and scope (`unified_governance`, `repo_specific`).
- Hard-coded non-mutation safety into schema shape: proposals require human review metadata and enforce `allows_direct_mutation=false`.
- Required rollback linkage for proposal implementation paths and repo scoping for repo-specific proposals.
- Updated governance loop and boundary matrix so proposals are explicitly advisory inputs under human review, not a direct mutation channel.
- Advanced governance-lane posture so `GAP-068` is now the only active queue item.

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
- This is a contract and planning boundary slice, not an execution engine for proposals. Runtime components still need explicit implementation to emit and consume these proposal records.
- Queue status now marks `GAP-067` complete; if closeout evidence in `GAP-068` finds unresolved implementation depth, claim language may need to tighten without relaxing the non-mutation guard.

## Rollback
- Revert the controlled-improvement proposal spec/schema/example and catalog/index links.
- Revert governance-boundary and governance-loop updates if proposal pipeline semantics are redesigned.
- Revert queue posture wording if the governance lane is re-sequenced.
- Remove this evidence file if the `GAP-067` contract slice is withdrawn.
