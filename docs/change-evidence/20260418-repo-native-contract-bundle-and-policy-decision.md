# 20260418 Repo-Native Contract Bundle And PolicyDecision

## Change Basis
- User asked to continue automatically after clarifying whether historical completed-stage plans and landed code conflict with the hybrid final state.
- The next dependency-safe execution step was to implement `GAP-042` and `GAP-043` work from the strategy-alignment plan:
  - repo-native contract bundle architecture
  - `PolicyDecision` contract
- Landing point: architecture docs, spec/schema/catalog, Python contract module, and runtime tests.
- Target destination: make the hybrid final-state boundary and policy interface explicit without changing unrelated runtime behavior.
- Active rule path: `D:\OneDrive\CODE\governed-ai-coding-runtime\AGENTS.md`, carrying `GlobalUser/AGENTS.md v9.39`.
- Clarification trace: `issue_id=gap-042-gap-043-auto-continue`, `attempt_count=1`, `clarification_mode=direct_fix`, `clarification_scenario=n/a`, `clarification_questions=[]`, `clarification_answers=[]`.

## Files Changed
- Added `docs/architecture/repo-native-contract-bundle.md`
- Added `docs/specs/policy-decision-spec.md`
- Added `schemas/jsonschema/policy-decision.schema.json`
- Added `packages/contracts/src/governed_ai_coding_runtime_contracts/policy_decision.py`
- Added `tests/runtime/test_policy_decision.py`
- Updated `docs/architecture/README.md`
- Updated `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
- Updated `docs/README.md`
- Updated `docs/specs/README.md`
- Updated `schemas/catalog/schema-catalog.yaml`
- Updated `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
- Updated `docs/change-evidence/README.md`

## Task 4 Summary
- Added a dedicated architecture document for the repo-native contract bundle.
- Made the bundle explicit as an attachment and packaging boundary, not a replacement for `docs/`, `schemas/`, or `packages/contracts/`.
- Documented source-of-truth inputs, runtime bundle outputs, repo-local versus machine-local placement, and local/CI same-contract consumption.
- Updated the architecture index and target architecture so the bundle is referenced as a stable boundary document.

## Task 5 Summary
- Added `PolicyDecision` as a first-class spec and JSON Schema.
- Added a Python contract module with:
  - `PolicyDecision`
  - `build_policy_decision(...)`
  - `is_executable_action(...)`
- Enforced minimal semantics:
  - `allow` is executable and cannot carry approval intent
  - `escalate` requires an approval reference and is not executable
  - `deny` fails closed, is not executable, and requires a remediation hint
- Exported the contract from the package root.

## TDD Evidence
Red:

```powershell
python -m unittest tests.runtime.test_policy_decision -v
```

- Exit code: `1`
- Key output: `ModuleNotFoundError: No module named 'governed_ai_coding_runtime_contracts.policy_decision'`

Green:

```powershell
python -m unittest tests.runtime.test_policy_decision -v
```

- Exit code: `0`
- Key output: `Ran 6 tests`, `OK`

## Verification
### Docs Gate
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
```

- Exit code: `0`
- Key output: `OK active-markdown-links`, `OK backlog-yaml-ids`, `OK old-project-name-historical-only`

### Targeted Gates
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

- Exit code: `0`
- Key output: `OK runtime-unittest`, `Ran 124 tests`, `OK`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

- Exit code: `0`
- Key output: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`

### Full Gate Order
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

- Exit code: `0`
- Key output: `OK python-bytecode`, `OK python-import`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

- Exit code: `0`
- Key output: `OK runtime-status-surface`, `OK maintenance-policy-visible`, `OK adapter-posture-visible`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

- Exit code: `0`
- Key output: `OK runtime-build`, `OK runtime-unittest`, `OK schema-catalog-pairing`, `OK runtime-doctor`, `OK active-markdown-links`, `OK issue-seeding-render`, `Ran 124 tests`, `OK`

```powershell
git diff --check
```

- Exit code: `0`
- Key output: no whitespace errors; line-ending warnings only

## Risks
- `PolicyDecision` is intentionally local and minimal; it is not yet wired into session bridge or write-side execution paths.
- The new bundle doc defines boundaries but does not yet materialize bundle generation or binding behavior.
- Follow-on work still needs `GAP-044` before broad adapter expansion hardens around the new interface.

## Rollback
- Remove `docs/architecture/repo-native-contract-bundle.md`.
- Remove `docs/specs/policy-decision-spec.md`, `schemas/jsonschema/policy-decision.schema.json`, `packages/contracts/src/governed_ai_coding_runtime_contracts/policy_decision.py`, and `tests/runtime/test_policy_decision.py`.
- Revert catalog, index, and package-root export updates.
- Remove this evidence file and its index entry.
