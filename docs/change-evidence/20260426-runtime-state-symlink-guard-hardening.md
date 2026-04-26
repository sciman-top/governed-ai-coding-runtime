# 20260426 Runtime State Symlink Guard Hardening

## Goal
- Review and harden runtime state persistence without changing public contracts, data formats, or operator-facing behavior.
- Keep the fix small and verifiable: reject pre-existing path indirections that would move task, artifact, or metrics state outside their declared roots.

## Baseline
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` -> pass (`OK python-bytecode`, `OK python-import`)
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> pass (`Ran 409 tests`, `OK`, `skipped=2`)
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` -> pass (`status=pass`, `drift_count=0`, `target_count=5`)
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` -> pass (`OK codex-capability-ready`, `OK adapter-posture-visible`)
- Supplementary baseline:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts` -> pass
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` -> pass
  - `python scripts/verify-target-repo-governance-consistency.py` -> pass (`sync_revision=2026-04-26.9`, `drift_count=0`)

## Main Issue
- `LocalArtifactStore`, `FileTaskStore`, and `persist_learning_efficiency_metrics(...)` generated safe relative paths, but they did not re-check the resolved final path before writing.
- Because shared `atomic_write_text(...)` intentionally preserves symlink targets for repo-local write compatibility, a pre-existing symlink under a state root could redirect task, artifact, or metrics writes outside the declared store root.
- The fix belongs at the store boundary because each store knows its allowed root; changing `atomic_write_text(...)` globally would risk breaking the existing attached-write contract that allows symlinks resolving inside the attachment root.

## Changes
- `packages/contracts/src/governed_ai_coding_runtime_contracts/artifact_store.py`
  - Resolves the artifact store root once during initialization.
  - Adds `_prepare_store_path(...)` to verify both parent path and final path stay under the artifact root before writing.
- `packages/contracts/src/governed_ai_coding_runtime_contracts/task_store.py`
  - Resolves the task store root once during initialization.
  - Verifies resolved task record paths stay under the task root on both save and load.
- `packages/contracts/src/governed_ai_coding_runtime_contracts/learning_efficiency_metrics.py`
  - Resolves `output_root` and verifies both metrics directory and final JSON path stay under that root before writing.
- Tests
  - Added symlink escape regression coverage for artifact, task, and metrics state persistence.

## Verification
- `python -m py_compile packages\contracts\src\governed_ai_coding_runtime_contracts\artifact_store.py packages\contracts\src\governed_ai_coding_runtime_contracts\task_store.py packages\contracts\src\governed_ai_coding_runtime_contracts\learning_efficiency_metrics.py` -> pass
- `python -m unittest tests.runtime.test_artifact_store tests.runtime.test_task_store tests.runtime.test_learning_efficiency_metrics -v` -> pass (`Ran 13 tests`, `OK`, `skipped=3`; symlink creation is unavailable in the current Windows process)
- `python -m unittest tests.runtime.test_attached_write_execution tests.runtime.test_attached_write_governance tests.runtime.test_execution_runtime tests.runtime.test_runtime_status tests.runtime.test_session_bridge tests.runtime.test_verification_runner tests.runtime.test_worker -v` -> pass (`Ran 91 tests`, `OK`, `skipped=2`)
- `python -m unittest tests.service.test_session_api tests.service.test_operator_api -v` -> pass (`Ran 5 tests`, `OK`)
- Final gate order after the fix:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` -> pass (`OK python-bytecode`, `OK python-import`)
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> pass (`Ran 412 tests`, `OK`, `skipped=5`; service checks `Ran 10 tests`, `OK`)
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` -> pass (`OK dependency-baseline`, `OK target-repo-governance-consistency`, `OK agent-rule-sync`)
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` -> pass (`OK codex-capability-ready`, `OK adapter-posture-visible`)
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts` -> pass
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` -> pass
  - `python scripts/verify-target-repo-governance-consistency.py` -> pass (`target_count=5`, `drift_count=0`)
  - `git diff --check` -> pass with line-ending conversion warnings only

## Risk And Rollback
- Risk: low. The change only rejects state writes whose resolved target escapes the declared store root; normal paths and generated relative-path formats are unchanged.
- Compatibility: attached-write behavior for symlinks resolving inside `attachment_root` is unchanged because the global atomic-write helper was not narrowed.
- Rollback: revert this evidence file plus:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/artifact_store.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/task_store.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/learning_efficiency_metrics.py`
  - `tests/runtime/test_artifact_store.py`
  - `tests/runtime/test_task_store.py`
  - `tests/runtime/test_learning_efficiency_metrics.py`
