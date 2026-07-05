# Governed AI Coding Runtime

## Language / 语言
- 中文说明: [README.zh-CN.md](README.zh-CN.md)
- English guide: [README.en.md](README.en.md)
- 文档索引 / Docs index: [docs/README.md](docs/README.md)

## Current Snapshot / 当前快照
- 当前唯一状态真源：`docs/architecture/planning-status.json`
- Single source of planning truth: `docs/architecture/planning-status.json`
- 规划状态锚点 / planning status anchor: `updated_on=2026-07-05`
- 最新 target-run / KPI / effect 刷新 / latest target-run / KPI / effect refresh: `2026-07-05`
- 较新的治理 / self-evolution 机器可读刷新 / latest governance / self-evolution machine-readable refresh: `2026-06-24`
- 当前 active queue / current active queue: `Continuous-Execution` (`Continuous Execution Readiness And Rollout`)
- `current decision gate`：`defer_ltp_and_refresh_evidence`
- `current live posture`：target-run freshness 为 `fresh`；Codex target runs 为 `native_attach` / ready；Claude workload probe 为 `native_attach` / ready
- `workflow-governor` 仍只是 owner-directed conditional follow-on package 的候选边界，不是当前 active queue，也不是替代宿主
- `current decision gate`: `defer_ltp_and_refresh_evidence`
- `current live posture`: target-run freshness is `fresh`; Codex target runs are `native_attach` / ready; Claude workload probe is `native_attach` / ready
- 认证基线 / certified baseline: `GAP-104..111`
- `GAP-104..111` 已在当前分支基线上完成，完整混合终态闭环由 `docs/change-evidence/20260427-gap-111-complete-hybrid-final-state-certification.md` 记录。
- 最新完成的治理硬化切片 / latest completed hardening slice: `GAP-169..172`
  - 已新增 repo-owned `reference-basis`、`scripts/governance/preflight.ps1`、以及 CI `release-preflight`

## Fastest Path / 最快路径
如果只想知道“现在先跑什么”，用下面 4 个入口：

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

区别如下：
- `run.ps1`：仓库根短入口，转发到 `scripts/operator.ps1`
- `run.ps1 fast`：日常内环反馈，执行 `build + RuntimeQuick`
- `run.ps1 readiness -OpenUi`：按本仓硬门禁执行 `build -> test -> contract/invariant -> hotspot`，然后打开默认中文 operator UI
- `scripts/governance/preflight.ps1 -DisableAutoCommit`：release-style closeout，在完整 gate 之上追加 `Docs`、`Scripts` 和 `git diff --check`

## What This Repo Is / 项目定位
- 这是一个 AI coding governance runtime / control plane，不是新的执行宿主。
- 它把治理契约、门禁、evidence、rollout、target-repo attach 和 host feedback 收敛成同一套 repo-owned 规则与脚本。
- 当前最佳工程终态仍是 `Governance Hub + Reusable Contract + Capability-First Host Adapters + Controlled Evolution + Evidence-First Delivery`。
- 本项目已证实的主要价值是 workflow / gate / evidence governance；尚未证实它已经在跨仓库、跨宿主、跨风险层级上证明内建“最佳工作流自动执行器”。
- 它可以演进成 `AI coding workflow governor`，但不是 replacement host，也不是已经在所有场景下证明的固定唯一最佳 workflow executor。
- Codex and Claude Code are cooperation hosts, not competitors；本仓治理它们的 attach、gate、evidence、handoff 和 degrade posture，不复制或替代宿主 UI、账号、provider 或模型循环。
- `apps/` 与 `infra/local-runtime/` 已提供 service-shaped scaffolds 和本地 compose helper，用于边界提取、打包与本地实验；默认 operator path 仍是 `run.ps1` / `scripts/operator.ps1` / `scripts/verify-repo.ps1`，不是 container-first 日常入口。
- 它不负责本机账号、provider、gateway 或宿主启动切换：
  - Codex/Cockpit 的 Direct OAuth、Direct API、API service 往返切换由 `Cockpit Tools` 负责。
  - Claude Code / Claude Desktop 的账号与 provider 切换由 `CC Switch` 负责。

