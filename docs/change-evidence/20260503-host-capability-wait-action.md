# 2026-05-03 Host Capability Wait Action

## Scope
- Rule IDs: `R1`, `R3`, `R4`, `R6`, `R8`, `E4`
- Risk: low-to-medium; selector/operator control-flow and product claim wording change, no target-repo mutation.
- Current landing: `scripts/select-next-work.py` stale evidence branch and operator preflight guards.
- Target home: autonomous next-work selector contract, operator UI/status surfaces, tests, and product evidence.
- Rollback: `git revert <commit>` for this change set.

## Problem
The latest target-run evidence is fresh but still degraded because current Codex host capability evidence remains at `process_bridge` instead of `native_attach`. After `GAP-140..143`, the selector only had one stale evidence action, `refresh_evidence_first`, so a completed refresh could still produce the same degraded evidence and create a misleading repeat-refresh loop.

The intended behavior is narrower:
- ordinary stale evidence still chooses `refresh_evidence_first`;
- fresh evidence that proves bounded host-capability degradation keeps implementation and LTP work blocked;
- when the bounded defer candidate and recovery guard exist, selector output becomes `wait_for_host_capability_recovery`.

## Pre-Change Drift Review
- `pre_change_review`: checked selector policy, runtime selector, recovery posture verifier, operator preflight, operator UI server, operator UI contract labels, backlog, claim catalog, and change-evidence index.
- `control_repo_manifest_and_rule_sources`: no rule-family source edits in this change; project hard gates remain the authority.
- `user_level_deployed_rule_files`: no deployed user-level rule edits in this change.
- `target_repo_deployed_rule_files`: no target-repo rule sync or target-repo mutation in this change.
- `target_repo_gate_scripts_and_ci`: operator and selector scripts only; target-repo gate scripts were not changed.
- `target_repo_repo_profile`: no target profile edits.
- `target_repo_readme_and_operator_docs`: product claim/backlog wording updated to avoid stale `refresh_evidence_first` completion wording.
- `current_official_tool_loading_docs`: no rule-loading behavior changed.
- `drift-integration decision`: integrate the stale selector contract in control repo before any future rule sync.

## Local Host Diagnostics
- `codex --version`: `codex-cli 0.125.0`
- `codex --help`: top-level commands include `exec`, `review`, `login`, `logout`, `mcp`, `plugin`, `app-server`, `app`, `completion`, `sandbox`, `debug`, `apply`, `resume`, `fork`, `cloud`, `exec-server`, and `features`; no top-level `status` command is advertised.
- `codex status`: exit code `1`, key output `Error: stdin is not a terminal`.
- `codex features list`: `remote_control` is `false`; no native attach recovery signal was available from this command surface.
- `codex debug prompt-input "probe"`: rendered prompt input only; it did not provide a session/status/native attach handshake.

## Changes
- Added selector field `evidence_blocker`.
- Added selector action `wait_for_host_capability_recovery`.
- Kept `evidence_state=stale` while degraded target runs remain present.
- Limited the new wait action to the case where the only stale reason is `host_capability_degraded` and bounded defer evidence exists.
- Kept generic stale evidence on `refresh_evidence_first`.
- Blocked `ApplyAllFeatures` and `EvolutionMaterialize` while waiting for host recovery.
- Added Operator UI labels/descriptions for the new action.
- Updated tests, backlog wording, claim wording, and evidence recovery posture verification.

## Verification
- `python scripts/select-next-work.py --as-of 2026-05-03`
  - `status=pass`
  - `next_action=wait_for_host_capability_recovery`
  - `evidence_state=stale`
  - `evidence_blocker=host_capability_degraded_bounded_defer`
  - `ltp_decision=defer_all`
- `python scripts/verify-evidence-recovery-posture.py --as-of 2026-05-03`
  - `status=pass`
  - selector, target-run attention, and effect report recovery guard agree.
- `python -m unittest tests.runtime.test_autonomous_next_work_selection tests.runtime.test_evidence_recovery_posture tests.runtime.test_operator_entrypoint tests.runtime.test_operator_ui tests.runtime.test_codex_adapter tests.runtime.test_host_feedback_summary`
  - `Ran 72 tests`
  - `OK`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - `OK python-bytecode`
  - `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `Completed 102 test files`
  - `failures=0`
  - `OK runtime-unittest`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - `OK pre-change-review`
  - `OK functional-effectiveness`
  - all contract checks passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - `OK gate-command-build`
  - `OK gate-command-test`
  - `OK gate-command-contract`
  - `OK gate-command-doctor`
  - `WARN codex-capability-degraded` remains expected host-layer evidence, not a repository gate failure.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - `OK evidence-recovery-posture`
  - `OK autonomous-next-work-selection`
  - `OK claim-drift-sentinel`
  - `OK claim-evidence-freshness`
