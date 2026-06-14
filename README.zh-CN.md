# Governed AI Coding Runtime 中文说明

## 当前快照
- 唯一状态真源：`docs/architecture/planning-status.json`
- 当前 active queue：`Continuous-Execution`（`Continuous Execution Readiness And Rollout`）
- `current decision gate`：`defer_ltp_and_refresh_evidence`
- `current live posture`：target-run freshness 为 `fresh`；Codex target runs 为 `native_attach` / ready；Claude workload probe 为 `native_attach` / ready
- 认证基线：`GAP-104..111`
- 最新完成的治理硬化切片：`GAP-169..172`
  - 已把 repo-owned `reference-basis`、release-style `preflight` 和 CI `release-preflight` 收进仓库基线

## 最快路径
如果只想知道“现在该执行什么”，优先使用这 4 个入口：

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

推荐理解：
- `run.ps1`：仓库根短入口，适合先看帮助和日常操作
- `run.ps1 fast`：日常内环反馈，执行 `build + RuntimeQuick`
- `run.ps1 readiness -OpenUi`：按本仓硬门禁执行 `build -> test -> contract/invariant -> hotspot`，并打开默认中文 operator UI
- `scripts/governance/preflight.ps1 -DisableAutoCommit`：release-style closeout，在完整 gate 上追加 `Docs`、`Scripts` 与 `git diff --check`

## 这是什么项目
- 这是一个 AI coding governance runtime / control plane，不是新的执行宿主。
- 它把治理契约、门禁、evidence、rollout、target-repo attach 和 host feedback 收敛到同一套 repo-owned 规则与脚本中。
- 当前最佳工程终态口径保持为 `Governance Hub + Reusable Contract + Capability-First Host Adapters + Controlled Evolution + Evidence-First Delivery`。
- Codex and Claude Code are cooperation hosts, not competitors；本仓只治理它们的 attach、gate、evidence、handoff 与 degrade posture，不复制或替代宿主 UI、账号、provider 或模型循环。
- 它不负责本机账号、provider、gateway 或宿主切换：
  - Codex/Cockpit 的 Direct OAuth、Direct API、API service 往返切换由 `Cockpit Tools` 负责。
  - Claude Code / Claude Desktop 的账号与 provider 切换由 `CC Switch` 负责。

## 已退休 Codex/Cockpit Shim 边界
- 当前只保留 `Disable-CodexProjectInterop.ps1` 与 `Test-CodexGuardAbsence.ps1`，用于旧项目互操作 shim 的清理与缺席验证。
- 禁止恢复或推荐旧路径：`CodexProjectionSmoke`、`CodexApiProjectionRepair`、`CodexOauthProjectionRepair`、`CodexLaunchBindingRepair`、`Manage-LiteLLMGateway.ps1`、`codex-mode-*`、`--migrate-provider-bucket`、`SQLite provider trigger`、`no-op launcher`、`restart wrapper`。

## 当前能做什么
- 运行本仓 canonical verification：`scripts/verify-repo.ps1`
- 运行 release-style preflight：`scripts/governance/preflight.ps1`
- 通过 `scripts/operator.ps1` 聚合 readiness、feedback、rules sync、target flows 与 operator UI
- 通过 `scripts/runtime-flow-preset.ps1` 对 target catalog 执行 attach、daily、治理基线同步和 apply-all
- 通过 `scripts/sync-agent-rules.ps1` 同步 `AGENTS.md` / `CLAUDE.md` / `GEMINI.md`
- 对外部仓执行 attach-first governance，并保留 approval / evidence / handoff / replay refs
- 以绿色包方式发布与初始化：
  - `.\release.ps1 -Version <version> -Channel portable`
  - `.\install.ps1 -Mode Portable`

## 当前不负责什么
- 不接管 Codex/Cockpit 的账号、provider、gateway、历史桶或 launcher 状态
- 不接管 Claude Code / Claude Desktop 的账号、provider、配置根目录或历史迁移
- 不应宣称“已经在所有环境里完整接管所有外部仓的真实执行”

## 硬门禁与参考纪律
- 交付底线固定为：`build -> test -> contract/invariant -> hotspot`
- 验收链统一执行：`build -> test -> contract/invariant -> hotspot` 由 runtime-managed gate 流统一执行，降低漏检。
- canonical verifier：`scripts/verify-repo.ps1`
  - `Build`：`scripts/build-runtime.ps1`
  - `Runtime`：runtime/service tests
  - `Contract`：source/repo/target governance invariants
  - `Doctor`：`scripts/doctor-runtime.ps1`
  - `Docs` / `DocsLinks` / `Scripts`：文档链接、规划一致性、PowerShell 解析等
- 高漂移改动现在是 fail-closed：
  - `scripts/verify-reference-required-changes.py` 约束 same-diff 官方来源、主参考与本地 evidence 审查
  - `scripts/verify-reference-basis.py` 约束命名本地 reference ids 的 same-diff 审查
