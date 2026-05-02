# GEMINI.md — governed-ai-coding-runtime（Gemini 项目级）
**项目**: governed-ai-coding-runtime
**承接来源**: `GlobalUser/GEMINI.md v9.47`
**适用范围**: 项目级（仓库根）
**最后更新**: `2026-04-28`

## 1. 阅读指引
- 本文件只写本仓事实、门禁命令、证据位置和回滚入口，不重写全局 `R/E` 语义。
- 固定结构：`1 / A / B / C / D`；三工具项目规则的 `A/C/D` 语义一致，`B` 只放平台差异。
- 裁决链：`运行事实/代码 > 项目级文件 > 全局文件 > 临时上下文`。
- 自包含约束：执行规则以本文件正文为准，不依赖外部子文档或治理脚本作为前置条件。
- 渐进披露边界：根文件保留本仓归宿、门禁、阻断、证据和回滚；长 runbook、批量目标仓细节和历史证据放入 `docs/` 或按需 imports。
- 精简原则：根文件只写本仓可验证事实、硬门禁、阻断和回滚；长示例、历史背景、排障细节进入子文档。

## A. 项目基线
### A.1 事实边界
- 本仓是 governed AI coding runtime 的控制仓；当前核心目录为 `docs/`、`schemas/`、`scripts/`、`packages/`、`tests/`。
- 文档、决策、审查结论归 `docs/`；机器可读契约归 `schemas/`；GitHub/规划/同步脚本归 `scripts/`；运行时契约代码归 `packages/`；验证归 `tests/`。
- 规则文件家族由 `rules/manifest.json` 管理，目标包括 3 个全局用户级文件与 15 个目标仓项目级文件。
- `docs/specs/*` 定义语义，`schemas/jsonschema/*` 是配套机器可读草案；修改其一必须同步检查另一侧。
- `scripts/github/create-roadmap-issues.ps1` 只负责 backlog/issue 种子生成，不代表运行时实现已经存在。

### A.2 执行锚点
- 每次改动先声明：当前落点 -> 目标归宿 -> 验证方式。
- 默认中文沟通、中文解释、中文汇报；代码标识符、命令、日志、报错和 schema 字段保留英文原文。
- 当前权威输入顺序：根 `README.md` -> `docs/README.md` -> PRD -> Architecture -> Roadmap -> Backlog -> Specs -> Schemas。
- 本仓面向 `Codex / Claude Code / 本机操作者` 的长期核心原则是“综合效率优先”：少打扰、自动连续执行、节省 token / 成本、高效率。
- 具体模型、推理档位、compact 阈值、provider、交互方式与自动化细节都只是该原则下的阶段性实现；后续可调整，但不得高于该原则本身。
- 全局规则给风险、语言、N/A 和门禁语义；本文件给本仓目录归宿、真实命令、阻断条件、证据位置和回滚入口。
- 项目规则只保留本仓不可由代码/CI自动推断且会改变执行、风险或验收的事实；长流程下沉到子文档或工具专属规则。
- 规则文件、门禁、profile、baseline 或同步脚本修改前，必须先比对控制仓 `governed-ai-coding-runtime/rules/manifest.json`、源文件、用户目录/目标仓已分发副本、目标仓真实 gate/profile/CI/script/README 差异和当前工具官方加载模型；发现漂移先整合再同步，不盲目覆盖。
- 面向操作者的使用说明/指南/教程类文档必须保持中英双语可用；纯策略、研究、架构、规划、ADR 默认不强制逐篇双语。

### A.3 N/A 分类与字段
- `platform_na`：平台能力缺失、命令不存在或非交互限制导致命令不可用。
- `gate_na`：门禁步骤客观不可执行（含脚本缺失、纯文档/注释/排版改动）。
- 两类 N/A 均必须记录：`reason`、`alternative_verification`、`evidence_link`、`expires_at`。
- N/A 不得改变门禁顺序：`build -> test -> contract/invariant -> hotspot`。

### A.4 触发式澄清协议
- 默认执行：`direct_fix`（先修复、后验证）。
- 触发条件：同一 `issue_id` 连续失败达到阈值（默认 `2`），或现象/期望持续冲突。
- 一次最多 3 个澄清问题；确认后恢复 `direct_fix` 并清零失败计数。
- 留痕字段：`issue_id`、`attempt_count`、`clarification_mode`、`clarification_questions`、`clarification_answers`。

