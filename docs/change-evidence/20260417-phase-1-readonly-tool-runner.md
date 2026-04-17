# 20260417 Phase 1 Read-Only Tool Runner

## Goal
Execute `GAP-005 Read-Only Governed Tool Runner` as a narrow runtime contract slice without executing real shell commands.

## Current Landing
- Runtime contract package: `packages/contracts/`
- Tool runner module: `packages/contracts/src/governed_ai_coding_runtime_contracts/tool_runner.py`
- Runtime tests: `tests/runtime/test_tool_runner.py`
- Verification entrypoint: `scripts/verify-repo.ps1 -Check Runtime`

## Implemented Slice
- `ToolRequest` models a governed read-only tool request.
- `validate_readonly_request` fail-closes when:
  - the tool is not in the repo profile allowlist
  - the side effect is not read-only
  - the target path is outside the repo profile read scope
- `run_readonly_session` validates a bounded list of read-only requests and returns an accepted summary.
- No real command execution, process spawning, network access, or filesystem mutation is implemented in this slice.

## TDD Evidence
```powershell
python -m unittest tests.runtime.test_tool_runner -v
python -m unittest discover -s tests/runtime -p "test_*.py" -v
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

## Observed Red/Green
- Initial tool runner tests failed because `tool_runner` did not exist.
- Bounded session test failed because `run_readonly_session` did not exist.
- Tests passed after adding the minimal read-only request validator and session summary.

## Verification Results
- `python -m unittest tests.runtime.test_tool_runner -v` -> pass
- `python -m unittest discover -s tests/runtime -p "test_*.py" -v` -> pass

## Gate Status
| gate | status | command | result | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|---|---|
| build | `gate_na` | `n/a` | not run | no buildable Python package or runtime service artifact exists yet | runtime unit tests plus repo verifier | `docs/change-evidence/20260417-phase-1-readonly-tool-runner.md` | `2026-05-31` |
| test | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | pass | Python runtime contract tests cover the read-only tool runner | direct `python -m unittest discover -s tests/runtime -p "test_*.py"` | `docs/change-evidence/20260417-phase-1-readonly-tool-runner.md` | `n/a` |
| contract/invariant | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | pass via `-Check All` | schema, examples, catalog, and paired specs remain the active contract baseline | full repository verification | `docs/change-evidence/20260417-phase-1-readonly-tool-runner.md` | `n/a` |
| hotspot | `gate_na` | `n/a` | not run | no runtime doctor or health entrypoint exists yet | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` | `docs/change-evidence/20260417-phase-1-readonly-tool-runner.md` | `2026-05-31` |

## Residual Risks
- The runner validates read-only requests but does not execute tools.
- The current path matcher is glob-based and intentionally minimal.
- Tool contract validation is implemented as runtime allowlist and side-effect checks, not full JSON Schema tool registry validation.
- Evidence timeline emission is deferred to `GAP-006`.
