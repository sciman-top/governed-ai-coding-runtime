# Infra

Infrastructure definitions and deployment notes will live here.

## Current Status
- The current infra baseline is still repo-local and verification-first.
- `.github/workflows/verify.yml` and the PowerShell gate scripts provide the active automation surface today.
- Deployment targets, containers, databases, and orchestration remain deferred until later stages.

## Boundaries
- CI and local verification wiring are in scope.
- Runtime deployment, databases, containers, and orchestration are out of scope until the first governed loop exists.
