# 多仓试运行快速开始

## Purpose
在不修改 kernel code 的前提下，运行 multi-repo onboarding trial（支持 repo-profile 输入和 attached-repo 输入）。

## 默认示例运行
从仓库根目录运行：

```powershell
python scripts/run-multi-repo-trial.py
```

默认使用：
- `schemas/examples/repo-profile/python-service.example.json`
- `schemas/examples/repo-profile/typescript-webapp.example.json`

## 自定义 profile
可以重复传入 `--repo-profile`：

```powershell
python scripts/run-multi-repo-trial.py `
  --repo-profile "schemas/examples/repo-profile/python-service.example.json" `
  --repo-profile "schemas/examples/repo-profile/typescript-webapp.example.json"
```

## Attached Repo 运行
可以通过重复 `--attachment-root` 直接对已 attach 的仓库执行试运行：

```powershell
python scripts/run-multi-repo-trial.py `
  --attachment-root "D:/repos/service-a" `
  --attachment-runtime-state-root "D:/runtime-state/service-a" `
  --attachment-root "D:/repos/service-b" `
  --attachment-runtime-state-root "D:/runtime-state/service-b"
```

可选写入探针（仅治理探测）：

```powershell
python scripts/run-multi-repo-trial.py `
  --attachment-root "D:/repos/service-a" `
  --attachment-runtime-state-root "D:/runtime-state/service-a" `
  --execute-write-probe
```

## 预期输出
每个 repo 都会包含：
- `attachment_posture`
- `adapter_tier`
- `verification_refs`
- `evidence_refs`
- `handoff_refs`
- `follow_ups`

## 当前边界
- 保留基于 repo-profile 的汇总模式
- attached-repo 模式会执行 doctor/posture 与 quick verification 循环
- write probe 为可选项，用于在真实高风险写入前记录治理摩擦

## 相关文档
- [Multi-Repo Trial Loop](../product/multi-repo-trial-loop.md)
- [Single-Machine Runtime Quickstart](./single-machine-runtime-quickstart.zh-CN.md)
- [在现有仓库中使用](./use-with-existing-repo.zh-CN.md)
- [English Version](./multi-repo-trial-quickstart.md)
