# Target Repo Managed Asset Retirement And Uninstall Plan

## Status
- Created: 2026-05-02.
- Queue: `GAP-144` through `GAP-151`.
- Current state: planning baseline only. No target repository file deletion is authorized by this plan.
- Trigger: owner-directed follow-up after target-repo overwrite protection landed. The remaining gap is safe retirement and one-click uninstall for files previously applied to target repositories by this runtime.

## Goal
Add a governed removal path that is as explicit and safe as the existing one-click apply path.

The runtime should be able to answer, for each target-repo file:

```text
is it currently managed, historically managed, target-owned, shared, drifted, or unknown?
```

Only after that classification may it propose or execute removal. The deletion path must be dry-run-first, path-bounded, reference-checked, backed up, evidence-producing, and reversible.

## Non-Goals
- Do not delete target-owned files automatically.
- Do not whole-file delete shared configuration files such as `.claude/settings.json` or `.governed-ai/repo-profile.json`.
- Do not treat a path under `.governed-ai/`, `.claude/`, `tests/`, `.github/`, or script directories as runtime-managed without provenance, baseline, historical-template, or hash evidence.
- Do not make `ApplyAllFeatures` silently remove files. Removal requires an explicit prune or uninstall action.
- Do not remove active evidence history or reviewed policy files as part of uninstall.

## Architecture Decisions
- Managed asset identity must use multiple signals: current baseline, rollout contract, sidecar provenance, content hash, git history, historical templates, and target-repo references.
- Current managed assets and retired managed assets are separate contracts. `required_managed_files` and `generated_managed_files` describe active ownership; a new retired contract describes removal candidates.
- Removal is a two-level capability:
  - `PruneRetiredManagedFiles`: remove historical runtime-managed files that are no longer active.
  - `UninstallGovernance`: detach runtime governance from a target repo, including active managed files, generated files, shared-file patches, light-pack/provenance, and profile-owned fields.
- Shared files are patched by ownership scope, not deleted as whole files.
- All apply modes require a prior dry-run result, backup location, and evidence report.

## Asset Classification Model
- `active_managed`: declared in current baseline or rollout contract and matching the expected source, generator, or merge result.
- `managed_drifted`: declared in current baseline or rollout contract but target content differs from expected content.
- `retired_managed_candidate`: not active now, but matched by historical baseline, historical rollout contract, previous template hash, provenance, or runtime-created commit evidence.
- `target_owned`: no current or historical runtime-managed evidence; preserve by default.
- `shared_or_field_owned`: the file is shared, and only specific fields, hooks, policy entries, or generated blocks belong to the runtime.
- `unknown`: insufficient evidence; block apply and report for manual review.

## Task List

### GAP-144 Managed Asset Identity Contract
**Description:** Define the machine-readable contract for classifying target-repo files and fields before prune or uninstall.

**Acceptance criteria:**
- [ ] A spec defines the six asset classes above and the evidence required for each class.
- [ ] The contract distinguishes whole-file ownership from field/block ownership.
- [ ] Unknown ownership fails closed for destructive actions.

**Verification:**
- [ ] Contract tests cover active, retired, drifted, shared, target-owned, and unknown classifications.
- [ ] `python scripts/verify-target-repo-rollout-contract.py` still passes.

**Dependencies:** None.

**Files likely touched:**
- `docs/specs/target-repo-managed-asset-lifecycle-spec.md`
- `docs/targets/target-repo-rollout-contract.json`
- `tests/runtime/test_target_repo_managed_asset_lifecycle.py`

**Estimated scope:** M.

### GAP-145 Target-Repo Managed Asset Inventory Dry Run
**Description:** Add a read-only inventory command that scans active targets and emits ownership classification without modifying target repos.

**Acceptance criteria:**
- [ ] The inventory command reads current baseline, rollout contract, historical templates, existing target files, and available provenance.
- [ ] The command reports `active_managed`, `managed_drifted`, `retired_managed_candidate`, `target_owned`, `shared_or_field_owned`, and `unknown`.
- [ ] The command includes `source_sha256`, `target_sha256`, `evidence_refs`, and `referenced_by` when available.

**Verification:**
- [ ] Unit tests prove dry-run does not modify files.
- [ ] A fixture target with mixed owned and target-owned files is classified correctly.

**Dependencies:** `GAP-144`.

