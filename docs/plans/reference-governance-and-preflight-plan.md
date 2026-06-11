# Reference Governance And Release Preflight Plan

## Status
- `GAP-169..172` are complete as an owner-directed bounded queue on `2026-06-09`; see `docs/change-evidence/20260609-reference-basis-and-preflight-hardening.md`
- `docs/architecture/planning-status.json` remains the single source of current active queue and current decision gate. This plan is a completed hardening slice, not a promotion of the active queue.

## Goal
Make `which references must be consulted` and `what release-style closeout means` executable inside the repository instead of leaving them as chat-only expectations.

## Fixed Boundaries
- Keep the current active queue and current decision gate authoritative through `planning-status.json`.
- Do not change host-family promotion posture or LTP selection as part of this slice.
- Reuse existing `verify-repo.ps1`, `gate-runner-common.ps1`, and CI entrypoints instead of introducing a parallel verifier stack.
- Canonical verification order remains `build -> test -> contract/invariant -> hotspot`.

## Task List

### Task 1: Freeze A Repo-Owned Reference Basis
**Maps to:** `GAP-169`

**Description:** Capture a checked-in `reference-basis` catalog and matrix so the repo no longer depends on conversation memory to answer which local references matter for which surfaces.

**Acceptance criteria:**
- [x] The repo carries a machine-readable catalog of the local external reference shelf entries it depends on most.
- [x] The repo carries a human-readable matrix from surface to required local references.
- [x] The keep/add/remove answer is explicit and does not recommend immediate deletion.

**Verification:**
- [x] `python -m unittest tests.runtime.test_reference_basis -v`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`

### Task 2: Add A Fail-Closed Reference Basis Guard
**Maps to:** `GAP-170`

**Description:** Add a verifier that looks at the current diff, finds guarded surfaces, and requires same-diff evidence naming the local reference ids that were actually reviewed.

**Acceptance criteria:**
- [x] Guarded surfaces fail if no same-diff `reference_basis_review` evidence exists.
- [x] Evidence must mention guarded paths, matched surface ids, and required local reference ids.
- [x] The guard is wired into the self-repo `Contract` gate.

**Verification:**
- [x] `python -m unittest tests.runtime.test_reference_basis -v`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`

### Task 3: Promote Full Gate Into Formal Preflight
**Maps to:** `GAP-171`

**Description:** Keep the generic `full-check` entrypoint, but add a repo-specific `preflight` wrapper that composes the full repo-profile gate, docs/scripts verification, and `git diff --check`.

**Acceptance criteria:**
- [x] Full repo-profile gate order explicitly includes `doctor`.
- [x] `scripts/governance/preflight.ps1` exists and runs release-ready checks after the full gate.
- [x] The extra release checks are explicit rather than hidden inside chat instructions.

**Verification:**
- [x] `python -m unittest tests.runtime.test_preflight_ci_wiring -v`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/governance/preflight.ps1 -DisableAutoCommit`

### Task 4: Close Local Plus CI Alignment
**Maps to:** `GAP-172`

**Description:** Wire CI to run the same formal `preflight` path while preserving the broader repository-integrity job.

**Acceptance criteria:**
- [x] `verify.yml` still runs `verify-repo.ps1 -Check All`.
- [x] `verify.yml` also runs `scripts/governance/preflight.ps1`.
- [x] Backlog, issue seeds, roadmap, plan, and evidence are aligned for the new queue.

**Verification:**
- [x] `python -m unittest tests.runtime.test_preflight_ci_wiring -v`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`

## Immediate Rule
Use this plan as a completed hardening record and future rollback map. It does not, by itself, change the current active queue or authorize broader host-family promotion work.
