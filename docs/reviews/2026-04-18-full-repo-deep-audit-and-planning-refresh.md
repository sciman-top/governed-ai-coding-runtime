# 2026-04-18 Full Repo Deep Audit And Planning Refresh

## Goal
再次对全仓做一轮深度审查，确认在 `Foundation / GAP-020` 到 `GAP-023` 完成后，当前活跃规划链、执行入口、自动化种子和子目录导航是否仍然一致，并把明显漂移收口到可直接执行的状态。

## Current Repo Facts
- 当前权威执行队列已经从 `Foundation` 切到 `Full Runtime / GAP-024`。
- `packages/contracts/`、`tests/runtime/`、`scripts/build-runtime.ps1`、`scripts/doctor-runtime.ps1` 与 `scripts/verify-repo.ps1` 已形成可运行的 Foundation 基线。
- `build -> test -> contract/invariant -> hotspot` 四个项目级硬门禁在本次审查开始时均可本地通过。
- 本轮审查过程中还确认并修复了 `verify-repo.ps1 -Check Docs` 的一个边界问题：它原本会把 `.worktrees/` 下的 ignored/generated Markdown 副本当作 active docs 扫描，导致 `-Check All` 误报失败；修复后全量 verifier 已恢复通过。
- 当前 Full Runtime 语义已经收敛为“先把真实 runtime path 跑通，再补更丰富的 operator UI”；也就是 `GAP-027` 优先交付 CLI-first operator surface，而不是先做 Web UI。
- `docs/change-evidence/` 与 `docs/change-evidence/snapshots/` 中存在大量历史术语、旧项目名、旧 `gate_na` 记录与旧路径，这是被保留的审计事实，不是当前 active docs baseline。

## Findings
1. 规划主线已经基本稳定。`README`、`docs/README`、Full Lifecycle Plan、Issue-Ready Backlog、Full Runtime Implementation Plan、Foundation closeout evidence 之间对“当前已完成什么、下一步从哪里开始”已经能形成主链。
2. 仍有一组 active planning artifacts 没有跟上最新主线。`docs/backlog/full-lifecycle-backlog-seeds.md` 还在写 `Foundation` 是当前执行队列，`docs/backlog/issue-seeds.yaml` 与 `scripts/github/create-roadmap-issues.ps1` 还在使用 `operator UI` 命名，这与 `20260418-full-runtime-cli-first-planning-realignment.md` 的结论不一致。
3. 若只看子目录 README，当前仓库状态会被低估。`packages/README.md`、`packages/contracts/README.md`、`tests/README.md`、`apps/README.md`、`infra/README.md` 中仍有明显的 `Phase 0` / `Phase 1 starts` 语气，无法准确表达当前“contracts + tests + live gates 已落地，但服务层仍未落地”的真实状态。
4. 审查与证据索引没有及时前移。`docs/reviews/README.md` 和 `docs/change-evidence/README.md` 仍把 `2026-04-17` 的 pre-Foundation 审查当作当前 baseline，这会让后续会话重复回到旧 handoff，而不是从最新 Full Runtime 入口继续。
5. 历史 evidence 文档中的 `gate_na`、旧项目名和旧阶段命名不应被“清理掉”。这些内容是审计事实，应通过索引和验证边界说明来隔离，而不是改写原始记录。
6. verifier 本身也存在一个真实 blind spot。`Invoke-ActiveMarkdownLinkCheck` 递归扫描整个工作区，未尊重 `.gitignore`，因此只要仓库里存在 ignored worktree 或 dist 副本，就可能出现与 active docs 无关的假失败。

## Optimization Decisions
- 不改写历史 evidence 正文，只修 active docs、active seeds、active script 与目录导航。
- 把 `GAP-027` 的 active 命名统一成 `Minimal Operator Surface`，并在自动化种子里同步 `CLI-first` 的阶段边界。
- 把 review/evidence 索引前移到本轮审查结果，避免下一次会话再次从 `2026-04-17` 的 pre-Foundation handoff 开始。
- 收紧根入口与子目录 README，使读者能更快区分“当前已落地的 contract substrate”和“仍未落地的 runtime/service/public-release 边界”。
- 明确保留一条审查边界：`docs/change-evidence/**` 与 `snapshots/**` 可以保留历史漂移，但它们不参与 active docs baseline 的命名与语义收口。
- 修复 `verify-repo.ps1` 的 Markdown 文件枚举逻辑，优先使用 `git ls-files --cached --others --exclude-standard` 收集 active docs，并补一个 `.worktrees/` 回归测试。

## Current Working Set
- lifecycle roadmap: `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- active plan: `docs/plans/full-runtime-implementation-plan.md`
- execution backlog: `docs/backlog/issue-ready-backlog.md`
- active seeds: `docs/backlog/full-lifecycle-backlog-seeds.md`, `docs/backlog/issue-seeds.yaml`
- seeding automation: `scripts/github/create-roadmap-issues.ps1`
- latest evidence anchor: `docs/change-evidence/20260418-full-repo-deep-audit-and-planning-refresh.md`

## Residual Risks
- `scripts/github/create-roadmap-issues.ps1` 已不再手写 task / epic / initiative body；其 Markdown parser contract 已纳入 `scripts/verify-repo.ps1 -Check Scripts`，后续如果 source docs 结构漂移，会在门禁中失败，而不是依赖人工记忆。
- 当前所有通过的门禁仍然只证明“Foundation substrate 可运行”，并不证明 `Full Runtime` 已经落地。
- 一些历史文档仍会继续出现 `Phase 0`、`Phase 1`、`gate_na`、旧项目名等词汇；必须依赖索引和验证边界，而不能要求历史证据与当前语义完全一致。
- `git diff --check` 当前没有空白错误，但会继续提示多个文件将在未来被 Git 归一化为 `CRLF`；这属于行尾告警，不是本轮功能性阻断。

## Recommended Next Step
直接从 `docs/plans/full-runtime-implementation-plan.md` 进入 `GAP-024`，优先落地：
1. execution worker
2. managed workspace runtime
3. artifact persistence
4. runtime health and query surface

在这些 runtime read models 稳定之前，不要把 `GAP-027` 重新扩展回强制 Web UI 任务。
