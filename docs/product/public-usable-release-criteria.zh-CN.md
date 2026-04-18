# Public Usable Release Criteria

## Goal
定义“本地 governed runtime 在一台机器上可公开使用”的最低标准。

## Required Capabilities
- 新用户可以通过 `scripts/bootstrap-runtime.ps1` 完成 bootstrap
- 可以通过 `scripts/run-governed-task.py` 创建并运行 governed task
- `build -> test -> contract/invariant -> hotspot` 可以按文档命令在本地执行
- runtime artifacts、evidence、verification、handoff 输出可以从本地路径检查
- 更丰富的本地 operator surface 可以通过 `scripts/serve-operator-ui.py` 生成
- package bundle 可以通过 `scripts/package-runtime.ps1` 组装
- 至少一个 sample repo profile 可以跑通文档化 runtime path

## Required Commands

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1
```

```powershell
python scripts/run-governed-task.py run --json
```

```powershell
python scripts/serve-operator-ui.py
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/package-runtime.ps1
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

## Exit Rule
只有当所有 required commands 成功，且文档、artifacts、packaging output、compatibility posture 彼此一致时，`Public Usable Release / GAP-029` 到 `GAP-032` 才算完成。

## Boundary Note
`scripts/run-governed-task.py` 证明的是本地 governed runtime path，不应被解读为已经通过 managed runtime adapter 直接调用 Codex CLI/App。

## Related
- [English Version](./public-usable-release-criteria.md)
