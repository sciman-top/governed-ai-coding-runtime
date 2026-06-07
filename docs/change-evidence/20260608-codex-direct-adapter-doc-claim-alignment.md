# 20260608 Codex Direct Adapter Claim Alignment

## Goal
- Align the public `Codex Direct Adapter` documentation with the current runtime probe behavior and current host-claim boundary.
- Remove the stale wording that implied `resume/help` surface alone could upgrade Codex to `native_attach`.

## Root Cause
- `docs/product/adapter-degrade-policy.md` and the live runtime probe already enforced a stricter rule: when `codex status` is absent, `resume/help` remains supporting evidence only.
- `docs/product/codex-direct-adapter.md` and `docs/product/codex-direct-adapter.zh-CN.md` still contained older wording that said native attach could be inferred from the resume surface.
- That wording drift could mislead future host-capability investigation and overstate current Codex posture.

## Changes
- Updated `[codex-direct-adapter.md](D:/CODE/governed-ai-coding-runtime/docs/product/codex-direct-adapter.md)` to state that missing `status` keeps `resume` as supporting evidence only.
- Updated `[codex-direct-adapter.zh-CN.md](D:/CODE/governed-ai-coding-runtime/docs/product/codex-direct-adapter.zh-CN.md)` to state that `resume/help surface` alone cannot promote Codex to `native_attach`.
- Added a regression test in `[test_codex_adapter.py](D:/CODE/governed-ai-coding-runtime/tests/runtime/test_codex_adapter.py)` so future edits cannot reintroduce the stale claim silently.

## Verification
- `python -m unittest tests.runtime.test_codex_adapter.CodexAdapterTests.test_codex_direct_adapter_docs_keep_resume_surface_as_supporting_evidence_only`
  - result: `OK`
- `python -m unittest tests.runtime.test_codex_adapter`
  - result: `Ran 23 tests`
  - result: `OK`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - result: `OK host-capability-claim-upgrade-policy`
  - result: `OK claim-evidence-freshness`
  - result: docs gate passed

## Risks
- This change does not claim Codex target-run recovery.
- This change does not modify `codex_adapter.py` behavior or any target-run evidence.
- A future runtime change may still choose to recognize a different Codex continuity surface, but that must arrive with fresh host evidence and matching contract updates.

## Rollback
- Revert the two product docs, the regression test, and this evidence file.
- Re-run the verification commands above.
