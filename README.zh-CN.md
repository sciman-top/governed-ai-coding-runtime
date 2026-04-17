# Governed AI Coding Runtime 中文使用说明

## 当前状态
`Foundation / GAP-020` 到 `GAP-023` 已完成，当前活跃执行队列已经切到 `Full Runtime / GAP-024` 与后续阶段。

本项目现在可以使用，但要按正确边界理解：

- 可以用作“治理运行时契约层”。
- 可以运行仓库验证和 runtime contract tests。
- 可以运行 Foundation 级 build 与 doctor 门禁。
- 可以运行第一个只读 trial 脚本。
- 可以作为后续实现生产 runtime service、worker、UI、持久化层的基础。

还不能作为完整产品直接部署：

- 没有生产级 runtime service。
- 没有数据库或 durable workflow worker。
- 没有真实 Web 控制台。
- 没有包构建产物或发布流程。
- `build` 与 `hotspot/doctor` 已有 Foundation 级真实入口，但还不是生产级构建与服务健康检查。

## 你可以怎样使用

### 1. 验证仓库是否健康
在仓库根目录执行：

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

### 3. 使用 runtime contract primitives
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
- `verification_runner.py`: quick/full verification plan 与 artifact
- `delivery_handoff.py`: 交付 handoff package
- `eval_trace.py`: eval baseline 与 trace grading
- `second_repo_pilot.py`: 第二 repo profile reuse pilot
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

### 4. 阅读文档的推荐顺序
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

## 当前完成度
当前已完成：

- `Phase 0` 到 `Phase 4` 的 MVP 合约层与验证基线
- 当前下一执行队列是 `Full Runtime / GAP-024+`

当前验证基线：

- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- `python -m unittest discover -s tests/runtime -p "test_*.py" -v`

## 下一步建议
如果继续推进产品化，建议下一阶段优先做：

1. 增加真实 Python package 元数据与更完整发布构建。
2. 增加 durable storage 或 workflow worker。
3. 把当前 `ControlPlaneConsole` facade 接到 CLI 或最小 Web UI。
4. 把 Foundation doctor 扩展为更接近服务健康检查的入口。
