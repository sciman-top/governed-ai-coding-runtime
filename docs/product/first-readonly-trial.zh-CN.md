# 首个只读试运行

## Purpose
通过脚本化入口运行第一版 governed read-only trial。

这条流程与 Codex CLI/App 兼容，因为它保留上游认证归属，并把 Codex 建模为 adapter capability declaration。

当前默认声明已切到 `native_attach` 优先（`probe_source=declared_defaults`），并保留 runtime 自动回退语义。
也可以通过 `--probe-live` 使用真实命令面探测。

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
  --max-minutes 5 `
  --probe-live
```

## 输出
命令会打印 JSON 摘要：

```json
{
  "accepted_count": 1,
  "adapter_tier": "native_attach",
  "auth_ownership": "user_owned_upstream_auth",
  "invocation_mode": "live_attach",
  "probe_source": "declared_defaults",
  "repo_id": "python-service-sample",
  "summary": "read-only trial accepted 1 tool request",
  "unsupported_capabilities": [],
  "unsupported_capability_behavior": "none"
}
```

## 边界
- runtime 会附加 repo profile 和 budgets
- runtime 会校验受限的 read-only 请求
- Codex 认证仍由上游 Codex CLI/App 工作流持有
- 不支持能力仍会被显式记录，必要时会降级到 `process_bridge` 或 `manual_handoff`
- 这个命令不会执行 Codex、不会启动 shell tools、不会修改文件、不会分配 isolated workspaces

## Related
- [English Version](./first-readonly-trial.md)
