# Infra

Local runtime scaffolding and deployment helpers live here.

## Current Surface
- `local-runtime/docker-compose.yml`
  - starts `postgres` plus the checked-in `control-plane`, `workflow-worker`, `agent-worker`, and `tool-runner` app scaffolds from this repo checkout
- `local-runtime/postgres/init.sql`
  - seeds the local `governed_runtime` database used by the compose scaffold

## Current Status
- Infra is no longer purely aspirational: a local compose scaffold exists for service-shape inspection and boundary testing.
- The canonical operator path is still repo-first verification and packaging (`run.ps1`, `scripts/verify-repo.ps1`, `scripts/governance/preflight.ps1`, `scripts/package-runtime.ps1`), not container-first day-to-day operation.
- Remote deployment, managed secrets, multi-machine orchestration, and production SRE posture remain follow-on work.

## Boundaries
- `infra/local-runtime/` is for local service-shape experiments and release-surface inspection.
- It does not replace the repo-owned gate chain or authorize stronger production-host claims.
- Treat database and container state as local scaffolding, not as the source of planning truth.

## Verification
```powershell
docker compose -f infra/local-runtime/docker-compose.yml config
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/governance/preflight.ps1 -DisableAutoCommit
```
