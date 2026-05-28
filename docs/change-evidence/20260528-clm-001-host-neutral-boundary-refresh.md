# 2026-05-28 CLM-001 Host-Neutral Boundary Refresh

## Goal
- Refresh `CLM-001` evidence without changing the claim text or expanding project scope.
- Keep the claim catalog current for the statement: "The runtime is a governance/runtime layer and not a universal host replacement."

## Root Cause And Changes
- `scripts/verify-repo.ps1 -Check Docs` failed because `CLM-001` still referenced `docs/change-evidence/20260420-gap-069-host-neutral-governance-boundary-hardening-closeout.md`, which is older than the 30-day claim evidence freshness window.
- The source claim remains valid: `README.en.md` still says the runtime does not fully replace Codex host execution in every environment, and `README.zh-CN.md` keeps the matching Chinese warning.
- Updated `docs/product/claim-catalog.json` so `CLM-001.evidence_link` points to this fresh evidence file.

## Verification
- Source text remains present in `README.en.md`: `not that this runtime fully replaces Codex host execution in every environment`.
- Source text remains present in `README.zh-CN.md`: `不应声称本项目已经在所有环境下完全接管 Codex 宿主执行`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` is the proof command for the refreshed claim catalog entry.

## Rollback
- Restore `CLM-001.evidence_link` in `docs/product/claim-catalog.json` to the previous evidence file if this refresh is invalid.
- Remove `docs/change-evidence/20260528-clm-001-host-neutral-boundary-refresh.md`.