**Files likely touched:**
- `scripts/inspect-target-repo-managed-assets.py`
- `tests/runtime/test_target_repo_managed_asset_inventory.py`
- `docs/targets/target-repo-rollout-contract.json`

**Estimated scope:** M.

### GAP-146 Managed File Provenance And Marker Policy
**Description:** Add provenance for future managed files so later prune/uninstall does not depend only on path guesses.

**Acceptance criteria:**
- [ ] Text files can carry a safe header marker when the file format allows comments.
- [ ] JSON or third-party config files that cannot safely accept extra fields use sidecar provenance under `.governed-ai/managed-files/`.
- [ ] Apply sync writes or refreshes provenance without overwriting target-local drift.

**Verification:**
- [ ] Tests prove schema-sensitive files are not polluted with unsupported fields.
- [ ] Tests prove provenance records include source path, sync revision, management mode, and source hash.

**Dependencies:** `GAP-144`, `GAP-145`.

**Files likely touched:**
- `scripts/apply-target-repo-governance.py`
- `scripts/verify-target-repo-governance-consistency.py`
- `docs/targets/target-repo-governance-baseline.json`
- `tests/runtime/test_target_repo_governance_consistency.py`

**Estimated scope:** M.

### GAP-147 Retired Managed Files Contract
**Description:** Add an explicit retired-file contract for old runtime-managed files that are no longer part of the active baseline.

**Acceptance criteria:**
- [ ] Baseline and rollout contract support `retired_managed_files`.
- [ ] Each retired entry records path, previous source, previous hash or evidence ref, retire reason, replacement, safe-delete conditions, and backup requirement.
- [ ] Contract verification fails if retired entries are missing safety metadata.

**Verification:**
- [ ] `python scripts/verify-target-repo-rollout-contract.py` fails on malformed retired entries and passes on valid entries.
- [ ] Tests cover retired entries for whole-file and shared-file retirement.

**Dependencies:** `GAP-144`.

**Files likely touched:**
- `docs/targets/target-repo-governance-baseline.json`
- `docs/targets/target-repo-rollout-contract.json`
- `scripts/verify-target-repo-rollout-contract.py`
- `tests/runtime/test_target_repo_rollout_contract.py`

**Estimated scope:** M.

### GAP-148 Prune Retired Managed Files
**Description:** Implement the explicit prune path for historical runtime-managed files that are no longer needed.

**Acceptance criteria:**
- [ ] Default mode is dry-run and reports candidates only.
- [ ] Apply mode deletes only retired candidates with matching provenance or hash evidence.
- [ ] Apply mode blocks files with target-local drift, unknown ownership, or active target references.
- [ ] Deleted files are backed up and reported with rollback instructions.

**Verification:**
- [ ] Tests prove matching retired files can be removed.
- [ ] Tests prove drifted, referenced, unknown, and target-owned files are not removed.
- [ ] `runtime-flow-preset.ps1` exposes a JSON field for prune results.

**Dependencies:** `GAP-145`, `GAP-147`.

**Files likely touched:**
- `scripts/prune-retired-managed-files.py`
- `scripts/runtime-flow-preset.ps1`
- `tests/runtime/test_prune_retired_managed_files.py`
- `tests/runtime/test_runtime_flow_preset.py`

**Estimated scope:** M.

### GAP-149 One-Click Governance Uninstall
**Description:** Add a target-repo detach/uninstall path that removes runtime governance assets without deleting target-owned work.

**Acceptance criteria:**
- [ ] Default uninstall mode is dry-run.
- [ ] Apply mode removes active whole-file managed assets only when provenance or expected hash proves runtime ownership.
- [ ] Apply mode patches shared files by field or block ownership instead of deleting whole files.
- [ ] Apply mode can remove runtime light-pack/provenance files while preserving target evidence and target-owned files.
- [ ] Uninstall emits an evidence report and rollback instructions.

**Verification:**
- [ ] Tests prove `.claude/settings.json` is patched, not deleted.
- [ ] Tests prove `.governed-ai/repo-profile.json` removes runtime-owned fields only.
- [ ] Tests prove uninstall blocks drifted or referenced files.

**Dependencies:** `GAP-144`, `GAP-145`, `GAP-146`, `GAP-148`.

**Files likely touched:**
- `scripts/uninstall-target-repo-governance.py`
- `scripts/runtime-flow-preset.ps1`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
- `tests/runtime/test_uninstall_target_repo_governance.py`

