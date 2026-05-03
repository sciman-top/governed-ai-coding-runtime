# 2026-05-04 ApplyAllFeatures Host-Recovery Preflight Split

## Scope
- Rule IDs: `R1`, `R3`, `R4`, `R6`, `R8`, `E4`
- Risk: low-to-medium; operator/UI preflight control flow only.
- Current landing: `scripts/operator.ps1` and `scripts/serve-operator-ui.py`.
- Target home: keep autonomous implementation work blocked while allowing operator-directed target-repo maintenance to use the canonical one-click entrypoint.
- Rollback: `git revert <commit>` for this change set.

## Problem
`wait_for_host_capability_recovery` correctly reports that current Codex host evidence is still bounded to `process_bridge` instead of proving `native_attach`. The operator used that selector action to block both implementation/evolution work and `ApplyAllFeatures`.

That was too broad. `ApplyAllFeatures` is the target-repo maintenance rollout path. It already runs through governance sync, target gates, drift checks, managed-file hash/reference guards, and target-governance consistency checks. Blocking it on host native-attach recovery prevents the project from using its own one-click maintenance path even when the action is explicitly requested by the operator and the runtime flow itself can produce fresh target-run evidence.

## Change
- Kept `repair_gate_first`, `refresh_evidence_first`, and `owner_directed_scope_required` as blockers for `ApplyAllFeatures`.
- Removed `wait_for_host_capability_recovery` as a blocker for `ApplyAllFeatures`.
- Kept `wait_for_host_capability_recovery` as a blocker for `EvolutionMaterialize`.
- Updated the operator UI next-work summary so the UI no longer disables `apply_all_features` while waiting for host recovery.
- Fixed operator argument forwarding so `-DisableManagedAssetRemoval` is passed through to `runtime-flow-preset.ps1`; otherwise direct `-ApplyAllFeatures` defaults could still apply managed-file removal.

## Verification
- `python -m unittest tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action ApplyAllFeatures -Mode quick -TargetParallelism 2 -DisableManagedAssetRemoval`
