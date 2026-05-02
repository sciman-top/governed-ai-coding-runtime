# 2026-05-02 Source/Target Drift Integration

## Rule
- Core principle: `source_target_drift_integration_before_sync`
- Risk: medium

## Basis
- Same-name managed files must not be blindly overwritten during one-click rollout.
- Project rule drift that can be structurally merged must update both the canonical source under `rules/projects/` and the deployed target copy.

## Commands
- `python -m unittest tests.runtime.test_agent_rule_sync tests.runtime.test_target_repo_governance_consistency tests.runtime.test_runtime_flow_preset tests.runtime.test_core_principles`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`

## Evidence
- `python -m py_compile scripts/sync-agent-rules.py scripts/apply-target-repo-governance.py scripts/verify-target-repo-governance-consistency.py scripts/verify-target-repo-rollout-contract.py scripts/verify-core-principles.py` passed.
- `python -m unittest tests.runtime.test_agent_rule_sync tests.runtime.test_target_repo_governance_consistency tests.runtime.test_runtime_flow_preset tests.runtime.test_core_principles tests.runtime.test_target_repo_rollout_contract` passed: 66 tests.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` passed: 95 test files, failures=0.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` passed.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` passed with existing `WARN codex-capability-degraded`.

## Rollback
- Revert changes to `scripts/sync-agent-rules.py`, `scripts/apply-target-repo-governance.py`, target governance verifiers, rollout contract, governance baseline, and core-principles policy/spec.
