# AGENTS.md — governed-agent-platform 项目承接规则
**承接来源**: `GlobalUser/AGENTS.md v9.38`  
**适用范围**: `D:\OneDrive\CODE\governed-agent-platform`  
**最后更新**: `2026-04-17`

## 1. 阅读指引
- 本文件只写本仓事实、门禁命令、证据位置和回滚入口，不重写全局 `R/E` 语义。
- 当前仓库处于 `docs-first / contracts-first` 阶段；已落地目录只有 `docs/`、`schemas/`、`scripts/`。
- 当前目标归宿：
  - 文档、决策、审查结论：`docs/`
  - 机器可读契约：`schemas/`
  - GitHub / 规划辅助脚本：`scripts/`
  - 后续实现骨架：`apps/`、`packages/`、`infra/`、`tests/`（规划中，尚未落地）

## A. 项目基线
- 当前权威输入顺序：根 `README.md` -> `docs/README.md` -> PRD -> Architecture -> Roadmap -> Backlog -> Specs -> Schemas。
- `docs/specs/*` 定义语义；`schemas/jsonschema/*` 是配套机器可读草案；修改其一必须同步检查另一侧。
- `scripts/github/create-roadmap-issues.ps1` 只负责 backlog/issue 种子生成，不代表运行时实现已经存在。
- 当前证据统一落在 `docs/change-evidence/`；当前工作区未见 `.git` 时，回滚快照落在 `docs/change-evidence/snapshots/`。

## B. 仓库门禁与阻断
| gate | status | command | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|---|
| build | `gate_na` | `n/a` | 运行时服务与构建入口尚未落地 | 核对根 README、docs index、roadmap、backlog 是否一致 | `docs/change-evidence/*.md` | `2026-05-31` |
| test | `gate_na` | `n/a` | 尚无测试 harness 或 CI 流水线 | 解析 PowerShell 脚本语法，检查关键计划文件链接完整性 | `docs/change-evidence/*.md` | `2026-05-31` |
| contract/invariant | `active` | `Get-ChildItem schemas/jsonschema/*.json | ForEach-Object { Get-Content -Raw $_.FullName | ConvertFrom-Json > $null }` | 当前仓库最硬的机器约束是 schema 完整性 | 同步检查 `schemas/catalog/schema-catalog.yaml` 与 `docs/specs/*` 引用完整性 | `docs/change-evidence/*.md` | `n/a` |
| hotspot | `gate_na` | `n/a` | 尚无 runtime health/doctor 入口 | 扫描缺失文档引用、过期规划基线、未闭合决策 | `docs/change-evidence/*.md` | `2026-05-31` |

- 阻断条件：
  - `docs/specs/*` 与 `schemas/jsonschema/*` 只改一侧时阻断。
  - 根 `README.md`、`docs/README.md`、`docs/roadmap/*`、`docs/backlog/*` 叙述不一致时阻断。
  - `scripts/github/create-roadmap-issues.ps1` 与当前 roadmap/backlog 基线不一致时阻断。

## C. 承接映射
- `E4 健康指标联动`：`gate_na`
  - `reason`: 尚无服务进程、指标栈和健康脚本
  - `alternative_verification`: 规划、schema、脚本三层一致性检查
  - `evidence_link`: `docs/change-evidence/*.md`
  - `expires_at`: `2026-05-31`
- `E5 供应链门禁`：`gate_na`
  - `reason`: 尚无 `pyproject.toml`、`package.json`、lockfile 或依赖清单
  - `alternative_verification`: 新增依赖前先落地包管理清单与 CI 校验
  - `evidence_link`: `docs/change-evidence/*.md`
  - `expires_at`: `2026-05-31`
- `E6 数据结构变更`：`active`
  - 触发范围：`docs/specs/*`、`schemas/jsonschema/*`、`schemas/catalog/schema-catalog.yaml`
  - 必做动作：同步更新配套文档/Schema/Catalog，并在证据中记录兼容性和回滚说明
- 失败分流：
  - doc link drift -> 先修文档入口与引用
  - schema parse fail -> 先修 schema/spec 配对
  - roadmap/script drift -> roadmap、backlog、issue script 同步修复

## D. 维护清单
- 保持根 `README.md`、`docs/README.md`、roadmap、backlog、issue seeding script 同步。
- 规划、schema、脚本类变更必须新增一条 `docs/change-evidence/*.md`。
- 在 git bootstrap 落地前，修改已有文件前先复制到 `docs/change-evidence/snapshots/<date>-<slug>/`，快照命名需保留原始相对路径信息。
- 当 `apps/`、`packages/`、`infra/`、`tests/` 落地后，用真实命令替换上表中的 `gate_na`，顺序必须保持 `build -> test -> contract/invariant -> hotspot`。
