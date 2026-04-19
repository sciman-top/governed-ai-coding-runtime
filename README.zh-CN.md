# Governed AI Coding Runtime 中文使用说明

## 当前状态
`Foundation / GAP-020` 到 `GAP-023`、`Full Runtime / GAP-024` 到 `GAP-028`、`Public Usable Release / GAP-029` 到 `GAP-032`、`Maintenance Baseline / GAP-033` 到 `GAP-034`、`Interactive Session Productization / GAP-035` 到 `GAP-039` 已完成。

这表示“混合最终形态的第一版产品化边界”已经落地，但不表示“所有上游宿主都已经接入完整 runtime-owned 真实执行能力”。

当前仓库现在应该理解为一个已经完成产品化第一版落地的本地 governed runtime；`Strategy Alignment Gates / GAP-040..044` 已在当前分支基线上完成，并作为这条产品化结果的硬化依赖保留下来。

定位与非目标：

- 定位：AI coding agents 的治理/运行时层，而不是新的执行宿主。
- 非目标：不做另一个宿主壳层，不做 wrapper-first 编排产品，也不做 generation guardrail 产品。
- 策略入口：[Positioning And Competitive Layering](docs/strategy/positioning-and-competitive-layering.md)
- 借鉴矩阵：[Runtime Governance Borrowing Matrix](docs/research/runtime-governance-borrowing-matrix.md)
- 边界 ADR：[ADR-0007 Source-Of-Truth And Runtime Contract Bundle](docs/adrs/0007-source-of-truth-and-runtime-contract-bundle.md)

本项目现在可以使用，但要按正确边界理解：

- 可以用作“治理运行时契约层”。
- 可以运行仓库验证和 runtime contract tests。
- 可以运行本地 build 与 doctor 门禁。
- 可以运行第一个只读 trial 脚本。
- 可以运行一个 safe-mode 的 Codex adapter smoke trial，并检查 task / binding / evidence / verification 线路是否连通。
- 可以运行一个基于 repo-profile 的 multi-repo trial runner，并输出每个 repo 的 posture、adapter tier、verification/evidence refs 和 follow-ups。
- 可以把外部仓库（例如 `D:\OneDrive\CODE\ClassroomToolkit`）attach 到本运行时，生成 `.governed-ai` 轻量接入包，并通过 status / doctor / session-bridge 使用这些能力。
- 可以运行 CLI-first governed runtime smoke task，得到本地 artifact、verification、evidence、handoff 与 runtime status。
- 可以直接查看 compatibility/upgrade/deprecation/retirement policy，并在 runtime status 与 operator UI 中看到维护状态。

还不能作为完整产品直接部署：

- 没有数据库或多机 durable workflow worker。
- 当前 package bundle 是本地分发目录，不是外部发布渠道。
- 当前 operator UI 是本地 HTML surface，不是长期运行的 Web 服务。
- 当前还不能宣称“外部目标仓里的真实高风险写入已经由本项目完整接管”。
- 当前 direct Codex adapter 仍应理解为 honest smoke-trial / posture / evidence wiring，不是完整生产级写入控制面。
- `GAP-045..060` 是当前直达完整混合终态的主线；`GAP-061..068` 是 `GAP-060` 之后的治理优化 follow-on lane。

## 现在能否用于其他项目
可以，但要按当前边界理解。

对 `D:\OneDrive\CODE\ClassroomToolkit` 这类仓库，你现在已经可以：

- 生成或校验 `.governed-ai/repo-profile.json` 和 `.governed-ai/light-pack.json`
- 把 repo-local 声明绑定到 machine-local runtime state
- 用 `status` / `doctor` 看 attachment posture
- 用 `session-bridge` 请求 posture 和 quick/full gate plan
- 用 Codex smoke-trial 与 multi-repo trial 验证 adapter / evidence / verification wiring

你现在还不能把它表述成：

- Codex CLI 已经被本项目完整接管
- 外部仓的真实高风险写入已经具备完整 runtime-owned approval / execution / rollback 闭环

## 你可以怎样使用

### 1. 验证仓库是否健康
在仓库根目录执行：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

这个命令会执行：

- runtime contract tests
- JSON Schema 解析
- schema example validation
- schema catalog 配对检查
- active Markdown links 检查
- backlog / YAML ID drift 检查
- PowerShell 脚本解析检查

