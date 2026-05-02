# 2026-05-02 Core Principles Efficiency Profile Alignment

## Goal
- Current landing: `D:\CODE\governed-ai-coding-runtime`.
- Target home: core-principles policy, project rule files, operator-facing docs, Codex local optimizer defaults, and verifier tests.
- Verification path: policy/spec/docs alignment -> focused unit tests -> core-principles verifier -> full gate slices where practical.

## Basis
- Stable owner preference: automatic continuous execution, lower token and cost burn, necessary explanation, and high throughput.
- Current implementation preference: `gpt-5.4 + medium + never` with `model_context_window = 272000` and `model_auto_compact_token_limit = 220000`.
- Decision: keep the stable preference in core principles and keep model/provider/context/compact values as replaceable implementation profiles. Existing safety, least-privilege, evidence, rollback, review, and gate constraints remain the enforcement layer rather than a new efficiency preference.
- Non-decision: do not add trigger-word model escalation or downgrade rules to the core policy.

## Changes
- Strengthened `efficiency_first` to include necessary explanatory density while keeping hard-gate completion in the existing hard-gate/evidence enforcement layer.
- Updated Codex, Claude, and Gemini project rules so all three hosts see the same stable principle.
- Updated README, docs index, and AI coding quickstarts to describe `gpt-5.4 + medium + never` as the current temporary implementation, not the long-term principle.
- Updated Codex local optimizer defaults and status profile from `gpt-5.5` to `gpt-5.4`.
- Added verifier coverage so the principle remains documented and the new source-target drift principle stays present in generated test policies.

## Verification
- `python -m unittest tests.runtime.test_codex_local tests.runtime.test_core_principles`: pass, 16 tests.
- `python scripts\verify-core-principles.py`: pass, no missing principles, doc refs, evidence refs, or forbidden pattern hits.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Optimize-CodexLocal.ps1`: pass dry-run after final wording cleanup; emitted `gpt-5.4`, `medium`, `272000`, `220000`, and efficiency targets `少打扰` / `自动连续执行` / `节省 token / 成本` / `保留必要解释` / `高效率`.
- `python scripts\sync-agent-rules.py --scope All --fail-on-change`: pass, `changed_count=0`, `blocked_count=0`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1`: pass after final wording cleanup, `OK python-bytecode`, `OK python-import`.
- `$env:GOVERNED_RUNTIME_TEST_TIMEOUT_SECONDS='300'; pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime`: pass after final wording cleanup, 95 test files, 0 failures.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Contract`: pass after final wording cleanup, including `agent-rule-sync`, `pre-change-review`, and `functional-effectiveness`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\doctor-runtime.ps1`: pass after final wording cleanup with existing `WARN codex-capability-degraded`; all hard checks returned `OK`.

## Intermediate Finding
- The first full `Runtime` attempt failed because project rule targets contained an auto-merged duplicate efficiency-principle line while the manifest-managed source and target needed to be structurally normalized.
- Resolution: moved the strengthened principle into the canonical A.2 line for Codex, Claude, and Gemini project rules, removed the auto-merged duplicate block, and confirmed rule sync drift returned to zero.

## N/A
- No `platform_na` or `gate_na` was used.

## Rollback
- Revert the policy/spec/docs/script/test changes from this slice.
- Restore `scripts/Optimize-CodexLocal.ps1` and `scripts/lib/codex_local.py` to the previous Codex default if the recommended local profile changes again.