## B. Gemini 平台差异
- 用户规则：`~/.gemini/GEMINI.md`；项目/工作区规则按 Gemini CLI 层级加载和按需发现执行。
- 启用 Trusted Folders 时，未受信目录可能进入 safe mode；遇到项目配置、环境变量、自动记忆或工具自动批准未生效，先记录 trust 状态或替代证据。
- 可用 `@file.md` imports 组织长内容；只有本机 `settings.json` 明确配置上下文文件名时，才把其他文件名视为 Gemini 上下文文件，具体键名以当前 schema/help 为准。
- 大仓或生成目录用 `.geminiignore` 排除缓存、构建产物、日志和敏感本地配置；修改后用 `/memory show` 核查完整上下文。
- 来源与刷新命令先看当前 `/memory` help，支持则用 `/memory list` / `/memory refresh`，否则记录版本并用 `/memory reload` 兜底；非交互不可用时按 `platform_na` 记录。
- 不假定 `GEMINI.override.md` 存在；临时排障规则必须记录清理点，结论后删除或恢复并复测。
- `GEMINI.md` 是上下文规则；确定性验证、安全拦截和回滚能力应落到本仓门禁、MCP/扩展、checkpoint/restore 或 CI。

## C. 项目差异
### C.1 模块职责
- `rules/`：Codex/Claude/Gemini 全局与项目规则源。
- `docs/targets/`：目标仓 catalog、governance baseline、rollout contract。
- `scripts/sync-agent-rules.py` / `.ps1`：规则源到用户目录和目标仓的同步入口。
- `scripts/runtime-flow-preset.ps1`：目标仓治理 baseline 下发与 runtime flow 编排。
- `scripts/verify-repo.ps1`：本仓 contract/runtime/dependency/doctor 门禁聚合入口。
- `packages/contracts/`、`tests/runtime/`：运行时契约代码与单元测试。

### C.2 门禁命令与顺序（硬门禁）
- build：`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- test：`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- contract/invariant：`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- hotspot：`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- fixed order：`build -> test -> contract/invariant -> hotspot`
- quick feedback：`python -m unittest tests.runtime.test_governance_gate_runner tests.runtime.test_target_repo_governance_consistency tests.runtime.test_runtime_flow_preset.RuntimeFlowPresetScriptTests.test_runtime_flow_preset_apply_governance_baseline_only_bootstraps_blank_target tests.runtime.test_target_repo_rollout_contract tests.runtime.test_target_repo_speed_kpi`，只作日常反馈，不替代 full gate。

### C.3 失败分流与阻断
- `docs/specs/*` 与 `schemas/jsonschema/*` 只改一侧时阻断。
- 根 `README.md`、`docs/README.md`、`docs/roadmap/*`、`docs/backlog/*` 叙述不一致时阻断。
- `scripts/github/create-roadmap-issues.ps1` 与当前 roadmap/backlog 基线不一致时阻断。
- agent rule sync drift、target governance consistency drift、dependency baseline drift 均属 contract 阻断。

### C.4 证据与回滚
- 证据统一落在 `docs/change-evidence/`；规划、schema、脚本、规则、治理 baseline 变更必须新增证据。
- 最低字段：规则 ID、风险等级、执行命令、关键输出、兼容性判断、回滚动作。
- 默认回滚优先使用 git 历史；需要额外快照时放入 `docs/change-evidence/snapshots/<date>-<slug>/`。

### C.5 同步入口
- drift dry-run：`python scripts/sync-agent-rules.py --scope All --fail-on-change`
- 一键同步：`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply`
- 目标仓治理一致性：`python scripts/verify-target-repo-governance-consistency.py`
- 同版本内容漂移不得盲覆盖；先整合源文件，再按 manifest 同步。

## D. 维护校验清单
- 仅落地本仓事实，不复述全局规则正文。
- 与全局职责互补，不重叠、不缺失。
- 协同链完整：`规则 -> 落点 -> 命令 -> 证据 -> 回滚`。
- `Global Rule -> Repo Action`：
  - `R6`: 本仓门禁命令是硬门禁；quick/fast 只能作为已声明的日常反馈切片，交付前仍按 full gate 或固定顺序收口。
  - `R8`: 证据与回滚字段是最小留痕；缺字段必须按 N/A 口径说明。
  - `E4`: `scripts/doctor-runtime.ps1` 与 `verify-repo.ps1 -Check Doctor` 承接健康/热点检查。
  - `E5`: `docs/dependency-baseline.*` 与 `scripts/verify-dependency-baseline.py` 承接供应链门禁。
  - `E6`: `docs/specs/*`、`schemas/jsonschema/*`、`schemas/catalog/schema-catalog.yaml`、`rules/manifest.json` 结构变化必须记录兼容性、迁移和回滚。
- 本文件属于控制仓 `governed-ai-coding-runtime/rules/manifest.json` 管理的规则家族；目标仓现场修改必须回写控制仓源文件后再同步。
- 子文档只承载细节，不替代根文件中的硬门禁和项目事实。
- 三文件同构约束：`A/C/D` 必须语义一致，仅 `B` 允许平台差异。