**Estimated scope:** M.

### GAP-150 Operator And All-Target Integration
**Description:** Expose prune and uninstall through the same one-click surfaces used for apply.

**Acceptance criteria:**
- [ ] `runtime-flow-preset.ps1` supports all-target and single-target dry-run for prune and uninstall.
- [ ] Apply requires explicit destructive-action flags and cannot be triggered by normal `ApplyAllFeatures`.
- [ ] JSON output includes candidate counts, blocked counts, backup paths, and evidence refs.
- [ ] Operator surfaces can invoke dry-run and display blocked reasons.

**Verification:**
- [ ] Runtime-flow preset tests cover all-target dry-run and single-target apply fixture behavior.
- [ ] Operator tests cover action visibility without enabling accidental destructive defaults.

**Dependencies:** `GAP-148`, `GAP-149`.

**Files likely touched:**
- `scripts/runtime-flow-preset.ps1`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py`
- `tests/runtime/test_runtime_flow_preset.py`
- `tests/runtime/test_operator_ui.py`

**Estimated scope:** M.

### GAP-151 Closeout Gates And Target Evidence
**Description:** Close the queue with fresh evidence from active target repos and hard gates.

**Acceptance criteria:**
- [ ] Active target catalog dry-run reports are generated for prune and uninstall.
- [ ] No target repo is modified by closeout dry-run evidence.
- [ ] Full repo gates pass after implementation.
- [ ] Evidence documents record commands, key output, compatibility, and rollback.

**Verification:**
- [ ] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- [ ] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- [ ] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- [ ] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- [ ] `python scripts/verify-target-repo-rollout-contract.py`
- [ ] `python scripts/verify-target-repo-governance-consistency.py`

**Dependencies:** `GAP-150`.

**Files likely touched:**
- `docs/change-evidence/`
- `docs/plans/target-repo-managed-asset-retirement-and-uninstall-plan.md`
- implementation evidence reports generated by the preceding tasks

**Estimated scope:** S.

## Checkpoints

### Checkpoint A: Identity And Inventory
- [ ] `GAP-144` and `GAP-145` complete.
- [ ] Inventory dry-run classifies fixture targets without mutation.
- [ ] Unknown ownership blocks destructive actions.

### Checkpoint B: Retired Contract And Prune
- [ ] `GAP-146` through `GAP-148` complete.
- [ ] Retired managed files can be proposed and pruned only with evidence.
- [ ] Referenced, drifted, and target-owned files are preserved.

### Checkpoint C: One-Click Uninstall
- [ ] `GAP-149` and `GAP-150` complete.
- [ ] Single-target and all-target dry-runs are available from the canonical one-click entrypoint.
- [ ] Apply mode requires explicit destructive intent and produces backups.

### Checkpoint D: Closeout
- [ ] `GAP-151` complete.
- [ ] Full hard-gate chain passes.
- [ ] Active target dry-run evidence proves no accidental target modifications.

## Risks And Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| A target-owned file is mistaken for a runtime-managed file | High | Require provenance, historical hash, baseline, or commit evidence; unknown ownership blocks apply |
| A shared file is deleted whole-file | High | Model shared files as field/block-owned and require patch tests |
| A retired file is still referenced by CI or hooks | High | Add reference scanning and block when references exist |
| Historical templates are incomplete | Medium | Treat missing history as unknown, not deletable |
| Dry-run and apply diverge | Medium | Require apply to consume or reproduce the same classification result and emit evidence |
| Operator UI makes destructive paths too easy | Medium | Keep destructive apply flags explicit and separate from normal apply features |

## Execution Order
1. Implement `GAP-144` and `GAP-145` first to make classification observable.
2. Implement provenance and retired contract after classification is stable.
3. Implement prune before uninstall because prune is a narrower deletion path.
4. Implement uninstall after shared-file patch semantics are covered by tests.
5. Integrate all-target/operator surfaces only after the lower-level safety checks are proven.
6. Close with active target dry-run evidence and the full gate sequence.

## Open Questions
- Exact flag names may change during implementation, but destructive apply must remain explicit and separate from normal `ApplyAllFeatures`.
- Historical managed-file extraction may need a bounded lookback window if full git-history scanning is too slow.
- The first implementation should decide whether backup artifacts live in each target repo under `.governed-ai/backups/` or in the control repo under `docs/change-evidence/`; either choice must be reported in JSON evidence.
