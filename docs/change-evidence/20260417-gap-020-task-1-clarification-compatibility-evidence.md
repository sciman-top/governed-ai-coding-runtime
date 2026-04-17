# 2026-04-17 GAP-020 Task 1 Clarification / Compatibility / Evidence Maturity

## Goal
- Land `Foundation / GAP-020 / Task 1`.
- Turn clarification policy, rollout posture, compatibility degrade behavior, and evidence quality into explicit contracts.

## Basis
- Execution source: `docs/plans/foundation-runtime-substrate-implementation-plan.md`, `Task 1`.
- Clarification semantics come from the trigger and reset rules already defined in `AGENTS.md`.
- Project gate order remains `build -> test -> contract/invariant -> hotspot`; this task only activates `test` and `contract/invariant`.

## Files Changed
- `docs/specs/clarification-protocol-spec.md`
- `docs/specs/evidence-bundle-spec.md`
- `docs/specs/agent-adapter-contract-spec.md`
- `docs/specs/repo-profile-spec.md`
- `schemas/jsonschema/clarification-protocol.schema.json`
- `schemas/jsonschema/evidence-bundle.schema.json`
- `schemas/jsonschema/agent-adapter-contract.schema.json`
- `schemas/jsonschema/repo-profile.schema.json`
- `schemas/examples/clarification-protocol/default-runtime.example.json`
- `schemas/examples/repo-profile/python-service.example.json`
- `schemas/examples/repo-profile/typescript-webapp.example.json`
- `schemas/catalog/schema-catalog.yaml`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/clarification.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/compatibility.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/evidence.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_profile.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/second_repo_pilot.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/trial_entrypoint.py`
- `tests/runtime/test_clarification.py`
- `tests/runtime/test_compatibility.py`
- `tests/runtime/test_evidence_timeline.py`
- `tests/runtime/test_repo_profile.py`

## Decisions Landed
- Clarification is now a first-class protocol with explicit trigger threshold, question cap, scenario set, reset semantics, and required audit fields.
- Repo profiles and adapter contracts can now declare rollout posture and compatibility signals instead of relying on prose-only intent.
- Compatibility helpers now distinguish `full_support`, `partial_support`, and `unsupported`, and resolve explicit degrade behavior to `observe`, `advisory`, or `blocked`.
- Evidence helpers now distinguish missing mandatory evidence from advisory-but-present verification outcomes.

## Verification Commands
1. `python -m unittest tests.runtime.test_clarification tests.runtime.test_compatibility tests.runtime.test_evidence_timeline -v`
2. `python -m unittest discover -s tests/runtime -p "test_*.py"`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
5. `git diff --check`

## Verification Result
- `tests.runtime.test_clarification/tests.runtime.test_compatibility/tests.runtime.test_evidence_timeline`: pass
- `python -m unittest discover -s tests/runtime -p "test_*.py"`: pass, `Ran 74 tests`
- `scripts/verify-repo.ps1 -Check Contract`: pass
  - `OK schema-json-parse`
  - `OK schema-example-validation`
  - `OK schema-catalog-pairing`
- `scripts/verify-repo.ps1 -Check All`: pass
  - `OK runtime-unittest`
  - `OK schema-json-parse`
  - `OK schema-example-validation`
  - `OK schema-catalog-pairing`
  - `OK active-markdown-links`
  - `OK backlog-yaml-ids`
  - `OK old-project-name-historical-only`
  - `OK powershell-parse`
  - `Ran 74 tests`
- `git diff --check`: pass with LF to CRLF normalization warnings only; no whitespace errors

## issue_id / clarification_mode
- `issue_id`: `GAP-020`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `bugfix`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Compatibility Notes
- Existing adapter declaration helpers were updated to emit rollout posture and compatibility signals so contract examples stay internally coherent.
- No external behavior was promoted to `enforced`; this task only makes the posture machine-readable.

## Gate Status
| gate | status | command | result | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|---|---|
| build | `gate_na` | `n/a` | not run | `GAP-021` owns first live build command | repo-wide `README/docs/roadmap/backlog` consistency still handled elsewhere | `docs/change-evidence/20260417-gap-020-task-1-clarification-compatibility-evidence.md` | `2026-05-31` |
| test | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | pass via full runtime unit suite | runtime contract helpers and tests are now extended for clarification/compatibility/evidence behavior | `python -m unittest discover -s tests/runtime -p "test_*.py"` | `docs/change-evidence/20260417-gap-020-task-1-clarification-compatibility-evidence.md` | `n/a` |
| contract/invariant | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | pass | schema/spec/example/catalog pairing remained consistent after adding the clarification asset family | schema JSON parse + example validation + catalog pairing | `docs/change-evidence/20260417-gap-020-task-1-clarification-compatibility-evidence.md` | `n/a` |
| hotspot | `gate_na` | `n/a` | not run | live doctor/hotspot command is still `GAP-021` scope | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` | `docs/change-evidence/20260417-gap-020-task-1-clarification-compatibility-evidence.md` | `2026-05-31` |

## Rollback
- Restore the modified `docs/specs/*`, `schemas/*`, `packages/contracts/*`, and `tests/runtime/*` files from git history for branch `feature/gap-020-task-1`.
- Remove the new clarification protocol spec/schema/example and this evidence file if the task is reverted.
