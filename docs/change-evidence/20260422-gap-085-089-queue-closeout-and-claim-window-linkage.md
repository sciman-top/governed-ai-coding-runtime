# 2026-04-22 GAP-085~089 Queue Closeout And Claim Window Linkage

## Goal
- 将 `GAP-085` 到 `GAP-089` 从“active queue item”收敛为“已完成闭环”状态。
- 对齐入口文档中的 queue posture，消除 active/completed 口径漂移。
- 把 speed 相关 claim 明确绑定到 KPI measured-window 快照证据。

## Changes
- backlog 状态闭环：
  - `docs/backlog/issue-ready-backlog.md`
    - `GAP-085`~`GAP-089` 状态更新为 complete（2026-04-22）
    - 对应 acceptance criteria 全部勾选为 `[x]`
    - 顶部执行姿态与队列说明更新为 `GAP-080`~`GAP-089` completed
- 入口口径同步：
  - `docs/backlog/README.md`
  - `docs/backlog/full-lifecycle-backlog-seeds.md`
  - `docs/README.md`
  - 同步为 `GAP-080`~`GAP-089` completed，后续新队列需使用 `GAP-089` 之后的新 id
- speed claim 窗口化：
  - `docs/product/multi-repo-trial-loop.md`
  - `docs/product/multi-repo-trial-loop.zh-CN.md`
  - 增加 measured-window 约束说明（引用 `kpi-latest.json` / `kpi-rolling.json`）
  - `docs/product/claim-catalog.json`
    - 新增 `CLM-005`，proof command 指向 `scripts/export-target-repo-speed-kpi.py`
    - evidence_link 绑定 `docs/change-evidence/20260421-gap-088-089-context-pack-and-speed-kpi-baseline.md`

## Verification
- 硬门禁顺序：
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- 文档与脚本漂移检查：
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`

## Risks
- queue 已闭环但 `GAP-090+` 尚未定义，后续执行需要先补新 ids 与依赖映射。
- speed KPI 仍是 baseline 指标，跨适配器精细时钟对齐仍有后续优化空间。

## Rollback
- `git checkout -- docs/backlog/issue-ready-backlog.md docs/backlog/README.md docs/backlog/full-lifecycle-backlog-seeds.md docs/README.md docs/product/multi-repo-trial-loop.md docs/product/multi-repo-trial-loop.zh-CN.md docs/product/claim-catalog.json`
- `git checkout -- docs/change-evidence/20260422-gap-085-089-queue-closeout-and-claim-window-linkage.md`
