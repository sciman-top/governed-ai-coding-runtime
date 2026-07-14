# AGENTS.md - governed-ai-coding-runtime
**项目契约**: 2.0
**全局规则复核**: 9.56
**适用范围**: 仓库根
**最后更新**: 2026-07-14

## 1. 当前落点与目标归宿
- 当前落点：本仓是 governed AI coding runtime 的控制仓，负责全局规则源、机器契约、治理运行时、审计与同步工具。
- 目标归宿：保持“全局 WHAT + 项目 WHERE/HOW + 宿主 DELTA + 确定性 enforcement”的治理 sidecar；不替代 Codex、Claude Code 或目标仓自身事实。
- 当前最小里程碑：完成 `9.56 / 项目契约 2.0 / coordination 2.3` 发布、9 个动态发现且显式登记的目标仓审计、受保护全局同步与 fresh-process 加载证明。
- 事实裁决顺序：运行事实/代码 -> 根 `README.md` -> `docs/README.md` -> PRD/Architecture/Roadmap/Backlog -> Specs/Schemas；这不是宿主指令优先级。
- 根规则只保留本仓高频事实、阻断、门禁、证据和回滚；长研究、runbook、计划与历史证据放入 `docs/`。

## A. 仓库事实与模块边界
- `rules/global/`：Codex/Claude 全局用户规则源；`rules/manifest.json` 只分发两个用户级全局副本。
- `rules/target-project-rule-coordination.json`：9 个目标仓的显式 allowlist、直接子 Git 根发现契约与审计契约；只审计，不保存或覆盖目标仓正文。
- `schemas/jsonschema/`：机器可读契约；`docs/specs/`：对应语义规范；修改任一侧必须检查另一侧与 schema catalog。
- `scripts/sync-agent-rules.py` / `.ps1`：global-only 同步入口；`scripts/verify-agent-rule-family.py` 与 `scripts/verify-target-project-rules.py`：规则协同 verifier。
- `rules/templates/github/agent-rule-contract.yml` 是目标仓规则 CI 规范模板；`scripts/export-target-rule-ci-matrix.py` 与 `.github/workflows/agent-rule-coordination.yml` 承接九仓矩阵聚合审计。
- `packages/contracts/`、`tests/runtime/`：运行时契约与回归测试；`scripts/verify-repo.ps1`、`scripts/doctor-runtime.ps1`：聚合门禁。
- 文档/决策/证据归 `docs/`；schema 归 `schemas/`；自动化归 `scripts/`；运行时代码归 `packages/`；测试归 `tests/`。
- `scripts/github/create-roadmap-issues.ps1` 只生成 backlog/issue 种子，不证明运行时实现已经存在。
- 本仓长期原则的机器细则以 `docs/architecture/core-principles-policy.json` 为准，根规则保留以下会改变执行和验收的五条口径。
- `综合效率优先，安全边界约束`：少打扰、自动连续执行、节省 token / 成本、保留必要解释、高效率；阶段性模型/provider/profile 选择不得绕过安全、证据、回滚、review 和门禁。
- `自动优先，外层 AI 辅助，门禁控制演进`：确定性治理工作优先自动化；外层 AI 只生成 review、知识、候选和建议，有效变更仍须经过风险分级、机器门禁、证据、回滚和必要 review。
- `治理中枢，可复用契约，宿主兼容执行`：本仓是治理 sidecar/control plane，不竞争或替代 Codex、Claude Code 等宿主；外部 agent 项目只作为可验证机制来源。
- `上下文预算与指令最小化 + 最小权限工具/凭据边界`：根规则短而硬；工具输出必须保持高信号、可裁剪、可复用；工具权限、凭据、sandbox、mount、network、provider secret 和 MCP/tool identity 必须可审计并尽量由确定性控制执行。
- `效果反馈优先于完成声明`：完成声明必须有 fresh repo-local evidence、eval trace、trace/replay/trajectory refs、effect feedback、verification command 与 rollback；文档、代码或候选文件存在本身不等于完成。

