# Use With An Existing Repo

## Short Answer
Yes, but with the current product boundary.

Today you can use this runtime against an existing repository such as `D:\OneDrive\CODE\ClassroomToolkit` as a machine-local governance sidecar:
- generate or validate a repo-local light pack under `.governed-ai/`
- keep mutable runtime state machine-local
- inspect attachment posture through `status` and `doctor`
- call the local session bridge for posture and gate-plan requests
- run Codex smoke-trial and multi-repo trial flows against the attached posture

What you do **not** have yet is a fully runtime-owned direct Codex coding path for real high-risk writes inside that target repository.

## Recommended Flow

### 1. Attach The Target Repo
From this repository root:

```powershell
python scripts/attach-target-repo.py `
  --target-repo "D:\OneDrive\CODE\ClassroomToolkit" `
  --runtime-state-root "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" `
  --repo-id "classroomtoolkit" `
  --display-name "ClassroomToolkit" `
  --primary-language "csharp" `
  --build-command "dotnet build ClassroomToolkit.sln -c Debug" `
  --test-command "dotnet test tests/ClassroomToolkit.Tests/ClassroomToolkit.Tests.csproj -c Debug" `
  --contract-command "dotnet test tests/ClassroomToolkit.Tests/ClassroomToolkit.Tests.csproj -c Debug --filter \"FullyQualifiedName~ArchitectureDependencyTests|FullyQualifiedName~InteropHookLifecycleContractTests|FullyQualifiedName~InteropHookEventDispatchContractTests|FullyQualifiedName~GlobalHookServiceLifecycleContractTests|FullyQualifiedName~CrossPageDisplayLifecycleContractTests\"" `
  --adapter-preference "process_bridge"
```

PowerShell note:
- if your `--contract-command` contains `|`, wrap the whole value in single quotes, or use a no-filter contract command first and narrow it later.

This creates or validates:

```text
D:\OneDrive\CODE\ClassroomToolkit\.governed-ai\repo-profile.json
D:\OneDrive\CODE\ClassroomToolkit\.governed-ai\light-pack.json
```

### 2. Check Attachment Posture

```powershell
python scripts/run-governed-task.py status --json `
  --attachment-root "D:\OneDrive\CODE\ClassroomToolkit" `
  --attachment-runtime-state-root "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit"
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1 `
  -AttachmentRoot "D:\OneDrive\CODE\ClassroomToolkit" `
  -RuntimeStateRoot "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit"
```

Expected attachment posture:
- `healthy`
- or one of `missing_light_pack`, `invalid_light_pack`, `stale_binding`

### 3. Use The Session Bridge
Inspect repo posture through the bridge:

```powershell
python scripts/session-bridge.py repo-posture `
  --command-id "cmd-classroom-posture-001" `
  --task-id "task-classroom-001" `
  --repo-binding-id "binding-classroomtoolkit" `
  --adapter-id "codex-cli" `
  --attachment-root "D:\OneDrive\CODE\ClassroomToolkit" `
  --attachment-runtime-state-root "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit"
```

Request a gate plan:

```powershell
python scripts/session-bridge.py request-gate `
  --command-id "cmd-classroom-gate-001" `
  --task-id "task-classroom-001" `
  --repo-binding-id "binding-classroomtoolkit" `
  --adapter-id "codex-cli" `
  --mode "quick" `
  --policy-status "allow" `
  --attachment-root "D:\OneDrive\CODE\ClassroomToolkit" `
  --attachment-runtime-state-root "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit"
```

Execute the declared gate commands inside the attached repo:

```powershell
python scripts/run-governed-task.py verify-attachment `
  --attachment-root "D:\OneDrive\CODE\ClassroomToolkit" `
  --attachment-runtime-state-root "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" `
  --mode "quick" `
  --task-id "task-classroom-verify-001" `
  --run-id "run-classroom-verify-001" `
  --json
```

Evaluate write governance posture before real edits:

```powershell
python scripts/run-governed-task.py govern-attachment-write `
  --attachment-root "D:\OneDrive\CODE\ClassroomToolkit" `
  --attachment-runtime-state-root "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" `
  --task-id "task-classroom-write-001" `
  --tool-name "apply_patch" `
  --target-path "src/ClassroomToolkit.App/MainWindow.ZOrder.cs" `
  --tier "medium" `
  --rollback-reference "git diff -- src/ClassroomToolkit.App/MainWindow.ZOrder.cs" `
  --json
```

Expected policy posture:
- `allow` for low-tier allowed write paths
- `escalate` with `approval_pending` for medium/high-tier requests
- `deny` for blocked or out-of-scope paths

Approve or reject an escalated write request:

```powershell
python scripts/run-governed-task.py decide-attachment-write `
  --attachment-runtime-state-root "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" `
  --approval-id "approval-xxxx" `
  --decision "approve" `
  --decided-by "operator" `
  --json
```

Execute an approved write request:

```powershell
python scripts/run-governed-task.py execute-attachment-write `
  --attachment-root "D:\OneDrive\CODE\ClassroomToolkit" `
  --attachment-runtime-state-root "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" `
  --task-id "task-classroom-write-001" `
  --tool-name "write_file" `
  --target-path "src/ClassroomToolkit.App/.governed-runtime-probe.txt" `
  --tier "medium" `
  --rollback-reference "git checkout -- src/ClassroomToolkit.App/.governed-runtime-probe.txt" `
  --approval-id "approval-xxxx" `
  --content "governed runtime write probe" `
  --json
```

