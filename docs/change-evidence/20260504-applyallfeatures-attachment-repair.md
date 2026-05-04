# 20260504 ApplyAllFeatures Attachment Repair

## Goal
- Current landing point: `scripts/runtime-flow-preset.ps1`, `scripts/attach-target-repo.py`, and repo attachment contracts.
- Target destination: make the unified `ApplyAllFeatures` target-repo path repair stale attachment light-pack provenance before the daily runtime flow, while preserving fail-closed profile drift behavior.
- Verification path: focused unit tests, target-repo reruns, and the hard gate order `build -> test -> contract/invariant -> hotspot`.

## pre_change_review
- `pre_change_review`: required because this change modifies `scripts/runtime-flow-preset.ps1`, a sensitive target-repo orchestration entrypoint.
- `control_repo_manifest_and_rule_sources`: reviewed the active project rule contract and `rules/manifest.json` ownership boundary; this patch does not change rule source files or manifest-managed rule content.
- `user_level_deployed_rule_files`: no user-level deployed rule file is changed by this patch.
- `target_repo_deployed_rule_files`: no target-repo deployed `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md` file is changed by this patch.
- `target_repo_gate_scripts_and_ci`: reviewed the catalog-driven `ApplyAllFeatures` path, target gate execution through runtime-check, and added focused regression coverage for repair-before-daily-flow.
- `target_repo_repo_profile`: preserved target repo profile ownership by allowing `--overwrite` to refresh runtime-owned light-pack files only when existing profile core fields match the catalog-derived attachment core.
- `target_repo_readme_and_operator_docs`: no operator docs or README workflow is changed; the existing one-click command surface remains `runtime-flow-preset.ps1 -ApplyAllFeatures`.
- `current_official_tool_loading_docs`: no Codex, Claude, or Gemini loading semantics are changed; this is repository-local orchestration and attachment repair behavior only.
- `drift-integration decision`: integrate the discovered stale-provenance failure into the control repo orchestrator and attachment contract instead of manually patching only `k12-question-graph`.

## Root Cause And Changes
- Initial all-target `ApplyAllFeatures` run failed 1/6 on `k12-question-graph`.
- First root cause: `runtime-flow-preset.ps1` did not pass a default target repo binding id to `runtime-flow.ps1`; `k12-question-graph` then failed with `Unable to resolve repo binding id`.
- Second root cause: target `.governed-ai/light-pack.provenance.json` could become stale after light-pack changes; posture/status paths could surface this as an unstructured exception, and `ApplyAllFeatures` had no repair preflight.
- Changed `runtime-flow-preset.ps1` to derive `binding-<repo_id>` when `-RepoBindingId` is omitted.
- Added attachment posture inspection and a repair preflight for `ApplyAllFeatures`; invalid or stale attachment packs are refreshed before baseline sync and daily flow.
- Changed `attach-target-repo.py` / `repo_attachment.py` so `--overwrite` refreshes runtime-owned light-pack/provenance while preserving compatible enriched `repo-profile.json` data.
- Changed attachment posture inspection so provenance digest mismatch becomes structured `invalid_light_pack` with remediation instead of an exception.

## Evidence
- Initial all-target evidence: `docs/change-evidence/target-repo-runs/apply-all-features-20260504-232856.json` -> `target_count=6`, `failure_count=1`, failed target `k12-question-graph`.
- Binding-fix rerun evidence: `docs/change-evidence/target-repo-runs/apply-all-features-k12-question-graph-after-binding-fix-20260504-233911.json` -> binding progressed, then stale provenance surfaced.
- Repair rerun evidence: `docs/change-evidence/target-repo-runs/apply-all-features-k12-question-graph-after-attachment-repair-20260504-235044.json` -> `overall_status=pass`, `attachment_repair.status=pass`, `reason=refreshed_invalid_light_pack`, `runtime_check.exit_code=0`.
- Full rerun evidence before self-runtime closeout: `docs/change-evidence/target-repo-runs/apply-all-features-after-fixes-20260504-235137.json` -> 5/6 target flows passed; remaining `self-runtime` failure was this missing pre-change-review evidence, not target attachment repair.
- Self-runtime closeout rerun: `docs/change-evidence/target-repo-runs/apply-all-features-self-runtime-after-evidence-20260505-000324.json` -> `overall_status=pass`, `runtime_check.exit_code=0`, `milestone_commit.status=pass`.
- Final all-target closeout rerun: `docs/change-evidence/target-repo-runs/apply-all-features-final-20260505-000644.json` -> `target_count=6`, `failure_count=0`, `batch_timed_out=false`.
- Focused regression command passed:
  `python -m unittest tests.runtime.test_repo_attachment.RepoAttachmentBindingTests.test_attach_target_repo_overwrite_blocks_existing_repo_profile_drift tests.runtime.test_repo_attachment.RepoAttachmentBindingTests.test_attach_target_repo_overwrite_refreshes_light_pack_with_enriched_profile tests.runtime.test_repo_attachment.RepoAttachmentBindingTests.test_validate_light_pack_rejects_tampered_provenance_digest tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_single_target_json_keeps_runtime_payload_when_sync_skipped tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_apply_all_features_repairs_invalid_light_pack_before_daily_flow tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_apply_all_features_syncs_baseline_before_daily_flow -v`
- Pre-change review verifier passed: `python scripts/verify-pre-change-review.py --repo-root .`.
- Build passed: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` -> `OK python-bytecode`, `OK python-import`.
- Runtime passed: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> `Completed 105 test files`, `failures=0`, `OK runtime-unittest`.
- Contract passed: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` -> includes `OK pre-change-review` and `OK functional-effectiveness`.
- Hotspot passed: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` -> existing `WARN codex-capability-degraded`; all required checks passed.

## Compatibility
- The unified one-click entrypoint is unchanged.
- Existing profile drift protection remains: core attachment fields must match before `--overwrite` preserves an enriched profile.
- Missing or incompatible profiles are not force-overwritten by the repair preflight; the flow continues to fail through normal runtime checks if the target cannot be safely repaired.

## Rollback
- Revert `scripts/runtime-flow-preset.ps1`, `scripts/attach-target-repo.py`, `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`, related tests, and this evidence file.
- For target state, use each target repo git history; the only direct repair observed here refreshed `D:\CODE\k12-question-graph\.governed-ai\light-pack.json` and `light-pack.provenance.json` through the governed attachment command.
