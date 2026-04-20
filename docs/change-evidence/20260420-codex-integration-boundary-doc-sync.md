# 20260420 Codex Integration Boundary Documentation Sync

## Purpose
- Eliminate documentation drift between older Codex integration wording and the current executable runtime surface on the branch baseline.
- Keep claim discipline strict: reflect landed capability improvements without overstating universal host takeover.

## Clarification Trace
- `issue_id`: `codex-integration-boundary-doc-sync`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `n/a`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Basis
- Runtime/contract surfaces:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py`
  - `scripts/run-governed-task.py`
- Recent executable evidence:
  - `docs/change-evidence/20260420-direct-to-hybrid-final-state-closeout.md`
  - `docs/change-evidence/20260420-codex-capability-stability-retry-and-readiness-surface-hardening.md`
  - `docs/change-evidence/20260420-native-attach-inferred-via-resume-surface-and-write-flow-adapter-evidence.md`
- Updated docs:
  - `docs/product/codex-cli-app-integration-guide.md`
  - `docs/product/codex-cli-app-integration-guide.zh-CN.md`
  - `README.md`
  - `README.en.md`
  - `README.zh-CN.md`

## What Changed
1. Codex integration guide (EN/ZH) now states current runtime reality:
   - Codex capability probe/readiness and tiered degrade semantics are available.
   - Session bridge gate/write commands are runtime-managed and carry adapter identity metadata.
   - Smoke trial remains safe-mode and deterministic.
2. Removed outdated wording that implied the Codex path is only manual-handoff/read-only.
3. Preserved non-overclaim boundaries:
   - no universal host replacement claim
   - no universal native-attach guarantee across all environments
   - no universal full-takeover claim for all external repos and all high-risk workflows
4. Synchronized root README + EN + ZH entry docs with the same capability/constraint language.

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
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
   - `exit_code`: `0`
   - `key_output`: `OK active-markdown-links`; `OK issue-seeding-render`; `Ran 250 tests`; `OK`

## Risks
- If runtime behavior changes again (especially Codex probe or session-bridge execution semantics), these entry docs can drift quickly and must be re-synced with fresh executable evidence.

## Rollback
- Revert:
  - `docs/product/codex-cli-app-integration-guide.md`
  - `docs/product/codex-cli-app-integration-guide.zh-CN.md`
  - `README.md`
  - `README.en.md`
  - `README.zh-CN.md`
  - `docs/change-evidence/20260420-codex-integration-boundary-doc-sync.md`
- Re-run:
  1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
