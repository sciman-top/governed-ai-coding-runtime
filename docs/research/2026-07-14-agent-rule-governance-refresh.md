# OpenAI / Anthropic Agent 规则治理事实刷新

- 研究日期：2026-07-14
- 研究范围：OpenAI ChatGPT Work / Codex App / Codex CLI 与 Anthropic Claude / Claude Code 的持久指令、项目规则、settings / permissions / hooks / sandbox / managed policy / 诊断边界，以及 Windows 本机可重复事实
- 不在范围：Gemini；修改用户 auth/provider/凭据或 live config；启动交互式或付费模型会话；升级宿主；目标仓逐仓审计
- 证据优先级：官方文档与本机 `--help` / schema / 只读探针 > 官方源码与官方示例 > 固定 commit 的成熟社区仓库
- OpenAI 取证路径：按 `openai-docs` 约束先运行 `fetch-codex-manual.mjs`；2026-07-14 返回的本机缓存为 current，manual 中各结论再回链到 `learn.chatgpt.com` 官方页面
- 历史基线：本报告复核并收窄 [2026-07-10 规则加载与协同实践研究](./2026-07-10-agent-rules-official-and-community-practices.md) 中的 OpenAI 与 Anthropic 结论，不继承其中任何完成声明

## 1. 可直接用于本轮改造的结论

