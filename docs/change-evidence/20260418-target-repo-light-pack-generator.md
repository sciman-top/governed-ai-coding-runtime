# 20260418 Target Repo Light Pack Generator

## Goal
Implement `GAP-035 Task 2` by creating the first repo-local light-pack generator and validator for target repository attachment.

## Landing
- Source plan: `docs/plans/interactive-session-productization-implementation-plan.md`
- Target destination:
  - runtime contract: `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
  - CLI: `scripts/attach-target-repo.py`
  - tests: `tests/runtime/test_repo_attachment.py`
  - product doc: `docs/product/target-repo-attachment-flow.md`
  - architecture alignment: `docs/architecture/generic-target-repo-attachment-blueprint.md`

## Changes
- Added `attach_target_repo` and `validate_light_pack`.
- Added `.governed-ai/repo-profile.json` and `.governed-ai/light-pack.json` generation semantics.
- Existing light packs are validated by default and are not overwritten unless overwrite is requested.
- Added validation for:
  - repo profile references escaping the target repo
  - empty gate command declarations
  - absolute or parent-escaping path policy scopes
  - mutable runtime state under the target repo
- Added `scripts/attach-target-repo.py --help` CLI surface.
- Documented the target repo attachment flow.

## TDD Evidence

### Red
- `cmd`: `python -m unittest tests.runtime.test_repo_attachment -v`
- `exit_code`: `1`
- `key_output`: `attach_target_repo is not implemented`; `validate_light_pack` missing; `scripts/attach-target-repo.py` missing
- `timestamp`: `2026-04-18`

### Green
- `cmd`: `python -m unittest tests.runtime.test_repo_attachment -v`
- `exit_code`: `0`
- `key_output`: `Ran 14 tests in 0.718s`; `OK`
- `timestamp`: `2026-04-18`

## Verification
- `cmd`: `python scripts/attach-target-repo.py --help`
- `exit_code`: `0`
- `key_output`: `Attach or validate a target repository light pack.`
- `timestamp`: `2026-04-18`

- `cmd`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `exit_code`: `0`
- `key_output`: `Ran 141 tests in 20.639s`; `OK`; `OK runtime-unittest`
- `timestamp`: `2026-04-18`

## Risks
- The light pack is intentionally minimal and does not yet detect adapter capabilities. Adapter detection remains later `GAP-037` and `GAP-038` work.
- The CLI generates a conservative repo profile from explicit command inputs. Repository-specific fine tuning remains a follow-up after real multi-repo trials.
- Doctor/status surfaces do not yet display live attachment posture. That is `Task 3`.

## Rollback
- Revert:
  - `scripts/attach-target-repo.py`
  - `docs/product/target-repo-attachment-flow.md`
  - Task 2 additions in `repo_attachment.py`
  - Task 2 additions in `tests/runtime/test_repo_attachment.py`
  - `.governed-ai` wording updates in `docs/architecture/generic-target-repo-attachment-blueprint.md`
- Re-run:
  - `python -m unittest tests.runtime.test_repo_attachment -v`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
