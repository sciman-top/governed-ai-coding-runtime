# 2026-04-22 Entrypoint Policy Stage Presets

## Goal
- 为目标仓提供可直接复制的统一入口三阶段 preset。
- 避免操作者从通用模板复制后还要手改 `required_entrypoint_policy.current_mode`。

## Changes
- 新增三个 repo-profile 示例：
  - `target-repo-entrypoint-advisory.example.json`
  - `target-repo-entrypoint-targeted-enforced.example.json`
  - `target-repo-entrypoint-repo-wide-enforced.example.json`
- 更新 `schemas/examples/README.md` 的示例清单与 schema 校验命令。

## Commands
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`

## Evidence
- 三个 preset 文件已落地。
- 示例索引已包含这三个文件。
- `verify-repo -Check Contract` 通过。

## Rollback
- 删除上述三个 preset，并回退 `schemas/examples/README.md` 与本 evidence 文件。