对应 quickstart：
- [Single-Machine Runtime Quickstart](docs/quickstart/single-machine-runtime-quickstart.md)
- [单机 Runtime 快速开始](docs/quickstart/single-machine-runtime-quickstart.zh-CN.md)

只运行 runtime contract tests：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

直接运行 Python unittest：

```powershell
python -m unittest discover -s tests/runtime -p "test_*.py" -v
```

### 2. 运行第一个只读 trial
当前 trial 是 scripted/read-only，不会调用真实 Codex，也不会写入目标仓库。

```powershell
python scripts/run-readonly-trial.py `
  --goal "inspect repository" `
  --scope "readonly trial" `
  --acceptance "readonly request accepted" `
  --repo-profile "schemas/examples/repo-profile/python-service.example.json" `
  --target-path "src/service.py" `
  --max-steps 1 `
  --max-minutes 5
```

预期输出是 JSON，包含：

- `repo_id`
- `accepted_count`
- `summary`
- `auth_ownership`
- `unsupported_capability_behavior`

### 3. 运行 Codex adapter smoke trial
这个 trial 默认是 safe-mode，用于验证 direct adapter contract 的最小通路，不代表真实高风险写入已经接通。

```powershell
python scripts/run-codex-adapter-trial.py `
  --repo-id "python-service" `
  --task-id "task-codex-trial" `
  --binding-id "binding-python-service"
```

预期输出是 JSON，包含：

- `adapter_tier`
- `task_id`
- `binding_id`
- `evidence_refs`
- `verification_refs`
- `unsupported_capability_behavior`

### 4. 运行一个完整 governed task
这里的 `run-governed-task.py` 当前应理解为 runtime smoke path，不应理解为“已经直接调用 Codex 完成真实编码”的集成入口。

```powershell
python scripts/run-governed-task.py status --json
```

```powershell
python scripts/run-governed-task.py run --json
```

预期输出会包含：

- `task_id`
- `state`
- `active_run_id`
- `verification_refs`
- `evidence_refs`
- `artifact_refs`

### 5. 运行 multi-repo trial runner
这个 runner 默认使用仓库内置的两个 sample repo-profile，输出多仓 onboarding evidence 汇总。

```powershell
python scripts/run-multi-repo-trial.py
```

预期输出会按 repo 给出：

- `attachment_posture`
- `adapter_tier`
- `verification_refs`
- `evidence_refs`
- `handoff_refs`
- `follow_ups`

### 6. 在现有仓库中使用本项目
如果目标仓是 `D:\OneDrive\CODE\ClassroomToolkit` 这类外部仓，推荐直接看：

- [Use With An Existing Repo](docs/quickstart/use-with-existing-repo.md)
- [在现有仓库中使用](docs/quickstart/use-with-existing-repo.zh-CN.md)
- [Target Repo Attachment Flow](docs/product/target-repo-attachment-flow.md)
- [Target Repo 接入流程](docs/product/target-repo-attachment-flow.zh-CN.md)

它已经包含实际可执行的 `ClassroomToolkit` attach 命令示例。

日常可以直接用一键检查命令：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-check.ps1 `
  -AttachmentRoot "D:\OneDrive\CODE\ClassroomToolkit" `
  -AttachmentRuntimeStateRoot "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" `
  -Mode "quick"
```

