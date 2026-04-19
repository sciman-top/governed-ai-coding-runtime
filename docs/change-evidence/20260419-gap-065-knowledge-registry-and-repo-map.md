# 20260419 GAP-065 Knowledge Registry And Repo-Map Context Shaping

## Change Basis
- `GAP-065` follows completed `GAP-064` control rollout and waiver recovery hardening.
- The previous knowledge-source and repo-map contracts did not make trust, review status, precedence, drift posture, or explicit knowledge-source linkage mandatory enough for governed reuse.
- Landing point:
  - `docs/specs/knowledge-source-spec.md`
  - `schemas/jsonschema/knowledge-source.schema.json`
  - `docs/specs/repo-map-context-shaping-spec.md`
  - `schemas/jsonschema/repo-map-context-shaping.schema.json`
  - updated knowledge-source and repo-map examples
  - queue posture sync in docs entrypoints
- Target destination: knowledge inputs become typed, reviewable, freshness-aware governance assets, and repo-map shaping remains an explicit governed input rather than hidden agent behavior.
- Active rule path: `D:\OneDrive\CODE\governed-ai-coding-runtime\AGENTS.md`, carrying `GlobalUser/AGENTS.md v9.39`.
- Clarification trace: `issue_id=gap-065-knowledge-registry-and-repo-map`, `attempt_count=1`, `clarification_mode=direct_fix`, `clarification_scenario=n/a`, `clarification_questions=[]`, `clarification_answers=[]`.

## Files Changed
- Updated `docs/specs/knowledge-source-spec.md`
- Updated `schemas/jsonschema/knowledge-source.schema.json`
- Updated `docs/specs/repo-map-context-shaping-spec.md`
- Updated `schemas/jsonschema/repo-map-context-shaping.schema.json`
- Updated `schemas/examples/knowledge-source/docs-index-authoritative.example.json`
- Updated `schemas/examples/repo-map-context-shaping/hybrid-default.example.json`
- Updated `docs/backlog/issue-ready-backlog.md`
- Updated `docs/README.md`
- Updated `docs/backlog/README.md`
- Updated `docs/roadmap/governance-optimization-lane-roadmap.md`
- Added `docs/change-evidence/20260419-gap-065-knowledge-registry-and-repo-map.md`

## Summary
- Expanded the knowledge-source contract so sources now carry explicit `review_status`, `precedence`, and `drift_policy` in addition to trust and freshness metadata.
- Kept memory-like sources explicitly non-authoritative while making stale or degraded knowledge posture visible instead of silently inheriting authority.
- Expanded repo-map shaping so every strategy now references reviewable `knowledge_source_refs` and carries its own `review_status`.
- Updated the canonical examples to reflect approved knowledge-source posture and governed repo-map linkage.
- Advanced governance-lane posture so `GAP-066` is now the next active task.

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
- This step defines the governance shape only; runtime selection and context assembly code still need to consume the richer review and drift metadata in later implementation slices.
- Tightened schema requirements mean future examples or repo-local manifests must always declare review and drift posture explicitly.

## Rollback
- Revert the knowledge-source and repo-map specs and schemas to the earlier minimal baseline.
- Revert the example updates if the governance contract is simplified again.
- Revert queue posture wording if governance-lane sequencing changes.
- Remove this evidence file if the `GAP-065` contract slice is withdrawn.
