# GEMINI.md — governed-ai-coding-runtime 项目承接规则
**承接来源**: `GlobalUser/GEMINI.md v9.44`
**适用范围**: `governed-ai-coding-runtime 仓库根目录（repo root）`
**最后更新**: `2026-04-27`

## 1. 阅读指引
- 本文件只写本仓事实、门禁命令、证据位置和回滚入口，不重写全局 `R/E` 语义。
- 渐进披露边界：本文件必须自包含保留本仓归宿、门禁、阻断、证据和回滚；长 runbook、批量目标仓细节和历史证据可放 `docs/` 子文档，但不得成为执行前置条件。
- 精简原则：根文件只写本仓可验证事实、硬门禁、阻断和回滚；长示例、历史背景、排障细节进入 `docs/` 或按需 imports。

## A. 项目基线
- 当前权威输入顺序：根 `README.md` -> `docs/README.md` -> PRD -> Architecture -> Roadmap -> Backlog -> Specs -> Schemas。
- AI 编码沟通默认中文；计划、审查、证据摘要和提交说明优先中文，代码标识符、命令、日志、报错、schema 字段保留英文原文。
- 全局规则给风险、语言、N/A 和门禁语义；本文件给本仓目录归宿、真实命令、阻断条件、证据位置和回滚入口。
- 项目规则只保留本仓不可由代码/CI自动推断且会改变执行、风险或验收的事实；长流程下沉到子文档或工具专属规则。
- 规则写法优先采用可验证边界：真实命令、禁止绕过项、证据路径和回滚入口；避免在根文件堆叠不可检查的抽象偏好。
- 文档、决策、审查结论归 `docs/`；机器可读契约归 `schemas/`；GitHub / 规划辅助脚本归 `scripts/`；实现骨架归 `apps/`、`packages/`、`infra/`、`tests/`。
- 面向操作者的使用说明/指南/教程类文档必须保持中英双语可用。

## B. Gemini 平台差异
- 用户规则：`~/.gemini/GEMINI.md`；项目/工作区规则按 Gemini CLI 层级加载和按需发现执行。
- 启用 Trusted Folders 时，未受信目录可能进入 safe mode；遇到项目配置、环境变量、自动记忆或工具自动批准未生效，先记录 trust 状态或替代证据。
- 可用 `@file.md` imports 组织长内容；只有本机 `settings.json` 明确配置 `context.fileName` 时，才把其他文件名视为 Gemini 上下文文件。
- 大仓或生成目录用 `.geminiignore` 排除缓存、构建产物、日志和敏感本地配置；修改后用 `/memory show` 核查完整上下文；来源与刷新命令先看当前 `/memory` help，支持则用 `/memory list` / `/memory refresh`，否则记录版本并用 `/memory reload` 兜底。
- 不假定 `GEMINI.override.md` 存在；诊断优先执行 `gemini --version`、`gemini --help`；交互场景用 `/memory show` 查完整上下文；来源与刷新命令先看当前 `/memory` help，支持则用 `/memory list` / `/memory refresh`，否则记录版本并用 `/memory reload` 兜底；非交互不可用时按 `platform_na` 记录。
- `GEMINI.md` 是上下文规则；确定性验证、安全拦截和回滚能力应落到本仓门禁、MCP/扩展、checkpoint/restore 或 CI。
- 替代命令仅用于补证据，不得改变本仓门禁顺序与阻断语义。

## C. 仓库门禁与阻断
- build：`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- test：`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- contract/invariant：`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- hotspot：`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- fixed order：`build -> test -> contract/invariant -> hotspot`
- 阻断：`docs/specs/*` 与 `schemas/jsonschema/*` 只改一侧；README/docs/roadmap/backlog 叙述不一致；issue seeding script 与 roadmap/backlog 基线不一致。

## D. 证据、回滚与维护
- 证据统一落在 `docs/change-evidence/`；规划、schema、脚本类变更必须新增证据。
- 历史回滚优先通过 git 提交或差异恢复；额外快照只作为兜底。
- `Global Rule -> Repo Action`：
  - `R6`: 本仓门禁命令是硬门禁；quick/fast 只能作为已声明的日常反馈切片，交付前仍按 full gate 或固定顺序收口。
  - `R8`: 证据与回滚字段是最小留痕；缺字段必须按 N/A 口径说明。
  - `E4`: `scripts/doctor-runtime.ps1` 与 `verify-repo.ps1 -Check Doctor` 承接健康/热点检查。
  - `E5`: `docs/dependency-baseline.*` 与 `scripts/verify-dependency-baseline.py` 承接供应链门禁。
  - `E6`: `docs/specs/*`、`schemas/jsonschema/*`、`schemas/catalog/schema-catalog.yaml` 的结构变更必须同步迁移与回滚说明。
- 若新增项目级子文档，只允许承载长清单、runbook、历史背景或示例；根规则文件仍必须能独立指导一次完整变更。
