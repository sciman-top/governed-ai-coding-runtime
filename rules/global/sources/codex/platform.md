## B. Codex 平台差异
### B.1 加载链
- 用户目录为 `~/.codex`，可由 `CODEX_HOME` 覆盖；同目录只取首个非空文件，优先级为 `AGENTS.override.md > AGENTS.md`。
- 项目规则从 Git root 到当前目录逐层加载；每层按 `AGENTS.override.md > AGENTS.md > project_doc_fallback_filenames` 取最多一个文件，更靠近当前目录的内容更晚进入上下文。
- `project_doc_max_bytes` 默认 32 KiB，约束的是一次项目规则链的总读取预算，不是每个文件各有 32 KiB；关键规则前置，超限内容下沉。
- fallback 只认显式配置文件名；不得假定 `CLAUDE.md` 会自动加载。当前官方稳定面未证明的选项不得写成既定能力。
- `AGENTS.override.md` 仅用于短期排障，结束后删除并用新 run/session 复测；不假定当前会话热加载。
- ChatGPT 桌面端 Personalization 可编辑 Codex personal instructions；ChatGPT Work Web 的 hosted/project instructions 与本机 `~/.codex/AGENTS.md` 不得假定为同一存储或自动双向投影。

### B.2 诊断与强制
- 最小诊断：`codex --version`、`codex --help`；加载核验优先使用新会话的 `codex debug prompt-input`，不可用时记录 `platform_na`、替代证据与复测条件。
- 扩展命令必须先由当前 help 证明存在；日志/session jsonl 只作补充证据。
- `AGENTS.md` 不是权限系统；可重复权限、危险命令拦截和沙箱边界放入 `config.toml`、hooks、仓库脚本或 CI；项目 config/hooks/rules 只在 trusted repo 中生效。
- `.codex/rules/*.rules` 当前仍是 experimental；使用时按精确命令前缀建模，提供 `match/not_match` 样例并以当前 `codex execpolicy check` 实测，避免过宽 allowlist。
- ChatGPT Work Web 运行于 hosted environment，不继承本机 Codex sandbox/approval 控件；`requirements.toml`、managed config 与 ChatGPT workspace RBAC 也不得混为同一层。
- `approval_policy = "never"`、`danger-full-access` 或 bypass 模式不取消 R4/R8；只在明确授权或外部隔离边界内使用。
- 修改 auth、provider、MCP 或权限前，先区分登录链路、执行权限、模型能力与仓库代码问题。
- 未经当前任务明确确认，不得重启、停止、杀掉或自动拉起 Codex App / `codex` 进程；先做文件级投影、dry-run、连通性探针与回滚证据。

### B.3 回退
- 命令缺失、help 与行为不一致或非交互失败时，按 `platform_na` 留痕；替代证据只补证明，不改变共同规则和门禁语义。