### 4. One-Command Runtime Check (Recommended For Daily Use)

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-check.ps1 `
  -AttachmentRoot "D:\OneDrive\CODE\ClassroomToolkit" `
  -AttachmentRuntimeStateRoot "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" `
  -Mode "quick" `
  -WriteTargetPath "src/ClassroomToolkit.App/MainWindow.ZOrder.cs" `
  -WriteTier "medium"
```

What this single command runs:
- `status` (with attachment posture)
- `doctor` (with attachment args)
- `session-bridge request-gate`
- `verify-attachment` (unless `-SkipVerifyAttachment`)
- optional `govern-attachment-write` when `-WriteTargetPath` is provided

Exit behavior:
- returns exit code `0` only when the chain passes and gate results are all `pass`
- returns exit code `1` when any step fails or any verification gate result is `fail`

### 5. Two-Mode One-Command Flow

Onboard mode (first-time attach + runtime check):

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 `
  -FlowMode "onboard" `
  -AttachmentRoot "D:\OneDrive\CODE\ClassroomToolkit" `
  -AttachmentRuntimeStateRoot "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" `
  -RepoId "classroomtoolkit" `
  -DisplayName "ClassroomToolkit" `
  -PrimaryLanguage "csharp" `
  -BuildCommand "dotnet build ClassroomToolkit.sln -c Debug" `
  -TestCommand "dotnet test tests/ClassroomToolkit.Tests/ClassroomToolkit.Tests.csproj -c Debug" `
  -ContractCommand "dotnet test tests/ClassroomToolkit.Tests/ClassroomToolkit.Tests.csproj -c Debug" `
  -Mode "quick"
```

Daily mode (skip attach, run check chain directly):

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 `
  -FlowMode "daily" `
  -AttachmentRoot "D:\OneDrive\CODE\ClassroomToolkit" `
  -AttachmentRuntimeStateRoot "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" `
  -Mode "quick"
```

ClassroomToolkit preset shortcut:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-classroomtoolkit.ps1 -FlowMode "daily"
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-classroomtoolkit.ps1 -FlowMode "onboard"
```

Multi-target preset shortcut (`classroomtoolkit` / `self-runtime` / `skills-manager`):

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -Target "skills-manager" `
  -FlowMode "daily" `
  -SkipVerifyAttachment
```

## What Happens If Paths Change
- If the target repo moves:
  - the `.governed-ai` files move with it
  - pass the new location as `--attachment-root`
- If the machine-local runtime state root moves:
  - pass the new location as `--attachment-runtime-state-root`
  - or re-run attach intentionally
- If the runtime repo itself moves:
  - the feature semantics do not change
  - but operator commands must point at the runtime scripts in the new location

The behavior is not permanently tied to one old absolute path, but every invocation must use the current valid paths.

Relative-path note:
- `runtime-check.ps1` and `runtime-flow.ps1` accept relative paths and normalize them to absolute paths at runtime.

## Can This Repo Attach To Itself
Yes.

The runtime repo itself can be attached as a target repo, but the same invariant still applies:
- `runtime_state_root` must stay outside the target repo root

Invalid self-attachment example:
- `D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\self-runtime`

Valid self-attachment example:
- `D:\OneDrive\CODE\governed-ai-runtime-state\self-runtime`

The special case is operational, not architectural:
- no separate contract path exists for self-attachment
- the same attachment, doctor, status, session-bridge, and verify-attachment flow still applies
- the main risk is accidentally placing machine-local runtime state inside the repo, which the validator rejects

### 4. Use Codex-Related Trial Surfaces Honestly
Codex smoke trial:

```powershell
python scripts/run-codex-adapter-trial.py `
  --repo-id "classroomtoolkit" `
  --task-id "task-classroom-codex-trial" `
  --binding-id "binding-classroomtoolkit"
```

Profile-based multi-repo trial:

```powershell
python scripts/run-multi-repo-trial.py `
  --repo-profile "D:\OneDrive\CODE\ClassroomToolkit\.governed-ai\repo-profile.json"
```

## Current Boundary
- good for attachment, posture inspection, attached gate planning, and executing declared verification gates inside the target repo
- good for establishing a governed repo profile for an external repository
- not yet the same thing as letting Codex CLI run inside `ClassroomToolkit` with full runtime-owned approval, execution, evidence, and rollback for real writes

## Related
- [Target Repo Attachment Flow](../product/target-repo-attachment-flow.md)
- [Target Repo 接入流程](../product/target-repo-attachment-flow.zh-CN.md)
- [Single-Machine Runtime Quickstart](./single-machine-runtime-quickstart.md)
- [单机 Runtime 快速开始](./single-machine-runtime-quickstart.zh-CN.md)
- [Multi-Repo Trial Quickstart](./multi-repo-trial-quickstart.md)
- [多仓试运行快速开始](./multi-repo-trial-quickstart.zh-CN.md)
- [Codex Direct Adapter](../product/codex-direct-adapter.md)
- [Chinese Version](./use-with-existing-repo.zh-CN.md)
