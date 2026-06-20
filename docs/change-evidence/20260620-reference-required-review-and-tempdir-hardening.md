# 20260620 Reference Required Review And Tempdir Hardening

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home:
  - `scripts/build-governance-hub-certification.py`
  - `scripts/build-policy-tool-credential-audit.py`
  - `scripts/build-repo-map-context-artifact.py`
  - `scripts/lib/evidence_paths.py`
  - `tests/__init__.py`
  - `scripts/Initialize-WindowsProcessEnvironment.ps1`
  - `scripts/verify-promotion-lifecycle.py`
  - `docs/change-evidence/20260620-reference-required-review-and-tempdir-hardening.md`
- verification path: keep the reference-required evidence fresh for the guarded script surfaces, normalize repo-local evidence paths, and harden the tempdir/runtime-home setup so the Windows test and verification entrypoints can run inside the worktree

## Pre-Change Review
pre_change_review

- changed_surface_paths:
  - `scripts/build-governance-hub-certification.py`
  - `scripts/build-policy-tool-credential-audit.py`
  - `scripts/build-repo-map-context-artifact.py`
  - `scripts/lib/evidence_paths.py`
  - `tests/__init__.py`
  - `scripts/Initialize-WindowsProcessEnvironment.ps1`
  - `scripts/verify-promotion-lifecycle.py`

- control_repo_manifest_and_rule_sources:
  - reviewed `AGENTS.md`
  - reviewed `rules/manifest.json`
  - confirmed this slice edits verifier surfaces, repo-local evidence helpers, and test/runtime initialization instead of managed rule source bodies

- user_level_deployed_rule_files:
  - reviewed the requirement boundary from project/global `AGENTS.md`
  - no user-level deployed `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` files are modified in this slice

- target_repo_deployed_rule_files:
  - reviewed `docs/targets/target-repo-governance-baseline.json`
  - confirmed this slice does not synchronize or edit target-repo deployed rule files

- target_repo_gate_scripts_and_ci:
  - reviewed `scripts/verify-repo.ps1`
  - reviewed `scripts/verify-reference-required-changes.py`
  - decision: keep the canonical gate order unchanged and only repair the guarded evidence/runtime surfaces needed by the existing gates

- target_repo_repo_profile:
  - reviewed `docs/architecture/planning-status.json`
  - confirmed this slice does not change queue selection or active-policy posture

- target_repo_readme_and_operator_docs:
  - reviewed `docs/change-evidence/README.md`
  - reviewed `docs/change-evidence/evidence-index.json`
  - decision: keep the evidence slice bounded to the scripts and runtime entrypoints listed above

- current_official_tool_loading_docs:
  - reviewed current Codex loading semantics from repo `AGENTS.md`
  - confirmed this slice does not alter live tool loading assumptions, provider/auth semantics, or host capability claims beyond local evidence/runtime hardening

- drift-integration decision:
  - integrate through the existing evidence and verifier surfaces:
    - normalize repo-local evidence paths through a shared helper
    - keep the guarded report builders pointing at canonical repo-relative paths
    - harden Windows process env so temp/runtime paths stay inside the worktree
    - keep `verify-promotion-lifecycle.py` on a manual temp-root cleanup path
  - do not promote a new queue or change selector truth

## Source Review
reference_required_review

- changed_surface_paths:
  - `scripts/build-governance-hub-certification.py`
  - `scripts/build-policy-tool-credential-audit.py`
  - `scripts/build-repo-map-context-artifact.py`
  - `scripts/verify-promotion-lifecycle.py`

- official_sources_reviewed:
  - `https://docs.python.org/3/library/tempfile.html`
  - `https://docs.python.org/3/library/pathlib.html`

- primary_references_reviewed:
  - `docs/change-evidence/20260620-active-queue-evidence-upkeep-refresh.md`
  - `docs/change-evidence/20260620-self-evolution-review-refresh.md`
  - `docs/change-evidence/20260618-planning-proof-and-claim-boundary-pre-change-review.md`

- local_runtime_evidence_reviewed:
  - `tests/__init__.py`
  - `scripts/Initialize-WindowsProcessEnvironment.ps1`
  - `scripts/verify-promotion-lifecycle.py`
  - `docs/change-evidence/governance-hub-certification-report.json`
  - `docs/change-evidence/policy-tool-credential-audit-report.json`
  - `docs/change-evidence/repo-map-context-artifact.json`

- source_decision:
  - keep the evidence and runtime changes narrow: canonical repo-relative evidence paths, worktree-local runtime-home/temp handling, and guarded temp-root cleanup are sufficient for the current slice, while new host or protocol claims remain out of scope

## Verification
- `python scripts/verify-planning-status.py`
  - result: pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - result: pass
  - note: verified against the intended worktree slice after the tempdir/runtime-home hardening

## Risk
- risk_level: `low`
- reason:
  - evidence path normalization and worktree-local temp/runtime-home hardening only
  - no selector or active-queue mutation
  - no effective policy expansion

## Rollback
- revert:
  - `scripts/build-governance-hub-certification.py`
  - `scripts/build-policy-tool-credential-audit.py`
  - `scripts/build-repo-map-context-artifact.py`
  - `scripts/lib/evidence_paths.py`
  - `tests/__init__.py`
  - `scripts/Initialize-WindowsProcessEnvironment.ps1`
  - `scripts/verify-promotion-lifecycle.py`
  - `docs/change-evidence/20260620-reference-required-review-and-tempdir-hardening.md`
- re-run:
  - `python scripts/verify-planning-status.py`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
