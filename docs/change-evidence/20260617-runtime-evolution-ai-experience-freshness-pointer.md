# 20260617 Runtime Evolution AI Experience Freshness Pointer

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home:
  - `scripts/evaluate-runtime-evolution.py`
  - `tests/runtime/test_runtime_evolution.py`
  - `scripts/generate-self-evolution-eval-dataset.py`
  - `tests/runtime/test_self_evolution_readiness.py`
  - `docs/change-evidence/governance-hub-certification-report.json`
  - `docs/change-evidence/runtime-evolution-candidates/20260617-runtime-evolution-candidates.json`
  - `docs/change-evidence/evolution-sources/20260617-runtime-evolution-sources.json`
  - `docs/change-evidence/self-evolution-evals/20260617-self-evolution-eval-dataset.json`
  - `docs/change-evidence/20260617-runtime-evolution-ai-experience-freshness-pointer.md`
- verification path: keep `EVOL-AI-EXPERIENCE` tied to fresh AI coding experience artifacts instead of a stale fixed-date reference

## Why This Slice Was Needed
- The active queue remains `Continuous-Execution`, and the selector still says `defer_ltp_and_refresh_evidence`.
- Under that bounded loop, the repo refreshes AI coding experience review artifacts regularly, including `20260617-ai-coding-experience-review.json`.
- But `scripts/evaluate-runtime-evolution.py` still hard-coded `EVOL-AI-EXPERIENCE.source_ref` to `.runtime/artifacts/ai-coding-experience/20260501-ai-coding-experience-review.json`.
- That made the candidate itself stale-looking even when the latest daily review artifacts were fresh.

## Root Cause
- Runtime evolution candidate construction used a fixed historical AI coding experience artifact path instead of resolving the current `as_of` artifact or falling back to the latest available review file.

## Change Summary
1. Resolved AI coding experience source refs dynamically
- `scripts/evaluate-runtime-evolution.py` now resolves:
  - the same-day `ai-coding-experience-review.json` when present
  - otherwise the latest available review artifact under `.runtime/artifacts/ai-coding-experience/`
  - and only falls back to the expected dated path when no artifact exists yet

2. Exposed the resolved artifact in the evidence snapshot
- `evidence_snapshot.ai_coding_experience` now records `artifact_source_ref` so downstream reports can show which concrete artifact was used.

3. Added regression coverage
- `tests/runtime/test_runtime_evolution.py` now asserts that `EVOL-AI-EXPERIENCE` uses the fresh `20260617` artifact ref for `as_of=2026-06-17`.

4. Refreshed dependent report output
- Rebuilt `docs/change-evidence/governance-hub-certification-report.json` so its embedded runtime-evolution candidate section now cites the fresh `20260617` AI coding experience artifact instead of the stale `20260501` path.

5. Filled runtime-evolution eval dataset verification refs
- `scripts/generate-self-evolution-eval-dataset.py` now derives runtime-evolution candidate `verification_refs` from:
  - explicit `expected_verification_refs`
  - `acceptance_gates` script/test paths
  - the local `source_ref` when it is a readable repo artifact
- `tests/runtime/test_self_evolution_readiness.py` now asserts runtime-evolution candidate cases no longer emit empty `verification_refs`.
- Refreshed:
  - `docs/change-evidence/runtime-evolution-candidates/20260617-runtime-evolution-candidates.json`
  - `docs/change-evidence/evolution-sources/20260617-runtime-evolution-sources.json`
  - `docs/change-evidence/self-evolution-evals/20260617-self-evolution-eval-dataset.json`

## Reference Required Review
reference_required_review:
- changed_surface_paths:
  - `scripts/evaluate-runtime-evolution.py`
  - `scripts/generate-self-evolution-eval-dataset.py`
- official_sources_reviewed:
  - `docs/change-evidence/20260501-runtime-evolution-planning.md`
- primary_references_reviewed:
  - `.runtime/artifacts/ai-coding-experience/20260617-ai-coding-experience-review.json`
  - `docs/change-evidence/governance-hub-certification-report.json`
  - `docs/change-evidence/self-evolution-evals/20260617-self-evolution-eval-dataset.json`
