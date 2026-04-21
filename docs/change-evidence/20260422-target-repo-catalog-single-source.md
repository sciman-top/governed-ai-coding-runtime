# 20260422 目标仓清单单一真源落地

## Goal
把“目标仓清单”从分散维护改为单一真源，并让 preset 执行入口直接读取该清单，避免脚本内硬编码 target 列表漂移。

## Scope
- `docs/targets/target-repos-catalog.json`
- `scripts/runtime-flow-preset.ps1`
- `docs/quickstart/use-with-existing-repo.md`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`

## Changes
1. 新增目标仓清单单一真源：
- `docs/targets/target-repos-catalog.json`
- 当前纳入目标：
  - `classroomtoolkit`
  - `self-runtime`
  - `skills-manager`

2. `runtime-flow-preset.ps1` 从清单动态加载：
- 移除参数层 `ValidateSet` 硬编码 target 列表。
- 新增 `-ListTargets`，可直接输出当前可用 target。
- 新增模板变量替换能力：
  - `${repo_root}`
  - `${code_root}`
  - `${runtime_state_base}`
- 对未知 target 返回“可用 target 列表”。

3. quickstart 文档补齐清单入口（中英双语）：
- `docs/quickstart/use-with-existing-repo.md`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`

## Verification
### Targeted
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -ListTargets`
- result:
  - `catalog=...docs/targets/target-repos-catalog.json`
  - `classroomtoolkit`, `self-runtime`, `skills-manager`

2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -ListTargets -Json`
- result:
  - `catalog_path` 指向 `docs/targets/target-repos-catalog.json`
  - `targets` 为 3 个目标仓数组

### Gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

### Supporting checks
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`

## Risks
- 目标仓新增/下线现在依赖 `docs/targets/target-repos-catalog.json` 维护流程；若人工漏改该文件，preset 不会自动发现新仓。
- 当前 catalog 只覆盖 preset 目标；历史运行证据目录仍可能保留旧 run 文件，不代表当前 active target 集合。

## Rollback
Revert:
- `docs/targets/target-repos-catalog.json`
- `scripts/runtime-flow-preset.ps1`
- `docs/quickstart/use-with-existing-repo.md`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`
- `docs/change-evidence/20260422-target-repo-catalog-single-source.md`