双模式一键流（支持首次接入和日常检查）：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 `
  -FlowMode "daily" `
  -AttachmentRoot "D:\OneDrive\CODE\ClassroomToolkit" `
  -AttachmentRuntimeStateRoot "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" `
  -Mode "quick"
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-classroomtoolkit.ps1 -FlowMode "daily"
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target "skills-manager" -FlowMode "daily" -SkipVerifyAttachment
```

### 7. 使用 runtime contract primitives
当前核心代码在：

```text
packages/contracts/src/governed_ai_coding_runtime_contracts/
```

规划入口：
- [Hybrid Final-State Master Outline](docs/architecture/hybrid-final-state-master-outline.md)
- [Direct-To-Hybrid Final-State Roadmap](docs/roadmap/direct-to-hybrid-final-state-roadmap.md)
- [Direct-To-Hybrid Final-State Implementation Plan](docs/plans/direct-to-hybrid-final-state-implementation-plan.md)
- [Governance Optimization Lane Roadmap](docs/roadmap/governance-optimization-lane-roadmap.md)
- [Governance Optimization Lane Implementation Plan](docs/plans/governance-optimization-lane-implementation-plan.md)

主要模块：

- `task_intake.py`: 任务输入与生命周期 transition 校验
- `repo_profile.py`: repo profile 加载与 admission minimums
- `tool_runner.py`: 只读工具请求治理
- `workspace.py`: 隔离工作区分配与写路径校验
- `write_policy.py`: medium/high 写入策略默认值
- `approval.py`: approval request 状态与审计
- `write_tool_runner.py`: 写侧工具治理与 rollback reference
- `execution_runtime.py`: 任务到运行实例的本地执行编排
- `worker.py`: 同步单机 worker 接口
- `artifact_store.py`: 本地 artifact 持久化与风险分类
- `replay.py`: 失败签名与 replay 引用
- `verification_runner.py`: quick/full verification plan 与 artifact
- `delivery_handoff.py`: 交付 handoff package
- `eval_trace.py`: eval baseline 与 trace grading
- `second_repo_pilot.py`: 第二 repo profile reuse pilot
- `runtime_status.py`: CLI-first operator read model
- `control_console.py`: 最小 approval/evidence console facade

示例：

```powershell
$env:PYTHONPATH="packages/contracts/src"
python - <<'PY'
from governed_ai_coding_runtime_contracts.repo_profile import load_repo_profile
from governed_ai_coding_runtime_contracts.write_policy import resolve_write_policy

profile = load_repo_profile("schemas/examples/repo-profile/python-service.example.json")
policy = resolve_write_policy(profile)
print(profile.repo_id)
print(policy.approval_mode("high"))
PY
```

### 5. 阅读文档的推荐顺序
如果你只想知道怎么用：

1. [本文档](README.zh-CN.md)
2. [文档索引](docs/README.md)
3. [第一个只读 Trial](docs/product/first-readonly-trial.md)
4. [Use With An Existing Repo](docs/quickstart/use-with-existing-repo.md)
5. [在现有仓库中使用](docs/quickstart/use-with-existing-repo.zh-CN.md)
5. [Codex Direct Adapter](docs/product/codex-direct-adapter.md)
6. [Multi-Repo Trial Loop](docs/product/multi-repo-trial-loop.md)
7. [写入策略默认值](docs/product/write-policy-defaults.md)
8. [审批流程](docs/product/approval-flow.md)
9. [写侧工具治理](docs/product/write-side-tool-governance.md)
10. [Verification Runner](docs/product/verification-runner.md)
11. [交付 Handoff](docs/product/delivery-handoff.md)
12. [Runbooks](docs/runbooks/README.md)

如果你要理解产品规划：

1. [90-Day Plan](docs/roadmap/governed-ai-coding-runtime-90-day-plan.md)
2. [Issue-Ready Backlog](docs/backlog/issue-ready-backlog.md)
3. [PRD](docs/prd/governed-ai-coding-runtime-prd.md)
4. [Target Architecture](docs/architecture/governed-ai-coding-runtime-target-architecture.md)
5. [Positioning And Competitive Layering](docs/strategy/positioning-and-competitive-layering.md)
6. [Generic Target-Repo Attachment Blueprint](docs/architecture/generic-target-repo-attachment-blueprint.md)
7. [Interactive Session Productization Implementation Plan](docs/plans/interactive-session-productization-implementation-plan.md)
8. [Governance Runtime Strategy Alignment Plan](docs/plans/governance-runtime-strategy-alignment-plan.md)

## 当前完成度
当前已完成：

- `Phase 0` 到 `Phase 4` 的 MVP 合约层与验证基线
- `Full Runtime / GAP-024` 到 `GAP-028`
- `Public Usable Release / GAP-029` 到 `GAP-032`
- `Maintenance Baseline / GAP-033` 到 `GAP-034`

当前产品化切片：

- `Interactive Session Productization / GAP-035` 到 `GAP-039` 已在当前分支基线上完成
- `Strategy Alignment Gates / GAP-040` 到 `GAP-044` 已在当前分支基线上完成

当前验证基线：

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- `python -m unittest discover -s tests/runtime -p "test_*.py" -v`

## 维护策略
- [Codex CLI/App Integration Guide](docs/product/codex-cli-app-integration-guide.md)
- [Codex CLI/App 集成指南](docs/product/codex-cli-app-integration-guide.zh-CN.md)
- [Runtime Compatibility And Upgrade Policy](docs/product/runtime-compatibility-and-upgrade-policy.md)
- [Maintenance, Deprecation, And Retirement Policy](docs/product/maintenance-deprecation-and-retirement-policy.md)
