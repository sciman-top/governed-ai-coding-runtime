# AGENTS.md - governed-ai-coding-runtime
**项目契约**: 2.0
**全局规则复核**: 9.57
**适用范围**: 仓库根
**最后更新**: 2026-07-17

## 1. 当前落点与目标归宿
- 当前落点：本仓是 OpenAI Codex 与 Anthropic Claude Code 规则治理控制仓，不是 AI coding runtime。
- 目标归宿：以静态文件和短生命周期 CLI 管理全局规则源、宿主差异、目标仓登记、确定性审计、受保护同步、CI 协同与发布证据。
- 当前最小里程碑：完成治理 v2 裁剪，使 `python scripts/rulesctl.py verify` 在控制仓内可复现通过，并让跨仓动态失败继续由 `status` / `audit` 独立暴露。
- 事实裁决顺序：当前代码与命令输出 -> 根 `README.md` -> `docs/README.md` -> 架构、runbook 与证据；这不改变宿主指令优先级。
- 旧 runtime 完整树由 tag `archive/runtime-v1-20260716` 和 Git 历史保留，不在活动树维护兼容入口。

## A. 仓库事实与模块边界
- `rules/global/sources/` 与 `rules/global/source-manifest.json`：Codex/Claude 全局规则的唯一装配源。
- `rules/global/codex/AGENTS.md` 与 `rules/global/claude/CLAUDE.md`：确定性生成并提交的全局投影。
- `rules/manifest.json`：只定义两个用户级全局投影；不得加入目标仓规则正文。
- `rules/target-project-rule-coordination.json`：9 个目标仓的显式 allowlist、Git 根发现和审计契约；发现不等于自动纳管。
- `rules/templates/github/agent-rule-contract.yml`：目标仓规则 CI 契约模板。
- `schemas/jsonschema/target-project-rule-coordination.schema.json`：跨仓登记表的唯一活动 schema。
- `scripts/rulesctl.py`：唯一主入口；其余保留脚本只实现装配、family 校验、目标审计、全局同步和 CI matrix 导出。
- `tests/runtime/`：只保留规则治理测试；`docs/`：只保留当前架构、runbook、来源依据和发布证据。
- 目标仓拥有自己的 `AGENTS.md`、一行 `CLAUDE.md` wrapper、真实产品门禁、证据和回滚。本地审计不移动、清理、覆盖或 blind-sync 现有目标工作树；聚合 CI 只使用隔离 checkout，不写回目标仓。

### A.1 产品非目标
- 不提供数据库、HTTP API、Web UI、daemon、task runtime、模型调用层或多代理编排。
- 不管理 provider、base URL、API key、OAuth、账号、计费、模型路由、MCP、session/history 或 gateway。
- 不启动、停止、重启或监督 Codex、Claude、Cockpit 或相关进程。
- 不把本地 hash、静态审计或控制仓通过解释为 native host 已加载、hosted surface 已接受或目标产品已验收。

## B. 执行与风险边界
- 改动前声明当前落点 -> 目标归宿 -> 验证方式；优先选择边界清楚、可验证、可回滚的最大合理切片。
- 全局 A/C/D 共同正文必须一致，平台差异只进入各自 B；生成文件不得手工漂移，先改 canonical sources，再执行 build/check。
- 目标 `AGENTS.md` 必须宿主中立；`CLAUDE.md` 默认是无 BOM、仅一行 `@AGENTS.md` 的适配器，除非存在已验证的 Claude-only delta。
- 同版本全局投影漂移必须阻断；同步先 dry-run，apply 属于持久化动作，必须保留 backup、零漂移复核和回滚证据。
- 规则 prose 不等于权限或安全强制；确定性约束应落到宿主 settings/policy/hooks、仓库脚本或 CI，并由各自所有者管理。
- 跨仓审计默认读取 `origin/main` 的 Git 对象，不 checkout、不 reset、不 clean 目标仓；workspace 审计是独立观察面。
- 未经当前任务明确确认，不得重启、停止、杀掉或自动拉起 Codex App、`codex`、Claude Code、Claude Desktop 或 `claude`。
- 不得恢复 archive 中的 runtime、Gemini、provider、session、operator UI、orchestration 或 Codex/Cockpit shim。

