# 20260418 Attached Write Governance Gate

## Purpose
Add a practical governance gate for attached target-repo write requests before real file mutation execution.

## Basis
- `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_governance.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/write_tool_runner.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/workspace.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/tool_runner.py`
- `scripts/run-governed-task.py`
- `tests/runtime/test_attached_write_governance.py`
- `tests/runtime/test_write_tool_runner.py`
- `tests/runtime/test_run_governed_task_cli.py`
- `docs/quickstart/use-with-existing-repo.md`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`

## Change
- Added `govern_attached_write_request(...)` to evaluate attached target-repo write requests through:
  - light-pack validation
  - repo-profile loading
  - write policy resolution
  - path policy checks
  - approval ledger routing
  - PolicyDecision normalization (`allow` / `escalate` / `deny`)
- Added CLI surface:
  - `python scripts/run-governed-task.py govern-attachment-write ...`
- Hardened nested path matching:
  - normalized path policy matching uses `fnmatch` semantics so patterns such as `src/**` consistently match nested file paths
- Updated existing-repo quickstarts (English and Chinese) with the write-governance command.

## Verification
1. `python -m unittest tests.runtime.test_write_tool_runner tests.runtime.test_attached_write_governance tests.runtime.test_run_governed_task_cli -v`
   - exit `0`
2. `python scripts/run-governed-task.py govern-attachment-write --help`
   - exit `0`
3. `python scripts/run-governed-task.py govern-attachment-write --attachment-root "D:\OneDrive\CODE\ClassroomToolkit" --attachment-runtime-state-root "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" --task-id "task-classroom-write-003" --tool-name "apply_patch" --target-path "src/ClassroomToolkit.App/MainWindow.ZOrder.cs" --tier "low" --rollback-reference "git diff -- src/ClassroomToolkit.App/MainWindow.ZOrder.cs" --json`
   - exit `0`
   - `governance_status = allowed`
   - `policy_decision.status = allow`
4. `python scripts/run-governed-task.py govern-attachment-write --attachment-root "D:\OneDrive\CODE\ClassroomToolkit" --attachment-runtime-state-root "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" --task-id "task-classroom-write-004" --tool-name "apply_patch" --target-path "src/ClassroomToolkit.App/MainWindow.ZOrder.cs" --tier "medium" --rollback-reference "git diff -- src/ClassroomToolkit.App/MainWindow.ZOrder.cs" --json`
   - exit `0`
   - `governance_status = paused`
   - `policy_decision.status = escalate`
   - `task_state = approval_pending`
5. `python scripts/run-governed-task.py govern-attachment-write --attachment-root "D:\OneDrive\CODE\ClassroomToolkit" --attachment-runtime-state-root "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" --task-id "task-classroom-write-005" --tool-name "apply_patch" --target-path "secrets/prod.env" --tier "low" --rollback-reference "git diff -- secrets/prod.env" --json`
   - exit `0`
   - `governance_status = denied`
   - `policy_decision.status = deny`
6. `python scripts/attach-target-repo.py ... --contract-command "dotnet test ... --filter \"A|B|C\""` (PowerShell)
   - first attempt failed because `|` inside the quoted value was parsed as pipeline tokens by PowerShell
   - mitigation: use a simplified no-filter contract command for attach, and document single-quote wrapping guidance in both quickstarts

## Rollback
- Remove `attached_write_governance.py`
- Remove `govern-attachment-write` CLI surface
- Revert path-matching changes in `workspace.py` and `tool_runner.py`
- Revert quickstart command additions
