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
- portable release zip 可以通过 `release.ps1` 一键生成，并在新机器用 `install.ps1 -Mode Portable` 初始化
- release version 在生成 archive 路径前必须通过文件名安全校验
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
.\release.ps1 -Version 0.1.0 -Channel portable
```

```powershell
.\install.ps1 -Mode Portable -DryRun
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

## Exit Rule
只有当所有 required commands 成功，且文档、artifacts、packaging output、compatibility posture 彼此一致时，`Public Usable Release / GAP-029` 到 `GAP-032` 才算完成。

## Boundary Note
`scripts/run-governed-task.py` 证明的是本地 governed runtime path，不应被解读为已经通过 managed runtime adapter 直接调用 Codex CLI/App。

portable release 只携带通用源文件、契约、规则、脚本、schema、docs、tests 和 hooks；不携带 `.runtime` 运行态、历史 evidence、凭据、provider 设置或目标仓工作树。新机器上的目标仓与全局规则必须重新 attach/sync。

## Related
- [English Version](./public-usable-release-criteria.md)
