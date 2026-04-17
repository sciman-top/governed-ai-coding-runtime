# 2026-04-17 Pre-Implementation Deep Audit And Doc Refresh

## Goal
在真正进入运行时代码实现前，再做一次全仓深度审查，确认规划链条是否已经足够稳定，并把“下一步从哪里开始”的文档入口收紧到可直接执行的状态。

## Current Repo Facts
- 仓库仍处于 `docs-first / contracts-first` 阶段。
- 已落地顶层目录仍是 `docs/`、`schemas/`、`scripts/`；`apps/`、`packages/`、`infra/`、`tests/` 仍是下一阶段要落地的骨架。
- 当前规划主线已经围绕 trial-first、governance-kernel-first、Codex-compatible-first adapter posture 收敛，不再处于“先补架构方向”的阶段。
- 当前工作区不是 clean state；后续实现前仍需先冻结或显式承接已有差异。

## Audit Findings
1. 规划语义主线已经基本一致。`README`、`docs/README`、PRD、交互模型、目标架构、90 天路线图、issue-ready backlog、Phase 0 计划，已经共同指向“先完成 Phase 0 baseline，再进入首个可试跑切片”。
2. 当前主要问题是可发现性而不是方向漂移。根入口和 docs 索引没有把“最新审查结论 + 最新证据 + 当前 Phase 0 执行计划”前置成明确 handoff，导致下次会话很容易再重复一轮仓库普查。
3. 项目级 `AGENTS.md` 仍写着承接 `GlobalUser/AGENTS.md v9.38`，而当前全局规则已经是 `v9.39`；同时，文档对回滚路径仍偏向“无 `.git` 时快照兜底”的旧表述，没有体现当前仓库已具备 git 历史这一事实。
4. 当前验证边界需要明确说明。对 live docs/specs/schemas/examples/script 做 scoped check 时，契约和脚本健康；但 `docs/change-evidence/`、快照副本、历史命名遗留本来就会包含旧路径、旧名称和内嵌命令片段，不应被当成 active docs link baseline。
5. 子目录层级仍缺少稳定导航。`docs/plans/`、`docs/backlog/`、`docs/reviews/`、`docs/change-evidence/` 内虽然已有内容，但没有目录级 README 解释“哪份是当前权威、哪份是历史里程碑、应该从哪里开始读”。
6. 架构与契约族虽然已经成形，但 `docs/architecture/` 与 `docs/specs/` 仍缺少本地索引，导致读者必须依赖根索引或文件名猜测阅读顺序。

## Optimization Decisions
- 不重写 PRD、架构、roadmap、backlog 或 schema 语义；本轮优化只做入口、规则承接、审查留痕收口。
- 在根 `README.md` 和 `docs/README.md` 增加当前 working set，让下一次实现会话直接进入最新 audit、evidence 和 Phase 0 plan。
- 更新项目级 `AGENTS.md` 的承接版本和 git-first rollback 叙述，保留快照作为补充而不是默认路径。
- 把“active verification 必须排除 change-evidence/snapshots”明确记录为当前仓库的审查边界。
- 给 `docs/plans/`、`docs/backlog/`、`docs/reviews/`、`docs/change-evidence/` 增加目录级索引，把当前执行入口和历史沉淀区分开。
- 把 Phase 0 plan 的 source inputs 和起跑说明收紧到“latest review + latest evidence + Task 0 first”，减少下次会话重新扫仓成本。
- 给 `docs/architecture/` 和 `docs/specs/` 增加本地索引，把最小治理闭环、边界矩阵、MVP/target stack、adapter/repo/task 契约的阅读顺序固定下来。

## Updated Execution Posture
- 下一步不是再补规划，而是按 `docs/plans/phase-0-runnable-baseline-implementation-plan.md` 启动 Phase 0。
- 真正开工前，先执行 Phase 0 Task 0：识别并冻结当前 dirty worktree，避免在未知差异上叠加运行时改动。
- 只有当本地 verifier、CI、runtime-consumable control pack、repo admission minimums 落地后，才应进入 deterministic task intake 和 read-only trial slice。
- 目录级导航应优先使用 `docs/plans/README.md`、`docs/backlog/README.md`、`docs/reviews/README.md`、`docs/change-evidence/README.md`，而不是再次从整个 `docs/` 目录做广撒网式重审。
- 深入架构和契约时，优先通过 `docs/architecture/README.md` 与 `docs/specs/README.md` 下钻，而不是仅靠根索引和文件名。

## Residual Risks
- 当前仓库仍缺少 repo-local verifier，导致审查和一致性校验仍依赖人工执行的 scoped commands。
- `build` / `test` / `hotspot` 仍是 `gate_na`，这一事实没有变化。
- 历史 evidence 文档数量已经增多，如果 docs index 不持续维护，未来仍会再次出现“信息在，但入口不清”的问题。

## Expected Benefit
- 下次实现会话可以从 Phase 0 plan 直接起跑，而不是再花一轮时间确认项目当前状态。
- 项目规则、入口文档、审查证据三者之间的承接关系更清楚，后续证据和门禁也更容易自动化。
- review、plan、backlog、evidence 四类资料的“当前权威入口”更稳定，文档规模继续扩大后也不容易再次退回到人工搜索模式。
- architecture 与 specs 的局部阅读成本进一步降低，后续实现会话更容易直接对准正确的约束文档。
