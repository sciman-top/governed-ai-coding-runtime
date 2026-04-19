# 在现有仓库中使用

## 简短结论
可以，但要按当前产品边界理解。

你现在可以把一个现有仓库，例如 `D:\OneDrive\CODE\ClassroomToolkit`，作为 machine-local governance sidecar 的 target repo 接入：
- 在目标仓生成或校验 `.governed-ai/` 轻量接入包
- 将可变 runtime state 保持在机器本地目录
- 通过 `status` 和 `doctor` 检查 attachment posture
- 通过本地 `session-bridge` 请求 posture 和 gate plan
- 在目标仓 cwd 执行声明的 verification gates

但这还不是“runtime 已经完整接管 Codex 在目标仓中的真实高风险写入”。

## 推荐流程

### 1. 接入目标仓
从本仓根目录运行：

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

PowerShell 注意：
- `--contract-command` 一旦包含 `|`，PowerShell 可能把它当作管道解析。建议把整个参数值改为单引号包裹，或先用无过滤版本命令接入，后续再收敛过滤条件。

这会创建或校验：

```text
D:\OneDrive\CODE\ClassroomToolkit\.governed-ai\repo-profile.json
D:\OneDrive\CODE\ClassroomToolkit\.governed-ai\light-pack.json
```

### 2. 检查 attachment posture

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

预期 posture：
- `healthy`
- 或 `missing_light_pack` / `invalid_light_pack` / `stale_binding`

### 3. 使用 session bridge
查看 repo posture：

```powershell
python scripts/session-bridge.py repo-posture `
  --command-id "cmd-classroom-posture-001" `
  --task-id "task-classroom-001" `
  --repo-binding-id "binding-classroomtoolkit" `
  --adapter-id "codex-cli" `
  --attachment-root "D:\OneDrive\CODE\ClassroomToolkit" `
  --attachment-runtime-state-root "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit"
```

执行 runtime 托管的 gate 流程（若仅需计划可加 `--plan-only`）：

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

在目标仓执行声明的 gate：

```powershell
python scripts/run-governed-task.py verify-attachment `
  --attachment-root "D:\OneDrive\CODE\ClassroomToolkit" `
  --attachment-runtime-state-root "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" `
  --mode "quick" `
  --task-id "task-classroom-verify-001" `
  --run-id "run-classroom-verify-001" `
  --json
```

在真实写入前先评估写治理姿态：

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

预期策略姿态：
- 低风险且路径允许时返回 `allow`
- 中/高风险请求返回 `escalate`，并给出 `approval_pending`
- blocked 或越界路径返回 `deny`

对升级写请求做审批决议：

```powershell
python scripts/run-governed-task.py decide-attachment-write `
  --attachment-runtime-state-root "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" `
  --approval-id "approval-xxxx" `
  --decision "approve" `
  --decided-by "operator" `
  --json
```

执行已批准写请求：

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

### 4. 一键检查脚本（建议日常使用）

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-check.ps1 `
  -AttachmentRoot "D:\OneDrive\CODE\ClassroomToolkit" `
  -AttachmentRuntimeStateRoot "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" `
  -Mode "quick" `
  -WriteTargetPath "src/ClassroomToolkit.App/MainWindow.ZOrder.cs" `
  -WriteTier "medium" `
  -WriteToolName "write_file" `
  -WriteContent "governed runtime write probe" `
  -ExecuteWriteFlow
```

这一个命令会串行执行：
- `status`（带 attachment posture）
- `doctor`（带 attachment 参数）
- `session-bridge request-gate`
- `verify-attachment`（可用 `-SkipVerifyAttachment` 跳过）
- 当提供 `-WriteTargetPath` 时，执行 `govern-attachment-write`
- 当再提供 `-ExecuteWriteFlow` 时，额外执行 `decide-attachment-write` 与 `execute-attachment-write`

退出码规则：
- 全链路通过且 gate 结果全是 `pass` 时，返回 `0`
- 任一步骤失败或任一 gate 为 `fail` 时，返回 `1`
- 开启 `-ExecuteWriteFlow` 后，输出会包含真实 `handoff_ref` 与 `replay_ref`

### 5. 双模式一键流

首次接入（先 attach，再执行检查链）：

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

日常检查（跳过 attach，直接执行检查链）：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 `
  -FlowMode "daily" `
  -AttachmentRoot "D:\OneDrive\CODE\ClassroomToolkit" `
  -AttachmentRuntimeStateRoot "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" `
  -Mode "quick"
```

ClassroomToolkit 预设快捷命令：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-classroomtoolkit.ps1 -FlowMode "daily"
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-classroomtoolkit.ps1 -FlowMode "onboard"
```

多目标预设快捷命令（`classroomtoolkit` / `self-runtime` / `skills-manager`）：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -Target "skills-manager" `
  -FlowMode "daily" `
  -SkipVerifyAttachment
```

## 路径变化会有什么影响
- 目标仓路径变化：
  - `.governed-ai` 会跟仓一起移动
  - 运行时调用时要传新的 `--attachment-root`
- machine-local runtime state 路径变化：
  - 要传新的 `--attachment-runtime-state-root`
  - 或重新 attach 一次
- 本仓路径变化：
  - 功能语义不变
  - 但你运行脚本时需要使用新的 runtime 仓路径

换句话说，功能不是绑定在旧绝对路径上，但命令调用时必须提供当前有效路径。

相对路径说明：
- `runtime-check.ps1` 与 `runtime-flow.ps1` 已支持相对路径输入，并在运行时规范化为绝对路径。

## 本仓也能作为 target repo 吗
可以。

本仓已经实测可以作为 target repo 生成 `.governed-ai` 接入包，但有一个硬约束：
- `runtime_state_root` 必须在目标仓外部

例如下面这种是无效的，因为 runtime state 放在仓内：
- `D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\self-runtime`

下面这种是有效的：
- `D:\OneDrive\CODE\governed-ai-runtime-state\self-runtime`

### 本仓作为 target repo 的特殊性
- 没有新的协议特例
- attachment contract、doctor、status、session-bridge、verify-attachment 仍然按同一套规则工作
- 特殊点只在于：
  - 目标仓和 runtime 仓是同一个目录
  - 因此更容易误把 `runtime_state_root` 放进仓内
  - 一旦放进仓内，验证器会拒绝并给出 `invalid_light_pack`

## 当前边界
- 适合做 attachment、posture inspection、attached gate planning、declared gate execution
- 适合为外部仓建立 governed repo profile
- 还不等于让 Codex CLI 在目标仓里进入完整 runtime-owned 的 approval / execution / evidence / rollback 闭环

## 相关文档
- [Target Repo Attachment Flow](../product/target-repo-attachment-flow.zh-CN.md)
- [Single-Machine Runtime Quickstart](./single-machine-runtime-quickstart.zh-CN.md)
- [Multi-Repo Trial Quickstart](./multi-repo-trial-quickstart.zh-CN.md)
- [English Version](./use-with-existing-repo.md)
