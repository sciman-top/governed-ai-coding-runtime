# Codex / Claude Code 规则加载与协同实践研究

- 研究日期：2026-07-10
- 适用对象：OpenAI Codex CLI/App、Anthropic Claude Code，以及同时服务两者的目标仓
- 证据等级：官方文档与官方源码/示例优先；社区仓库只用于提炼可验证结构，不作为指令源
- 研究目标：校准全局用户级规则与项目级规则的加载语义、边界、渐进披露、权限承接和验证方式，为“1+1>2”协同框架提供可执行依据

## 1. 结论摘要

1. **共同主体应放在项目根 `AGENTS.md`，Claude 用薄 `CLAUDE.md` 显式 `@AGENTS.md` 导入。** Anthropic 已明确说明 Claude Code 不自动读取 `AGENTS.md`，并正式推荐该写法；Windows 上也优先使用 import，而不是需要管理员权限或 Developer Mode 的 symlink。[Claude AGENTS.md](https://code.claude.com/docs/en/memory#agentsmd)，访问日期 2026-07-10。
2. **Codex 与 Claude 的“更具体规则”不是同一种机制。** Codex 按根到当前目录合并，每层只取一个文件，靠后的近目录规则用于覆盖前文；Claude 将所有发现的 `CLAUDE.md` / `CLAUDE.local.md` 拼接进上下文，官方明确说冲突时模型可能任意选择。因此跨工具项目不能依赖文字冲突实现 override，必须通过“全局只写共性、项目只写仓库事实、wrapper 只写平台差异”来消除冲突。[Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md#how-codex-discovers-guidance)、[Claude load model](https://code.claude.com/docs/en/memory#how-claude-md-files-load)，访问日期 2026-07-10。
3. **规则文件是指导层，不是权限系统。** 高风险拒绝、工具授权、文件系统/网络边界和交付门禁应分别落到 Codex sandbox/approval/exec policy、Claude permissions/PreToolUse hook/sandbox，以及仓库脚本或 CI。[Codex approvals & security](https://developers.openai.com/codex/agent-approvals-security)、[Claude permissions](https://code.claude.com/docs/en/permissions)，访问日期 2026-07-10。
4. **渐进披露必须使用宿主的真实按需能力。** Codex 用目录级嵌套 `AGENTS.md`；Claude 用按目录读取触发的嵌套 `CLAUDE.md`、带 `paths` 的 `.claude/rules/**/*.md`，低频多步骤流程用 skills。Claude import 在启动时展开，不能节省 context。[Codex AGENTS.md](https://developers.openai.com/codex/guides/agents-md)、[Claude rules](https://code.claude.com/docs/en/memory#organize-rules-with-clauderules)、[Claude imports](https://code.claude.com/docs/en/memory#import-additional-files)，访问日期 2026-07-10。
5. **完成验证不能只检查文件存在。** Codex 应用新 run/session 询问活动指令并查 TUI/session 日志；Claude 应结合 `/context`、`/memory`、`/permissions`、`InstructionsLoaded`、`claude doctor`，必要时用 `--safe-mode` 做差分诊断。[Codex verification](https://developers.openai.com/codex/guides/agents-md#verify-your-setup)、[Claude configuration debugging](https://code.claude.com/docs/en/debug-your-config)，访问日期 2026-07-10。
6. **“事实裁决”和“平台指令优先级”必须拆开写。** Codex 官方基础提示明确是 system/developer/user 指令高于 `AGENTS.md`；运行结果和代码用于发现规则漂移，不是一个可覆盖平台指令的提示层。[Codex base instructions](https://github.com/openai/codex/blob/6138909d6ec58b2fbe635ef973e02caecad5a5aa/codex-rs/protocol/src/prompts/base_instructions/default.md#L17-L27)，访问日期 2026-07-10。

## 2. OpenAI Codex 官方加载模型

| 主题 | 官方事实 | 对本仓与目标仓的建议 | 来源 |
|---|---|---|---|
| 用户级入口 | `CODEX_HOME` 默认为 `~/.codex`；同层先读非空 `AGENTS.override.md`，否则读 `AGENTS.md`，只取第一个非空文件。 | 用户全局源保持单一；`AGENTS.override.md` 仅作短期排障，设清理与复测动作。 | [How Codex discovers guidance](https://developers.openai.com/codex/guides/agents-md#how-codex-discovers-guidance)，访问日期 2026-07-10 |
| 项目发现链 | 从项目根（通常 Git root）走到当前目录；每层依次检查 `AGENTS.override.md`、`AGENTS.md`、`project_doc_fallback_filenames`，每层至多加载一个。无项目根时只检查当前目录。 | 不要假定 `CLAUDE.md` 会被 Codex 读取；如配置 fallback，必须把实际 `config.toml` 和新会话实测列为证据。 | 同上 |
| 合并顺序 | 从根到当前目录拼接；越接近当前目录越晚出现。 | 根文件只放仓库共性；子目录只补该模块不变量、命令和局部风险，避免复制根正文。 | 同上 |
| 容量 | 空文件跳过；`project_doc_max_bytes` 默认 32 KiB，是单个 environment 内“项目根到当前目录”的项目规则链总预算，不是每文件预算；全局用户规则由另一 loader 加载。最后一个文件可能被截断。 | verifier 检查项目链总字节和截断风险；关键规则前置，避免上层过长导致深层规则缺失；超限优先下沉到 skills 或缩减常驻内容。 | [AGENTS size limit](https://developers.openai.com/codex/guides/agents-md#how-codex-discovers-guidance)、[budget implementation](https://github.com/openai/codex/blob/6138909d6ec58b2fbe635ef973e02caecad5a5aa/codex-rs/core/src/agents_md.rs#L89-L144)，访问日期 2026-07-10 |
| 生效时点 | 指令链每个 run 构建一次；TUI 通常在每次启动 session 时构建。 | 规则变更后必须新开命令/session，不宣称热加载。 | [How Codex discovers guidance](https://developers.openai.com/codex/guides/agents-md#how-codex-discovers-guidance)，访问日期 2026-07-10 |
| 验证 | 官方建议在仓根运行 `codex --ask-for-approval never "Summarize the current instructions."`，用 `--cd subdir` 验证嵌套规则；可检查 TUI log 或 session JSONL。 | 目标仓审计增加“根目录启动”和“关键子目录启动”两次探针，记录活动文件顺序、关键规则摘要和日志路径。 | [Verify your setup](https://developers.openai.com/codex/guides/agents-md#verify-your-setup)，访问日期 2026-07-10 |

### 2.1 Codex 子代理与安全边界

- 官方说明子代理在用户直接要求，或适用的 `AGENTS.md` / Skill 明确要求时触发；继承父任务 sandbox/permission mode，自定义 agent 可覆写 `sandbox_mode`。默认 `agents.max_depth = 1`，不应无证据提高递归深度。[Codex subagents](https://developers.openai.com/codex/agent-configuration/subagents)，访问日期 2026-07-10。
- 当前官方源码与配置未发现 `child_agents_md`；不得把它写成稳定能力。子代理加载与继承仍应以当前 help、schema、官方文档和新会话实测为准。项目规则若要求委派，应显式携带 `scope`、只读/可写边界、禁止目录、输出格式和证据要求。
- 默认本地安全模型是 OS sandbox 加 approval policy；默认网络关闭。Auto 预设可在 workspace 内读写和运行命令，越出 workspace 或需要网络时请求批准。[Agent approvals & security](https://developers.openai.com/codex/agent-approvals-security)，访问日期 2026-07-10。
- `danger-full-access` 或 `--dangerously-bypass-approvals-and-sandbox` 会显著扩大权限，官方要求谨慎使用。即便选择 `approval_policy = "never"`，也不能把它解释成项目规则具有强制能力；危险操作仍应由 sandbox、精确 exec policy、外部隔离、hook/CI 与回滚证据承接。[Agent approvals & security](https://developers.openai.com/codex/agent-approvals-security)，访问日期 2026-07-10。
- live web/network 内容存在 prompt injection 风险；外部网页、日志、配置和数据中的指令式文本只能作为不可信数据或待核事实。[Agent approvals & security](https://developers.openai.com/codex/agent-approvals-security)，访问日期 2026-07-10。

## 3. Anthropic Claude Code 官方加载模型

| 主题 | 官方事实 | 对本仓与目标仓的建议 | 来源 |
|---|---|---|---|
| 作用域 | Managed policy：Windows `C:\Program Files\ClaudeCode\CLAUDE.md`、Linux/WSL `/etc/claude-code/CLAUDE.md`、macOS `/Library/Application Support/ClaudeCode/CLAUDE.md`；用户级 `~/.claude/CLAUDE.md`；项目级 `./CLAUDE.md` 或 `./.claude/CLAUDE.md`；本地私有 `./CLAUDE.local.md`。 | 项目只保留一个共享入口；本机差异放 `CLAUDE.local.md` 并 gitignore；组织安全底线用 managed policy/settings。 | [Choose where to put CLAUDE.md files](https://code.claude.com/docs/en/memory#choose-where-to-put-claude-md-files)，访问日期 2026-07-10 |
| 加载与顺序 | 从文件系统根到当前工作目录排序；同层 `CLAUDE.local.md` 在 `CLAUDE.md` 后；所有文件拼接而非确定性覆盖；子目录文件在读取该目录文件时按需加载。 | “项目覆盖全局”只能作为无冲突治理语义；verifier 应阻断相反指令，不能押注后文获胜。 | [How CLAUDE.md files load](https://code.claude.com/docs/en/memory#how-claude-md-files-load)，访问日期 2026-07-10 |
| 与 AGENTS 协同 | Claude Code 读 `CLAUDE.md`，不自动读 `AGENTS.md`；官方推荐 `CLAUDE.md` 首行独立写 `@AGENTS.md`，其后追加 Claude 特有内容。 | 目标仓统一采用“共同 `AGENTS.md` + Claude 薄 wrapper”；wrapper 禁止复制共同正文。 | [AGENTS.md](https://code.claude.com/docs/en/memory#agentsmd)，访问日期 2026-07-10 |
| import | 相对路径基于包含 import 的文件；支持绝对路径；递归最多四跳；反引号和 fenced code block 内不解析；启动时展开并进入 context。外部 import 首次需要批准。 | `@AGENTS.md` 使用裸文本独立行；共享仓外规则需记录首次批准；import 只消除维护重复，不作为 token 优化。 | [Import additional files](https://code.claude.com/docs/en/memory#import-additional-files)，访问日期 2026-07-10 |
| 模块化规则 | `.claude/rules/**/*.md` 递归发现；无 `paths` 的规则每 session 加载，带 `paths` 的规则在读取匹配文件后加载；用户级规则位于 `~/.claude/rules/` 且先于项目规则。 | 语言/目录约束放 path rule；必须在新建文件前生效的关键安全约束不能只放 path rule，因为单纯 Write/Create 不保证触发，应保留在根规则或 hook。 | [Organize rules](https://code.claude.com/docs/en/memory#organize-rules-with-clauderules)、[Path-specific rules](https://code.claude.com/docs/en/memory#path-specific-rules)、[Debug your configuration](https://code.claude.com/docs/en/debug-your-config)，访问日期 2026-07-10 |
| 规模 | 官方建议 `CLAUDE.md` 少于 200 行；只保留每个会话都需要、具体且可验证的内容。 | 同时度量 wrapper 行数和 import 展开后的有效上下文；README 可发现事实、教程和长 runbook 下沉。 | [Write effective instructions](https://code.claude.com/docs/en/memory#write-effective-instructions)、[Best practices](https://code.claude.com/docs/en/best-practices#write-an-effective-claudemd)，访问日期 2026-07-10 |

### 3.1 Claude 子代理规则继承

- 普通 custom/general-purpose subagent 会加载主会话使用的 memory hierarchy，包括用户、项目、rules、local 与 managed policy；custom agent 自身正文成为其 system prompt。[What loads at startup](https://code.claude.com/docs/en/sub-agents#what-loads-at-startup)，访问日期 2026-07-10。
- **内置 `Explore` 和 `Plan` 是明确例外：它们跳过 `CLAUDE.md` 与 git status，且没有 frontmatter 可改变。** 若搜索边界必须传达，应在委派 prompt 重述；主会话接收结果时仍有完整规则上下文。[What loads at startup](https://code.claude.com/docs/en/sub-agents#what-loads-at-startup)，访问日期 2026-07-10。
- 子代理继承父会话 permission context；代理间消息不能代表用户批准，也不能改变子代理权限、`CLAUDE.md` 或配置。[Subagent permission modes](https://code.claude.com/docs/en/sub-agents#permission-modes)，访问日期 2026-07-10。

### 3.2 Claude 权限与强制层

- `CLAUDE.md` 是 context，不是 enforced configuration。权限规则按 `deny -> ask -> allow` 评估，任一 scope 的 deny 不能被另一 scope 的 allow 放宽。[Configure permissions](https://code.claude.com/docs/en/permissions)，访问日期 2026-07-10。
- settings 确定性优先级为 Managed > CLI > `.claude/settings.local.json` > `.claude/settings.json` > `~/.claude/settings.json`。这与 `CLAUDE.md` 的拼接顺序是两套不同机制，不应混写。[Settings precedence](https://code.claude.com/docs/en/permissions#settings-precedence)，访问日期 2026-07-10。
- 项目 `.claude/settings.json` 的 allow 和 `additionalDirectories` 属于授予能力，需 workspace trust 后生效；非交互 `claude -p` 不显示 trust 对话框，不能单独证明这些规则有效。[Project allow rules and workspace trust](https://code.claude.com/docs/en/permissions#project-allow-rules-and-workspace-trust)，访问日期 2026-07-10。
- permission 覆盖工具授权；sandbox 提供 Bash 及其子进程的 OS 边界；PreToolUse hook 可基于状态动态阻断；CI/仓库 gate 负责交付结果。应组合使用，不能相互替代。[Claude permissions](https://code.claude.com/docs/en/permissions)、[Claude security](https://code.claude.com/docs/en/security)，访问日期 2026-07-10。

## 4. 推荐的“1+1>2”协同框架

| 层 | 只放什么 | 不放什么 | 确定性承接 |
|---|---|---|---|
| 全局共同语义 | 语言、通用风险分级、澄清阈值、通用 N/A、证据/回滚最低要求、跨仓稳定禁区 | 仓库路径、私有命令、模块结构、会变化的工具细节 | 用户级 `AGENTS.md` / `CLAUDE.md`，但避免复制共同正文 |
| 项目共同主体 `AGENTS.md` | 仓库事实、模块边界、目标归宿、真实 build/test/contract/hotspot、阻断条件、证据路径、回滚入口 | 全局 R/E 正文复述、README 全文、平台特有诊断 | 仓库脚本、tests、schema、CI |
| Claude 薄 wrapper `CLAUDE.md` | 独立 `@AGENTS.md`；Claude 的加载差异、Explore/Plan 例外、`/context`/`/memory` 诊断、permissions/hook 边界 | 共同项目正文副本 | import verifier、`InstructionsLoaded`、`claude doctor` |
| Codex 平台差异 | `CODEX_HOME`、fallback/byte limit、新 session 验证、sandbox/approval/exec policy 边界 | Claude import、Claude path rule 语义 | `config.toml`、`.codex/rules/*.rules`、运行日志 |
| 局部渐进披露 | Codex 嵌套 `AGENTS.md`；Claude `.claude/rules/` path rule；低频任务 skill/runbook | 每次 session 都不需要的长知识 | 路径探针、skill validator、局部门禁 |

协同有效的判断不是“两份文件都存在”，而是仅凭全局 + 项目规则即可推出：`当前落点 -> 目标归宿 -> 风险等级 -> 固定门禁 -> 证据路径 -> 回滚入口`，同时两宿主都能证明实际加载了预期来源，且不存在相反指令。

## 5. 建议的验证矩阵

### 5.1 Codex

1. `codex --version`、`codex --help` 记录版本与可用命令。
2. 先以当前 help 判断 `codex debug prompt-input` 是否可用；该命令直接渲染 model-visible prompt JSON，比模型复述更确定。[CLI source](https://github.com/openai/codex/blob/6138909d6ec58b2fbe635ef973e02caecad5a5aa/codex-rs/cli/src/main.rs#L227-L236)，访问日期 2026-07-10。
3. 仓根新 run：`codex --ask-for-approval never "Summarize the current instructions and list their sources in load order."`
4. 关键子目录新 run：`codex --cd <subdir> --ask-for-approval never "Show which instruction files are active."`
5. 检查当前 `config.toml` 中 `project_root_markers`、`project_doc_fallback_filenames`、`project_doc_max_bytes`、sandbox、approval；不从文件名猜语义。
6. 必要时使用交互 TUI `/status`、plaintext TUI log 或最近的 session JSONL；顶层 `codex status` 仅在当前 help 明确存在时调用。记录 `cmd / exit_code / key_output / timestamp / active_rule_path`。

### 5.2 Claude Code

1. `claude --version`、`claude --help`、`claude doctor`。
2. 新交互 session 使用 `/context`、`/memory`、`/permissions`；分别验证 context 来源与确定性授权结果。
3. 加载疑难启用 `InstructionsLoaded` hook；必要时用 `--safe-mode` 与正常模式做差分诊断。
4. 根与关键子目录各启动一次，验证嵌套规则是否按 Read 触发；验证 `Explore`/`Plan` 委派 prompt 已显式包含必需边界。
5. 非交互探针同时记录 workspace trust；未信任时，不能把项目 allow 未报错当作已生效。

### 5.3 静态 verifier 应新增的检查

- `CLAUDE.md` 是否存在且首个有效 import 为独立 `@AGENTS.md`。
- wrapper 是否复制 `AGENTS.md` 段落；共同正文重复率是否超过阈值。
- 全局、根、嵌套规则是否有语义冲突；Claude 冲突必须阻断，不能声明“后者覆盖”。
- Codex 合并链总字节是否逼近 `project_doc_max_bytes`；Claude wrapper 和展开上下文是否过长。
- 每条项目长期规则能否映射到命令、路径、阻断、证据字段或明确 N/A。
- 权限性措辞是否已有 settings/rules/hook/sandbox/CI 承接；只有自然语言“禁止”则标记为治理缺口。

## 6. 社区优秀项目的可验证结构实践

> 下列仓库只提供结构借鉴。其内容、权限假设和命令都不能直接覆盖官方加载语义，也不能无审查复制到本机或目标仓。

### 6.1 `agentsmd/agents.md`：工具中立的最小共同格式

- 可验证结构：把 `AGENTS.md` 定义为“给 agent 的 README”，最小样例只覆盖环境、测试与 PR；强调使用可执行命令和仓库事实，而非人格化长提示。
- 可借鉴：共同主体保持工具中立；优先写 setup、test、lint、PR/交付标准。
- 不可照搬：该格式说明不定义 Codex/Claude 的权限、加载容量、import 或子代理语义，仍须以官方宿主文档为准。
- 来源：[README at d1ac7f0](https://github.com/agentsmd/agents.md/blob/d1ac7f063d20e70015ed6732664049ae4ba9d74e/README.md)，访问日期 2026-07-10。

### 6.2 `getsentry/sentry`：共同主体、薄 wrapper、目录局部规则

- 可验证结构：根 `AGENTS.md` 是 source of truth；根、`src/`、`tests/` 等目录各有局部 `AGENTS.md`；相应 `CLAUDE.md` 只有一行 `@AGENTS.md`。局部文件引用根命令入口，并补充安全不变量、测试定位和领域规则。
- 可借鉴：这是“共同根 + 薄 wrapper + 目录渐进披露”的直接实例；局部规则不复制全局命令全文。
- 风险提醒：Sentry 文件中的具体权限参数和命令只对其仓库有效，不应跨仓采用。
- 来源：[root AGENTS at 20ef5cf](https://github.com/getsentry/sentry/blob/20ef5cf33812bee91de66dfba9a52386b3599911/AGENTS.md)、[root CLAUDE at 20ef5cf](https://github.com/getsentry/sentry/blob/20ef5cf33812bee91de66dfba9a52386b3599911/CLAUDE.md)、[src AGENTS at 20ef5cf](https://github.com/getsentry/sentry/blob/20ef5cf33812bee91de66dfba9a52386b3599911/src/AGENTS.md)、[tests AGENTS at 20ef5cf](https://github.com/getsentry/sentry/blob/20ef5cf33812bee91de66dfba9a52386b3599911/tests/AGENTS.md)，访问日期 2026-07-10。

### 6.3 `github/awesome-copilot`：指令资产分类、元数据与机器校验

- 可验证结构：根 `AGENTS.md` 将 agents、instructions、skills、hooks、workflows、plugins 分目录；不同资产有 frontmatter 必填字段、命名约定、schema/validator 和构建命令；`instructions` 用 `applyTo` 做路径范围。
- 可借鉴：把“每会话规则”“路径条件规则”“任务 skill”“自动 hook”“工作流”分开，并用机器校验确保 metadata、命名和范围完整。
- 不可照搬：其格式和 `applyTo` 属 GitHub Copilot 生态；本仓只能借鉴资产分类与 verifier 思路，Codex/Claude 的真实字段必须回到各自官方 schema。
- 来源：[AGENTS at 30472ec](https://github.com/github/awesome-copilot/blob/30472ecf0fe34cc561df958c08501ecc5ca80ea4/AGENTS.md)、[CONTRIBUTING at 30472ec](https://github.com/github/awesome-copilot/blob/30472ecf0fe34cc561df958c08501ecc5ca80ea4/CONTRIBUTING.md)，访问日期 2026-07-10。

### 6.4 `vercel/next.js`：训练数据失效提醒与极窄局部规则

- 可验证结构：根 `AGENTS.md` 给出 monorepo 定位、命令与 README 读取链；`packages/next/AGENTS.md` 只保留一个高价值事实：当前版本可能与训练数据中的 Next.js 不同，修改前读取仓内 `dist/docs/`。`CLAUDE.md` 使用到共同主体的链接方式。
- 可借鉴：局部规则只保留“删除后会导致模型犯错”的高价值差异；仓内运行事实/生成文档优先于模型既有知识。
- 风险提醒：其 symlink 方式在 Windows 部署条件更高；本任务的 Windows 目标仓应按 Anthropic 官方建议使用 `@AGENTS.md` import。
- 来源：[root AGENTS at 3bb780e](https://github.com/vercel/next.js/blob/3bb780e7d65f723297c93640d0ca24c730037770/AGENTS.md)、[packages/next AGENTS at 3bb780e](https://github.com/vercel/next.js/blob/3bb780e7d65f723297c93640d0ca24c730037770/packages/next/AGENTS.md)、[CLAUDE at 3bb780e](https://github.com/vercel/next.js/blob/3bb780e7d65f723297c93640d0ca24c730037770/CLAUDE.md)，访问日期 2026-07-10。

## 7. 对当前规则家族的优先改进清单

### P0：纠正语义与安全边界

1. 将 Codex 的“平台指令优先级”和“运行事实用于发现漂移”拆开；不得把临时 user 指令写成低于 `AGENTS.md`。
2. 把 Claude 的“项目覆盖全局”改成“从根到当前目录拼接；治理上禁止冲突，更具体规则只能补充/收窄”。
3. 明确 Claude 不自动读取 `AGENTS.md`，目标仓 `CLAUDE.md` 必须显式 `@AGENTS.md`。
4. 写清 `@ import` 最多四跳，且 import 不节省 context。
5. 写清 `Explore` / `Plan` 不加载 `CLAUDE.md`，委派时显式携带关键边界；删除或条件化 Codex `child_agents_md`。
6. 把自然语言指导、permissions/exec policy、hook、sandbox、CI 的责任分开；禁止把规则文件描述为权限保障。

### P1：落实渐进披露与验证

1. 根规则保留高频、跨模块、会改变风险或验收的事实；目录差异下沉；低频多步骤流程进入 skill/runbook。
2. Claude path rule 的关键限制增加 Read 触发说明；新建文件前必须生效的边界由根规则或 hook 承接。
3. verifier 增加 import 完整性、重复正文、语义冲突、展开上下文体积和 enforcement 映射检查。
4. 规则改动必须用新 session 验证实际加载，而不是只做文件 diff。

### P2：持续治理

1. 对每个目标仓生成机器可读审计记录：规则源、wrapper 方式、嵌套层级、命令门禁、证据/回滚、Codex 字节预算、Claude 展开行数、最近验证时间。
2. 官方文档属于高漂移能力面；记录访问日期和本机版本，升级宿主后重跑最小诊断矩阵。
3. 社区样例必须固定 commit URL、提炼结构、不复制命令；采纳前回查官方 schema/help 并做本仓实测。

## 8. 证据限制

- 官方网页会持续更新；本报告固定访问日期，不把页面当前内容当作永久兼容保证。
- 官方 GitHub `examples/settings` README 自身说明其中部分内容是 community-maintained snippets；即使位于官方仓，也只能作为配置起点，不能高于正式文档与本机 `help`/`doctor`/实测。[Anthropic settings examples](https://github.com/anthropics/claude-code/tree/main/examples/settings)，访问日期 2026-07-10。
- 社区仓库的规则内容可能包含其自身权限、平台和 CI 假设。本报告只采纳可由固定 commit 验证的结构实践。
