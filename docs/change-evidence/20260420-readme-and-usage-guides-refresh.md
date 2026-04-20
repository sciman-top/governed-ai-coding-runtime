# 20260420 README And Usage Guides Refresh

## Goal
Refresh operator-facing docs so users can quickly answer:
- how to use this project in daily AI coding workflows
- what concrete assistance the runtime provides

## Scope
- Added bilingual AI coding usage guides:
  - `docs/quickstart/ai-coding-usage-guide.md`
  - `docs/quickstart/ai-coding-usage-guide.zh-CN.md`
- Updated entry and navigation docs:
  - `README.md`
  - `README.en.md`
  - `README.zh-CN.md`
  - `docs/README.md`
  - `docs/quickstart/use-with-existing-repo.md`
  - `docs/quickstart/use-with-existing-repo.zh-CN.md`

## What Changed
1. Added explicit "quick usage paths" for three modes:
   - governance sidecar mode
   - attach-first daily mode
   - governed write mode for medium/high risk
2. Added concrete AI coding assistance mapping (capability visibility, gate execution, risky-write controls, evidence/handoff/replay linkage, multi-repo reuse).
3. Synced usage boundaries to avoid overclaim:
   - runtime is a governance layer over hosts
   - native attach is environment-dependent with explicit degrade paths
   - no universal full-takeover claim across all hosts/repos/workflows
4. Added docs index links for the new bilingual quickstart guides.

## Verification
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - `exit_code`: `0`
   - `key_output`: `OK python-bytecode`; `OK python-import`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - `exit_code`: `0`
   - `key_output`: `OK runtime-unittest`; `Ran 250 tests`; `OK`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - `exit_code`: `0`
   - `key_output`: `OK schema-json-parse`; `OK schema-example-validation`; `OK schema-catalog-pairing`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
   - `exit_code`: `0`
   - `key_output`: `OK runtime-status-surface`; `OK codex-capability-ready`; `OK adapter-posture-visible`

## Risks
- If capability posture or command surfaces change again, README/quickstart wording may drift and needs periodic resync with executable evidence.

## Rollback
- Revert:
  - `README.md`
  - `README.en.md`
  - `README.zh-CN.md`
  - `docs/README.md`
  - `docs/quickstart/ai-coding-usage-guide.md`
  - `docs/quickstart/ai-coding-usage-guide.zh-CN.md`
  - `docs/quickstart/use-with-existing-repo.md`
  - `docs/quickstart/use-with-existing-repo.zh-CN.md`
  - `docs/change-evidence/20260420-readme-and-usage-guides-refresh.md`
- Re-run gates:
  1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
