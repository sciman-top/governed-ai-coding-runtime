# 20260609 Reference Basis And Preflight Hardening

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home:
  - `docs/architecture/reference-basis-policy.json`
  - `docs/research/reference-basis-catalog.json`
  - `docs/research/reference-basis-matrix.md`
  - `scripts/verify-reference-basis.py`
  - `scripts/verify-repo.ps1`
  - `scripts/governance/preflight.ps1`
  - `.governed-ai/repo-profile.json`
  - `.github/workflows/verify.yml`
  - `docs/roadmap/reference-governance-and-preflight-roadmap.md`
  - `docs/plans/reference-governance-and-preflight-plan.md`
  - `docs/backlog/issue-ready-backlog.md`
  - `docs/backlog/issue-seeds.yaml`
- verification path: keep `build -> test -> contract/invariant -> hotspot` as the hard floor, then close with formal `preflight`, docs/scripts checks, issue rendering, and `git diff --check`

## Root Cause And Changes
- Before this slice, the repository already had:
  - a strong local external reference shelf
  - a narrow `reference-required` Contract guard
  - a generic `full-check` gate runner
  - a minimal CI `verify.yml`
- It still lacked:
  - a repo-owned answer to `which surfaces must consult which local references`
  - a fail-closed guard that checks named local reference ids instead of only broad source categories
  - a formal release-style `preflight` entrypoint that can run locally and in CI
- This slice adds:
  - a checked-in `reference-basis` policy, catalog, and matrix
  - a new `scripts/verify-reference-basis.py`
  - `Contract` gate wiring for `reference-basis`
  - `doctor` inside repo-profile full gate
  - rollout-contract and target-governance ownership alignment for `hotspot_command`
  - `scripts/governance/preflight.ps1`
  - CI `release-preflight`
  - a bounded roadmap / plan / backlog / issue-seed package for `GAP-169..172`

## Source Review
reference_required_review:
- changed_surface_paths:
  - `docs/architecture/reference-required-change-policy.json`
  - `docs/architecture/reference-basis-policy.json`
  - `docs/research/reference-basis-catalog.json`
  - `docs/research/reference-basis-matrix.md`
  - `docs/targets/target-repo-governance-baseline.json`
  - `docs/targets/target-repo-rollout-contract.json`
  - `docs/targets/target-repos-catalog.json`
  - `scripts/verify-reference-basis.py`
  - `scripts/verify-target-repo-rollout-contract.py`
  - `scripts/verify-repo.ps1`
  - `scripts/governance/preflight.ps1`
  - `scripts/apply-target-repo-governance.py`
  - `scripts/lib/target_repo_speed_profile.py`
  - `scripts/verify-target-repo-governance-consistency.py`
  - `.github/workflows/verify.yml`
  - `.governed-ai/repo-profile.json`
- official_sources_reviewed:
  - `https://developers.openai.com/codex/guides/agents-md`
  - `https://docs.anthropic.com/en/docs/claude-code/settings`
  - `https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices`
  - `https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule`
- primary_references_reviewed:
  - `D:\CODE\external\ai-coding-runtime-references\README.md`
  - `D:\CODE\external\ai-coding-runtime-references\references.manifest.json`
  - `docs/research/external-reference-repo-one-page-overview.md`
  - `docs/research/external-reference-repo-tiering.md`
  - `docs/research/external-reference-repos-index.md`
  - `docs/research/reference-basis-catalog.json`
  - `docs/research/reference-basis-matrix.md`
- local_runtime_evidence_reviewed:
  - `docs/change-evidence/20260418-local-ci-same-contract-verification.md`
  - `docs/change-evidence/20260609-reference-required-change-enforcement.md`
  - `docs/architecture/planning-status.json`
- source_decision:
  - Keep the current external shelf intact for this slice; the highest-value gap is not `more clones`, but a repo-owned rule for `which current clones must be reviewed for which surfaces`.
  - Reuse the existing `reference-required` Contract gate and extend it with named local-reference discipline plus release-style preflight, instead of inventing a parallel verifier stack.