1. **共同项目主体使用 `AGENTS.md`，但两宿主的加载语义不能混写。** Codex 原生分层读取 `AGENTS.md`；Claude Code 不自动读取它，必须由薄 `CLAUDE.md` 显式 `@AGENTS.md` 导入。Windows 应优先 import，而不是依赖需要 Administrator 或 Developer Mode 的 symlink。[Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[Claude AGENTS.md](https://code.claude.com/docs/en/memory#agentsmd)
2. **Codex 的 root-to-cwd 指令链与 Claude 的拼接 context 不是同一种 override。** Codex 每层最多取一个候选文件，并把近目录内容放在后面作为更具体指导；Claude 将发现的文件拼接，官方明确说相反规则可能被任意选择。跨宿主治理必须消除冲突，不能用相反 prose 模拟权限或覆盖。[Codex discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md#how-codex-discovers-guidance)、[Claude load order](https://code.claude.com/docs/en/memory#how-claude-md-files-load)
3. **ChatGPT Work、Codex Local 与 Claude Web/Desktop、Claude Code 必须按 surface 分开取证。** ChatGPT Work web/mobile 运行在 hosted environment，workspace RBAC、apps 和 source-system permissions 适用；本机 Codex App/CLI/IDE 受本地 sandbox、approval、config 和 managed requirements 约束。Claude 的 account/project instructions 也不能自动等同本机 `~/.claude/CLAUDE.md`。[Work Admin FAQ](https://learn.chatgpt.com/docs/enterprise/work-admin-faq)、[Claude personalization](https://support.claude.com/en/articles/10185728-understanding-claude-s-personalization-features)
4. **自然语言规则是指导，settings / requirements / permissions / hooks / sandbox / CI 才是强制层。** Codex `AGENTS.md` 与 Claude `CLAUDE.md` 都不能替代权限系统；需要保证的限制必须落到宿主确定性控制或仓库 scripts / schema / tests / CI。[Codex security](https://learn.chatgpt.com/docs/agent-approvals-security)、[Claude permissions](https://code.claude.com/docs/en/permissions)
5. **import 只减少维护重复，不减少上下文。** Claude import 在 session 启动时展开并进入 context，递归上限 4 hops；Codex 项目指令链默认总预算 32 KiB。根规则过长时应删减或使用宿主真实的局部规则 / skills，而不是拆 import 后宣称节省 token。[Claude imports](https://code.claude.com/docs/en/memory#import-additional-files)、[Codex size limit](https://learn.chatgpt.com/docs/agent-configuration/agents-md#how-codex-discovers-guidance)
6. **fresh-process 证明必须分开验证 context 与 enforcement。** Codex 优先使用当前 help 已证明的 `codex debug prompt-input`，再辅以新 run/TUI/session log；Claude 用 `/context`、`/memory`、`InstructionsLoaded` 证明规则来源，用 `/permissions`、`/hooks`、`/status` 证明 resolved enforcement。任何当前会话自述、文件存在或 `claude -p` 单点结果都不足以证明完整加载。[Codex CLI reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli)、[Claude debug](https://code.claude.com/docs/en/debug-your-config)
7. **本机当前有两个必须保留的版本/诊断边界。** Codex CLI 为 `0.144.1`，但 `codex doctor` 与 `codex debug prompt-input` 在短时只读探针中未返回，不能作为成功证据；Claude Code 为 `2.1.206`，落后于当前文档中的若干 `2.1.207+` trust / glob 语义。两者都必须按本机可证能力设计，不把网页最新字段无条件写成已部署事实。

## 2. OpenAI Codex / ChatGPT Work 官方事实

### 2.1 Surface boundary

| Surface | 持久指令与上下文 | 权限 / 执行边界 | 可接受证明 |
|---|---|---|---|
| ChatGPT Work web/mobile | ChatGPT account personalization、当前对话、上传文件、workspace resources、plugins / connected systems；项目或 memory 仅在相应产品控制允许时进入上下文 | OpenAI hosted environment；workspace RBAC、app action controls、source-system permissions、Work access 与 data controls | workspace/admin settings、连接器原生权限、当前 Work task evidence；不能用本机文件 hash 代替 |
| ChatGPT desktop / Codex App local | Codex personal instructions 与 global `AGENTS.md`、项目 `AGENTS.md`、本机 config / plugins / skills | OS sandbox、approval policy、permission profile、managed requirements；desktop Work access 与 web/mobile entitlement 仍是不同控制 | App version、managed config、fresh local task / prompt-input / logs |
| Codex CLI / IDE local | `CODEX_HOME` 全局规则、root-to-cwd 项目规则、trusted `.codex/` 层 | local sandbox、approval、hooks、exec rules、MCP、requirements | CLI `--help` / schema、fresh process、`debug prompt-input` 或 session log |
| Codex cloud | 仓库内规则与 cloud environment / task context | OpenAI-managed isolated environment；不是本机 Windows sandbox | cloud task/environment evidence 与 workspace policy |

OpenAI 的 [Personalize ChatGPT](https://learn.chatgpt.com/docs/personalize) 说明 custom instructions 可跨 chats 和 tasks 使用，并说明 Codex personal instructions 存放在 global `AGENTS.md`。这能证明 Codex 的个人规则入口，但**不能单凭某台机器的 `~/.codex/AGENTS.md` hash 推导 ChatGPT Work web 已加载同一字节内容或存在双向同步**。Work Admin FAQ 同时明确 web/mobile Work 与 desktop Codex Local 的权限控制不同。因此本轮采用“语义协同、surface 分别验证”，拒绝“一个本机文件证明所有 OpenAI surface”的假设。

### 2.2 `AGENTS.md` 加载模型

| 主题 | 当前官方事实 | 治理结论 |
|---|---|---|
| Global scope | `CODEX_HOME` 默认 `~/.codex`；先取非空 `AGENTS.override.md`，否则取 `AGENTS.md`，全局层只取第一个非空文件 | global override 只用于有期限的排障；删除后必须新 run 复测 |
| Project root | 通常以 Git root 为项目根；可用 `project_root_markers` 调整；未找到项目根时只检查 cwd | 目标仓必须从真实 root 启动探针，不能从目录名猜测加载链 |
| 每层候选 | 从 root 到 cwd，每层依次检查 `AGENTS.override.md`、`AGENTS.md`、`project_doc_fallback_filenames`，最多取一个 | 不得假定 `CLAUDE.md` 会自动被 Codex 读取；fallback 必须由 live config 和 fresh probe 证明 |
| 合并与预算 | 从 broad 到 specific 拼接；项目规则链受 `project_doc_max_bytes` 限制，默认 32 KiB，空文件跳过，达到预算后停止或截断 | verifier 计算整条项目链，不按“每文件 32 KiB”误报；关键规则前置 |
| 生效时点 | 每个 run 构建一次；TUI 通常每个新 session 构建 | 规则变更后新进程 / 新 session 验证，不宣称热加载 |
| 验证 | 官方文档建议新 run 总结活动指令；当前 CLI 还公开 `codex debug prompt-input` 渲染 exact model-visible JSON | 优先 deterministic prompt-input；不可用时记录 `platform_na` 并用 help、source、session log 等替代证据 |

来源：[Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)、[Advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced)，访问日期 2026-07-14。官方源码固定到 [openai/codex `effd58d`](https://github.com/openai/codex/tree/effd58d7505382f6b2d1736a4fc9e3eb90df1966)；`codex-rs/core/src/agents_md.rs` 仍实现 override / default / fallback、root-to-cwd 拼接和 `max_total` 总预算。

### 2.3 Config、trust 与 managed requirements

Codex 普通配置优先级为：

`CLI flags / --config > trusted project .codex/config.toml (root -> cwd, nearest wins) > selected profile file > ~/.codex/config.toml > system config > built-in defaults`

关键边界：

- 未信任项目会跳过项目 `.codex/config.toml`、项目 hooks 与项目 rules；user / system 层仍独立加载。
- 项目 config 不能覆写 `openai_base_url`、`chatgpt_base_url`、`model_provider(s)`、`profile(s)`、`notify`、`otel` 等 host-owned/provider/auth/telemetry 入口。将这些键放入项目层时客户端会忽略并警告。
- Profiles 自 Codex `0.134.0+` 使用 `~/.codex/<name>.config.toml` 叠加，不再使用旧 `[profiles.<name>]` 表。规则文档不得把旧语义写成当前事实。
- `requirements.toml` 是 admin-enforced runtime constraint，不是 ChatGPT workspace entitlement 或 RBAC。Windows system 路径为 `%ProgramData%\OpenAI\Codex\requirements.toml`；其上还可组合 cloud-managed requirements、legacy managed config 与 macOS MDM，字段有各自合并规则，不能假设所有数组/表同样覆盖。
- Codex `0.138.0+` 的 managed permission profiles 是当前推荐路径；旧 `allowed_sandbox_modes` 只适合兼容旧部署。部署前必须按 fleet/client version 验证。

来源：[Config basics](https://learn.chatgpt.com/docs/config-file/config-basic#configuration-precedence)、[Advanced config](https://learn.chatgpt.com/docs/config-file/config-advanced)、[Managed configuration](https://learn.chatgpt.com/docs/enterprise/managed-configuration)，访问日期 2026-07-14。

### 2.4 Hooks、exec rules、sandbox 与 approval

| 机制 | 当前状态 / 语义 | 本轮采用方式 |
|---|---|---|
| Codex hooks | 当前 manual 将 `hooks` 列为 stable feature；从 active config layer 的 `hooks.json` 或 inline `[hooks]` 加载，匹配的多来源 hooks 都运行，同事件 command hooks 可并行启动 | 用于 lifecycle observability / deterministic decision；不能假定一个 hook 能阻止另一个并行 hook 启动 |
| Hook trust | 非 managed command hook 按 exact definition hash 要求 review/trust；变更后重新待审。managed hooks 由 policy 信任且用户不能在 hook browser 禁用 | verifier 检查来源与 trust；自动化绕过 trust 的危险 flag 不能写成日常默认 |
| Exec rules | `.rules` 当前仍标为 experimental；`prefix_rule` 精确匹配 argv prefix，冲突取最严格 `forbidden > prompt > allow`，支持 `match/not_match` 自测 | 只用于 sandbox 外命令决策；必须用 `codex execpolicy check` 做正反例，避免宽前缀 |
| Sandbox | `read-only`、`workspace-write`、`danger-full-access`；workspace-write 仍保护 `.git`、`.agents`、`.codex` 等路径，network 与 filesystem 分开配置 | 选择最小权限；外部网页和 live network 内容仍作不可信数据 |
| Approval | `untrusted`、`on-request`、`never` 或 granular；`never` 只代表不弹确认，失败直接返回，不等于 full access | 不把 `approval_policy = "never"` 写成授权扩张；auto-review 仅在仍会产生 approval prompt 时工作 |
| Repo gate / CI | 不依赖单个宿主 session | 承接 `build -> test -> contract/invariant -> hotspot` 与跨人员交付阻断 |

来源：[Hooks](https://learn.chatgpt.com/docs/hooks)、[Rules](https://learn.chatgpt.com/docs/agent-configuration/rules)、[Agent approvals & security](https://learn.chatgpt.com/docs/agent-approvals-security)，访问日期 2026-07-14。

### 2.5 OpenAI 本机只读事实

2026-07-14 在 `D:\CODE\governed-ai-coding-runtime` 执行的非交互只读探针：

```powershell
node C:\Users\sciman\.codex\skills\.system\openai-docs\scripts\fetch-codex-manual.mjs
codex --version
codex --help
codex debug --help
codex debug prompt-input --help
codex doctor --help
codex app-server generate-json-schema --help
codex execpolicy --help
Get-AppxPackage -Name OpenAI.Codex
```

结果：

- Codex manual helper：`local manual was already current`；manual path 位于 `%TEMP%\openai-docs-cache`，outline 明确包含 AGENTS、config、hooks、rules、managed configuration 与 ChatGPT Work 章节。
- Codex CLI：`0.144.1`；npm package `@openai/codex 0.144.1`。
- Codex Windows App：`OpenAI.Codex 26.707.9981.0`，package status `Ok`。
- 当前 help 明确公开 `doctor`、`debug prompt-input`、`--strict-config`、sandbox / approval flags、`--dangerously-bypass-hook-trust`；`codex execpolicy` 虽未列在顶层摘要中，但 `codex execpolicy --help` 可用。
- `CODEX_HOME` 未设置，故默认 `~/.codex`；`~/.codex/AGENTS.override.md` 不存在，`~/.codex/AGENTS.md` 存在且 UTF-8 无 BOM。
- repo source `rules/global/codex/AGENTS.md` 与 deployed `~/.codex/AGENTS.md` SHA-256 同为 `6B6D478CCD29BB5406F9B586C72AF9B34CE9DFF6BA25E629C6FE8B314C237E0F`；这只证明当前文件零漂移，不代替 fresh-process 加载证明。
- user config 中当前仓 `D:\CODE\governed-ai-coding-runtime` 的 `trust_level = "trusted"`；repo `.codex/config.toml` 存在，只有 `sandbox_workspace_write` 顶层键，并通过 2026-07-14 官方 schema 校验。
- user 与 Windows system `requirements.toml` 文件均未发现；这只证明这些 file-based layer 缺席，不证明 cloud-managed requirement 或其他 enterprise delivery 不存在。

### 2.6 Schema drift 与 `platform_na`

官方 [Codex `config-schema.json`](https://developers.openai.com/codex/config-schema.json) fresh fetch 的 title 为 `ConfigToml`、dialect 为 JSON Schema Draft-07。使用 Python `tomllib` + `jsonschema.validators.validator_for(schema)` 对 live `~/.codex/config.toml` 只读校验：

- `error_count = 8`；
- 全部错误都是八个 `mcp_servers.*` 表中的 `transport` 被当前 schema 判为 `additionalProperties`；
- 本研究不输出 MCP value、provider、auth 或 secret，也不修改 live config；
- 该 drift 可能影响 strict validation，但**没有证据证明它就是后续诊断超时的根因**。

`codex debug prompt-input "local instruction probe"` 与 `codex doctor --summary --ascii` / `--json` 都未在短时限内返回。探针派生进程随后自然退出；本研究没有停止、杀掉或重启任何 Codex 进程。处理口径：

```text
type: platform_na
reason: current live diagnostic commands did not return within the bounded read-only probe window
alternative_verification: current manual + CLI help + official source + schema + file hashes + project trust evidence
evidence_link: this report, sections 2.2-2.6
expires_at: next controlled fresh-process verification window or after live config drift is resolved by its owner
recovery_condition: `codex --strict-config` validation is clean and `codex debug prompt-input` returns model-visible JSON in a new isolated process
```

不得把该 `platform_na` 写成“Codex 已实际加载全部规则”。

## 3. Anthropic Claude / Claude Code 官方事实

### 3.1 Surface boundary

| Surface | 当前官方事实 | 治理结论 |
|---|---|---|
| Claude Chat web / Desktop Chat | “Instructions for Claude” 是 account-wide；Project instructions 只适用于该 project 内 chats | 它们是 Claude chat 产品的 profile / project surface，不能用本机 `CLAUDE.md` hash 证明加载 |
| Claude Desktop Code local | Code tab 的 local session 与 CLI 读取同一 settings files；每个 session 有独立 history、project folder 和 changes | local Code 与 CLI 可共享项目规则与 settings，但 Desktop 的 mode selector 还会保存 per-folder 选择，需查 resolved state |
| Claude Code CLI local | 用户 `~/.claude/CLAUDE.md`、repo `CLAUDE.md` / rules / settings 及本机 managed policy | 用 `/memory`、`/status`、`/permissions`、`/hooks` 和 fresh process 验证 |
| Claude Code cloud / web | fresh clone 中已提交的 repo `CLAUDE.md`、`.claude/rules/`、project settings/hooks 可用；server-managed settings 单独到达 | 本机 `~/.claude/CLAUDE.md`、user skills/agents/commands、user-only plugins 与 MCP 不随 cloud session 携带 |

来源：[Claude personalization](https://support.claude.com/en/articles/10185728-understanding-claude-s-personalization-features)、[Claude Desktop Code](https://code.claude.com/docs/en/desktop)、[Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web#whats-available-in-cloud-sessions)，访问日期 2026-07-14。

### 3.2 作用域与路径

| 作用域 | 官方位置 | 本轮治理含义 |
|---|---|---|
| Managed policy | Windows `C:\Program Files\ClaudeCode\CLAUDE.md` | 只放组织级行为指导；不能被用户排除。技术强制仍放 managed settings。 |
| User | `~/.claude/CLAUDE.md` | 只放跨仓稳定偏好与风险语义，不放目标仓路径、命令、provider 或短期机器状态。 |
| Project | `./CLAUDE.md` 或 `./.claude/CLAUDE.md` | 对跨宿主仓，保持薄 wrapper；共同项目主体在 `AGENTS.md`。 |
| Local | `./CLAUDE.local.md` | 私人且项目特定，加入 `.gitignore`；不得成为团队契约唯一载体。 |

来源：[Choose where to put CLAUDE.md files](https://code.claude.com/docs/en/memory#choose-where-to-put-claude-md-files)，访问日期 2026-07-14。

Windows managed settings 的文件路径同样是 `C:\Program Files\ClaudeCode\managed-settings.json`；旧 `C:\ProgramData\ClaudeCode\managed-settings.json` 自 `2.1.75` 起不再支持。官方还支持 server-managed、HKLM/HKCU policy 和 `managed-settings.d/*.json`，因此“文件不存在”不能证明没有任何 managed policy 生效。[Settings files](https://code.claude.com/docs/en/settings#settings-files)

### 3.3 拼接、冲突与按需加载

- 启动时，Claude Code 从文件系统根到当前工作目录查找 `CLAUDE.md` 与 `CLAUDE.local.md`，按 broad -> specific 顺序拼接，而不是让下层文件确定性覆盖上层文件。
- 当前工作目录之下的嵌套 `CLAUDE.md` 不在启动时加载；Claude 使用 Read 打开该子目录文件后才按需加载。
- `.claude/rules/**/*.md` 会递归发现。无 `paths` frontmatter 的规则每 session 加载；带 `paths` 的规则在读取匹配文件时触发，不是在每次 tool use 或仅 Write/Create 时触发。
- 用户级 `~/.claude/rules/` 早于项目规则加载，但官方同时警告相反规则可能被任意选择。治理 verifier 应阻断矛盾语义，不应依赖“后出现者一定获胜”。
- 官方建议单个 `CLAUDE.md` 目标低于 200 行；删除后不会增加犯错概率的内容应下沉或移除。

来源：[How CLAUDE.md files load](https://code.claude.com/docs/en/memory#how-claude-md-files-load)、[Organize rules with `.claude/rules/`](https://code.claude.com/docs/en/memory#organize-rules-with-clauderules)、[Write effective instructions](https://code.claude.com/docs/en/memory#write-effective-instructions)，访问日期 2026-07-14。

### 3.4 `AGENTS.md` wrapper

Anthropic 当前推荐格式是：

```markdown
@AGENTS.md

## Claude Code

<only real Claude-specific deltas, if any>
```

对本仓的具体约束建议保持为：

- 第一物理行必须是无 BOM 的独立 `@AGENTS.md`；这是本仓为了静态可验与一致投影选择的更强 contract，不是 Anthropic 语法强制。
- 没有真实 Claude 差异时，wrapper 只保留这一行。
- 禁止复制 `AGENTS.md` 正文；禁止使用 import 假装缩短 model-visible context。
- import 相对路径以包含 import 的文件为基准；最多递归 4 hops；code span 与 fenced code block 中的 `@path` 不会解析。
- 仓库外 import 第一次出现时需要批准；不能在无人值守验证中假定已经批准。

来源：[AGENTS.md](https://code.claude.com/docs/en/memory#agentsmd)、[Import additional files](https://code.claude.com/docs/en/memory#import-additional-files)，访问日期 2026-07-14。

## 4. settings、权限与确定性强制

### 4.1 settings precedence 与 schema

普通 scalar setting 的优先级为：

`Managed > CLI arguments > .claude/settings.local.json > .claude/settings.json > ~/.claude/settings.json`

数组字段通常跨 scope 合并、去重，不是简单替换；permission rules 又按 `deny -> ask -> allow` 评估，任意 scope 的 deny 都不能被另一 scope 的 allow 放宽。managed-only 的 `allowManagedPermissionRulesOnly`、`allowManagedHooksOnly`、`allowManagedMcpServersOnly` 等可以进一步收紧用户与项目扩展面。[Settings precedence](https://code.claude.com/docs/en/settings#settings-precedence)、[Permissions precedence](https://code.claude.com/docs/en/permissions#settings-precedence)

官方 settings 示例使用 [Claude Code settings JSON schema](https://json.schemastore.org/claude-code-settings.json)。官方同时提醒该发布 schema 是周期更新，可能暂时落后于最新 CLI 字段，因此：

1. schema validation 是必要静态检查，但不是唯一真实性来源；
2. 新字段还必须由当前 `claude --help`、官方 min-version 标记或 read-only doctor 证明；
3. 未被当前版本证明的字段不得写成已部署能力。

来源：[Settings files and JSON schema](https://code.claude.com/docs/en/settings#settings-files)，访问日期 2026-07-14。

### 4.2 permission、hook、sandbox、CI 的职责

| 层 | 适合承接 | 不能证明 |
|---|---|---|
| `CLAUDE.md` / rules | 仓库定位、命令入口、领域不变量、解释性风险边界 | 工具调用必然被拒绝、测试必然执行 |
| permissions | tool / command / path 的 allow、ask、deny；deny 跨 scope 收紧 | Bash 子进程的完整 OS 隔离、交付门禁通过 |
| `PreToolUse` hook | 基于实时 tool input 动态 allow / deny / ask；在执行前拦截 | `@file` prompt 注入的 Read，因为该路径不产生 Read tool call |
| sandbox | Bash 及其子进程的文件系统和网络隔离 | Read/Edit/Write、Computer Use、MCP、hook 的通用隔离；native Windows 支持 |
| repo scripts / CI | `build -> test -> contract/invariant -> hotspot` 与跨客户端交付阻断 | Claude 当前 session 实际加载了哪些 prose |

关键 hook 语义：

- 对大多数 hook，只有 `exit 2` 表示阻断；传统的 `exit 1` 是非阻断错误，执行继续。
- `PreToolUse` 的 `exit 2` 阻止 tool call；JSON 应使用 `hookSpecificOutput.permissionDecision`，其多 hook 冲突顺序为 `deny > defer > ask > allow`。
- `InstructionsLoaded` 可记录 `file_path`、`memory_type`、`load_reason`、`parent_file_path`，但它是异步 observability 事件，不能阻断或修改规则加载。
- `TaskCompleted` 可用 `exit 2` 阻止 task 被标为完成并运行 test/lint，但只覆盖对应任务生命周期；不应代替仓库 CI。
- `ConfigChange` 可审计或阻断 user/project/local settings 变更；managed policy 变更只能观察，不能被 hook 阻断。

来源：[Hooks reference](https://code.claude.com/docs/en/hooks)、[Sandbox scope](https://code.claude.com/docs/en/sandboxing#scope)，访问日期 2026-07-14。

### 4.3 Windows 特别边界

1. Claude Code 内建 Bash sandbox 在 native Windows 上不受支持；WSL2 才在支持范围。
2. 即使在 WSL2，`sandbox.failIfUnavailable` 才能把依赖缺失或 sandbox 启动失败从 warning + unsandboxed fallback 变成 fail-closed。
3. sandbox 只覆盖 Bash subprocess；Read/Edit/Write 仍由 permission system 控制。
4. 因此 native Windows 项目规则不得笼统写“由 Claude sandbox 保证”。应明确：`platform_na`、原因、permissions/hook/CI 替代验证、切换 WSL2 或官方支持 native Windows 后的复测条件。

来源：[Configure the sandboxed Bash tool](https://code.claude.com/docs/en/sandboxing)，访问日期 2026-07-14。

## 5. skills 与 subagent 的渐进披露边界

- 只在特定任务需要的流程放 skill，不放每 session 的仓库基线。skill description 常驻 listing，正文按调用加载；大参考文件可作为 supporting files 按需读取。
- `disable-model-invocation: true` 适合 commit、deploy、send 等必须由用户决定触发时点的副作用流程。
- `allowed-tools` 是 skill 激活期间的免询问授权，不是“只允许这些工具”；若要限制可用工具，使用 `disallowed-tools` 或全局 permission deny。
- 项目 skill 的 `allowed-tools` 也受 workspace trust 约束。
- 普通 non-fork subagent 使用新的 isolated context，但加载主会话 memory hierarchy；内置 Explore 与 Plan 是唯一明确跳过 `CLAUDE.md` 和 git status 的例外。
- agent 间消息不能代表用户批准，不能改变 subagent 的 permissions、`CLAUDE.md` 或配置。若 Explore/Plan 必须知道某个搜索禁区，应在 delegation prompt 重述。

来源：[Skills](https://code.claude.com/docs/en/skills)、[Subagents: what loads at startup](https://code.claude.com/docs/en/sub-agents#what-loads-at-startup)，访问日期 2026-07-14。

## 6. Anthropic 本机可重复事实

### 6.1 版本与安装

2026-07-14 在 `D:\CODE\governed-ai-coding-runtime` 只读执行：

```powershell
Get-Command claude
claude --version
claude --help
claude doctor --help
claude agents --help
claude mcp --help
claude plugin --help
```

结果：

- 命令入口：`C:\Users\sciman\AppData\Roaming\npm\claude.ps1`
- npm package：`@anthropic-ai/claude-code 2.1.206`
- 实际 executable：npm wrapper 下的 `node_modules/@anthropic-ai/claude-code/bin/claude.exe`
- 当前 help 明确列出 `--safe-mode`、`--bare`、`--setting-sources`、`--settings`、`--permission-mode`、`--allowed-tools`、`--disallowed-tools`、`--agents` 与 `agents` 子命令。
- 当前 help 没有顶层 `config` 子命令；`claude config --help` 只回显顶层 help。项目文档不得把 `claude config` 写成当前稳定 CLI 入口；交互 `/config` 是另一能力。
- 官方和 help 均说明终端 `claude doctor` 是 read-only diagnostics；本研究因“不启动 session/不执行 doctor”边界只运行了 `claude doctor --help`，没有把 doctor 结果作为本机证据。

### 6.2 settings 与 schema

只读取路径存在性和 JSON key，不输出任何 setting value：

| 路径 | 结果 |
|---|---|
| `~/.claude/settings.json` | 存在；顶层 keys 为 `$schema, alwaysThinkingEnabled, cleanupPeriodDays, defaultShell, enabledPlugins, env, language, permissions, skipDangerousModePermissionPrompt, statusLine` |
| `~/.claude/settings.local.json` | 存在；无顶层 key |
| `~/.claude/CLAUDE.md` | 存在；本研究不评审正文 |
| `C:\Program Files\ClaudeCode\CLAUDE.md` | 文件不存在 |
| `C:\Program Files\ClaudeCode\managed-settings.json` | 文件不存在 |
| `C:\Program Files\ClaudeCode\settings.json` | 文件不存在 |

限制：上述结果只证明 file-based managed files 缺席，不证明 server-managed、HKLM/HKCU policy 或 embedding host policy 未生效。后者需要 fresh interactive session 的 `/status` 或等价管理面证据。

本机 user settings 的 `$schema` 指向官方文档引用的 SchemaStore URL。fresh fetch 结果为：

- schema title：`Claude Code Settings`
- JSON Schema Draft-07；顶层 properties：125
- 当前 user settings 的全部顶层 keys 均可识别
- schema 自声明 dialect：JSON Schema Draft-07
- 使用 Python `jsonschema.validators.validator_for(schema)` 选择 `Draft7Validator`，对完整 user settings 校验：`error_count=0`

这证明当前文件与 2026-07-14 获取的发布 schema 一致；不证明所有字段在本机 `2.1.206` 的运行行为，也不证明合并后的 resolved settings。

### 6.3 本机与最新网页的版本差

| 能力 | 官方文档标记 | 本机判断 |
|---|---|---|
| path rule 中一个非法 glob 只让该 pattern 匹配失败 | `2.1.207+` | 本机 `2.1.206` 不可依赖；verifier 应在静态阶段拒绝非法 glob。 |
| 未信任 workspace 中 untracked `settings.local.json` 的 allow 行为修正 | 文档说明 `2.1.207` 改变 | 不把 `-p` 或未显示 trust prompt 当授权生效证明。 |
| subagent sibling roster | `2.1.206+` | 版本满足，但与规则治理非关键，不进入根规则。 |
| `InstructionsLoaded` | 当前 official hooks reference | 可作为 fresh-session 可观测证据；尚未在本研究启动 session 实测。 |

## 7. 推荐的协同架构

| 层 | OpenAI 侧 | Anthropic 侧 | 确定性承接 | 静态 / 动态验证 |
|---|---|---|---|---|
| 全局共同 WHAT | `~/.codex/AGENTS.md` 中跨仓稳定语义 | `~/.claude/CLAUDE.md` 中语义一致的 common body | user / managed policy 中的通用限制 | family verifier + 两宿主 fresh load |
| Platform DELTA | `CODEX_HOME`、AGENTS discovery / byte budget、config / requirements、sandbox / approval、hooks / exec rules、Work surface boundary | CLAUDE 拼接 / import、settings precedence、permissions / hooks、Windows sandbox N/A、chat / code / cloud boundary | config、requirements、settings、permissions、hooks | current help / schema + prompt-input / `/status` 等动态证据 |
| 项目共同 WHERE/HOW | 根 `AGENTS.md`：项目定位、边界、真实门禁、证据、回滚、N/A | 通过薄 wrapper 导入同一 `AGENTS.md` | repo scripts、schema、tests、CI | project contract verifier + full gate |
| Claude project wrapper | Codex 不需要 wrapper，也不得默认把 `CLAUDE.md` 加入 fallback | 第一物理行 `@AGENTS.md`；仅真实 Claude 差异 | import / encoding / duplicate-content verifier | `/memory` + `InstructionsLoaded` |
| 局部渐进披露 | nested `AGENTS.md` / override；低频流程进入 skills | `.claude/rules/` path rule；低频流程进入 skills | permissions / hook / CI，不靠 path rule 做新文件前的唯一安全阻断 | Codex 子目录 prompt-input；Claude Read-trigger probe + glob validator |
| 跨 surface 边界 | Work web/mobile、Codex Local、Codex cloud 分别验证 | Claude Chat、Desktop Code local、CLI、cloud 分别验证 | workspace RBAC / source permissions 与 local runtime policy 分层 | 不用本机文件 hash外推 hosted surface |

“1+1>2”的验收条件不是文件存在，而是：

1. `AGENTS.md` 与 wrapper 没有重复或相反语义；
2. 从 global + project 能推出当前落点、目标归宿、门禁、证据、回滚；
3. 需要保证的限制在 permission / hook / script / CI 中有机器承接；
4. Codex 与 Claude 的 fresh process 都能证明预期规则来源与 resolved enforcement 实际生效；
5. ChatGPT Work / Codex Local / Codex cloud 与 Claude Chat / Code local / cloud 的边界分别成立；
6. native Windows、版本差、schema drift 与诊断缺口被显式记录，而不是被 prose 掩盖。

## 8. 推荐验证协议

### 8.1 静态验证

1. OpenAI / Anthropic 全局共同段逐字或语义一致，platform DELTA 不含目标仓私有事实。
2. Codex 每条 root-to-cwd chain 每层最多一个候选，总字节不超过 `project_doc_max_bytes`，fallback 名来自 current config。
3. `CLAUDE.md` 第一物理行等于 `@AGENTS.md`，UTF-8 无 BOM，无循环 import，import depth `<= 5`。此项于 2026-07-15 按官方现行文档校正。
4. wrapper 与 `AGENTS.md` 共同段落重复率低于阈值；无 Claude 差异时 wrapper 只能有一行。
5. global / project / nested rules 无相反指令；不能用“project override global”豁免 Claude 冲突。
6. 每个 `.claude/rules/*.md` 的 frontmatter 可解析、glob 合法；关键安全约束不得只放 Read-trigger 的 path rule。
7. Codex TOML 与 Claude JSON settings 通过 current schema，再按 installed CLI version 检查 min-version 与 experimental 字段。
8. 权限性措辞必须映射到 requirements / settings / permission / hook / script / CI，或产生带复测条件的 N/A / waiver。

### 8.2 fresh-session 动态验证

在用户明确允许新宿主进程后，对全局与每个目标仓至少执行：

**Codex：**

1. 记录 `codex --version`、`codex --help` 与 config schema 结果。
2. 在仓根和关键子目录分别运行新的 `codex debug prompt-input`，记录 model-visible instruction list 与来源；失败时按本报告 `platform_na` 字段留痕。
3. 用无副作用正反例验证 sandbox、approval、hook trust 和 `codex execpolicy check`，不把模型复述当 enforcement 证明。
4. 如使用 hosted Work / Codex cloud，另取对应 workspace / cloud task 证据，不能复用 local prompt-input 结论。

**Claude：**

1. 记录 `claude --version`、`claude --help`。
2. 从仓根启动新的 interactive session，运行 `/context`、`/memory`、`/permissions`、`/hooks`、`/status`。
3. 用 `InstructionsLoaded` hook 或 debug log 记录 `file_path / memory_type / load_reason / parent_file_path`；该 hook 只作 observability。
4. Read 一个具有 nested `CLAUDE.md` 或 path rule 的文件，证明 lazy load；不要用 Write/Create 作为触发证明。
5. 对 permission/hook 做无副作用正反例：一个明确 allow、一个明确 deny、一个 hook `exit 2`；记录 resolved source 与结果。
6. 如配置疑难，用 `--safe-mode` 做差分；不要将 safe-mode session 当正常规则已加载的证据。
7. 不用 `claude -p` 单独证明 workspace trust、project allow 或 settings 校验成功。

终端 `claude doctor` 按官方文档是 read-only，可在任务授权范围内作为 settings validation 补充；交互 `/doctor` 会提出修复并在确认后应用，不属于只读探针。

## 9. 官方示例与社区结构启发

### 9.1 OpenAI 官方源码与 Anthropic 官方仓库示例

`openai/codex` 的当前源码与测试可用于核对文档实现，但仍不能替代 installed version help / schema。固定 commit `effd58d7505382f6b2d1736a4fc9e3eb90df1966` 的 `codex-rs/core/src/agents_md.rs` 可验证 override / fallback、空文件跳过、root-to-cwd 拼接与总字节预算；本轮只采纳这些由 manual 同时支持的 loader 事实，不把 main 分支未发布能力写成本机既定能力。

- 固定版本：[openai/codex at `effd58d`](https://github.com/openai/codex/tree/effd58d7505382f6b2d1736a4fc9e3eb90df1966)
- 采纳：loader provenance、总预算与当前 CLI 诊断入口的源码交叉验证。
- 拒绝：仅因 main 已出现某字段就宣称本机 `0.144.1` 支持；仍需 installed help / schema / probe。

`anthropics/claude-code` 的 settings 示例展示 managed-only permission / hook / sandbox 组合，但 README 明确称这些是 community-maintained snippets，可能 unsupported 或 incorrect，用户需自行负责正确性。因此它只能作为配置候选，不能高于正式文档、当前 schema 和本机 help。

- 固定版本：[examples/settings/README.md at `988b3e5`](https://github.com/anthropics/claude-code/blob/988b3e56432775c09bba903ba22522b97cd0f2fb/examples/settings/README.md)
- 采纳：将 permission、hook、Bash sandbox 分层；部署前用本地 managed/user/project scope 分别验证。
- 拒绝：整份复制 strict/lax 示例；把“位于官方仓库”误当“正式支持契约”。

### 9.2 `getsentry/sentry`

当前 root `CLAUDE.md` 仍只有 `@AGENTS.md`；root `AGENTS.md` 声明其为 source of truth，并把目录规则与 workflow skills 分开。这是“共同主体 + 薄 wrapper + 目录渐进披露”的成熟实例。

- [CLAUDE.md at `088a5db`](https://github.com/getsentry/sentry/blob/088a5dbdc40a157a49047eaa47982b13ce9183fd/CLAUDE.md)
- [AGENTS.md at `088a5db`](https://github.com/getsentry/sentry/blob/088a5dbdc40a157a49047eaa47982b13ce9183fd/AGENTS.md)
- 采纳：source-of-truth 单一、wrapper 极薄、局部事实与 workflow skill 分离。
- 不采纳：其具体 permission、Python 环境和部署命令；这些只属于 Sentry。

### 9.3 `vercel/next.js`

当前 `CLAUDE.md` 是到 `AGENTS.md` 的 symlink，结构上避免了正文漂移；根规则还把高频基线和专项 skills 分开。

- [CLAUDE.md at `303f7ff`](https://github.com/vercel/next.js/blob/303f7ffd4a0db19948a71eba73cd85f366625a65/CLAUDE.md)
- [AGENTS.md at `303f7ff`](https://github.com/vercel/next.js/blob/303f7ffd4a0db19948a71eba73cd85f366625a65/AGENTS.md)
- 采纳：单一共同主体、专项技能按需披露。
- 拒绝：Windows 目标仓使用 symlink；Anthropic 官方已明确建议 Windows 用 `@AGENTS.md` import。

### 9.4 `agentsmd/agents.md`

开放格式把 `AGENTS.md` 定位为“agent 的 README”，最小示例优先写环境、测试和 PR 的真实命令。

- [README at `d1ac7f0`](https://github.com/agentsmd/agents.md/blob/d1ac7f063d20e70015ed6732664049ae4ba9d74e/README.md)
- 采纳：项目主体宿主中立、命令具体、直接指向 CI/test。
- 不采纳：把该格式当作 Claude 的加载、权限、import 或 hook 规范；这些仍以 Anthropic 为准。

## 10. 采纳、拒绝与暂缓矩阵

| 结论 | Decision | 原因 / 后续 |
|---|---|---|
| `AGENTS.md` common body + 一行 `CLAUDE.md` import | `adopt` | 官方明确支持，Windows 兼容，消除正文漂移。 |
| 用本机 global `AGENTS.md` hash 证明 ChatGPT Work web 已加载同一规则 | `reject` | local 与 hosted surface 控制不同；需要各自 fresh evidence。 |
| trusted project `.codex/config.toml` 承载本仓 sandbox / hook 等差异 | `adopt (conditional)` | 官方支持，但必须受 trust、schema 与 project 禁止键约束。 |
| 把 provider / auth / telemetry 设置放项目 `.codex/config.toml` | `reject` | 客户端明确忽略 host-owned keys 并警告；也越过本任务禁区。 |
| Codex hooks 作为 lifecycle enforcement / observability | `adopt (conditional)` | 当前 manual 标 stable；非 managed hook 仍需 hash trust，匹配 command hooks 可并行。 |
| Codex exec `.rules` 作为唯一安全边界 | `reject` | 当前仍 experimental，且只控制 sandbox 外命令；需 sandbox / hooks / CI 组合。 |
| `approval_policy = "never"` 等于 full access | `reject` | 它只关闭 prompt；实际权限仍由 sandbox / permission profile 决定。 |
| `requirements.toml` 等同 ChatGPT workspace RBAC | `reject` | managed runtime constraints 与 workspace access / role 是不同层。 |
| 修复 live config 的八个 MCP `transport` schema drift | `defer` | 属用户 live config，且可能涉及 provider / MCP 行为；本研究只读并未获修复授权。 |
| `codex doctor` / `debug prompt-input` 超时后仍声明加载成功 | `reject` | 本轮为 `platform_na`，需在 controlled window 复测。 |
| 项目规则通过相反文字覆盖全局规则 | `reject` | 文件是拼接 context；冲突时模型可能任意选择。 |
| import 作为 token 优化 | `reject` | import 在启动时展开并占 context。 |
| 根规则保留所有教程与低频流程 | `reject` | 官方建议 `<200` 行且只保留每 session 必需内容；低频流程进入 skill/runbook。 |
| permission deny + narrower allow 形成例外 | `reject` | deny 先于 ask/allow，specificity 不改变顺序。 |
| hook `exit 1` 作为阻断 | `reject` | 除少数事件外仅 `exit 2` 阻断。 |
| native Windows 宣称 Claude Bash sandbox 已启用 | `reject` | 官方不支持；必须 WSL2 或 N/A + 替代控制。 |
| `claude -p` 作为 fresh trust / settings 证明 | `reject` | 无 trust dialog，invalid settings 可静默忽略。 |
| `InstructionsLoaded` 作为加载审计 | `adopt` | 能提供路径、scope、原因；仅 observability，不夸大为强制。 |
| `TaskCompleted` hook 统一跑全量门禁 | `defer` | 仅在使用 Task 生命周期时触发，且可能昂贵；应按仓先做 quick gate，full gate 留 CI。 |
| 部署 managed settings / registry policy | `defer` | 属组织级持久化与权限决策；本轮未获授权，也未核实 remote/registry 当前状态。 |
| 升级本机到 `2.1.207+` | `defer` | 本任务是审查与治理，不包含安装升级；升级后重跑 schema、trust、glob 与 fresh-session 探针。 |
| `claudeMdExcludes` | `adopt (conditional)` | 只在 monorepo 实测出现无关 sibling 规则时使用，不作为默认复杂度。 |

## 11. 证据限制与完成边界

- 官方网页是 2026-07-14 的 live 内容；后续 CLI 更新可能改变 min-version 与字段。发布规则时应固定访问日期并重新取证。
- OpenAI manual helper 报告当前缓存为 current，但页面仍是在线可变资料；fixed commit 源码只补交叉验证，不代表 installed binary 已包含 main 全部行为。
- 本研究没有启动 ChatGPT Work、Codex cloud、Codex App 新 task 或付费模型调用；`codex doctor` / `debug prompt-input` 没有在短时探针内返回，因此 OpenAI fresh-process loading 仍未关闭。
- 本研究没有启动 Claude interactive / print session，没有运行 `claude doctor`，没有修改 `~/.claude`，没有检查或改变 auth、provider、remote managed settings、HKLM/HKCU policy，也没有启动/停止/杀掉 Claude 进程。
- 本研究没有修改 `~/.codex`、`~/.claude`、auth、provider、凭据或 managed policy，也没有重启、停止或杀掉 Codex / Claude 进程。
- Codex schema 校验发现 8 个 live config drift；Claude schema 校验为 0 error。两者都不证明 resolved settings、cloud-managed layer、workspace trust 或 runtime behavior。
- 本研究只提供跨平台架构与验证依据，不等于全局规则已优化、目标仓已逐仓审计、规则已同步、门禁已通过、fresh loading 已验收或远端已生效。
- Gemini 完全不在研究与建议范围内。

## 12. 官方来源索引

### OpenAI

- [Codex manual](https://developers.openai.com/codex/codex-manual.md)（通过 `openai-docs` helper 获取并按 outline 定向阅读）
- [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Config basics](https://learn.chatgpt.com/docs/config-file/config-basic)
- [Advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced)
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [Codex config JSON schema](https://developers.openai.com/codex/config-schema.json)
- [Agent approvals & security](https://learn.chatgpt.com/docs/agent-approvals-security)
- [Hooks](https://learn.chatgpt.com/docs/hooks)
- [Rules](https://learn.chatgpt.com/docs/agent-configuration/rules)
- [Managed configuration](https://learn.chatgpt.com/docs/enterprise/managed-configuration)
- [Personalize ChatGPT](https://learn.chatgpt.com/docs/personalize)
- [ChatGPT Work Admin FAQ](https://learn.chatgpt.com/docs/enterprise/work-admin-faq)
- [CLI command reference](https://learn.chatgpt.com/docs/developer-commands?surface=cli)
- [openai/codex at `effd58d`](https://github.com/openai/codex/tree/effd58d7505382f6b2d1736a4fc9e3eb90df1966)

### Anthropic

- [Memory / CLAUDE.md](https://code.claude.com/docs/en/memory)
- [Settings](https://code.claude.com/docs/en/settings)
- [Permissions](https://code.claude.com/docs/en/permissions)
- [Hooks reference](https://code.claude.com/docs/en/hooks)
- [Sandboxing](https://code.claude.com/docs/en/sandboxing)
- [Debug your configuration](https://code.claude.com/docs/en/debug-your-config)
- [CLI reference](https://code.claude.com/docs/en/cli-reference)
- [Skills](https://code.claude.com/docs/en/skills)
- [Subagents](https://code.claude.com/docs/en/sub-agents)
- [Best practices](https://code.claude.com/docs/en/best-practices)
- [Claude Desktop Code](https://code.claude.com/docs/en/desktop)
- [Claude Code on the web](https://code.claude.com/docs/en/claude-code-on-the-web)
- [Claude personalization](https://support.claude.com/en/articles/10185728-understanding-claude-s-personalization-features)
- [Claude projects](https://support.claude.com/en/articles/9519177-how-can-i-create-and-manage-projects)
- [Claude Code settings JSON schema](https://json.schemastore.org/claude-code-settings.json)
- [anthropics/claude-code at `988b3e5`](https://github.com/anthropics/claude-code/tree/988b3e56432775c09bba903ba22522b97cd0f2fb)

以上官方页面访问日期均为 2026-07-14。
