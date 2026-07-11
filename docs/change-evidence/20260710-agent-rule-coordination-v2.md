# 20260710 Agent Rule Coordination v2

## Change Identity

- `issue_id`: `agent-rule-coordination-v2`
- `status`: `complete`
- 风险等级：中；规则源、审计器、控制仓 contract gate 与用户级已部署副本都在变更面内，但不修改 provider/auth/MCP/permission/sandbox，也不重启宿主进程。
- 当前落点：`governed-ai-coding-runtime` 管理 Codex/Claude 用户级全局规则源、同步与目标仓协同审计；9 个目标仓各自维护项目规则真相。
- 目标归宿：`global WHAT + project WHERE/HOW + host DELTA + deterministic enforcement`，形成可验证、可回滚且不盲覆盖目标仓正文的 `1+1>2` 协同框架。

## Before And After

- before：`rule_release=9.54`；项目规则承接仍以 pilot 为主；目标仓范围和 contract 兼容未形成统一机器接口。
- after：`rule_release=9.55`、`project_contract_version=2.0`；9 个目标仓显式 allowlist；共同项目主体为宿主中立 `AGENTS.md`，Claude 默认使用无 BOM 单行 `@AGENTS.md` wrapper。
- scope：`ai-content-delivery-studio`、`classroom-answer-toolkit`、`ClassroomToolkit`、`github-toolkit`、`k12-question-graph`、`local-ai-dev-orchestrator`、`qq-codex-bot`、`skills-manager`、`vps-ssh-launcher`。
- non-target：`external`、`governed-ai-coding-runtime`、`physicist_chinese_poster_batch_tool`、`system-audit`、`文档` 及未显式登记的相邻目录不接受目标仓批量整合；它们仍受用户级全局规则影响。控制仓根规则按自身治理职责单独维护。
- Gemini：不在 managed family；不新增同步、审计或项目正文，不删除历史兼容文件。

## Pre-Change Review

### pre_change_review

- 变更前共同核对控制仓规则源、已部署用户级副本、9 仓真实规则/gate/evidence、目标 allowlist、Schema、同步器、verifier、操作文档与 Codex/Claude 当前官方加载模型；发现 drift 后先整合 canonical source，再执行受保护同步。

### control_repo_manifest_and_rule_sources

- 联合审查 `rules/manifest.json`、`rules/global/codex/AGENTS.md`、`rules/global/claude/CLAUDE.md` 与 `rules/target-project-rule-coordination.json`；manifest 只拥有两个用户级全局副本，coordination 文件只审计 9 个显式目标，不保存或覆盖项目正文。

### user_level_deployed_rule_files

- 同步前比较 `~/.codex/AGENTS.md`、`~/.claude/CLAUDE.md` 与源文件的版本和规范化文本；先 dry-run、再备份/apply、最后 zero-drift。Gemini 不进入 managed family，也没有新增或删除其用户级文件。

### repo_local_gate_scripts_and_ci

- 审查 `scripts/build-runtime.ps1`、`scripts/verify-repo.ps1`、`scripts/doctor-runtime.ps1`、规则同步/审计器及现有 CI/治理入口；本轮只把目标清单 Schema 与可用目标仓审计接入现有 Contract，不新建绕过固定门禁的平行入口。

### repo_local_repo_profile

- 审查 `.governed-ai/repo-profile.json` 与依赖/工具边界；它仍是控制仓自身 profile，不承担目标仓规则分发。context audit 仅用本机 Codex catalog 解析宿主默认窗口，不修改 profile 或用户配置。

### repo_local_readme_and_operator_docs

- 联合审查 `README.md`、`README.zh-CN.md`、`README.en.md`、`docs/README.md` 与 `docs/quickstart/use-with-existing-repo*.md`，确保 global-only sync、9 仓显式审计、Claude 单行 wrapper、非目标目录和回滚口径一致；操作者指南保持中英双语。

### current_official_tool_loading_docs

- Codex 以官方 discovery/源码/本机 `debug prompt-input` 证明用户级与项目链、单环境项目文档总预算和新会话加载；Claude 以官方 memory/import/debug/permissions/subagents 与本机 fresh probe 证明拼接、单行 `@AGENTS.md` import 和 enforcement 边界。

### drift-integration decision

- 决定保留 `global WHAT + project WHERE/HOW + host DELTA + deterministic enforcement`：全局 A/C/D 同义且 B 分宿主，9 仓各自拥有项目正文，控制仓只审计契约。拒绝 blind target sync、同版本盲覆盖、共同正文复制和 Gemini managed family 回归。

