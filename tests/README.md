# Tests

Runtime, governance, and service-boundary tests live here.

## Canonical Entrypoints
Use the repository verifier first so Windows process-environment normalization happens before Python imports modules that may touch `asyncio`, subprocess APIs, or host-local state.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check RuntimeQuick
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

## What The Gates Cover
- `Runtime`
  - runtime contract tests under `tests/runtime/`
  - service-boundary tests under `tests/service/`
- `RuntimeQuick`
  - bounded inner-loop slice for target-governance speed-profile work
- `Contract`
  - reference-required changes, reference-basis enforcement, target-governance consistency, rollout contracts, dependency baseline, and other fail-closed invariants
- `All`
  - build, runtime, contract, doctor-adjacent integrity, docs, links, and script checks

## Notable Current Test Clusters
- host and adapter posture:
  - `test_codex_adapter.py`
  - `test_claude_code_adapter.py`
  - `test_codex_cockpit_policy_contract.py`
  - `test_agent_continuity.py`
- reference discipline and release hardening:
  - `test_reference_required_changes.py`
  - `test_reference_basis.py`
  - `test_preflight_ci_wiring.py`
- target-repo governance and speed:
  - `test_target_repo_governance_consistency.py`
  - `test_target_repo_rollout_contract.py`
  - `test_target_repo_speed_kpi.py`
  - `test_governance_gate_runner.py`
- operator and runtime read models:
  - `test_operator_ui.py`
  - `test_runtime_status.py`
  - `test_session_bridge.py`

## Direct Commands
Use direct unittest commands only when the current shell environment is already known-good:

```powershell
python -m unittest discover -s tests/runtime -p "test_*.py"
```

```powershell
python -m unittest discover -s tests/service -p "test_*.py"
```

For targeted current hardening checks:

```powershell
python -m unittest tests.runtime.test_reference_basis tests.runtime.test_preflight_ci_wiring -v
```

## Release-Style Closeout
When you need the same release-style closeout path that CI uses:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/governance/preflight.ps1 -DisableAutoCommit
```
