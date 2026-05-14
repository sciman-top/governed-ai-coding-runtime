# 2026-05-15 Codex Hot Switch Plan API Service Boundary

- rule_id: `local-codex-cockpit-auth-interop`
- risk: low documentation and contract-test hardening
- landing: `docs/plans/codex-cli-continuity-and-hot-switch-plan.md`, `docs/plans/README.md`, `tests/runtime/test_codex_cockpit_policy_contract.py`
- destination: keep Cockpit Tools automatic switching, Codex batch quota refresh, and Cockpit Codex API service as disabled-by-default operator modes unless fresh listener-scope and projection evidence exists
- rollback: revert this evidence file plus the plan/index/test changes in the same commit

## Decision

Do not create a new roadmap `GAP` item for the Cockpit API service risk. The existing `Codex CLI Continuity And Hot-Switch Plan` remains an owner-directed scoped spike, not a heavy product mainline.

Update the implementation plan instead, because the newer live evidence changed the safe proxy boundary:

- Cockpit Tools' `127.0.0.1:2876/v1` Codex API service is not the default proxy implementation.
- Cockpit API service is a temporary operator mode only.
- Before Codex CLI/App is pointed at Cockpit API service, verify listener scope and host firewall posture.
- Default posture stays: automatic switching off, Codex batch quota refresh off, Cockpit API service off.

## Planned Verification

- `python -m unittest tests.runtime.test_codex_cockpit_policy_contract` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` -> pass with expected `codex-capability-degraded` warning
- `git diff --check` -> pass
