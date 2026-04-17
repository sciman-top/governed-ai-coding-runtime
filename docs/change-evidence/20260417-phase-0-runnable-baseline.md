# 20260417 Phase 0 Runnable Baseline

## Goal
Execute the Phase 0 runnable baseline plan on top of the current docs-first, contracts-first repository.

## Current Landing
- Plan source: `docs/plans/phase-0-runnable-baseline-implementation-plan.md`
- Evidence destination: `docs/change-evidence/20260417-phase-0-runnable-baseline.md`
- Rollback path: git history or current diff; optional snapshots remain under `docs/change-evidence/snapshots/`

## Task 0 Baseline Decision
- Decision: explicitly carry forward the current dirty worktree
- Reason: the existing uncommitted diff is a known planning and index hardening baseline, not runtime code drift
- Scope observed:
  - `AGENTS.md`
  - `README.md`
  - `docs/README.md`
  - `docs/plans/phase-0-runnable-baseline-implementation-plan.md`
  - deletion of one historical duplicate file outside the active docs index

## Commands
```powershell
git status --short
git diff --stat
Get-ChildItem schemas/jsonschema/*.json |
  ForEach-Object { Get-Content -Raw $_.FullName | ConvertFrom-Json > $null }

$tokens = $null
$errors = $null
[void][System.Management.Automation.Language.Parser]::ParseFile(
  (Resolve-Path 'scripts/github/create-roadmap-issues.ps1'),
  [ref]$tokens,
  [ref]$errors
)
if ($errors.Count -gt 0) { $errors | Format-List *; exit 1 }
```

## Evidence
- `git status --short` showed only planning/doc changes plus one deleted historical duplicate file.
- `git diff --stat` reported docs-heavy churn and no runtime source tree changes.
- schema parse baseline passed.
- `scripts/github/create-roadmap-issues.ps1` PowerShell parse baseline passed.

## Phase 0 Progress
- [x] Task 0: baseline freeze or explicit carry-forward
- [x] Task 1: repository skeleton directories created
- [x] Task 2: local verifier added
- [x] Task 3: CI verifier added
- [x] Task 4: runtime-consumable control-pack reference asset added
- [x] Task 5: repo admission minimums spec added
- [x] Task 6: project gates routed through the verifier
- [ ] Task 7: final verification and handoff (verification passed; clean-worktree handoff still pending)

## Phase 0 Assets
- `apps/README.md`
- `packages/README.md`
- `infra/README.md`
- `tests/README.md`
- `scripts/verify-repo.ps1`
- `.github/workflows/verify.yml`
- `schemas/control-packs/README.md`
- `schemas/control-packs/minimum-governance-kernel.control-pack.json`
- `docs/specs/repo-admission-minimums-spec.md`

## Verification Results
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` -> pass

## Gate Status
| gate | status | command | result | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|---|---|
| build | `gate_na` | `n/a` | not run | runtime services and build entrypoints still do not exist | repository skeleton plus verifier/CI baseline | `docs/change-evidence/20260417-phase-0-runnable-baseline.md` | `2026-05-31` |
| test | `gate_na` | `n/a` | not run | no runtime test harness exists yet | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts` and `-Check Docs` | `docs/change-evidence/20260417-phase-0-runnable-baseline.md` | `2026-05-31` |
| contract/invariant | `active` | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | pass | schema, examples, catalog, and paired specs are the active contract baseline | full repository verification also passed | `docs/change-evidence/20260417-phase-0-runnable-baseline.md` | `n/a` |
| hotspot | `gate_na` | `n/a` | not run | no runtime doctor or health entrypoint exists yet | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` | `docs/change-evidence/20260417-phase-0-runnable-baseline.md` | `2026-05-31` |

## Working Tree Status
- `git status --short` remains non-empty.
- This is expected at this stage because the repository started from an explicitly carried-forward dirty worktree and this session added additional Phase 0 files without creating a scoped commit.
- Phase 0 implementation artifacts are present and verified locally, but the handoff is not a clean-commit baseline yet.

## Residual Risks
- Runtime task execution is still absent.
- Repo admission is now specified and schema-paired, but not enforced by runtime code.
- Build/test gates remain `gate_na` until the first runtime package exists.
- CI validates repository integrity, not governed task behavior.
- The working tree still contains pre-existing and current uncommitted changes, so rollback should be reviewed file-by-file.

## Rollback
- Revert uncommitted changes with targeted git restore/reset only when explicitly desired.
- Prefer reverting Phase 0 increments by file-level git diff review because the worktree already carried unrelated planning edits.