reference_basis_review:
- changed_surface_paths:
  - `docs/architecture/reference-basis-policy.json`
  - `scripts/verify-reference-basis.py`
  - `scripts/verify-repo.ps1`
  - `scripts/governance/preflight.ps1`
  - `.github/workflows/verify.yml`
  - `.governed-ai/repo-profile.json`
- reference_basis_surface_ids:
  - `host-and-adapter-boundaries`
  - `release-gate-and-ci-boundaries`
- required_local_reference_ids_reviewed:
  - `openai-codex`
  - `openai-agents-python`
  - `openai-agents-js`
  - `anthropic-claude-code`
  - `anthropic-claude-code-action`
  - `github-copilot-cli`
  - `google-antigravity-cli`
- reference_adoption_decision:
  - Use a checked-in `reference-basis` catalog for CI-visible truth and long-lived repo memory.
  - Keep the maintainer's `D:\CODE\external\ai-coding-runtime-references` shelf as the physical clone location, but require same-diff evidence to prove which named shelf entries were actually reviewed on guarded surfaces.
  - Because `doctor/hotspot` was promoted into the self-runtime full gate, the target-governance baseline, rollout contract, and speed-profile derivation path also need to recognize `hotspot_command`; otherwise preflight fails on self-generated drift instead of on real release risk.

pre_change_review:
- control_repo_manifest_and_rule_sources: checked current `AGENTS.md`, `scripts/verify-pre-change-review.py`, `scripts/verify-repo.ps1`, `docs/README.md`, `docs/plans/README.md`, and `docs/backlog/README.md` before tightening self-repo gate and planning surfaces.
- user_level_deployed_rule_files: no user-level deployed rule files are changed by this slice.
- target_repo_deployed_rule_files: no target-repo deployed rule files are changed by this slice.
- target_repo_gate_scripts_and_ci: target-repo gate commands are unchanged; this slice only hardens self-repo `verify-repo.ps1`, repo-profile full gate, repo-local `preflight`, and self-repo CI.
- target_repo_repo_profile: target repo profiles are unchanged; only the self-runtime `.governed-ai/repo-profile.json` gains explicit hotspot coverage in full gate.
- target_repo_readme_and_operator_docs: target-repo README/operator contracts are unchanged; only self-repo docs, plan indexes, and backlog indexes are updated.
- current_official_tool_loading_docs: loading semantics remain anchored in existing official Codex/Claude/GitHub/MCP docs; this slice adds reference and preflight discipline rather than changing host loading behavior.
- drift-integration decision: integrate `reference-basis` into the existing Contract gate and wire release-style `preflight` into the existing `verify.yml`, instead of creating a new isolated gate system.

## Verification
- `python -m unittest tests.runtime.test_reference_basis tests.runtime.test_preflight_ci_wiring -v`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/governance/preflight.ps1 -DisableAutoCommit`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
- `git diff --check`

## Risk
- risk_level: `low`
- reason: governance policy, verifier, queue docs, repo-profile, and CI composition hardening only; no provider/account mutation, target-repo sync, credential rewrite, push, or merge.
- compatibility: current active queue and current decision gate remain unchanged in `planning-status.json`; this slice hardens how future guarded changes prove reference review and release readiness.

## Rollback
- Revert:
  - `docs/architecture/reference-required-change-policy.json`
  - `docs/architecture/reference-basis-policy.json`
  - `docs/research/reference-basis-catalog.json`
  - `docs/research/reference-basis-matrix.md`
  - `docs/roadmap/reference-governance-and-preflight-roadmap.md`
  - `docs/plans/reference-governance-and-preflight-plan.md`
  - `docs/backlog/issue-ready-backlog.md`
  - `docs/backlog/issue-seeds.yaml`
  - `docs/README.md`
  - `docs/plans/README.md`
  - `docs/backlog/README.md`
  - `docs/change-evidence/README.md`
  - `docs/change-evidence/20260609-reference-basis-and-preflight-hardening.md`
  - `scripts/verify-reference-basis.py`
  - `scripts/verify-repo.ps1`
  - `scripts/governance/preflight.ps1`
  - `.governed-ai/repo-profile.json`
  - `.github/workflows/verify.yml`
- Re-run the hard gate order after rollback.
