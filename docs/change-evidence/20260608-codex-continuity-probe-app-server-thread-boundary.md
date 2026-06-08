# 20260608 Codex Continuity Probe App-Server Thread Boundary

## Goal
- Verify whether newer Codex surfaces expose a stronger, auditable attached-session boundary than the historical `status`-only probe.
- Keep `process_bridge` as the honest fallback unless a stronger signal is proven first.

## Root Cause
- The historical runtime contract already enforced an honest lower bound: `resume/help` surface alone could not promote Codex to `native_attach`.
- Newer Codex CLI builds now expose `app-server`, `remote-control`, and `doctor`, but the runtime probe still only recognized the `status` handshake path.
- Without a tighter distinction, future work could either underclaim a now-real boundary (`app-server` thread semantics) or overclaim from weaker supporting surfaces (`remote-control` / `doctor`).

## Findings
- `doctor --json` exposes app-server daemon posture and thread inventory, but not an attached-session boundary by itself.
- `remote-control` is a daemon-management surface; it ensures app-server is running with remote-control enabled, but it does not itself identify an attached thread/session boundary.
- Official Codex app-server docs and the locally generated app-server JSON schema both expose a stronger contract:
  - `thread.sessionId`
  - `thread/resume`
  - running-thread rejoin or session-tree semantics
- That combination is strong enough to treat `app-server` as a new attached-session boundary signal when `status` is unavailable.

## Changes
- Updated `[codex_adapter.py](D:/CODE/governed-ai-coding-runtime/packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py)` so native attach can be recognized from the `app-server` thread-boundary signal when:
  - `codex app-server` is available
  - generated schema proves `thread.sessionId`
  - generated schema proves `thread/resume`
  - generated schema proves session-tree or running-thread rejoin semantics
- Kept `remote-control` and `doctor` as supporting surfaces only; they do not promote Codex to `native_attach`.
- Added regression tests in `[test_codex_adapter.py](D:/CODE/governed-ai-coding-runtime/tests/runtime/test_codex_adapter.py)` for:
  - promoting from app-server thread-boundary evidence
  - refusing promotion from doctor/remote-control-only evidence
  - documenting the new boundary in product docs
- Updated product docs in:
  - `[codex-direct-adapter.md](D:/CODE/governed-ai-coding-runtime/docs/product/codex-direct-adapter.md)`
  - `[codex-direct-adapter.zh-CN.md](D:/CODE/governed-ai-coding-runtime/docs/product/codex-direct-adapter.zh-CN.md)`
  - `[codex-cli-app-integration-guide.md](D:/CODE/governed-ai-coding-runtime/docs/product/codex-cli-app-integration-guide.md)`
  - `[codex-cli-app-integration-guide.zh-CN.md](D:/CODE/governed-ai-coding-runtime/docs/product/codex-cli-app-integration-guide.zh-CN.md)`

## Verification
- `python -m unittest tests.runtime.test_codex_adapter.CodexAdapterTests.test_codex_live_probe_promotes_native_attach_from_app_server_thread_boundary_signal`
  - result: `FAIL` before implementation
  - result: `OK` after implementation
- `python -m unittest tests.runtime.test_codex_adapter.CodexAdapterTests.test_codex_live_probe_does_not_upgrade_from_doctor_and_remote_control_without_thread_boundary`
  - result: `OK`
- `python -m unittest tests.runtime.test_codex_adapter.CodexAdapterTests.test_codex_direct_adapter_docs_keep_resume_surface_as_supporting_evidence_only`
  - result: `FAIL` before doc updates
  - result: `OK` after doc updates
- `python -m unittest tests.runtime.test_codex_adapter`
  - result: `Ran 25 tests`
  - result: `OK`
- `python -m unittest tests.runtime.test_codex_adapter tests.runtime.test_trial_entrypoint`
  - result: `Ran 29 tests`
  - result: `OK`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - result: `OK python-bytecode`
  - result: `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - result: `Completed 114 test files`
  - result: `failures=0`
  - result: `OK runtime-unittest`
  - result: `OK runtime-service-parity`
  - result: `OK runtime-service-wrapper-drift-guard`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - result: `OK functional-effectiveness`
  - result: `OK agent-rule-sync`
  - result: contract gate passed
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - result: `OK codex-capability-ready`
  - result: `OK adapter-posture-visible`

## Risks
- This does not prove that every Codex host/build/environment supports the app-server thread-boundary path.
- This change only upgrades when machine-readable app-server schema evidence is present; weaker surfaces still degrade honestly.
- Runtime full-gate duration remains long; earlier timeout reports in this session were verification-window limits, not runtime regression evidence.

## Rollback
- Revert:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
  - `tests/runtime/test_codex_adapter.py`
  - the four updated product docs
  - this evidence file
- Re-run the verification commands above.
