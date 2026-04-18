# Multi-Repo Trial Quickstart

## Purpose
Run the current profile-based multi-repo onboarding trial without changing kernel code.

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

## Expected Output
JSON output includes, per repo:
- `attachment_posture`
- `adapter_tier`
- `verification_refs`
- `evidence_refs`
- `handoff_refs`
- `follow_ups`

## Current Boundary
- this runner works from repo-profile inputs
- it does not attach external repositories or mutate target repos
- it provides the onboarding evidence shape needed for later real attached-repo trials

## Related
- [Multi-Repo Trial Loop](../product/multi-repo-trial-loop.md)
- [Single-Machine Runtime Quickstart](./single-machine-runtime-quickstart.md)
- [Use With An Existing Repo](./use-with-existing-repo.md)
