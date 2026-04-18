# 多仓试运行快速开始

## Purpose
在不修改 kernel code 的前提下，运行当前基于 repo-profile 的 multi-repo onboarding trial。

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

## 预期输出
每个 repo 都会包含：
- `attachment_posture`
- `adapter_tier`
- `verification_refs`
- `evidence_refs`
- `handoff_refs`
- `follow_ups`

## 当前边界
- 这个 runner 以 repo-profile 为输入
- 它不会直接 attach 外部仓，也不会修改 target repo
- 它提供后续真实 attached-repo trial 所需的 onboarding evidence shape

## 相关文档
- [Multi-Repo Trial Loop](../product/multi-repo-trial-loop.md)
- [Single-Machine Runtime Quickstart](./single-machine-runtime-quickstart.zh-CN.md)
- [在现有仓库中使用](./use-with-existing-repo.zh-CN.md)
- [English Version](./multi-repo-trial-quickstart.md)
