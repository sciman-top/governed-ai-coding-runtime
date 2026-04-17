# First Read-Only Trial

## Purpose
Run the first governed read-only trial through a scripted entrypoint.

This flow is Codex CLI/App compatible because it preserves upstream authentication ownership and models Codex as an adapter capability declaration. It does not invoke Codex directly yet.

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
  --max-minutes 5
```

## Output
The command prints a JSON summary:

```json
{
  "accepted_count": 1,
  "auth_ownership": "user_owned_upstream_auth",
  "repo_id": "python-service-sample",
  "summary": "read-only trial accepted 1 tool request",
  "unsupported_capability_behavior": "degrade_to_manual_handoff"
}
```

## Boundaries
- The runtime attaches repo profile and budgets.
- The runtime validates the bounded read-only request.
- Codex authentication remains owned by the upstream Codex CLI/App workflow.
- Unsupported capabilities degrade to manual handoff for this first slice.
- This command does not execute Codex, spawn shell tools, mutate files, or allocate isolated workspaces.
