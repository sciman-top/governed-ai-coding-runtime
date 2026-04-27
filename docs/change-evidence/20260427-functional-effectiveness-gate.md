# 2026-04-27 Functional Effectiveness Gate

## Goal
- Make autonomous functional/effect verification mandatory instead of relying on manual reading of evidence notes.
- Fail closed when recent functional verification evidence is missing, stale, or lacks proof for runtime execution, target batch gates, attached write closure, packaging, operator UI, hooks, and governance fast-check surfaces.

## Changes
- Added `scripts/verify-functional-effectiveness.py`.
- Added `tests/runtime/test_functional_effectiveness.py`.
- Wired `Invoke-FunctionalEffectivenessChecks` into `scripts/verify-repo.ps1 -Check Contract`, so `Contract` and `All` now enforce this evidence gate.

## Verification
- `python scripts/verify-functional-effectiveness.py --as-of 2026-04-27` -> pass; selected `docs/change-evidence/20260427-autonomous-functional-verification.md`, `evidence_age_days=0`, all proof checks passed.
- `python -m unittest tests.runtime.test_functional_effectiveness -v` -> pass; 4 tests.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` -> pass; includes `OK functional-effectiveness`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Build` -> pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> pass; 450 runtime tests, 5 skipped, 12 service tests.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Doctor` -> pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` -> pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts` -> pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` -> pass; includes build, runtime, contract, doctor, docs, scripts, and `OK functional-effectiveness`.

## Rollback
- Code rollback:
  - `git restore -- scripts/verify-repo.ps1 scripts/verify-functional-effectiveness.py tests/runtime/test_functional_effectiveness.py docs/change-evidence/20260427-functional-effectiveness-gate.md`
