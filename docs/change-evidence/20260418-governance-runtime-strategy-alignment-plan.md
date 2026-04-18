# 20260418 Governance Runtime Strategy Alignment Plan Evidence

## Change Basis

- Request: consolidate the discussion about final product shape, external references, repo-native contract bundles, and whether current `docs/`, `schemas/`, and `packages/contracts/` should be changed.
- Current landing point: planning only.
- Target destination: a bounded strategy-alignment plan that can guide later edits without replacing the active `GAP-035` through `GAP-039` interactive-session productization queue.

## Files Changed

- Added `docs/plans/governance-runtime-strategy-alignment-plan.md`
- Updated `docs/plans/README.md`

## Decision Summary

- Keep `docs/`, `schemas/`, and `packages/contracts/` as the repository source-of-truth structure.
- Treat future repo-local light packs or `.governed-ai/`-style directories as runtime-consumable attachment surfaces, not immediate replacements for current authoring directories.
- Use external products as mechanism references through a borrowing matrix:
  - governance control plane
  - policy engine
  - identity and scope
  - gateway
  - adapter protocol
  - execution host
  - wrapper/orchestration
  - generation guardrail
- Preserve the active interactive-session productization plan as the current execution plan.

## Commands

Executed from repository root on 2026-04-18:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

- Exit code: `0`
- Key output: `OK python-bytecode`, `OK python-import`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

- Exit code: `0`
- Key output: `OK runtime-unittest`, `Ran 116 tests`, `OK`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

- Exit code: `0`
- Key output: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

- Exit code: `0`
- Key output: `OK runtime-policy-compatibility`, `OK runtime-policy-maintenance`, `OK runtime-status-surface`, `OK adapter-posture-visible`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

- Exit code: `0`
- Key output: `OK runtime-build`, `OK runtime-unittest`, `OK schema-catalog-pairing`, `OK runtime-doctor`, `OK active-markdown-links`, `OK issue-seeding-render`, `Ran 116 tests`, `OK`

## Risks

- The strategy plan is not implementation. Later tasks must still create the borrowing matrix, ADR, architecture document, PolicyDecision contract, and backlog updates.
- External product references can become stale. Later execution must verify official sources again before writing detailed claims.
- If the plan is treated as replacing `GAP-035` through `GAP-039`, execution order may drift. The plan explicitly keeps it as a strategy-alignment track.

## Rollback

- Remove `docs/plans/governance-runtime-strategy-alignment-plan.md`.
- Revert the added entry in `docs/plans/README.md`.