- 关键策略入口：
  - `docs/architecture/reference-required-change-policy.json`
  - `docs/architecture/reference-basis-policy.json`
  - `docs/research/reference-basis-matrix.md`
  - `docs/research/reference-basis-catalog.json`
- 同一次 diff 的 evidence 必须写到 `docs/change-evidence/*.md`
  - 常见字段：`official_sources_reviewed`、`primary_references_reviewed`、`local_runtime_evidence_reviewed`、`source_decision`
  - 若命中 `reference-basis` surface，还要补 `reference_basis_surface_ids`、`required_local_reference_ids_reviewed`、`reference_adoption_decision`
- GitHub Actions 当前会同时执行：
  - `scripts/verify-repo.ps1 -Check All`
  - `scripts/governance/preflight.ps1 -DisableAutoCommit`

## 主入口建议
- `run.ps1`
  - 少记命令的仓库根短入口
- `scripts/operator.ps1`
  - 聚合 `Readiness`、`FeedbackReport`、`RulesDryRun`、`RulesApply`、`DailyAll`、`ApplyAllFeatures`、`SelfEvolutionPromotionPlan`、`CorePrincipleMaterialize`、`OperatorUi`
- `scripts/verify-repo.ps1`
  - 本仓 canonical verification surface
- `scripts/governance/preflight.ps1`
  - release-style closeout
- `scripts/runtime-flow-preset.ps1`
  - 面向 target catalog 的 attach/daily/baseline/apply-all
- `scripts/sync-agent-rules.ps1`
  - 从 `rules/manifest.json` 同步三套规则文件
- `claude-provider continuity`
  - Claude 连续性只读检查
- `scripts/Disable-CodexProjectInterop.ps1` 与 `scripts/Test-CodexGuardAbsence.ps1`
  - 仅用于旧 Codex shim 的清理与缺席验证

## 快速使用路径（推荐）
- 路径 A（治理侧车，阻力最低）：继续用 Codex/Claude Code 编码，同时运行 `bootstrap + doctor + verify-repo -Check All + status` 做 readiness 与门禁检查。
- 路径 B（外部仓 attach-first，推荐）：先 `attach-target-repo`，再跑 `runtime-flow.ps1 -FlowMode daily` 作为日常治理链。
- 路径 C（中高风险写入）：用 `govern-attachment-write -> decide-attachment-write -> execute-attachment-write` 走审批与回滚引用闭环。

## 在其他仓库中使用的边界
对外部仓（例如 `..\ClassroomToolkit`）当前支持的是 attach-first governance：
- attach target repo，并生成/校验 `.governed-ai` 轻量接入资产
- 执行 daily gate、治理基线同步、rules sync 和 governed write flow
- 记录 approval / evidence / handoff / replay refs

当前不应宣称：
- 不应声称本项目已经在所有环境下完全接管 Codex 宿主执行
- “所有外部仓和所有高风险流程都已形成统一 runtime-owned 闭环”

## 继续阅读
- 当前导航入口：
  - [docs/README.md](docs/README.md)
  - [planning-status.json](docs/architecture/planning-status.json)
- 快速上手：
  - [Single-Machine Runtime Quickstart](docs/quickstart/single-machine-runtime-quickstart.md)
  - [单机 Runtime 快速开始](docs/quickstart/single-machine-runtime-quickstart.zh-CN.md)
  - [Use With An Existing Repo](docs/quickstart/use-with-existing-repo.md)
  - [在现有仓库中使用](docs/quickstart/use-with-existing-repo.zh-CN.md)
  - [Agent Continuity Guide](docs/product/agent-continuity.md)
  - [共享上下文连续性指南](docs/product/agent-continuity.zh-CN.md)
- 近期治理硬化：
  - [20260614 Continuous Execution Promotion](docs/change-evidence/20260614-continuous-execution-promotion.md)
  - [20260614 Active Queue Evidence-Upkeep Refresh](docs/change-evidence/20260614-active-queue-evidence-upkeep-refresh.md)
  - [20260609 Live Posture Recovery](docs/change-evidence/20260609-live-posture-recovery.md)
  - [20260609 Reference Basis And Preflight Hardening](docs/change-evidence/20260609-reference-basis-and-preflight-hardening.md)
- reference governance：
  - [Reference Basis Matrix](docs/research/reference-basis-matrix.md)
  - [Reference Governance And Release Preflight Roadmap](docs/roadmap/reference-governance-and-preflight-roadmap.md)
  - [Reference Governance And Release Preflight Plan](docs/plans/reference-governance-and-preflight-plan.md)
- 历史与证据：
  - [已完成 GAP 历史归档](docs/archive/completed-gap-history.zh-CN.md)
  - [Change Evidence Index](docs/change-evidence/README.md)

## 常用验证命令
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check RuntimeQuick
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/governance/preflight.ps1 -DisableAutoCommit
```
