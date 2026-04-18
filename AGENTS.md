# AGENTS.md — governed-ai-coding-runtime 项目承接规则
**承接来源**: `GlobalUser/AGENTS.md v9.39`
**适用范围**: `D:\OneDrive\CODE\governed-ai-coding-runtime`  
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
- 当前仓库已存在 `.git`；默认回滚优先使用 git 历史，`docs/change-evidence/snapshots/` 只作为补充留痕或无 git 场景兜底。
- 当前证据统一落在 `docs/change-evidence/`。
- 面向操作者的使用说明/指南/教程类文档必须保持中英双语可用；最低覆盖范围包括 `README*`、`docs/quickstart/*`、`docs/product/*guide*`、`docs/product/*flow*`、`docs/product/*commands*`、`docs/product/*trial*`、`docs/product/*pilot*`、`docs/product/*console*`、`docs/product/*criteria*`、以及其他直接描述运行步骤或操作路径的文档。
- 纯策略、研究、架构、规划、ADR、spec/schema 配套说明默认不强制逐篇双语，但只要文档直接承担操作者使用入口，就应补齐对应中英版本或明确链接到可替代的双语入口。

## B. 仓库门禁与阻断
| gate | status | command | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|---|
| build | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` | Foundation 阶段的 build 语义是验证 Python runtime substrate 可字节编译且可导入 | `python -m compileall packages/contracts/src scripts/run-readonly-trial.py` | `docs/change-evidence/*.md` | `n/a` |
| test | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | Phase 1 已落地 Python runtime contract unit tests | `python -m unittest discover -s tests/runtime -p "test_*.py"` | `docs/change-evidence/*.md` | `n/a` |
| contract/invariant | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | 当前仓库最硬的机器约束是 schema、example、catalog 与 spec 配对完整性 | 同步检查 `schemas/catalog/schema-catalog.yaml`、`docs/specs/*`、`schemas/examples/*` 配对完整性 | `docs/change-evidence/*.md` | `n/a` |
| hotspot | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` | Foundation 阶段的 hotspot/doctor 语义是验证 runtime prerequisites、schema/catalog 可见性与活跃 gate 命令存在 | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Doctor` | `docs/change-evidence/*.md` | `n/a` |

- 阻断条件：
  - `docs/specs/*` 与 `schemas/jsonschema/*` 只改一侧时阻断。
  - 根 `README.md`、`docs/README.md`、`docs/roadmap/*`、`docs/backlog/*` 叙述不一致时阻断。
  - `scripts/github/create-roadmap-issues.ps1` 与当前 roadmap/backlog 基线不一致时阻断。

## C. 承接映射
- `E4 健康指标联动`：`active`
  - `reason`: 当前以 Foundation doctor 入口替代未来服务级 health 指标栈
  - `alternative_verification`: `scripts/verify-repo.ps1 -Check Doctor`
  - `evidence_link`: `docs/change-evidence/*.md`
  - `expires_at`: `n/a`
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
- 历史回滚优先通过 git 提交或差异恢复；当工作区无 `.git` 或需要额外证据快照时，再复制到 `docs/change-evidence/snapshots/<date>-<slug>/`，快照命名需保留原始相对路径信息。
- 当前真实门禁顺序为 `build -> test -> contract/invariant -> hotspot`；后续服务化阶段只能增强，不得改序。

## E. 提交信息规范
- 提交信息以中文为主，但不强制全中文。
- `subject` 需要短、具体、可检索，优先表达本次变更的事实，不写口号。
- 技术名词、文件名、协议名、ADR 编号可以保留英文或中英混合，以保证跨工具检索和历史追溯。
- 若变更面向外部共享历史、跨团队协作或后续回滚定位，优先保证语义清晰，其次再考虑语言纯度。

