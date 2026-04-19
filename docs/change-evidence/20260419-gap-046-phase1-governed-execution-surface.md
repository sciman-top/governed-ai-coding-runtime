# 20260419 GAP-046 Phase1 Governed Execution Surface

## Goal
- Close `GAP-046` Phase1 execution-surface gaps with executable evidence.
- Move session bridge gate flow from plan-only posture to runtime-managed lifecycle.
- Unify gate/write/approval/evidence/handoff identity on stable `execution_id` + `continuation_id`.
- Add bounded governed tool execution (`shell` / `git` / `package`) under the same approval and evidence model.
- Prove one attached-repo end-to-end loop can execute with real refs.

## Scope
- Task 1: session bridge gate lifecycle execution and `--plan-only` compatibility.
- Task 2: live write-flow identity binding and high-risk fail-closed approval handling.
- Task 3: bounded tool-governance and tool execution surface.
- Task 4: attached-repo E2E loop via runtime-check flow with approval + execution + handoff + replay refs.

## Key Changes
1. Session bridge:
   - `run_quick_gate` / `run_full_gate` now execute runtime-managed verification by default.
   - `request-gate --plan-only` preserves executable-plan output mode.
   - write/gate/approval/evidence/handoff payloads now carry stable identity fields.
2. Attached write flow:
   - added high-risk fail-closed behavior when approval is missing or stale.
   - approval records now include request/decision timestamps.
3. Governed tool path:
   - added bounded governance for `shell`, `git`, `package`.
   - added execution path with explicit allow/escalate/deny semantics and artifact refs.
4. Runtime scripts:
   - `runtime-check.ps1` can now execute full write flow (`govern -> decide -> execute`) with `-ExecuteWriteFlow`.
   - `runtime-flow.ps1` and `runtime-flow-preset.ps1` now forward write-flow execution controls.
5. Tests and docs:
   - added `tests/runtime/test_tool_runner_governance.py`.
   - added `tests/runtime/test_attached_repo_e2e.py`.
   - updated session bridge, write governance, and quickstart docs (EN/ZH).

## Commands
1. `python -m unittest tests.runtime.test_session_bridge -v`
2. `python -m unittest tests.runtime.test_attached_write_governance tests.runtime.test_attached_write_execution tests.runtime.test_session_bridge -v`
3. `python -m unittest tests.runtime.test_tool_runner tests.runtime.test_tool_runner_governance tests.runtime.test_write_tool_runner tests.runtime.test_session_bridge tests.runtime.test_run_governed_task_cli -v`
4. `python -m unittest tests.runtime.test_attached_repo_e2e -v`
5. `python scripts/session-bridge.py --help`
6. `python scripts/session-bridge.py request-gate --help`
7. `python scripts/run-governed-task.py govern-attachment-write --help`
8. `python scripts/run-governed-task.py decide-attachment-write --help`
9. `python scripts/run-governed-task.py execute-attachment-write --help`
10. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
11. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
12. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
13. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
14. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
15. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Verification Result
- Session bridge tests: pass (`test_session_bridge` full suite).
- Attached write tests: pass (including high-risk missing/stale approval fail-closed paths).
- Tool governance tests: pass (`test_tool_runner_governance`).
- Attached E2E test: pass (`test_attached_repo_e2e`).
- Repository gates: `build`, `runtime`, `contract`, `docs`, `scripts`, `doctor` all pass.

## E2E Evidence Shape
- Attached E2E path now emits real:
  - `execution_id`
  - `continuation_id`
  - `approval_ref`
  - `artifact_ref` / `artifact_refs`
  - `handoff_ref`
  - `replay_ref`

## Risk
- Medium:
  - execution surface changed from plan-only to executable by default for gate requests.
  - bounded tool execution introduces new policy branches that require future hardening in Task5+.
- Mitigation:
  - `--plan-only` fallback preserved.
  - explicit deny/escalate outputs remain fail-closed and auditable.

## Rollback
- Revert modified files in:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/`
  - `scripts/`
  - `tests/runtime/`
  - `docs/product/`
  - `docs/quickstart/`
  - `docs/specs/`
  - `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- Or revert this commit as one unit.
