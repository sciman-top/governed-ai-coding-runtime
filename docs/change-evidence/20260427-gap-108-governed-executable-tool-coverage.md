# 20260427 GAP-108 Governed Executable Tool Coverage Batch

## Goal
- Close `GAP-108` by moving executable tool families onto the governed containment and evidence surface.
- Preserve truthful boundaries: shell, git, and package-manager execution are supported; browser automation and MCP/tool-bridge families are declared but fail closed until separately implemented or waived.

## Implementation
- `session_bridge` now routes executable tool families through containment-aware governance before execution.
- Tool approval records preserve approved or rejected decisions when `execute_attachment_write` replays the request step before execution.
- Tool execution artifacts, handoff payloads, replay payloads, and response payloads now include:
  - `command_class`
  - `containment_profile`
  - approval decision/status
  - `verification_result`
  - rollback posture

## Runtime Evidence
- Shell:
  - Command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 -FlowMode daily -AttachmentRoot . -AttachmentRuntimeStateRoot "$env:LOCALAPPDATA\governed-ai-coding-runtime\gap-108-shell-loop" -Mode quick -TaskId gap-108-shell-loop -RunId gap-108-shell-loop -CommandId cmd-gap-108-shell-loop -RepoBindingId binding-governed-ai-coding-runtime -WriteTargetPath docs/change-evidence/gap-108-shell-loop-probe.txt -WriteTier medium -WriteToolName shell -WriteToolCommand "git status --short" -RollbackReference "git diff" -WriteContent "unused" -ExecuteWriteFlow -Json`
  - Result: `overall_status=pass`, `summary.closure_state=live_closure_ready`, `write_execute.execution_status=executed`, `write_execute.command_class=shell`, `write_execute.approval_status=approved`.
- Git:
  - Command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 -FlowMode daily -AttachmentRoot . -AttachmentRuntimeStateRoot "$env:LOCALAPPDATA\governed-ai-coding-runtime\gap-108-git-loop" -Mode quick -TaskId gap-108-git-loop -RunId gap-108-git-loop -CommandId cmd-gap-108-git-loop -RepoBindingId binding-governed-ai-coding-runtime -WriteTargetPath docs/change-evidence/gap-108-git-loop-probe.txt -WriteTier medium -WriteToolName git -WriteToolCommand "git status --short" -RollbackReference "git diff" -WriteContent "unused" -ExecuteWriteFlow -Json`
  - Result: `overall_status=pass`.
- Package manager:
  - Command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 -FlowMode daily -AttachmentRoot . -AttachmentRuntimeStateRoot "$env:LOCALAPPDATA\governed-ai-coding-runtime\gap-108-package-loop" -Mode quick -TaskId gap-108-package-loop -RunId gap-108-package-loop -CommandId cmd-gap-108-package-loop -RepoBindingId binding-governed-ai-coding-runtime -WriteTargetPath docs/change-evidence/gap-108-package-loop-probe.txt -WriteTier medium -WriteToolName package -WriteToolCommand "python -m pip list --disable-pip-version-check" -RollbackReference "pip uninstall <pkg>" -WriteContent "unused" -ExecuteWriteFlow -Json`
  - Result: `overall_status=pass`.

## Test Evidence
- `python -m unittest tests.runtime.test_tool_runner tests.runtime.test_session_bridge`
  - `Ran 64 tests ... OK`
- Added regression coverage for:
  - medium-tier executable tool approval preservation
  - containment metadata in execution artifacts
  - browser/MCP executable family fail-closed behavior

## Planning Updates
- `GAP-108` is marked complete in backlog and implementation plan.
- Roadmap and indexes now state `GAP-104..108` complete and `GAP-109..111` remaining.

## Risks And Boundaries
- This does not promote browser automation or MCP/tool-bridge execution to supported runtime execution. They are declared and fail closed.
- Complete hybrid final-state closure is still not certified. `GAP-109`, `GAP-110`, and `GAP-111` remain active.

## Rollback
- Revert the `GAP-108` change set.
- Remove machine-local evidence roots if needed:
  - `$env:LOCALAPPDATA\governed-ai-coding-runtime\gap-108-shell-loop`
  - `$env:LOCALAPPDATA\governed-ai-coding-runtime\gap-108-git-loop`
  - `$env:LOCALAPPDATA\governed-ai-coding-runtime\gap-108-package-loop`
