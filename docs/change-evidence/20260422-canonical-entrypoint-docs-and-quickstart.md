# 2026-04-22 Canonical Entrypoint Docs And Quickstart

## Goal
- 把统一入口策略补成操作者可直接使用的说明。
- 明确 `advisory / targeted_enforced / repo_wide_enforced` 三阶段的选择方式、配置块和 canonical 命令。

## Changes
- `README.md` 增加 canonical entrypoint recommendation。
- `README.zh-CN.md` 增加统一入口建议。
- `docs/quickstart/use-with-existing-repo.md` 增加 `required_entrypoint_policy` 配置块、模式说明、晋级路径、canonical 日常命令。
- `docs/quickstart/use-with-existing-repo.zh-CN.md` 增加对应中文版说明。

## Commands
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`

## Evidence
- 中英 README 已出现统一入口建议。
- 中英 quickstart 已提供可复制的 `required_entrypoint_policy` 示例。
- `verify-repo -Check Contract` 通过。

## Rollback
- 回滚上述四个文档文件与本 evidence 文件即可。
