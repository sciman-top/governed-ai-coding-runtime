# Target Repo 接入流程

## Purpose
说明目标仓如何生成或校验 repo-local light pack，以及 machine-local governed runtime 如何消费这套接入信息。

这条流程对应第一版 `GAP-035` onboarding path。目标仓保持声明式，mutable runtime state 继续放在目标仓之外。

## 默认命令

```powershell
python scripts/attach-target-repo.py `
  --target-repo <target-repo-root> `
  --runtime-state-root <machine-local-runtime-state-root> `
  --repo-id <repo-id> `
  --primary-language <language> `
  --build-command "<build command>" `
  --test-command "<test command>" `
  --contract-command "<contract command>"
```

如果 `.governed-ai/light-pack.json` 已存在，默认只校验不覆盖。只有明确要重建时才使用 `--overwrite`。

## ClassroomToolkit 示例

```powershell
python scripts/attach-target-repo.py `
  --target-repo "..\ClassroomToolkit" `
  --runtime-state-root ".runtime\attachments\classroomtoolkit" `
  --repo-id "classroomtoolkit" `
  --display-name "ClassroomToolkit" `
  --primary-language "csharp" `
  --build-command "dotnet build ClassroomToolkit.sln -c Debug" `
  --test-command "dotnet test tests/ClassroomToolkit.Tests/ClassroomToolkit.Tests.csproj -c Debug" `
  --contract-command "dotnet test tests/ClassroomToolkit.Tests/ClassroomToolkit.Tests.csproj -c Debug --filter \"FullyQualifiedName~ArchitectureDependencyTests|FullyQualifiedName~InteropHookLifecycleContractTests|FullyQualifiedName~InteropHookEventDispatchContractTests|FullyQualifiedName~GlobalHookServiceLifecycleContractTests|FullyQualifiedName~CrossPageDisplayLifecycleContractTests\"" `
  --adapter-preference "native_attach"
```

当前推荐姿态：
- 接入时显式声明 `native_attach` 偏好
- 若 live probe 判定 native attach 不可用，由 runtime 自动回退到 `process_bridge` 或 `manual_handoff`

## Repo-Local 文件

```text
.governed-ai/
  repo-profile.json
  light-pack.json
  light-pack.provenance.json
```

它们应只包含声明信息：
- repo profile
- gate command declarations
- path policy scopes
- approval / risk defaults
- adapter preference
- contract refs
- 生成 light pack 的 provenance ref

不应包含：
- runtime 实现代码副本
- task/run state
- approval ledgers
- artifact payloads
- replay bundles

`light-pack.provenance.json` 会在 attach 流程写入新 light pack 时同步生成。它记录 generator、source reference、repo-profile input digest、light-pack output digest、target binding id 和 rollback reference。使用 `--overwrite` 重建 light pack 时，provenance 也会同步重建。

## Machine-Local State
attachment binding 指向 machine-local `runtime_state_root`，mutable state 放在这里：
- tasks
- runs
- approvals
- artifacts
- replay

`RepoAttachmentBinding` 会拒绝放在目标仓内部的 runtime state。

接入时还会在 machine-local runtime state 生成 context pack：
- `context/context-pack.json`
- 包含 repo-map hot files、dominant gate commands、recent failure signatures
- 提供 `generated_at`、`age_seconds`、`is_stale`、`refresh_command` 供启动复用

## 验证失败条件
- `repo_profile_ref` 逃出目标仓
- `light_pack_path` 逃出目标仓
- build / test / contract / invariant declaration 缺少 id 或 command
- path policy 使用绝对路径或 `..`
- mutable runtime state 被放进目标仓

## Runtime 如何消费
成功生成或校验后会返回 `RepoAttachmentBinding`，包含：
- target repo root
- repo profile path
- light-pack path
- runtime state root
- adapter preference
- gate profile
- doctor posture

## Status 和 Doctor

```powershell
python scripts/run-governed-task.py status --json `
  --attachment-root <target-repo-root> `
  --attachment-runtime-state-root <machine-local-runtime-state-root>
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1 `
  -AttachmentRoot <target-repo-root> `
  -RuntimeStateRoot <machine-local-runtime-state-root>
```

attachment posture：
- `missing_light_pack`
- `invalid_light_pack`
- `stale_binding`
- `healthy`

light-pack provenance：
- 由 attach 流程生成且 digest 匹配时，doctor 输出 `OK attachment-light-pack-provenance`
- 旧的手写 light pack 若没有 `provenance_ref`，doctor 输出 `WARN attachment-light-pack-provenance-unsupported`
- 如果声明了 provenance 但文件缺失或 digest 不匹配，会按 invalid light pack 处理，应通过 attach 流程重建

remediation 行为：
- `missing_light_pack`：重新执行 `scripts/attach-target-repo.py ...`，补齐 light pack。
- `invalid_light_pack`：通过 attach 流程重建 `.governed-ai/light-pack.json`。
- `stale_binding`：重新 attach，刷新 `binding_id`。
- `healthy`：无需 remediation。

context-pack 新鲜度：
- 当 `age_seconds > stale_after_seconds` 时标记 stale
- 用 `python scripts/attach-target-repo.py --target-repo <target-repo-root> --runtime-state-root <machine-local-runtime-state-root> --overwrite` 刷新

fail-closed 行为：
- 当提供 attachment 参数时，doctor 遇到非 healthy posture 会输出 `FAIL attachment-posture-<state>` 并返回非零退出码。
- posture 处于 fail-closed 时，不应继续执行 attachment 写入链路。

## 特别说明：本仓也可以作为 target repo
可以，但必须把 `runtime_state_root` 放在仓外。

例如：
- 无效：`.runtime\attachments\self-runtime`
- 有效：`..\governed-ai-runtime-state\self-runtime`

## 相关文档
- [Repo Attachment Binding Spec](../specs/repo-attachment-binding-spec.md)
- [Generic Target-Repo Attachment Blueprint](../architecture/generic-target-repo-attachment-blueprint.md)
- [在现有仓库中使用](../quickstart/use-with-existing-repo.zh-CN.md)
- [English Version](./target-repo-attachment-flow.md)

