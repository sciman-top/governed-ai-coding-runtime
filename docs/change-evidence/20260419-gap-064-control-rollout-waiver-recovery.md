# 20260419 GAP-064 Control Rollout Matrix And Waiver Recovery

## Change Basis
- `GAP-064` is the next governance-lane task after completed `GAP-063` repo admission hardening.
- The previous control and waiver contracts captured only a minimal observe/enforce posture and temporary exception record. They did not define `canary`, rollback semantics, health signals, recovery gates, or expiry-to-recovery linkage strongly enough for promotion governance.
- Landing point:
  - `docs/specs/control-registry-spec.md`
  - `schemas/jsonschema/control-registry.schema.json`
  - `docs/specs/waiver-and-exception-spec.md`
  - `schemas/jsonschema/waiver-and-exception.schema.json`
  - example records for progressive control rollout and temporary waivers
  - maintenance policy and queue posture docs
- Target destination: progressive controls can move through `observe -> canary -> enforce -> rollback` with explicit evidence and rollback criteria, while waivers remain time-bounded, recovery-linked, and non-permanent.
- Active rule path: `D:\OneDrive\CODE\governed-ai-coding-runtime\AGENTS.md`, carrying `GlobalUser/AGENTS.md v9.39`.
- Clarification trace: `issue_id=gap-064-control-rollout-waiver-recovery`, `attempt_count=1`, `clarification_mode=direct_fix`, `clarification_scenario=n/a`, `clarification_questions=[]`, `clarification_answers=[]`.

## Files Changed
- Updated `docs/specs/control-registry-spec.md`
- Updated `schemas/jsonschema/control-registry.schema.json`
- Updated `docs/specs/waiver-and-exception-spec.md`
- Updated `schemas/jsonschema/waiver-and-exception.schema.json`
- Added `schemas/examples/control-registry/verification-hotspot-progressive-rollout.example.json`
- Added `schemas/examples/waiver-and-exception/temporary-canary-waiver.example.json`
- Updated `schemas/examples/waiver-and-exception/temporary-gate-waiver.example.json`
- Updated `docs/product/maintenance-deprecation-and-retirement-policy.md`
- Updated `docs/backlog/issue-ready-backlog.md`
- Updated `docs/README.md`
- Updated `docs/backlog/README.md`
- Updated `docs/roadmap/governance-optimization-lane-roadmap.md`
- Added `docs/change-evidence/20260419-gap-064-control-rollout-waiver-recovery.md`

## Summary
- Expanded the control registry contract so progressive controls now carry explicit rollout state, promotion criteria, rollback criteria, rollback owner, and health signals.
- Added `canary` and `rollback` semantics to the control posture model, making rollout transitions machine-readable instead of implied.
- Hardened the waiver record so active waivers now require `recovery_gate` and `rollback_ref`, and expiry/recovery behavior is defined explicitly.
- Added examples for one progressive control rollout and one canary-bounded temporary waiver, then updated the older gate-waiver example to satisfy the tightened schema.
- Synced maintenance policy and queue-entry docs so governance-lane posture now points to `GAP-065` as the next active task.

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
- This remains a governance-contract slice, not a runtime control promotion engine. Later implementation work still needs to enforce health-signal checks and waiver expiry behavior in live runtime paths.
- The stronger waiver contract will require any future sample or fixture to carry rollback visibility; forgetting that will now fail contract checks immediately.

## Rollback
- Revert the expanded rollout and waiver specs and schemas to the earlier minimal forms.
- Remove the new progressive control and canary waiver examples if the rollout surface is simplified.
- Revert maintenance-policy and queue-posture wording if governance-lane sequencing changes.
- Remove this evidence file if the `GAP-064` contract slice is withdrawn.
