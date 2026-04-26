# 20260427 GAP-096 Transition Stack Convergence

## Goal
Close `GAP-096 Service-Shaped Transition Stack Convergence Gate` by turning the staged stack recommendation into a mechanical contract.

## Scope
- `docs/architecture/transition-stack-convergence-policy.json`
- `docs/specs/transition-stack-convergence-spec.md`
- `schemas/jsonschema/transition-stack-convergence.schema.json`
- `schemas/examples/transition-stack-convergence/default-runtime.example.json`
- `schemas/catalog/schema-catalog.yaml`
- `scripts/verify-transition-stack-convergence.py`
- `scripts/verify-repo.ps1`
- `tests/runtime/test_transition_stack_convergence.py`
- architecture and planning status docs

## Change Summary
- Added a machine-readable transition-stack convergence policy for `FastAPI`, `Pydantic`, PostgreSQL adapter modules, and external `OpenTelemetry`.
- Added a verifier that scans Python imports and fails closed when transition-stack modules appear without an active boundary.
- Kept local filesystem/SQLite-style operation valid for single-machine use.
- Preserved JSON Schema as the cross-tool source of truth while allowing future boundary-scoped typed validation.
- Required CLI/API parity tests, tracing hook refs, and wrapper drift guard refs to remain present.
- Integrated the verifier into `verify-repo.ps1 -Check Contract`.

## Verification
Commands:
- `python scripts/verify-transition-stack-convergence.py`
- `python -m unittest tests.runtime.test_transition_stack_convergence`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- `git diff --check`

Key output:
- transition verifier: `"status": "pass"`, `"observed_modules": []`, watched modules include `fastapi`, `pydantic`, `psycopg`, `psycopg2`, `asyncpg`, `sqlalchemy`, and `opentelemetry`; wrapper drift tokens are empty
- targeted tests: `Ran 4 tests ... OK`
- build: `OK python-bytecode`, `OK python-import`, `OK runtime-build`
- runtime: `Ran 422 tests ... OK (skipped=5)`, `Ran 10 tests ... OK`, `OK runtime-service-wrapper-drift-guard`
- contract: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`, `OK dependency-baseline`, `OK transition-stack-convergence`, `OK target-repo-rollout-contract`, `OK target-repo-governance-consistency`, `OK target-repo-powershell-policy`, `OK agent-rule-sync`
- doctor: `OK runtime-status-surface`, `OK maintenance-policy-visible`, `OK codex-capability-ready`, `OK adapter-posture-visible`
- docs/scripts: `OK active-markdown-links`, `OK backlog-yaml-ids`, `OK issue-seeding-render`

## Risk
- No new runtime dependency is introduced.
- The main behavior change is stricter contract gating: future transition-stack imports must be explicitly classified and evidence-backed.

## Rollback
Use git to revert the transition-stack policy, spec/schema/example, verifier, tests, `verify-repo.ps1` integration, and this evidence file.
