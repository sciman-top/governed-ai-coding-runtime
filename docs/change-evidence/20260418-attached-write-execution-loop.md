# 20260418 Attached Write Execution Loop

## Purpose
Close the first practical write loop for attached target repos: write governance -> approval decision -> controlled write execution.

## Basis
- `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_governance.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_execution.py`
- `scripts/run-governed-task.py`
- `tests/runtime/test_attached_write_execution.py`
- `tests/runtime/test_run_governed_task_cli.py`
- `docs/quickstart/use-with-existing-repo.md`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`

## Change
- Persisted escalated approval requests under attachment runtime state:
  - `<attachment_runtime_state_root>/approvals/<approval_id>.json`
- Added approval decision API:
  - `decide_attached_write_request(...)`
- Added controlled write execution API:
  - `execute_attached_write_request(...)`
  - supports `write_file` and `append_file`
  - enforces path policy and approval requirement for medium/high tiers
- Added CLI commands:
  - `decide-attachment-write`
  - `execute-attachment-write`
- Added bilingual quickstart commands for the new loop.

## Verification
1. `python -m unittest tests.runtime.test_attached_write_execution tests.runtime.test_attached_write_governance tests.runtime.test_run_governed_task_cli tests.runtime.test_write_tool_runner -v`
   - exit `0`
2. `python scripts/run-governed-task.py govern-attachment-write ... --tool-name write_file --tier medium --json`
   - returns `escalate` and `approval_pending`
3. `python scripts/run-governed-task.py decide-attachment-write ... --decision approve --json`
   - approval becomes `approved`
4. `python scripts/run-governed-task.py execute-attachment-write ... --tool-name write_file --approval-id ... --json`
   - returns `execution_status = executed`
5. Probe content verified and probe file removed from target repo after run.

## Rollback
- Remove `attached_write_execution.py`
- Remove new CLI commands from `run-governed-task.py`
- Revert approval-persistence changes in `attached_write_governance.py`
- Revert quickstart additions

