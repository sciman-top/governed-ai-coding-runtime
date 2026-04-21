# 20260422 Repo-Profile 字段草案与 Fast/Full 门禁骨架

## Goal
在不改变现有全局/项目级硬门禁语义的前提下，补齐可迁移到目标仓的最小落地资产：
- 可直接复用的 `repo-profile` 字段草案样例
- 可执行的 `fast/full` 门禁脚本骨架
- 项目级规则文件中的跨仓迁移入口说明

## Scope
- `AGENTS.md`
- `schemas/examples/repo-profile/target-repo-fast-full-template.example.json`
- `schemas/examples/README.md`
- `scripts/governance/gate-runner-common.ps1`
- `scripts/governance/fast-check.ps1`
- `scripts/governance/full-check.ps1`

## Changes
1. 项目级规则增强（不改硬门禁语义）
- 在 `AGENTS.md` 增加 `F. 跨仓迁移最小模板（可选增强）`：
  - 明确 `repo-profile` 字段草案入口。
  - 明确 `fast/full` 脚本骨架入口及 fallback 行为。
  - 明确该增强不改变 canonical gate 顺序。

2. 新增可落地 `repo-profile` 字段草案样例
- 新增 `schemas/examples/repo-profile/target-repo-fast-full-template.example.json`。
- 样例覆盖：
  - 必填基础字段（repo identity、risk/approval、path policy、branch policy、delivery format）。
  - `quick_gate_commands` 与 `full_gate_commands`。
  - 兼容信号与交付交接模板。

3. 新增 fast/full 门禁脚本骨架
- 新增 `scripts/governance/gate-runner-common.ps1`：
  - 统一加载 `repo-profile`、解析 gate 命令、顺序执行、失败短路、JSON/文本输出。
  - `fast` 优先 `quick_gate_commands`，缺失时回退 `test + contract(or invariant)`。
  - `full` 优先 `full_gate_commands`，缺失时回退 `build + test + contract(or invariant)`。
- 新增 `scripts/governance/fast-check.ps1` 与 `scripts/governance/full-check.ps1` 作为薄封装入口。

4. 示例索引同步
- `schemas/examples/README.md` 增加新样例引用与验证命令。

## Verification
### Gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- result: all pass

### Supporting checks
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
- result: pass (`OK powershell-parse`, `OK issue-seeding-render`)

2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- result: pass (`OK active-markdown-links`, `OK claim-drift-sentinel`, `OK post-closeout-queue-sync`)

3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/governance/fast-check.ps1 -RepoProfilePath schemas/examples/repo-profile/governed-ai-coding-runtime.example.json -WorkingDirectory . -Json`
- result: pass (`exit_code=0`)

4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/governance/full-check.ps1 -RepoProfilePath schemas/examples/repo-profile/governed-ai-coding-runtime.example.json -WorkingDirectory . -Json`
- result: pass (`exit_code=0`, gate_order=`build,test,contract,hotspot`)

## Risks
- `scripts/governance/*` 当前作为“骨架入口”，尚未内置跨平台 shell 适配策略（默认通过 `pwsh -Command` 执行 profile command）。
- `target-repo-fast-full-template` 为迁移模板，不应直接作为生产仓最终 profile；必须按目标仓真实命令替换。

## Rollback
Revert:
- `AGENTS.md`
- `schemas/examples/README.md`
- `schemas/examples/repo-profile/target-repo-fast-full-template.example.json`
- `scripts/governance/gate-runner-common.ps1`
- `scripts/governance/fast-check.ps1`
- `scripts/governance/full-check.ps1`
- `docs/change-evidence/20260422-repo-profile-fast-full-gate-skeleton.md`
