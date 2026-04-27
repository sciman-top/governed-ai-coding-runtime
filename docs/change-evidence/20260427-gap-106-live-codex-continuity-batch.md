# 20260427 GAP-106 Live Codex Continuity Batch

## Goal
- Close `GAP-106` by replacing posture-only Codex evidence with a canonical runtime-owned live continuity loop.
- Preserve truthful scope: this validates the current host's `codex exec resume` command surface and runtime continuity chain; it does not claim deeper native session introspection beyond the available Codex CLI surface.

## Changes
- `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
  - `build_codex_adapter_trial_result(...)` now accepts a real `CodexSurfaceProbe` so trial identity, `probe_source`, tier, and handshake posture can come from live probe evidence instead of copied boolean flags.
- `scripts/run-codex-adapter-trial.py`
  - passes `--probe-live` probe data into the trial result builder; live trial output now reports top-level `probe_source=live_probe`.
- `scripts/runtime-check.ps1`
  - hardened strict-mode optional field/object reads so degraded or denied payloads classify as structured runtime problems instead of crashing PowerShell.
- `tests/runtime/test_codex_adapter.py`
  - added coverage proving live-probe trial results preserve `live_session_id`, `live_resume_id`, `native_attach`, and `probe_source=live_probe`.
- Planning docs now mark `GAP-106` complete and keep `GAP-107..111` active.

## Evidence
- Live Codex probe:
  - command: `python scripts/run-codex-adapter-trial.py --repo-id self-runtime --task-id gap-106-live-probe --binding-id self-runtime-binding --run-id gap-106-live-probe --probe-live`
  - result: `adapter_tier=native_attach`, `flow_kind=live_attach`, `probe_source=live_probe`, `version=codex-cli 0.125.0`
  - note: `live_session_id` and `live_resume_id` are not exposed by the current CLI probe; runtime handshake therefore uses deterministic continuity ids and records the posture reason.
- Rejected non-canonical entrypoint trial:
  - command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-check.ps1 ... -EntrypointId runtime-check ... -ExecuteWriteFlow -Json`
  - result: correctly classified as `entrypoint_policy_denied` / `request_gate_failed` when targeted enforcement blocked non-canonical `runtime-check`.
- Canonical live continuity loop:
  - command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 -FlowMode daily -AttachmentRoot . -AttachmentRuntimeStateRoot "$env:LOCALAPPDATA\governed-ai-coding-runtime\gap-106-live-loop" -Mode quick -TaskId gap-106-live-loop -RunId gap-106-live-loop -CommandId cmd-gap-106-live-loop -RepoBindingId binding-governed-ai-coding-runtime -WriteTargetPath docs/change-evidence/gap-106-live-loop-probe.txt -WriteTier medium -WriteToolName write_file -RollbackReference "git checkout -- docs/change-evidence/gap-106-live-loop-probe.txt" -WriteContent "GAP-106 live loop probe executed on 2026-04-27." -ExecuteWriteFlow -Json`
  - result: `overall_status=pass`, `summary.closure_state=live_closure_ready`, `summary.flow_kind=live_attach`, `entrypoint_drift=false`, `entrypoint_blocked=false`
  - continuity: `session_identity_continuity=true`, `resume_identity_continuity=true`, `continuation_continuity=true`, `evidence_linkage_complete=true`
  - medium-risk write path: `governance_status=paused`, `policy_status=escalate`, approval decided as `approved`, `execution_status=executed`, `write_tier=medium`
  - linkage: runtime refs include request adapter events, verification output, write execution artifact, adapter events, handoff package, and replay package.

## Verification
- `python -m unittest tests.runtime.test_codex_adapter`
  - `Ran 22 tests ... OK`
- `python -m unittest tests.runtime.test_attached_repo_e2e tests.runtime.test_codex_adapter`
  - `Ran 27 tests ... OK`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 ... -ExecuteWriteFlow -Json`
  - `overall_status=pass`

## Risks And Boundaries
- The current Codex CLI surface supports `codex exec resume`; `codex status` is unavailable. `GAP-106` therefore proves runtime-owned continuity and evidence linkage through the available live launch/resume posture, not full native interactive session introspection.
- `GAP-107..111` remain active. This commit does not certify non-Codex parity, broader governed tool coverage, data/provenance release readiness, operations soak, or complete final-state closure.

## Rollback
- Revert this change set and remove `docs/change-evidence/gap-106-live-loop-probe.txt`.
- Delete the machine-local evidence root if needed: `$env:LOCALAPPDATA\governed-ai-coding-runtime\gap-106-live-loop`.
