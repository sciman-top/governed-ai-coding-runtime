# 20260616 Continuous Execution Runtime Gate Refresh

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home:
  - `tests/__init__.py`
  - `tests/runtime/test_run_governed_task_service_wrapper.py`
  - `docs/architecture/planning-status.json`
  - `docs/change-evidence/README.md`
  - `docs/change-evidence/20260616-continuous-execution-runtime-gate-refresh.md`
- verification path: keep `Continuous-Execution` in its bounded evidence-and-gates loop by closing today's real Runtime gate failure under the current restricted workspace boundary and then publishing fresh gate-backed evidence without changing the selector

## Why This Slice Was Needed
- `planning-status.json` still correctly keeps the active queue at `Continuous-Execution` and the selector at `defer_ltp_and_refresh_evidence`.
- Under today's managed workspace boundary, the active loop exposed a real gate defect instead of a new implementation queue:
  - `tests.runtime.test_repo_attachment.RepoAttachmentBindingTests.test_attach_target_repo_can_resolve_runtime_state_root_from_runtime_roots_model`
  - `tests.runtime.test_run_governed_task_service_wrapper.RunGovernedTaskServiceWrapperTests.test_write_replay_case_returns_runtime_relative_ref_for_external_runtime_root`
- The truthful next move was to repair the Runtime verification surface itself, not to infer permission for heavy LTP work.

## Root Cause
1. Default machine-local runtime home in tests
- `tests/__init__.py` only redirected `TMP/TEMP/TMPDIR`.
- The attachment test that intentionally exercises default runtime-root resolution still wrote through `GOVERNED_RUNTIME_HOME` fallback into host-local `LocalAppData`.
- In the current restricted environment that path is not writable, so the Runtime gate failed with a permission error even though the runtime-root contract itself was still correct.

2. External-runtime replay-path test fixture
- `test_write_replay_case_returns_runtime_relative_ref_for_external_runtime_root` created its temporary runtime under `ROOT.parent` (`D:\CODE`), which is outside the current writable root.
- After moving the temp root inside the repo, the test still needed to isolate module `ROOT` as well, because `_runtime_ref_for_path()` first prefers repo-relative refs before runtime-relative refs.
- The implementation behavior stayed correct; the test fixture was the unstable piece.

## Change Summary
1. Stabilized test-local machine runtime home
- Updated `tests/__init__.py` to set `GOVERNED_RUNTIME_HOME` to repo-local `.runtime/home`.
- This preserves the "machine-local, outside attached repo" runtime-root contract while keeping test writes inside the current workspace.

2. Hardened the external-runtime replay test fixture
- Updated `tests/runtime/test_run_governed_task_service_wrapper.py` so the temporary runtime lives under repo-local `.runtime`.
- Patched the module `ROOT` together with `RUNTIME_ROOT` and `REPLAY_ROOT` inside that test, making the asserted `replay/...` runtime-relative ref deterministic and independent of the repository root.

3. Refreshed bounded-loop proof
- Re-ran selector truth, planning truth, Docs gate, Build gate, Contract gate, Doctor gate, and the full Runtime gate.
- Refreshed `planning-status.json` to point the current decision-gate proof at this file for the 2026-06-16 bounded loop refresh.

## Verification
### Selector and planning truth
- `python scripts/select-next-work.py`
  - result: pass
  - result: `next_action=defer_ltp_and_refresh_evidence`
- `python scripts/verify-planning-status.py`
  - result: pass

### Targeted failure reproduction and fix validation
- `python -m unittest tests.runtime.test_repo_attachment.RepoAttachmentBindingTests.test_attach_target_repo_can_resolve_runtime_state_root_from_runtime_roots_model -v`
  - before fix: failed under host-local runtime-home permission boundary
  - after fix: pass
- `python -m unittest tests.runtime.test_run_governed_task_service_wrapper -v`
  - before fix: final replay-path case timed out / failed because the temp root escaped the writable workspace and then asserted against repo-relative precedence
  - after fix: pass

### Full bounded-loop gate result
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- result: pass
- runtime timing note:
  - `docs/change-evidence/runtime-test-speed-latest.json` refreshed to `elapsed_seconds=396.7313830999992`, `failure_count=0`
  - the previously stuck wrapper module now completes in `1.787s`

## Queue Boundary
- This slice keeps `Continuous-Execution` active as a bounded evidence-and-gates loop.
- This slice does **not** change the selector away from `defer_ltp_and_refresh_evidence`.
- This slice does **not** authorize heavy `LTP-01..06` implementation.
- This slice closes a real gate defect encountered during autonomous continuation, which is aligned with the active loop's truthful maintenance boundary.

## Risk
- risk_level: `low`
- reason:
  - test-environment and test-fixture hardening only
  - no production contract broadening
  - verification uses the existing hard gate order and fresh full Runtime evidence

## Rollback
- revert:
  - `tests/__init__.py`
  - `tests/runtime/test_run_governed_task_service_wrapper.py`
  - `docs/architecture/planning-status.json`
  - `docs/change-evidence/README.md`
  - `docs/change-evidence/20260616-continuous-execution-runtime-gate-refresh.md`
- re-run:
  - `python -m unittest tests.runtime.test_repo_attachment.RepoAttachmentBindingTests.test_attach_target_repo_can_resolve_runtime_state_root_from_runtime_roots_model -v`
  - `python -m unittest tests.runtime.test_run_governed_task_service_wrapper -v`
  - `python scripts/select-next-work.py`
  - `python scripts/verify-planning-status.py`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