## Retired Codex/Cockpit Shims / 已退休边界
- 当前只保留 `Disable-CodexProjectInterop.ps1` 与 `Test-CodexGuardAbsence.ps1`，用于旧项目互操作 shim 的清理与缺席验证。
- 禁止恢复或推荐旧路径：`CodexProjectionSmoke`、`CodexApiProjectionRepair`、`CodexOauthProjectionRepair`、`CodexLaunchBindingRepair`、`Manage-LiteLLMGateway.ps1`、`codex-mode-*`、`--migrate-provider-bucket`、`SQLite provider trigger`、`no-op launcher`、`restart wrapper`。

## Hard Gates And Reference Discipline / 硬门禁与参考纪律
- 交付底线：`build -> test -> contract/invariant -> hotspot`
- Canonical acceptance chain: runtime-managed `build -> test -> contract/invariant -> hotspot`.
- 验收链统一执行：`build -> test -> contract/invariant -> hotspot` 由 runtime-managed gate 流统一执行，降低漏检。
- Canonical verifier: `scripts/verify-repo.ps1`
  - `Build`: `scripts/build-runtime.ps1`
  - `Runtime`: runtime/service tests
  - `Contract`: source/repo/target governance invariants
  - `Doctor`: `scripts/doctor-runtime.ps1`
  - `Docs` / `DocsLinks` / `Scripts`: 文档链接、规划一致性、PowerShell 解析等
- 高漂移改动现在是 fail-closed：
  - `scripts/verify-reference-required-changes.py` 约束官方来源、主参考和本地 evidence 的 same-diff 审查
  - `scripts/verify-reference-basis.py` 约束命名本地 reference ids 的 same-diff 审查
- 相关策略入口：
  - `docs/architecture/reference-required-change-policy.json`
  - `docs/architecture/reference-basis-policy.json`
  - `docs/research/reference-basis-matrix.md`
  - `docs/research/reference-basis-catalog.json`
- 同一次 diff 的 evidence 必须写到 `docs/change-evidence/*.md`
  - 常见字段：`official_sources_reviewed`、`primary_references_reviewed`、`local_runtime_evidence_reviewed`、`source_decision`
  - 若命中 `reference-basis` surface，还要补 `reference_basis_surface_ids`、`required_local_reference_ids_reviewed`、`reference_adoption_decision`
- GitHub Actions 当前会同时执行：
  - `.github/workflows/verify.yml` -> `scripts/verify-repo.ps1 -Check All`
  - `.github/workflows/verify.yml` -> `scripts/governance/preflight.ps1 -DisableAutoCommit`

## Main Entrypoints / 主要入口
- `run.ps1`
  - 面向少记命令的仓库根短入口
- `scripts/operator.ps1`
  - 聚合 `Readiness`、`FeedbackReport`、`RulesDryRun`、`RulesApply`、`DailyAll`、`ApplyAllFeatures`、`SelfEvolutionPromotionPlan`、`CorePrincipleMaterialize`、`OperatorUi`
- `scripts/verify-repo.ps1`
  - 本仓 canonical verification surface
- `scripts/governance/preflight.ps1`
  - release-style closeout surface
- `scripts/runtime-flow-preset.ps1`
  - 面向 target catalog 的 attach/daily/baseline/apply-all
- `scripts/sync-agent-rules.ps1`
  - 从 `rules/manifest.json` 同步 `AGENTS.md` / `CLAUDE.md` / `GEMINI.md`
- `scripts/package-runtime.ps1`
  - 组装 portable staging tree、zip、sha256、manifest 与 provenance 输出
- `claude-provider continuity`
  - Claude 连续性只读检查
