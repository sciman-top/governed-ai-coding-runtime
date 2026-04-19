# Multi-Repo Trial Quickstart

## Purpose
Run multi-repo onboarding trials using either profile inputs or attached repositories without changing kernel code.

## Default Sample Run
From the repository root:

```powershell
python scripts/run-multi-repo-trial.py
```

By default the runner uses:
- `schemas/examples/repo-profile/python-service.example.json`
- `schemas/examples/repo-profile/typescript-webapp.example.json`

## Custom Profiles
You can add more profiles with repeated `--repo-profile` flags:

```powershell
python scripts/run-multi-repo-trial.py `
  --repo-profile "schemas/examples/repo-profile/python-service.example.json" `
  --repo-profile "schemas/examples/repo-profile/typescript-webapp.example.json"
```

## Attached Repositories
You can run the trial directly on attached repos with repeated `--attachment-root`:

```powershell
python scripts/run-multi-repo-trial.py `
  --attachment-root "D:/repos/service-a" `
  --attachment-runtime-state-root "D:/runtime-state/service-a" `
  --attachment-root "D:/repos/service-b" `
  --attachment-runtime-state-root "D:/runtime-state/service-b"
```

Optional write-governance probe:

```powershell
python scripts/run-multi-repo-trial.py `
  --attachment-root "D:/repos/service-a" `
  --attachment-runtime-state-root "D:/runtime-state/service-a" `
  --execute-write-probe
```

## Expected Output
JSON output includes, per repo:
- `attachment_posture`
- `adapter_tier`
- `verification_refs`
- `evidence_refs`
- `handoff_refs`
- `follow_ups`

## Current Boundary
- profile-based summary mode remains available
- attached-repo mode executes doctor/posture and quick verification loops
- write probe is optional and records governance friction before any real high-risk write

## Related
- [Multi-Repo Trial Loop](../product/multi-repo-trial-loop.md)
- [Single-Machine Runtime Quickstart](./single-machine-runtime-quickstart.md)
- [Use With An Existing Repo](./use-with-existing-repo.md)
