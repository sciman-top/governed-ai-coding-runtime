# 20260420 Readonly Path Traversal Guard

## Change Basis
- Review identified a correctness and security bug in readonly request validation: `tool_runner._is_allowed_path` accepted traversal paths like `docs/../../secrets/prod.env` when the prefix matched an allow scope such as `docs/**`.
- The issue is real and reproducible on current baseline using `validate_readonly_request` with the governed runtime example repo profile.
- Root cause: path policy matching used glob checks only and did not reject `..` segments before evaluating allow/block rules.
- Active rule path: `D:\OneDrive\CODE\governed-ai-coding-runtime\AGENTS.md`, carrying `GlobalUser/AGENTS.md v9.39`.
- Clarification trace: `issue_id=readonly-path-traversal-guard`, `attempt_count=1`, `clarification_mode=direct_fix`, `clarification_scenario=n/a`, `clarification_questions=[]`, `clarification_answers=[]`.

## Files Changed
- Updated `packages/contracts/src/governed_ai_coding_runtime_contracts/tool_runner.py`
- Updated `tests/runtime/test_tool_runner.py`
- Updated `docs/change-evidence/README.md`
- Added `docs/change-evidence/20260420-readonly-path-traversal-guard.md`

## Summary
- Added an explicit traversal guard in readonly path validation: reject any target path containing `..` segments.
- Added regression coverage that asserts traversal is denied even when the path prefix matches an allowed read scope.
- Preserved existing allow/block glob behavior for normal repo-relative paths.

## Verification
```powershell
python -m unittest tests.runtime.test_tool_runner -v
```
- Exit code: `0`
- Key output: `test_path_traversal_fails_closed_even_when_prefix_matches_allow_scope ... ok`

```powershell
python -m unittest tests.runtime.test_tool_runner_governance -v
```
- Exit code: `0`
- Key output: `Ran 4 tests`, `OK`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```
- Exit code: `0`
- Key output: `OK runtime-unittest`, `Ran 242 tests`

## Risks
- This change intentionally tightens readonly path acceptance. Any existing caller that relied on traversal-like paths will now fail closed.
- No contract/schema format changes were introduced.

## Rollback
- Revert `packages/contracts/src/governed_ai_coding_runtime_contracts/tool_runner.py` to remove the traversal guard.
- Revert `tests/runtime/test_tool_runner.py` to remove the traversal regression test.
- Remove this evidence file and index entry if the change is withdrawn.