- local_runtime_evidence_reviewed:
  - `python -m unittest tests.runtime.test_runtime_evolution -v`
  - `python -m unittest tests.runtime.test_self_evolution_readiness -v`
  - `python scripts/evaluate-runtime-evolution.py --as-of 2026-06-17`
  - `python scripts/generate-self-evolution-eval-dataset.py --as-of 2026-06-17 --write-artifacts`
  - `python scripts/verify-governance-hub-certification.py`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- source_decision:
  - Keep `EVOL-AI-EXPERIENCE` bound to the freshest available AI coding experience review artifact so the runtime-evolution candidate and downstream certification reports point at current bounded-loop evidence instead of a stale historical snapshot.

reference_basis_review:
- changed_surface_paths:
  - `scripts/evaluate-runtime-evolution.py`
  - `scripts/generate-self-evolution-eval-dataset.py`
  - `tests/runtime/test_runtime_evolution.py`
  - `tests/runtime/test_self_evolution_readiness.py`
  - `docs/change-evidence/20260617-runtime-evolution-ai-experience-freshness-pointer.md`
  - `docs/change-evidence/README.md`
  - `docs/change-evidence/evolution-sources/20260617-runtime-evolution-sources.json`
  - `docs/change-evidence/runtime-evolution-candidates/20260617-runtime-evolution-candidates.json`
  - `docs/change-evidence/self-evolution-evals/20260617-self-evolution-eval-dataset.json`
  - `docs/change-evidence/governance-hub-certification-report.json`
- reference_basis_surface_ids:
  - `host-and-adapter-boundaries`
- required_local_reference_ids_reviewed:
  - `openai-codex`
  - `openai-agents-python`
  - `openai-agents-js`
  - `anthropic-claude-code`
  - `github-copilot-cli`
  - `google-antigravity-cli`
- reference_adoption_decision:
  - Keep this slice anchored to first-party host/runtime semantics for Codex, Claude Code, Copilot CLI, Antigravity CLI, and OpenAI Agents surfaces instead of treating stale repo prose as sufficient basis.
  - Limit adoption to bounded evidence freshness and traceability upkeep; do not widen this slice into effective runtime mutation or new autonomous host behavior.

## Verification
- `python -m unittest tests.runtime.test_runtime_evolution -v`
  - result: pass
- `python scripts/evaluate-runtime-evolution.py --as-of 2026-06-17`
  - result: pass
  - result: `EVOL-AI-EXPERIENCE.source_ref=.runtime/artifacts/ai-coding-experience/20260617-ai-coding-experience-review.json`
- `python scripts/build-governance-hub-certification.py`
  - result: pass
  - result: refreshed `docs/change-evidence/governance-hub-certification-report.json`
- `python -m unittest tests.runtime.test_self_evolution_readiness -v`
  - result: pass
- `python scripts/generate-self-evolution-eval-dataset.py --as-of 2026-06-17 --write-artifacts`
  - result: pass
  - result: `docs/change-evidence/self-evolution-evals/20260617-self-evolution-eval-dataset.json` now cites `docs/change-evidence/runtime-evolution-candidates/20260617-runtime-evolution-candidates.json`
  - result: runtime-evolution candidate cases now carry non-empty `verification_refs`
- `python scripts/verify-governance-hub-certification.py`
  - result: pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - result: pass

## Risk
- risk_level: `low`
- reason:
  - no new mutation lane was enabled
  - no selector state changed
  - the slice only corrects which review artifact the existing candidate points at

## Truth Boundary
- This slice improves repo-side traceability for the existing `EVOL-AI-EXPERIENCE` dry-run candidate.
- It does not promote any candidate into effective change.
- It does not change the current selector result `defer_ltp_and_refresh_evidence`.

## Rollback
- revert:
  - `scripts/evaluate-runtime-evolution.py`
  - `scripts/generate-self-evolution-eval-dataset.py`
  - `tests/runtime/test_runtime_evolution.py`
  - `tests/runtime/test_self_evolution_readiness.py`
  - `docs/change-evidence/governance-hub-certification-report.json`
  - `docs/change-evidence/runtime-evolution-candidates/20260617-runtime-evolution-candidates.json`
  - `docs/change-evidence/evolution-sources/20260617-runtime-evolution-sources.json`
  - `docs/change-evidence/self-evolution-evals/20260617-self-evolution-eval-dataset.json`
  - `docs/change-evidence/20260617-runtime-evolution-ai-experience-freshness-pointer.md`
- re-run:
  - `python -m unittest tests.runtime.test_runtime_evolution -v`
  - `python scripts/evaluate-runtime-evolution.py --as-of 2026-06-17`
  - `python scripts/verify-governance-hub-certification.py`
