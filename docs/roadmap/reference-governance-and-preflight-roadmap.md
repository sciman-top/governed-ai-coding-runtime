# Reference Governance And Release Preflight Roadmap

## Status
- `GAP-169..172` are complete as an owner-directed bounded governance hardening queue on `2026-06-09`; see `docs/change-evidence/20260609-reference-basis-and-preflight-hardening.md`
- This queue does **not** replace the current active queue in `docs/architecture/planning-status.json`. It is a bounded follow-on slice that hardens reference discipline and release-preflight truth without reopening host-family promotion or LTP selection.

## Goal
Turn the local external reference shelf into a machine-checkable `reference-basis`, then upgrade self-repo closeout from raw hard gates into a formal `preflight` path backed by CI.

## Why This Slice Exists
- The repository already had:
  - a strong external reference shelf
  - a narrow `reference-required` Contract guard
  - a local `verify-repo.ps1` hard-gate chain
  - a minimal CI workflow
- It still lacked three things:
  1. a repo-owned matrix that says which sections must consult which local references
  2. a fail-closed guard that checks named local reference ids instead of only broad source categories
  3. a release-style `preflight` entrypoint that can be used locally and mirrored in CI

## Principles
1. Reference mapping before borrowing.
2. Same-diff evidence before guarded source claims.
3. `preflight` wraps the existing hard-gate chain; it does not replace `verify-repo.ps1`.
4. Local and CI must read the same repo-owned contracts even when CI cannot see the maintainer's full `D:\CODE\external` shelf.

## Dependency Line
`GAP-168 -> GAP-169 -> GAP-170 -> GAP-171 -> GAP-172`

## Milestone Overview
| milestone | closes | outcome |
| --- | --- | --- |
| `RBP-0` | local reference ambiguity | repo-owned `reference-basis` matrix and catalog exist |
| `RBP-1` | must-read drift | guarded surfaces fail closed without same-diff `reference-basis` evidence |
| `RBP-2` | local release-check ambiguity | self-repo gets a formal `preflight` entrypoint over existing gates |
| `RBP-3` | local-only gate posture | CI runs the same release-style preflight path as a second layer |

## Queue

### GAP-169 Reference Basis Matrix And Retention Rule
- freeze a repo-owned answer for `keep / add later / no immediate delete`
- map code and doc surfaces to named local reference ids
- keep the current external shelf authoritative for clone storage, but make the repo own a checked-in catalog snapshot

### GAP-170 Reference Basis Guard And Same-Diff Evidence Contract
- add a machine-readable `reference-basis` policy
- add a verifier that inspects changed paths and requires named local references in same-diff evidence
- keep the existing `reference-required` guard as the broader high-drift source-category rule

### GAP-171 Release Preflight Entrypoint And Hotspot Coverage
- make full repo-profile gate order include `doctor`
- add a formal `scripts/governance/preflight.ps1`
- close with `build -> test -> contract/invariant -> hotspot` plus docs/scripts and `git diff --check`

### GAP-172 Local Plus CI Preflight Alignment Closeout
- wire CI to run the same `preflight` path
- keep the existing `verify-repo -Check All` integrity job
- close with backlog/seed/plan/evidence/render alignment
