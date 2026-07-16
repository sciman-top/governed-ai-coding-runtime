# Codex + Claude 规则治理控制仓

## 结论

本项目的最优终态不是“通用 AI coding runtime”，而是一个无服务、静态、可审计的
规则治理控制仓，只负责 OpenAI Codex 与 Anthropic Claude Code 两套规则。

技术栈保持为 Markdown、JSON/JSON Schema、Python、PowerShell、Git 与 GitHub
Actions。现有需求不需要数据库、Web UI、HTTP API、daemon、消息队列、模型调用层，
也没有依据改写为 Node.js、Rust 或另建微服务。

## 所有权边界

- 本仓拥有：全局 canonical sources、Codex/Claude 宿主差异、显式九仓登记、确定性
  校验、受保护全局投影、跨仓 CI matrix 与发布证据。
- 目标仓拥有：项目 `AGENTS.md`、一行 `CLAUDE.md` wrapper、真实产品命令、门禁、
  证据与回滚。
- 本地审计不移动、reset、clean、覆盖或 blind-sync 现有目标工作树；聚合 CI 只使用
  隔离 checkout，不写回目标仓。
- provider、base URL、API key、OAuth、账号、session/history、MCP、gateway、进程启停
  均不属于本产品。

旧 runtime 完整树保存在 tag `archive/runtime-v1-20260716`，不在活动树提供兼容入口。

## 使用

```powershell
python scripts/rulesctl.py status
python scripts/rulesctl.py verify
```

- `status` 严格报告 source、global projection、target default branch 与 workspace；
  外部目标不合规时可以失败。
- `verify` 是控制仓可复现门禁，固定执行
  `build -> test -> contract/invariant -> hotspot`。
- `verify --include-targets` 才显式把可变九仓审计加入门禁。

其他入口：

```powershell
python scripts/rulesctl.py audit --state default
python scripts/rulesctl.py audit --state workspace
python scripts/rulesctl.py sync --check
python scripts/rulesctl.py matrix
```

`sync --apply` 会写用户级全局规则，属于独立持久化动作；它不会分发目标仓规则正文。

## 状态边界

`workspace_effective`、`default_branch_effective`、`host_loaded`、
`hosted_accepted` 必须分别取证。控制仓通过不代表九仓全通过，本地文件 hash 相等也不
代表 native host 已加载或 hosted surface 已接受。

## 为什么这是当前最优架构

- 符合宿主原生机制：Codex 原生读取 `AGENTS.md`；Claude Code 读取 `CLAUDE.md`，
  并可通过 `@AGENTS.md` 复用共同正文。
- 目标仓事实不离开目标仓，避免中央副本与真实命令漂移。
- 两个宿主的加载、信任、settings、permissions 与 hooks 语义不同，分别适配比伪造
  统一运行时更准确。
- immutable Git revision audit、dry-run、原子投影、backup、回滚与 CI drift gate 已
  覆盖真实风险，运维面最小。

后续阅读：[文档索引](docs/README.md)、[架构](docs/architecture/agent-rule-governance-v2.md)、
[发布 runbook](docs/runbooks/agent-rule-release.md)、
[来源依据](docs/research/agent-rule-governance-v2-sources.md)。
