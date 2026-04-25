# 20260425 Target Repo Problem Trace Retention Hardening

## Goal
- Strengthen target-repo AI coding problem traces so this repo can discover runtime/governance defects exposed in real target coding loops.
- Make target-repo evidence retention cleanup easier to audit before deletion.

## Clarification Trace
- `issue_id=target-repo-problem-trace-retention-hardening`
- `attempt_count=1`
- `clarification_mode=direct_fix`
- `clarification_scenario=bugfix`
- `clarification_questions=[]`
- `clarification_answers=[]`

## Changes
1. `scripts/runtime-check.ps1`
   - Added `problem_trace.problem_kind` for coarse routing across target repo contract, gate, write policy, write execution, runtime status, runtime doctor, and runtime contract failures.
   - Added `problem_trace.evidence_refs` and `problem_trace.target_context` so a single problem trace is reusable without manually joining summary/live-loop fields.
   - Added fallback `failure_reason` synthesis when a failing step has no parseable payload.
2. `packages/contracts/src/governed_ai_coding_runtime_contracts/target_repo_speed_kpi.py`
   - Added `problem_signature_counts` for selected-window aggregation.
   - Added `latest_problem_evidence_ref` so the latest problem record points directly to supporting evidence when available.
3. `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
   - Fixed Windows Codex capability probes so controlled `codex` probe commands run through `ComSpec` when the executable is a command shim instead of a direct `.exe`.
   - This repaired a live `WARN codex-capability-blocked` false negative even though `codex --version` worked from PowerShell.
4. `schemas/jsonschema/target-repo-speed-kpi.schema.json`
   - Added optional schema fields for the new KPI read-model values without making historical snapshots invalid.
5. `scripts/prune-target-repo-runs.py`
   - Added `retention_policy` to the cleanup report.
   - Added per-flow cleanup rows so `onboard` and `daily` retention effects are visible in dry-run and apply modes.
6. Tests and examples
   - Updated runtime-check, KPI, prune, spec, and example coverage for the expanded fields.

## Verification
1. Runtime-check targeted test
   - Command: `python -m unittest tests.runtime.test_attached_repo_e2e`
   - Result: `Ran 5 tests ... OK`
2. KPI targeted test
   - Command: `python -m unittest tests.runtime.test_target_repo_speed_kpi`
   - Result: `Ran 3 tests ... OK`
3. Prune targeted test
   - Command: `python -m unittest tests.runtime.test_prune_target_repo_runs`
   - Result: `Ran 2 tests ... OK`
4. Codex adapter targeted test
   - Command: `python -m unittest tests.runtime.test_codex_adapter`
   - Result: `Ran 21 tests ... OK`
5. Combined targeted test
   - Command: `python -m unittest tests.runtime.test_attached_repo_e2e tests.runtime.test_target_repo_speed_kpi tests.runtime.test_prune_target_repo_runs`
   - Result: `Ran 10 tests ... OK`
6. Build gate
   - Command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - Key output: `OK python-bytecode`, `OK python-import`
7. Runtime test gate
   - Command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - Key output: `OK runtime-unittest`, `OK runtime-service-parity`, `Ran 378 tests ... OK (skipped=2)`, `Ran 5 tests ... OK`
8. Contract/invariant gate
   - Command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - Key output: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`, `OK dependency-baseline`, `OK target-repo-rollout-contract`, `OK target-repo-governance-consistency`
9. Hotspot gate
   - Command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
   - Key output: `OK codex-capability-ready`, `OK adapter-posture-visible`

## Risks
- `problem_trace` and KPI outputs are additive JSON changes. Consumers with strict field allowlists should allow the new fields.
- Cleanup behavior is unchanged; only reporting is expanded.
- Historical target-repo run evidence will not backfill the new fields, but KPI inference remains backward compatible.
- Windows Codex probing now uses shell execution for non-`.exe` command shims. The command surface is controlled by runtime probe code, not arbitrary target-repo input.

## Rollback
- `git checkout -- scripts/runtime-check.ps1 scripts/prune-target-repo-runs.py`
- `git checkout -- packages/contracts/src/governed_ai_coding_runtime_contracts/target_repo_speed_kpi.py packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
- `git checkout -- docs/specs/target-repo-speed-kpi-spec.md schemas/jsonschema/target-repo-speed-kpi.schema.json schemas/examples/target-repo-speed-kpi/latest.example.json`
- `git checkout -- tests/runtime/test_attached_repo_e2e.py tests/runtime/test_target_repo_speed_kpi.py tests/runtime/test_prune_target_repo_runs.py tests/runtime/test_codex_adapter.py`
- `git checkout -- docs/change-evidence/20260425-target-repo-problem-trace-retention-hardening.md docs/change-evidence/README.md`
