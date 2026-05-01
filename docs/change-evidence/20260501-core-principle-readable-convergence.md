# 2026-05-01 Core Principle Readable Convergence Evidence

## Goal
Converge the human-readable core-principle wording after the best-practice review without adding another top-level principle set or weakening the active machine policy.

## Changes
- Updated `docs/README.md` to expose the concise summary `Automation-first, gate-controlled, evidence-measured governance`.
- Made the conflict rule explicit: efficiency does not override safety, permissions or least privilege, evidence, rollback, or review boundaries for effective changes.
- Added comparable evidence field guidance so effect feedback remains measurable across future target-run evidence.
- Updated `docs/specs/core-principles-spec.md` with the same conflict and comparable-evidence invariants.
- Extended `docs/architecture/core-principles-policy.json` doc references so `verify-core-principles.py` checks the new human-readable wording.

## Risk
Risk level: low.

This is documentation and policy-reference convergence only. It does not add or remove required principles, change outer-AI allowed actions, enable automatic policy mutation, enable skills, sync target repositories, push, merge, or delete reviewed evidence.

## Commands
Pending verification:

```powershell
python scripts/verify-core-principles.py
python -m unittest tests.runtime.test_core_principles
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
```

## Rollback
Revert this evidence file plus the matching `docs/README.md`, `docs/specs/core-principles-spec.md`, and `docs/architecture/core-principles-policy.json` edits.
