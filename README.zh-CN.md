# Governed AI Coding Runtime 中文使用说明

## 当前状态
`Foundation / GAP-020` 到 `GAP-023`、`Full Runtime / GAP-024` 到 `GAP-028`、`Public Usable Release / GAP-029` 到 `GAP-032`、`Maintenance Baseline / GAP-033` 到 `GAP-034` 已完成。

这表示“本地单机运行时基线”已经落地，不表示“最终产品边界”已经完成。

当前仓库现在应该理解为一个可运行的本地 baseline，活跃下一阶段是 `Interactive Session Productization / GAP-035..039`。

本项目现在可以使用，但要按正确边界理解：

- 可以用作“治理运行时契约层”。
- 可以运行仓库验证和 runtime contract tests。
- 可以运行 Foundation 级 build 与 doctor 门禁。
- 可以运行第一个只读 trial 脚本。
- 可以运行 CLI-first governed runtime smoke task，得到本地 artifact、verification、evidence、handoff 与 runtime status。
- 可以直接查看 compatibility/upgrade/deprecation/retirement policy，并在 runtime status 与 operator UI 中看到维护状态。

还不能作为完整产品直接部署：

- 没有数据库或多机 durable workflow worker。
- 当前 package bundle 是本地分发目录，不是外部发布渠道。
- 当前 operator UI 是本地 HTML surface，不是长期运行的 Web 服务。
- 当前还没有 direct Codex adapter；与 Codex CLI/App 的关系仍然是 compatibility + manual handoff，不是 runtime 内直接编排真实编码执行。
- 当前还没有通用 target-repo 接入包，也还没有 attach-first 的会话桥接层。

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

### 3. 运行一个完整 governed task
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

### 4. 使用 runtime contract primitives
当前核心代码在：

```text
packages/contracts/src/governed_ai_coding_runtime_contracts/
```

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
4. [写入策略默认值](docs/product/write-policy-defaults.md)
5. [审批流程](docs/product/approval-flow.md)
6. [写侧工具治理](docs/product/write-side-tool-governance.md)
7. [Verification Runner](docs/product/verification-runner.md)
8. [交付 Handoff](docs/product/delivery-handoff.md)
9. [Runbooks](docs/runbooks/README.md)

如果你要理解产品规划：

1. [90-Day Plan](docs/roadmap/governed-ai-coding-runtime-90-day-plan.md)
2. [Issue-Ready Backlog](docs/backlog/issue-ready-backlog.md)
3. [PRD](docs/prd/governed-ai-coding-runtime-prd.md)
4. [Target Architecture](docs/architecture/governed-ai-coding-runtime-target-architecture.md)
5. [Generic Target-Repo Attachment Blueprint](docs/architecture/generic-target-repo-attachment-blueprint.md)
6. [Interactive Session Productization Plan](docs/plans/interactive-session-productization-plan.md)

## 当前完成度
当前已完成：

- `Phase 0` 到 `Phase 4` 的 MVP 合约层与验证基线
- `Full Runtime / GAP-024` 到 `GAP-028`
- `Public Usable Release / GAP-029` 到 `GAP-032`
- `Maintenance Baseline / GAP-033` 到 `GAP-034`

当前活跃队列：

- `Interactive Session Productization / GAP-035` 到 `GAP-039`

当前验证基线：

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- `python -m unittest discover -s tests/runtime -p "test_*.py" -v`

## 维护策略
- [Codex CLI/App Integration Guide](docs/product/codex-cli-app-integration-guide.md)
- [Codex CLI/App 集成指南](docs/product/codex-cli-app-integration-guide.zh-CN.md)
- [Runtime Compatibility And Upgrade Policy](docs/product/runtime-compatibility-and-upgrade-policy.md)
- [Maintenance, Deprecation, And Retirement Policy](docs/product/maintenance-deprecation-and-retirement-policy.md)
