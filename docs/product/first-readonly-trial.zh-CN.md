# 首个只读试运行

## Purpose
通过脚本化入口运行第一版 governed read-only trial。

这条流程与 Codex CLI/App 兼容，因为它保留上游认证归属，并把 Codex 建模为 adapter capability declaration。当前还不会直接调用 Codex。

## 命令
从仓库根目录运行：

```powershell
python scripts/run-readonly-trial.py `
  --goal "inspect repository" `
  --scope "readonly trial" `
  --acceptance "readonly request accepted" `
  --repo-profile "schemas/examples/repo-profile/python-service.example.json" `
  --target-path "src/service.py" `
  --max-steps 1 `
  --max-minutes 5
```

## 输出
命令会打印 JSON 摘要：

```json
{
  "accepted_count": 1,
  "auth_ownership": "user_owned_upstream_auth",
  "repo_id": "python-service-sample",
  "summary": "read-only trial accepted 1 tool request",
  "unsupported_capability_behavior": "degrade_to_manual_handoff"
}
```

## 边界
- runtime 会附加 repo profile 和 budgets
- runtime 会校验受限的 read-only 请求
- Codex 认证仍由上游 Codex CLI/App 工作流持有
- 不支持的能力会降级到 manual handoff
- 这个命令不会执行 Codex、不会启动 shell tools、不会修改文件、不会分配 isolated workspaces

## Related
- [English Version](./first-readonly-trial.md)