## B. 执行与风险边界
- 改动前声明当前落点 -> 目标归宿 -> 验证方式，并比对规则源、已部署副本、manifest、coordination allowlist、目标真实 gate/CI/script/README 与当前官方加载模型。
- 全局共同 A/C/D 必须逐字一致，平台差异只在 B；目标 `AGENTS.md` 必须宿主中立，目标 `CLAUDE.md` 默认只有无 BOM 首行 `@AGENTS.md`。
- 同版本内容漂移不得盲覆盖；先整合源文件，再 dry-run、备份、apply、零漂移复核。
- 规则 prose 不代替 permissions、sandbox、exec policy、hooks、scripts、schema 或 CI；强制性声明必须能指向机器控制或明确记录缺口。
- 本机 Codex/Cockpit Direct OAuth、Direct API 和 Cockpit API service 往返切换由 Cockpit Tools 完全负责；本仓不得提供 8770 页面动作、operator action、repair/smoke/checker、profile 写入、LiteLLM gateway 管理、history bucket 写入、launcher/no-op 包装或后台切换守护。
- 本仓只允许保留旧项目 shim 清理和缺席验证：`Disable-CodexProjectInterop.ps1` 与 `Test-CodexGuardAbsence.ps1`。它们只能证明或移除旧 guard/wrapper/shortcut，不得写入当前 Codex auth/provider/history/Cockpit account state。
- 禁止恢复 `codex-interop-check.py`、`CodexProjectionSmoke`、`CodexApiProjectionRepair`、`CodexOauthProjectionRepair`、`CodexLaunchBindingRepair`、`Manage-LiteLLMGateway.ps1`、`codex-cockpit-switch-guard.py`、generic `--apply`、`--migrate-provider-bucket`、SQLite provider trigger、后台 guard、no-op launcher、restart wrapper 或自动重启 Codex。
- 未经当前任务明确确认，不得重启、停止、杀掉或自动拉起 Codex App、`codex`、Claude Code、Claude Desktop 或 `claude` 进程。
- 面向操作者的指南/教程保持中英双语可用；策略、研究、架构、规划与 ADR 默认不要求逐篇双语。

## C. 门禁、阻断与证据
### C.1 固定门禁
- fixed order：`build -> test -> contract/invariant -> hotspot`。
- build：`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- test：`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- contract/invariant：`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`；包含全局 family、目标清单 schema 与当前可用目标仓审计，正式发布仍额外执行 `--require-all`。
- hotspot：`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- quick feedback：`python -m unittest tests.runtime.test_verify_target_project_rules tests.runtime.test_verify_agent_rule_family tests.runtime.test_agent_rule_sync`；只作日常切片，不替代 full gate。

### C.2 规则发布入口
- family：`python scripts/verify-agent-rule-family.py`
- target audit：`python scripts/verify-target-project-rules.py --require-all`
- target CI matrix：`python scripts/export-target-rule-ci-matrix.py`
- global dry-run：`python scripts/sync-agent-rules.py --scope All --fail-on-change`
- global apply：`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply`
- 发布顺序：静态 family/target 审计 -> dry-run 与备份确认 -> apply -> 零漂移 -> fresh loading probes -> 固定门禁。

### C.3 阻断、证据与回滚
- `docs/specs/*` 与 `schemas/jsonschema/*` 只改一侧、schema catalog 未登记、规则 family 漂移、目标契约不兼容或依赖 baseline 漂移时阻断。
- README/docs/roadmap/backlog 与代码事实不一致，或把 setup/install、重复命令伪装为独立门禁时阻断。
- 证据落在 `docs/change-evidence/`；最低字段为规则/issue ID、风险、命令、exit code、关键输出、兼容性、N/A、回滚与 fresh evidence 时间。
- 全局部署回滚使用 sync backup + 回退后的规则源；控制仓回滚仅撤销本任务文件；各目标仓只撤销各自 `AGENTS.md / CLAUDE.md / rollout evidence`，不得碰既有脏工作树。
- 额外快照仅在 Git 历史不足时放入 `docs/change-evidence/snapshots/<date>-<slug>/`。

## D. Global Rule -> Repo Action
- `R1/R2/R3/R5`：先声明落点/归宿/验证，以计划与小步测试闭环；临时兼容必须写回收条件。
- `R4/R7`：规则发布先静态审计与 dry-run；同步、持久化、provider/auth 和进程操作遵守确认与兼容边界。
- `R6`：交付前严格执行 C.1；quick feedback 不能替代 full gate。
- `R8`：`docs/change-evidence/` 承接依据、命令、证据与回滚，缺失项按全局 N/A 字段记录。
- `E4`：`doctor-runtime.ps1` 与 `verify-repo.ps1 -Check Doctor` 承接健康/热点。
- `E5`：`docs/dependency-baseline.*` 与 `scripts/verify-dependency-baseline.py` 承接供应链。
- `E6`：Specs/Schemas/catalog/manifest 结构变化必须记录兼容、迁移与回滚。
- 协同验收：仅凭全局 + 本文件必须能推出当前落点、目标归宿、门禁顺序、证据路径和回滚入口。
