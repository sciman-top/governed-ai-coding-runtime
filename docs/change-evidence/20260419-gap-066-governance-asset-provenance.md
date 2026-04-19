# 20260419 GAP-066 Provenance And Attestation For Governance Assets

## Change Basis
- `GAP-066` follows completed `GAP-065` knowledge-registry and repo-map shaping work.
- The previous provenance contract covered basic attestation records, but it did not make rollback linkage mandatory enough for governance assets or make review-decision reuse explicit.
- Landing point:
  - `docs/specs/provenance-and-attestation-spec.md`
  - `schemas/jsonschema/provenance-and-attestation.schema.json`
  - `schemas/examples/provenance-and-attestation/schema-bundle-release.example.json`
  - queue posture sync in docs entrypoints
- Target destination: governance assets can carry stable provenance records with rollback visibility, and provenance can inform review or promotion decisions without replacing runtime evidence or approvals.
- Active rule path: `D:\OneDrive\CODE\governed-ai-coding-runtime\AGENTS.md`, carrying `GlobalUser/AGENTS.md v9.39`.
- Clarification trace: `issue_id=gap-066-governance-asset-provenance`, `attempt_count=1`, `clarification_mode=direct_fix`, `clarification_scenario=n/a`, `clarification_questions=[]`, `clarification_answers=[]`.

## Files Changed
- Updated `docs/specs/provenance-and-attestation-spec.md`
- Updated `schemas/jsonschema/provenance-and-attestation.schema.json`
- Updated `schemas/examples/provenance-and-attestation/schema-bundle-release.example.json`
- Updated `docs/backlog/issue-ready-backlog.md`
- Updated `docs/README.md`
- Updated `docs/backlog/README.md`
- Updated `docs/roadmap/governance-optimization-lane-roadmap.md`
- Added `docs/change-evidence/20260419-gap-066-governance-asset-provenance.md`

## Summary
- Expanded provenance to cover `governance_asset` subjects in addition to the earlier artifact and schema-oriented subjects.
- Made `rollback_ref` mandatory so attested governance assets stay reviewable and reversible.
- Added optional `review_decision_refs` to show how provenance can participate in promotion or review decisions without displacing the primary evidence chain.
- Updated the canonical example to include rollback and review-decision linkage.
- Advanced governance-lane posture so `GAP-067` is now the next active task.

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
- This is still a provenance contract slice, not a provenance verifier or attestation issuer. Runtime or CI enforcement will need later implementation work.
- Mandatory rollback linkage means future governance-asset attestations must always name a reversible reference, even for documentation-only assets.

## Rollback
- Revert the provenance spec and schema to the earlier minimal attestation baseline.
- Revert the example update if governance-asset provenance is simplified.
- Revert queue posture wording if governance-lane sequencing changes.
- Remove this evidence file if the `GAP-066` contract slice is withdrawn.
