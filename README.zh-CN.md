# Governed AI Coding Runtime 中文说明

## 当前边界
- 唯一状态真源：`docs/architecture/planning-status.json`
- 唯一规划真源仍是 `docs/architecture/planning-status.json`。
- 当前 active queue：`Continuous-Execution`
- `current decision gate`：`defer_ltp_and_refresh_evidence`
- 本仓当前只保留四类 live 能力：
  - 本仓自治理：`build -> test -> contract/invariant -> hotspot`
  - 用户目录级全局规则同步：`~/.codex`、`~/.claude`
  - 目标仓项目规则协同审计：`AGENTS.md + CLAUDE.md thin wrapper`
  - host/self-evolution/continuity 的只读反馈、证据与门禁
- 当前规则协调版本：`rule_release=9.55 / project_contract_version=2.0`。9 个目标仓来自显式 allowlist，不自动扫描纳管相邻目录。
- 目标仓 `AGENTS.md` 保持宿主中立；`CLAUDE.md` 默认仅含无 BOM 首行 `@AGENTS.md`。全局同步只写两个用户级副本，不写目标仓正文。
- CI 协同版本为 `coordination_schema=2.2 / ci_contract=2.1`：每仓本地 workflow 验证规则变更；控制仓按清单生成 9 仓矩阵，实际 checkout 审计 7 个公开仓，并将 2 个私有仓明确分流到 target-local enforcement；两者都不能替代产品门禁。
- 历史 `docs/change-evidence/**` 继续保留，但不再表示 target-repo rollout、attachment、session-bridge write 仍是当前能力。

## 最快路径
```powershell
.\run.ps1
```

```powershell
.\run.ps1 fast
```

```powershell
.\run.ps1 readiness -OpenUi
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/governance/preflight.ps1 -DisableAutoCommit
```

- `run.ps1`：仓库根短入口
- `run.ps1 fast`：执行 `build + RuntimeQuick`
- `run.ps1 readiness -OpenUi`：执行完整硬门禁并打开 operator UI
- `preflight.ps1`：在完整门禁之上追加 `Docs`、`Scripts`、`git diff --check`

## 本仓现在负责什么
- 运行本仓 canonical gate：`scripts/build-runtime.ps1`、`scripts/verify-repo.ps1`、`scripts/doctor-runtime.ps1`
- 通过 `scripts/run-governed-task.py` 生成 repo-local task/evidence/handoff/status
- 通过 `scripts/sync-agent-rules.ps1` 同步 Codex/Claude 全局规则文件
- 通过 `scripts/verify-target-project-rules.py` 审计受管目标仓的项目规则协同
- 通过 `scripts/export-target-rule-ci-matrix.py` 生成跨仓 CI matrix
- 生成 host feedback、自演化建议、continuity 证据与 operator UI
- 通过 `scripts/package-runtime.ps1` 组装 portable release
- 只保留旧 Codex shim 的清理与缺席验证
- Codex and Claude Code are cooperation hosts, not competitors.
- Codex/Cockpit 的 Direct OAuth、Direct API、Cockpit API service 往返切换由 `Cockpit Tools` 负责。

## 已退休 Codex/Cockpit Shim
- 当前只保留 `Disable-CodexProjectInterop.ps1` 与 `Test-CodexGuardAbsence.ps1`。
- 禁止恢复或推荐旧路径：`CodexProjectionSmoke`、`CodexApiProjectionRepair`、`CodexOauthProjectionRepair`、`CodexLaunchBindingRepair`、`Manage-LiteLLMGateway.ps1`、`codex-mode-*`、`--migrate-provider-bucket`、`SQLite provider trigger`、`no-op launcher`、`restart wrapper`。

## 已退役能力
- 不再提供 target-repo `daily`、`governance-baseline`、`apply-all`、`cleanup-targets`、`uninstall-governance`
- 不再提供 attachment/light-pack/session-bridge/attached-write 桥接链
- `rules/manifest.json` 不再分发任何 `rules/projects/**` 项目规则副本
- 不再向目标仓 blind sync `AGENTS.md` / `CLAUDE.md`；目标差异只允许通过 audit + integration + verification 闭环处理
- target-run、KPI、effect 相关文件只保留历史证据意义

已退役命令名仍会 fail-closed 返回退休提示，不会静默兼容执行。

## 主要入口
- `run.ps1`
- `scripts/operator.ps1`
- `scripts/verify-repo.ps1`
- `scripts/governance/preflight.ps1`
- `scripts/sync-agent-rules.ps1`
- `scripts/verify-agent-rule-family.py`
- `scripts/verify-target-project-rules.py`
- `scripts/export-target-rule-ci-matrix.py`
- `scripts/run-governed-task.py`
- `scripts/package-runtime.ps1`

## 验证命令
```powershell
python scripts/verify-agent-rule-family.py
python scripts/verify-target-project-rules.py --require-all
python scripts/export-target-rule-ci-matrix.py
python scripts/sync-agent-rules.py --scope All --fail-on-change
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

## 继续阅读
- [docs/README.md](docs/README.md)
- [单机 Runtime 快速开始](docs/quickstart/single-machine-runtime-quickstart.zh-CN.md)
- [在现有仓库中使用](docs/quickstart/use-with-existing-repo.zh-CN.md)
- [功能反馈闭环](docs/product/host-feedback-loop.zh-CN.md)
- [共享上下文连续性指南](docs/product/agent-continuity.zh-CN.md)
- [20260617 Active Queue Evidence-Upkeep Refresh](docs/change-evidence/20260617-active-queue-evidence-upkeep-refresh.md)
- [20260617 Planning EntryPoint Proof Refresh](docs/change-evidence/20260617-planning-entrypoint-proof-refresh.md)