## C. 门禁、阻断与证据
### C.1 固定门禁
- fixed order：`build -> test -> contract/invariant -> hotspot`。
- build：`python scripts/rulesctl.py build`
- test：`python scripts/rulesctl.py test`
- contract/invariant：`python scripts/rulesctl.py contract`
- hotspot：`python scripts/rulesctl.py hotspot`
- full repo-local gate：`python scripts/rulesctl.py verify`
- `verify` 默认不纳入外部可变九仓状态；显式 `--include-targets` 才把 default-branch audit 加入 contract。

### C.2 动态状态与发布入口
- 分层状态：`python scripts/rulesctl.py status`
- 九仓 default branch 审计：`python scripts/rulesctl.py audit --state default`
- 九仓 workspace 审计：`python scripts/rulesctl.py audit --state workspace`
- CI matrix：`python scripts/rulesctl.py matrix`
- 全局 dry-run：`python scripts/rulesctl.py sync --check`
- 全局 apply：`python scripts/rulesctl.py sync --apply`
- 发布顺序：canonical build/check -> repo-local verify -> default-branch audit -> sync dry-run -> 授权后 apply -> 零漂移 -> fresh native loading probes -> hosted acceptance（若适用）。

### C.3 阻断、证据与回滚
- canonical source/output 漂移、manifest/schema 不兼容、wrapper 形态错误、未登记/缺失目标仓、旧产品 surface 回流时阻断。
- 控制仓 `verify` 通过不消除 `status` / `audit` 的目标失败；任一聚合状态不得覆盖 target-level finding。
- `host_loaded` 与 `hosted_accepted` 没有 fresh native/hosted evidence 时保持 `unknown`，不得推断。
- 当前证据落在 `docs/change-evidence/`；最低字段为 scope、revision、risk、command、exit code、关键输出、兼容性、N/A、回滚和 fresh timestamp。
- 控制仓回滚只撤销本切片；全局同步回滚使用同步 backup 与恢复后的 canonical source；目标仓回滚只由目标仓执行。
- 旧 runtime 回溯使用 `git show archive/runtime-v1-20260716:<path>`，不得把 archive 文件复制回活动树充当兼容层。

## D. Global Rule -> Repo Action
- `R1/R2/R3/R5`：以本文件 1/B 和 `tasks/plan.md` 确定归宿，按测试后提交的小步闭环推进；临时兼容必须写回收条件。
- `R4/R7`：同步先 dry-run；目标审计只读 Git 对象；provider/auth/进程和目标仓写入不在本产品授权内。
- `R6`：交付前严格执行 C.1；动态 fleet 审计按 C.2 单独报告，不伪装为 repo-local gate。
- `R8`：`docs/change-evidence/` 记录依据、命令、结果和回滚；缺失能力按全局 N/A 字段完整留痕。
- `E4`：`rulesctl status`、`verify` 和 `audit` 提供健康状态；JSON 输出是机器证据。
- `E5`：`gate_na`；reason=`活动树无第三方运行时依赖或包管理器`；alternative_verification=`rulesctl build + GitHub Actions pinned action review`；evidence_link=`docs/research/agent-rule-governance-v2-sources.md`；expires_at=`2026-10-15`；recovery_condition=`新增依赖清单或外部执行依赖时恢复供应链门禁`。
- `E6`：只保留 coordination JSON/schema；修改时必须同步 schema、测试、兼容说明和回滚。数据库迁移为 `gate_na`；reason=`活动树无数据库或持久化服务`；alternative_verification=`coordination schema + JSON parse + contract tests`；evidence_link=`schemas/jsonschema/target-project-rule-coordination.schema.json`；expires_at=`2026-10-15`；recovery_condition=`活动树重新引入持久化数据结构时恢复迁移门禁`。
- 协同验收：仅凭全局规则与本文件，应能推出产品边界、唯一入口、门禁顺序、动态状态、证据路径和回滚入口。