## Source Basis

- 完整研究：[Codex / Claude Code 规则加载与协同实践研究](../research/2026-07-10-agent-rules-official-and-community-practices.md)，访问日期 2026-07-10。
- Codex 官方：[AGENTS.md discovery](https://developers.openai.com/codex/guides/agents-md)、[approvals and security](https://developers.openai.com/codex/agent-approvals-security)、[subagents](https://developers.openai.com/codex/agent-configuration/subagents)。
- Codex 固定源码证据：[project rule budget](https://github.com/openai/codex/blob/6138909d6ec58b2fbe635ef973e02caecad5a5aa/codex-rs/core/src/agents_md.rs#L89-L144)、[`debug prompt-input`](https://github.com/openai/codex/blob/6138909d6ec58b2fbe635ef973e02caecad5a5aa/codex-rs/cli/src/main.rs#L227-L236)。
- Claude 官方：[memory and AGENTS import](https://code.claude.com/docs/en/memory#agentsmd)、[configuration debugging](https://code.claude.com/docs/en/debug-your-config)、[permissions](https://code.claude.com/docs/en/permissions)、[subagents](https://code.claude.com/docs/en/sub-agents)。
- 社区固定版本结构参考：[`agentsmd/agents.md@d1ac7f0`](https://github.com/agentsmd/agents.md/blob/d1ac7f063d20e70015ed6732664049ae4ba9d74e/README.md)、[`getsentry/sentry@20ef5cf`](https://github.com/getsentry/sentry/blob/20ef5cf33812bee91de66dfba9a52386b3599911/AGENTS.md)、[`github/awesome-copilot@30472ec`](https://github.com/github/awesome-copilot/blob/30472ecf0fe34cc561df958c08501ecc5ca80ea4/AGENTS.md)、[`vercel/next.js@3bb780e`](https://github.com/vercel/next.js/blob/3bb780e7d65f723297c93640d0ca24c730037770/AGENTS.md)。社区内容只用于结构启发，不作为加载或权限语义真源。

## Freshness And Reference Review

- `python scripts/evaluate-runtime-evolution.py --as-of 2026-07-10 --online-source-check`：`exit_code=0`、`status=pass`、`source_count=35`、`invalid_reasons=0`、`mutation_allowed=false`；复核窗口更新为 `2026-07-10 -> 2026-08-09`。
- 本轮只刷新 `docs/architecture/runtime-evolution-policy.json`、`docs/architecture/reference-required-change-policy.json` 与 `docs/architecture/reference-basis-policy.json` 的已复核日期，不接受或自动落地 evaluator 产生的候选。
- `codex debug models --bundled` 证明当前 `gpt-5.5` 的 `context_window=272000`、`max_context_window=1000000`；用户配置未显式写 `model_context_window`，但 `model_auto_compact_token_limit=220000` 与本机目录有效窗口比例为 `0.8088`。因此修复审计器以读取本机目录事实，不持久化修改用户配置。

### reference_required_review

- 本轮更改规则源、项目规则契约、受保护全局同步、控制仓 release gate、宿主配置审计和三项 30 天 freshness policy；这些高漂移表面必须在同一 diff 中保留官方来源、主要实现、本机证据和采纳决定。

### changed_surface_paths

- `docs/architecture/reference-basis-policy.json`
- `docs/architecture/reference-required-change-policy.json`
- `docs/architecture/runtime-evolution-policy.json`
- `docs/specs/agent-rule-coordination-v2-spec.md`
- `scripts/build-policy-tool-credential-audit.py`
- `scripts/lib/codex_local.py`
- `scripts/verify-agent-rule-family.py`
- `scripts/verify-repo.ps1`
- `scripts/verify-target-project-rules.py`
- `rules/global/codex/AGENTS.md`
- `rules/global/claude/CLAUDE.md`
- `rules/manifest.json`
- `rules/target-project-rule-coordination.json`

### official_sources_reviewed

- OpenAI Codex：官方 `AGENTS.md` discovery、approvals/security、subagents，以及固定提交 `6138909d6ec5` 中的项目规则总预算与 `debug prompt-input` 实现。
- Anthropic Claude Code：官方 memory/import、configuration debugging、permissions 与 subagents 文档；本机 `claude 2.1.206` 和 `claude doctor` 作为实现侧复核。
- 35 项 runtime-evolution source catalog 在 2026-07-10 以只读 online-source-check 重跑；社区文本仅作为候选信号，不进入指令优先级或权限层。

### primary_references_reviewed

- 官方/社区固定版本结构研究见 `docs/research/2026-07-10-agent-rules-official-and-community-practices.md`；规则只采纳可由官方加载模型、本机 help/catalog 和 verifier 共同证明的部分。
- 本地 reference shelf 中所需 13 仓均存在；当前提交记录在下方 `required_local_reference_ids_reviewed`，用于验证宿主、release gate 与 spec-driven workflow 边界。

### local_runtime_evidence_reviewed

- 复核全局 family、九仓 target audit、sync dry-run/apply/zero-drift、九仓 Codex model-visible prompt、三仓 Claude fresh-session probe 与本轮 focused tests。
- 初次 full Runtime gate 暴露三类真实问题：控制仓根规则精简丢失机器依赖语义、测试夹具把当前日期耦合到固定到期日、本机 Codex audit 未读取模型目录默认窗口；均以现有失败或新增 RED 用例复现后修复。
- 未修改 provider/auth/MCP/permission/sandbox、未重启宿主进程、未更改用户 `config.toml`；本机目录读取是只读诊断。

### source_decision

- 采纳官方加载/权限语义、项目链总预算、Claude import 与本机模型目录事实；保留机器门禁和项目不变量所需的精确短句。
- 暂缓 runtime-evolution 候选，不执行 mutation、自动 skill enablement、target sync、push 或 merge；Gemini 继续不属于 managed rule family，历史/观察性参考不获得阻断或同步所有权。

### reference_basis_review

- 规则协同 spec、三项 freshness policy 与 `scripts/verify-repo.ps1` 分别触发宿主边界、spec-driven workflow 与 release-gate reference surface；本轮逐项核对对应 local shelf，而不是把网页研究当成本地引用替代品。

### reference_basis_surface_ids

- `host-and-adapter-boundaries`
- `release-gate-and-ci-boundaries`
- `workflow-governance-and-spec-driven-delivery`

### required_local_reference_ids_reviewed

- `1code@9f1bc76fa437`
- `aider@5dc9490bb35f`
- `anthropic-claude-code@ca9f6045fc90`
- `anthropic-claude-code-action@3d9f0dc7dc27`
- `github-copilot-cli@9776ad4cd36c`
- `github-spec-kit@1b0556c711b6`
- `google-antigravity-cli@ee726c11164d`（仅历史/兼容性 reference，不恢复 Gemini managed family）
- `obra-superpowers@6fd450765978`
- `openai-agents-js@edd0a07b7bcc`
- `openai-agents-python@c359c20647b0`
- `openai-codex@1f0566d3f592`
- `openclaw-code-agent@98ee59b313af`
- `swe-agent@c53556f61b11`

### reference_adoption_decision

- 采用：小而稳定的根规则、共同项目主体、宿主薄 wrapper、明确 gate/evidence/rollback、确定性 schema/verifier、fresh load probes。
- 不采用：盲目 target sync、复制共同正文、把后加载视为 Claude 确定性覆盖、用规则 prose 代替 permissions/hooks/sandbox/CI、恢复 Gemini managed family 或因目录中存在参考仓而声称已实现其能力。

## Changes

- 全局：Codex/Claude 的 A/C/D 共同正文保持逐字一致，B 只保留真实宿主差异；删除易漂移 provider/profile 事实和受管 Gemini 表述。
- 项目：9 仓 `AGENTS.md` 只保留仓库事实、真实 gate、领域不变量、证据与回滚；`CLAUDE.md` 收敛为 import-only wrapper。
- 机器契约：新增 JSON Schema、`9.55 / 2.0` 双版本模型、仓库 anchor/预算/evidence 配置与 enforce/observe 审计。
- verifier：检查首物理行、BOM、wrapper import 集、宿主中立、版本、anchor、预算、证据、回滚、嵌套规则和脏工作树 observation；全局 family 检查 A/C/D 正文 hash 与项目契约版本。
- contract gate：使用 JSON Schema 验证目标清单实例，并审计当前机器可用的目标仓；正式发布仍以 `--require-all` 阻断任一目标缺席。
- 同步：`rules/manifest.json` 只管理 `~/.codex/AGENTS.md` 与 `~/.claude/CLAUDE.md`，不恢复 target-repo blind sync。

## Verification

### TDD Evidence

- RED：新增 contract metadata、schema required field、control-gate wiring 与 global project-contract-version 回归后，focused suite 出现 4 个预期失败。
- GREEN：`python -m unittest tests.runtime.test_verify_target_project_rules tests.runtime.test_verify_agent_rule_family`，`exit_code=0`，`Ran 15 tests`，`OK`。

### Static And Target Audit

- `python -m unittest tests.runtime.test_verify_target_project_rules tests.runtime.test_verify_agent_rule_family tests.runtime.test_agent_rule_sync`：`exit_code=0`，`Ran 20 tests`，`OK`。
- `python scripts/verify-agent-rule-family.py`：`status=pass`、`project_contract_version=2.0`、`common_sections_match=true`、`failures=[]`；Codex/Claude 共同 A/C/D SHA-256 均为 `ebd3666065a2940bd3d038921cfe4e38fc4acb9749c65103b7e9a1a39e248077`。
- `python scripts/verify-target-project-rules.py --require-all`：`status=pass`、`selected=9`、`failed=0`、`unavailable=0`、`blocking=[]`；9 仓 dirty-worktree observation 来自本轮规则改动及已声明既有改动，不是阻断。
- 9 个项目规则为 40-43 行 / 3219-4208 bytes；9 个 wrapper 都是 11 bytes、无 BOM、1 行、精确 `@AGENTS.md`、有末尾换行。
- JSON Schema 实例验证、修改 Python 编译、`verify-repo.ps1` parser、控制仓 `git diff --check` 与 9 仓 scoped diff/UTF-8/尾随空白检查通过。
- 非目标目录未出现本轮项目规则状态变化；`skills-manager/imports/**` 未进入受管嵌套规则审计或改写。

### Deployment And Loading

- pre-sync：live Codex/Claude 都为 `9.54`；intentional dry-run 返回命令 `exit_code=1`、`status=dry_run_changes`、`changed=2`、`blocked=0`，两个条目均为 `would_update 9.54 -> 9.55`。
- apply：`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply` 返回 `exit_code=0`、`status=applied`、`changed=2`、`blocked=0`。
- backup：`docs/change-evidence/rule-sync-backups/20260710-230304/`；其中 Codex/Claude 备份版本均为 `9.54`，raw SHA-256 分别为 `4265d586241b62e0e47ee66e7b68480e262c1dbb0138c5d3ce19525ad69f0d89`、`59d53bad34ad30ff1cd4871e6d72698d8c5fb9e892461a44089d59a2a1aa2adf`。
- post-sync：再次运行 `--fail-on-change` 返回 `exit_code=0`、`status=pass`、`changed=0`、`blocked=0`；Codex/Claude source/live 规范化文本 SHA-256 分别同为 `23c03cfe75852696c403f848e38358407b2583a3860dc2595ae799a0bbab49ae`、`45abc091b82398edcaa15eef1f1065a5de85664e227832ea89eef58e47c46eff`。raw bytes 仅因源 LF/live CRLF 不同，不构成语义漂移。
- Codex：`codex-cli 0.144.1`；help 证明 `debug prompt-input` 可用。9/9 目标仓 fresh process 均从 model-visible prompt 检出全局 `9.55`、项目契约 `2.0`、仓库 heading/anchor、固定门禁、证据和回滚。
- Claude：`2.1.206`，`claude doctor` 返回 `No installation issues found`。在 `ClassroomToolkit`、`ai-content-delivery-studio`、`skills-manager` 的无工具、无会话持久化 fresh probe 中，均返回 `9.55 / 2.0 / repository / gate_order / repo_anchor / evidence_path`；其余 6 仓由全量 wrapper 字节与 import-only audit 覆盖。
- Claude 首次 structured-output 探针因 `$0.05` 上限返回 `error_max_budget_usd`，未作为成功证据；改用单轮文本 JSON 后 3 次成功。全部 Claude 探针累计报告成本约 `$0.20`，未修改 auth/provider/settings。
- 未重启、停止、杀掉或自动拉起 Codex App、Codex/Claude Desktop 或既有 CLI 进程。

### Fixed Gate Order

- build `pass`：`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`，`exit_code=0`，`OK python-bytecode`、`OK python-import`。
- test `pass`：`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`，`exit_code=0`，`100` 个测试文件、`failures=0`、总耗时 `270.673s`，并通过 runtime/service parity 与 wrapper drift guard。
- contract/invariant `pass`：`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`，`exit_code=0`；Schema/catalog、依赖、规则 sync/family、9 仓 target audit、pre-change、reference-required、reference-basis 与 functional-effectiveness 全部 `OK`。
- hotspot `pass`：`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`，`exit_code=0`，`29` 项 doctor 检查全部 `OK`。

### Repair Trace

- `issue_id=runtime-gate-rule-contract-regression`：初次 Runtime 暴露控制仓 `AGENTS.md` 精简丢失核心原则/Cockpit 精确语义；恢复五条高信号长期原则与机器校验短句后，相关测试通过。
- `issue_id=runtime-gate-calendar-fixture-drift`：引用策略与 runtime-evolution 测试把证据逻辑耦合到固定日期；测试改为显式 fixture `as_of` 或从 policy 日期计算，未放宽生产 freshness 检查。
- `issue_id=codex-context-default-audit`：本机 `gpt-5.5` 使用 catalog 默认 `272000` 窗口，audit 误要求显式配置；新增 RED 用例后改为只读解析本机 catalog，保留 `220000 / 272000 = 0.8088` guard-band 校验，不修改用户配置。
- `issue_id=contract-pre-change-evidence-token`：首次 Contract 仅因主证据缺少八个机器 token 阻断；补齐同一 diff 的 manifest/deployed/gate/profile/docs/official/drift review 后，直接 verifier 与最终聚合 Contract 均通过。
- 各 issue 根因不同，均在首次针对性修复后通过；`clarification_mode=direct_fix`，未触发同一 `issue_id` 连续失败阈值。

### Final Closeout

- `python -m unittest tests.runtime.test_verify_target_project_rules tests.runtime.test_verify_agent_rule_family tests.runtime.test_agent_rule_sync`：`Ran 20 tests`、`OK`。
- family：`status=pass`、`9.55 / 2.0`、A/C/D hash 一致、`failures=[]`。
- target：`status=pass`、`selected=9`、`failed=0`、`unavailable=0`、`blocking=[]`；dirty worktree 仅作为 observation。
- global sync zero-drift：`status=pass`、`changed=0`、`blocked=0`，Codex/Claude source 与 deployed normalized hash 分别一致。
- control repo 与 9 仓 scoped `git diff --check` 均 `exit_code=0`；9 份 evidence 为严格 UTF-8、无 BOM、无尾随空白；非目标仓未出现项目规则状态变化。
- `skills-manager` 的 imports/audit/MCP/配置/测试改动和 `vps-ssh-launcher` 的 README/主机脚本/`ssh_tool.py`/测试/live evidence 均保留，未被规则任务回退或覆盖。

## N/A And Evidence Boundary

- 9 个目标仓本轮只修改 Markdown 项目规则/wrapper/evidence；各仓 evidence 逐项记录产品 build/test 的 `gate_na` 四字段，并以控制仓 contract verifier、BOM/首行/anchor/预算检查和 scoped diff hygiene 作为替代证据。
- 静态规则审计不等于目标产品 runtime、真实 provider、数据库、远端发布或真实主机验证；本文件不得据此升级这些能力声明。
- fresh-session 探针若受 workspace trust、外部 import approval、非交互入口或 CLI 能力限制，将记录 `platform_na` 的 `reason / alternative_verification / evidence_link / expires_at`，不得伪造成功。

## Compatibility And Worktree Protection

- 未改公开 API、数据格式、provider/auth、MCP、permission、sandbox、依赖或目标产品运行时代码。
- `skills-manager` 的 `imports/**`、audit/MCP 源码/测试/配置与其他 evidence 是用户既有改动；本任务不回退、不覆盖、不纳入回滚。
- `vps-ssh-launcher` 的 README、主机维护脚本、`ssh_tool.py`、测试与 live-maintenance evidence 是用户既有改动；本任务不回退、不覆盖、不纳入回滚。
- 不修改第三方/generated/vendor/import 目录内的规则文件，不删除历史 `GEMINI.md`，不执行 commit/stage/push。

## Rollback

- 控制仓：仅撤销本任务列出的规则源、manifest/schema、verifier/test、docs 与本 evidence，不对整个工作树执行 reset/restore。
- 用户级副本：优先从 `docs/change-evidence/rule-sync-backups/<timestamp>/` 恢复；或回退规则源后重新执行 guarded global sync，再做零漂移验证。
- 目标仓：每仓只撤销自己的 `AGENTS.md`、`CLAUDE.md` 与 `20260710-agent-rule-contract-v2.md`；不得覆盖其他任务或用户既有改动。
- 回滚后重新运行 family、target audit、sync dry-run 与适用控制仓门禁，确认没有混合版本。
