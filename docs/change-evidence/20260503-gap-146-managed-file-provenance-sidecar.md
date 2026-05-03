# 2026-05-03 GAP-146 Managed File Provenance Sidecar

## Rule
- `R1`: current landing point is target-repo managed-file sync; target home is the baseline provenance contract and apply/runtime consistency checks.
- `R4`: medium-risk governance baseline and sync-script change; apply remains non-destructive for drifted target files, and provenance is observe-mode sidecar metadata.
- `R8`: record basis, changed files, verification, compatibility, and rollback.

## Pre-Change Review
- Source baseline: `docs/targets/target-repo-governance-baseline.json`.
- Sync entrypoint: `scripts/apply-target-repo-governance.py`.
- Consistency gate: `scripts/verify-target-repo-governance-consistency.py`.
- Target-repo safety posture: existing `block_on_drift` managed-file policy remains unchanged; target-local drift is still blocked rather than overwritten.
- Platform/tooling review: no Codex/Claude/Gemini rule source, provider, MCP, auth, or login-chain change.

## pre_change_review
- `control_repo_manifest_and_rule_sources`: reviewed `rules/manifest.json`, the loaded project `AGENTS.md` contract, `docs/targets/target-repo-governance-baseline.json`, and prior managed-asset cleanup evidence before changing the baseline and sync verifier surface.
- `user_level_deployed_rule_files`: no user-level deployed Codex/Claude/Gemini rule file is changed by this slice; rule sync drift remains outside this implementation.
- `target_repo_deployed_rule_files`: no target-repo deployed rule file is changed by this slice; the new sidecar policy is additive metadata for future managed-file apply runs.
- `target_repo_gate_scripts_and_ci`: reviewed the existing gate chain and kept `scripts/verify-target-repo-governance-consistency.py` as the consistency contract; full gate replay is required before closeout.
- `target_repo_repo_profile`: no target repo `repo-profile.json` is edited here; managed-file apply still refuses target-local drift and preserves profile ownership rules.
- `target_repo_readme_and_operator_docs`: docs/backlog status is updated, but target operator docs and target README files are not distributed by this slice.
- `current_official_tool_loading_docs`: no Codex/Claude/Gemini loading model is changed; current session rules are treated as context, while deterministic enforcement stays in scripts and gates.
- `drift-integration decision`: integrate the missing provenance policy into the control-repo baseline first, keep target-repo sidecars observe-mode, and do not blind-overwrite historical target repos that lack sidecars.

## Basis
- `GAP-146` required future managed-file provenance so prune and uninstall do not rely only on path guesses or historical hashes.
- JSON and third-party config files cannot safely receive unsupported marker fields.
- Existing destructive paths already failed closed when provenance/hash evidence was absent; the missing slice was deterministic future provenance writing for managed files.

## Changes
- Added `managed_file_provenance_policy` to the target-repo governance baseline with `status=observe`, `strategy=sidecar`, `sidecar_root=.governed-ai/managed-files`, `write_on_apply=true`, and `require_in_consistency=false`.
- Added deterministic sidecar provenance records for managed-file apply paths under `.governed-ai/managed-files/<managed-path>.provenance.json`.
- Each record includes `path`, `source`, `sync_revision`, `management_mode`, `ownership_scope`, `marker_strategy`, `source_sha256`, `target_sha256`, and `expected_sha256`.
- `json_merge` files are recorded as `ownership_scope=field_or_block`; other managed-file modes are recorded as `ownership_scope=whole_file`.
- The apply command refreshes provenance only after the target content matches expected managed content; drifted target-local files remain blocked.
- `managed_file_provenance_policy.status=disabled` or `write_on_apply=false` prevents sidecar writing.
- The consistency checker validates the policy shape but does not require historical target repos to already contain sidecars because `require_in_consistency=false`.

## Verification
- `python -m py_compile scripts/apply-target-repo-governance.py scripts/verify-target-repo-governance-consistency.py`: pass.
- `python -m unittest tests.runtime.test_target_repo_governance_consistency`: pass; `Ran 29 tests`.
- `python scripts/verify-target-repo-governance-consistency.py`: pass; `target_count=5`, `drift_count=0`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`: pass; `rendered_tasks=136`, `rendered_issue_creation_tasks=1`, `completed_task_count=135`, `active_task_count=1`.
- `python -m unittest tests.runtime.test_issue_seeding`: pass; `Ran 9 tests`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`: pass; includes `OK backlog-yaml-ids`, `OK evidence-recovery-posture`, `OK autonomous-next-work-selection`, and `OK post-closeout-queue-sync`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`: pass; `OK python-bytecode`, `OK python-import`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`: pass; `102` test files, `failures=0`, `Completed 102 test files in 133.275s`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`: pass; includes `OK target-repo-governance-consistency`, `OK pre-change-review`, and `OK functional-effectiveness`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`: pass; hard checks OK with existing `WARN codex-capability-degraded`.
- `git diff --check`: pass; CRLF normalization warnings only.
- `python scripts/select-next-work.py`: pass; `gate_state=pass`, `source_state=fresh`, `evidence_state=stale`, `next_action=refresh_evidence_first`, `ltp_decision=defer_all`.

## Compatibility
- Existing target repos are not required to already have sidecar provenance files.
- Sidecar records are additive files under `.governed-ai/managed-files/`; JSON and third-party config files are not polluted with unsupported fields.
- Existing target-local drift handling is unchanged: `replace` and `block_on_drift` refuse existing drift, and `json_merge` preserves local keys outside runtime-owned fields.
- `GAP-151` remains active because it needs fresh all-target dry-run evidence and hard-gate closeout, not just implementation presence.
- This change does not promote or implement any `LTP-01..06` heavy-stack package.

## Rollback
- Revert this file and the related changes to `docs/targets/target-repo-governance-baseline.json`, `scripts/apply-target-repo-governance.py`, `scripts/verify-target-repo-governance-consistency.py`, `tests/runtime/test_target_repo_governance_consistency.py`, `docs/plans/target-repo-managed-asset-retirement-and-uninstall-plan.md`, and backlog/docs status files.
