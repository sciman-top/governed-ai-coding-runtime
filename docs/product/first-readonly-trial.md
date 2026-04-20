# First Read-Only Trial

## Purpose
Run the first governed read-only trial through a scripted entrypoint.

This flow is Codex CLI/App compatible because it preserves upstream authentication ownership and models Codex as an adapter capability declaration.

The default declaration is now `native_attach` preferred (`probe_source=declared_defaults`) and still allows runtime fallback semantics.
You can also request a real surface probe with `--probe-live`.

## Command
Run from the repository root:

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

## Output
The command prints a JSON summary:

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

## Boundaries
- The runtime attaches repo profile and budgets.
- The runtime validates the bounded read-only request.
- Codex authentication remains owned by the upstream Codex CLI/App workflow.
- Unsupported capabilities are still explicitly surfaced and can degrade to `process_bridge` or `manual_handoff` when probe posture requires.
- This command does not execute Codex, spawn shell tools, mutate files, or allocate isolated workspaces.
