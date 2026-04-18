# 20260418 Repo Attachment Binding Contract

## Goal
Implement the `GAP-035` Task 1 contract boundary for attaching one target repository to the machine-local governed runtime.

## Landing
- Source plan: `docs/plans/interactive-session-productization-implementation-plan.md`
- Target destination:
  - spec: `docs/specs/repo-attachment-binding-spec.md`
  - schema: `schemas/jsonschema/repo-attachment-binding.schema.json`
  - Python contract: `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
  - tests: `tests/runtime/test_repo_attachment.py`

## Changes
- Added `RepoAttachmentBinding` with `build_repo_attachment_binding`.
- Added validation that repo-local declarations stay inside `target_repo_root`.
- Added validation that `runtime_state_root` and mutable task/run/approval/artifact/replay state stay machine-local.
- Added schema and spec pairing for repo attachment bindings.
- Exported the contract from the package root.
- Added schema catalog entry and specs index link.

## TDD Evidence

### Red
- `cmd`: `python -m unittest tests.runtime.test_repo_attachment -v`
- `exit_code`: `1`
- `key_output`: `ModuleNotFoundError: No module named 'governed_ai_coding_runtime_contracts.repo_attachment'`
- `timestamp`: `2026-04-18`

### Green
- `cmd`: `python -m unittest tests.runtime.test_repo_attachment -v`
- `exit_code`: `0`
- `key_output`: `Ran 8 tests in 0.553s`; `OK`
- `timestamp`: `2026-04-18`

## Gate Evidence

### Task 0 Preconditions
- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `exit_code`: `0`
- `key_output`: `OK active-markdown-links`; `OK backlog-yaml-ids`; `OK old-project-name-historical-only`
- `timestamp`: `2026-04-18`

- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- `exit_code`: `0`
- `key_output`: `{"issue_seed_version":"3.2","rendered_tasks":27,"rendered_issue_creation_tasks":27,"rendered_epics":7,"rendered_initiative":true}`
- `timestamp`: `2026-04-18`

### Build
- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `exit_code`: `0`
- `key_output`: `OK python-bytecode`; `OK python-import`
- `timestamp`: `2026-04-18`

### Runtime
- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `exit_code`: `0`
- `key_output`: `Ran 135 tests in 19.192s`; `OK`; `OK runtime-unittest`
- `timestamp`: `2026-04-18`

### Contract / Invariant
- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `exit_code`: `0`
- `key_output`: `OK schema-json-parse`; `OK schema-example-validation`; `OK schema-catalog-pairing`
- `timestamp`: `2026-04-18`

### Hotspot / Doctor
- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- `exit_code`: `0`
- `key_output`: `OK runtime-status-surface`; `OK maintenance-policy-visible`; `OK adapter-posture-visible`
- `timestamp`: `2026-04-18`

### All
- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- `exit_code`: `0`
- `key_output`: `Ran 135 tests in 19.081s`; `OK`; `OK issue-seeding-render`
- `timestamp`: `2026-04-18`

### Diff Hygiene
- `cmd`: `git diff --check`
- `exit_code`: `0`
- `key_output`: no whitespace errors; only LF/CRLF working-copy warnings
- `timestamp`: `2026-04-18`

## Risks
- JSON Schema can express required fields and enums but cannot prove path containment. Python contract tests enforce the path containment and machine-local state invariants.
- This slice does not generate or validate an actual light pack; that remains Task 2.
- Doctor only has the binding posture vocabulary in this slice. Surfacing live attachment status remains Task 3.

## Rollback
- Revert:
  - `docs/specs/repo-attachment-binding-spec.md`
  - `schemas/jsonschema/repo-attachment-binding.schema.json`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
  - `tests/runtime/test_repo_attachment.py`
  - the `repo-attachment-binding` catalog/index/export additions
- Re-run:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
