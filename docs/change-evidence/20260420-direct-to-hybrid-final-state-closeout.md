# 20260420 Direct-To-Hybrid Final-State Closeout

## Goal
Close `GAP-046` through `GAP-060` with executable proof and claim-discipline updates so backlog, roadmap, master outline, issue seeds, and gate evidence stay aligned.

## Landing
- Runtime contracts:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/operator_queries.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/verification_runner.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_registry.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
- Service/persistence fix:
  - `packages/agent-runtime/persistence.py`
- Scripts:
  - `scripts/doctor-runtime.ps1`
  - `scripts/github/create-roadmap-issues.ps1`
- Tests:
  - `tests/service/test_session_api.py`
  - `tests/runtime/test_operator_queries.py`
  - `tests/runtime/test_contract_reader_parity.py`
  - `tests/runtime/test_verification_runner.py`
  - `tests/runtime/test_session_bridge.py`
  - `tests/runtime/test_runtime_status.py`
  - `tests/runtime/test_repo_attachment.py`
  - `tests/runtime/test_runtime_doctor.py`
- Planning/docs sync:
  - `docs/backlog/issue-ready-backlog.md`
  - `docs/backlog/issue-seeds.yaml`
  - `docs/roadmap/direct-to-hybrid-final-state-roadmap.md`
  - `docs/architecture/hybrid-final-state-master-outline.md`

## Key Changes
- Task 10/11 stabilization:
  - fixed SQLite connection lifecycle in `SqliteMetadataStore` to prevent Windows file-lock cleanup failures in service tests.
- Task 12:
  - added attachment-scoped read model (`operator_queries`) for approvals/evidence/handoff/replay/posture.
  - `inspect_evidence` and `inspect_handoff` now return read-only query payloads on the primary attached path instead of default degradation.
- Task 13:
  - added strict runtime readers and parity tests:
    - session bridge result reader
    - adapter selection reader
    - runtime snapshot reader
    - verification artifact reader
  - declared repo-profile gate contracts now fail loudly on incompatible shapes or missing required canonical gates.
- Task 14:
  - attachment posture now includes remediation and fail-closed semantics.
  - doctor now enforces fail-closed behavior for unhealthy attachment posture when attachment arguments are provided.
- Task 15:
  - backlog `GAP-046` through `GAP-060` marked complete with acceptance checkboxes closed.
  - issue seed version bumped to `3.6`.
  - issue-seed validation output now includes completed/active counts.
  - roadmap/master outline wording updated to keep complete-closure claims evidence-gated.

## Verification
- `cmd`: `python -m unittest tests.service.test_session_api tests.service.test_operator_api -v`
  - `exit_code`: `0`
  - `key_output`: `Ran 3 tests`; `OK`
- `cmd`: `python -m unittest tests.runtime.test_runtime_doctor tests.runtime.test_repo_attachment tests.runtime.test_verification_runner tests.runtime.test_runtime_status tests.runtime.test_session_bridge tests.runtime.test_contract_reader_parity tests.runtime.test_operator_queries -v`
  - `exit_code`: `0`
  - `key_output`: `Ran 72 tests`; `OK`
- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
  - `exit_code`: `0`
  - `key_output`: `{"issue_seed_version":"3.6","rendered_tasks":51,"rendered_issue_creation_tasks":8,"rendered_epics":14,"rendered_initiative":true,"completed_task_count":43,"active_task_count":8}`
- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - `exit_code`: `0`
  - `key_output`: `OK python-bytecode`; `OK python-import`
- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `exit_code`: `0`
  - `key_output`: `OK runtime-unittest`; `Ran 241 tests`; `OK`
- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - `exit_code`: `0`
  - `key_output`: `OK schema-json-parse`; `OK schema-example-validation`; `OK schema-catalog-pairing`
- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - `exit_code`: `0`
  - `key_output`: `OK runtime-status-surface`; `OK adapter-posture-visible`
- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
  - `exit_code`: `0`
  - `key_output`: `OK runtime-build`; `OK runtime-unittest`; `OK runtime-doctor`; `OK issue-seeding-render`; `Ran 241 tests`; `OK`

## Risks / Residuals
- Final-state claim remains valid only while closeout evidence stays reproducible against current runtime behavior.
- External attached-repo reality checks should be periodically re-run; if they drift, claim wording must be downgraded immediately.

## Rollback
- Revert the closeout commit(s) touching:
  - operator query surfaces
  - strict reader parity enforcement
  - fail-closed attachment doctor behavior
  - backlog/roadmap/master-outline/seed sync
- Re-run:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