- `scripts/Disable-CodexProjectInterop.ps1` 与 `scripts/Test-CodexGuardAbsence.ps1`
  - 仅用于旧 Codex shim 的清理与缺席验证
- 绿色打包 / portable packaging:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/package-runtime.ps1`
  - `.\release.ps1 -Version <version> -Channel portable`
  - `.\install.ps1 -Mode Portable`

## External Repo Boundary / 外部仓边界
对外部仓（例如 `..\ClassroomToolkit`）当前支持的是 attach-first governance：
- attach target repo，并生成/校验 `.governed-ai` 轻量接入资产
- 执行 target-repo daily gate、governance baseline sync、rules sync 和 governed write flow
- 记录 approval / evidence / handoff / replay refs

当前不应宣称：
- “本项目已经在所有环境里完整接管 Codex/Claude 的真实执行”
- “所有外部仓和所有高风险流程都已实现统一 runtime-owned 闭环”

## Read Next / 继续阅读
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
  - [20260705 Readme And Docs Current-State Refresh](docs/change-evidence/20260705-readme-and-docs-current-state-refresh.md)
  - [20260705 Runtime Evolution Functional Verification](docs/change-evidence/20260705-runtime-evolution-functional-verification.md)
  - [20260705 Claim Catalog Freshness Refresh](docs/change-evidence/20260705-claim-catalog-freshness-refresh.md)
  - [20260623 Active Queue Evidence-Upkeep Refresh](docs/change-evidence/20260623-active-queue-evidence-upkeep-refresh.md)
  - [20260623 Self-Evolution Review Refresh](docs/change-evidence/20260623-self-evolution-review-refresh.md)
  - [20260620 Active Queue Evidence-Upkeep Refresh](docs/change-evidence/20260620-active-queue-evidence-upkeep-refresh.md)
  - [20260620 Self-Evolution Review Refresh](docs/change-evidence/20260620-self-evolution-review-refresh.md)
  - [20260618 Active Queue Evidence-Upkeep Refresh](docs/change-evidence/20260618-active-queue-evidence-upkeep-refresh.md)
  - [20260617 Active Queue Evidence-Upkeep Refresh](docs/change-evidence/20260617-active-queue-evidence-upkeep-refresh.md)
  - [20260617 Planning EntryPoint Proof Refresh](docs/change-evidence/20260617-planning-entrypoint-proof-refresh.md)
  - [20260616 Continuous Execution Runtime Gate Refresh](docs/change-evidence/20260616-continuous-execution-runtime-gate-refresh.md)
  - [20260614 Continuous Execution Promotion](docs/change-evidence/20260614-continuous-execution-promotion.md)
  - [20260609 Reference Basis And Preflight Hardening](docs/change-evidence/20260609-reference-basis-and-preflight-hardening.md)
- reference governance：
  - [Reference Basis Matrix](docs/research/reference-basis-matrix.md)
  - [Reference Governance And Release Preflight Roadmap](docs/roadmap/reference-governance-and-preflight-roadmap.md)
  - [Reference Governance And Release Preflight Plan](docs/plans/reference-governance-and-preflight-plan.md)
  - [Workflow Governor Governance Plan](docs/plans/workflow-governor-governance-plan.md)
  - [Workflow Governor Governance Roadmap](docs/roadmap/workflow-governor-governance-roadmap.md)
- 历史与证据：
  - [20260609 Live Posture Recovery](docs/change-evidence/20260609-live-posture-recovery.md)（历史恢复里程碑，已归档）
  - [Completed GAP History](docs/archive/completed-gap-history.md)
  - [已完成 GAP 历史归档](docs/archive/completed-gap-history.zh-CN.md)
  - [Change Evidence Index](docs/change-evidence/README.md)

## Verification Shortcuts / 验证捷径
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check RuntimeQuick
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/governance/preflight.ps1 -DisableAutoCommit
```
