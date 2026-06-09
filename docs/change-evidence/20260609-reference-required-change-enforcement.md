# 20260609 Reference-Required Change Enforcement

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home: `docs/architecture/reference-required-change-policy.json`, `scripts/verify-reference-required-changes.py`, `scripts/verify-repo.ps1`, `docs/architecture/runtime-evolution-policy.json`, and `scripts/evaluate-runtime-evolution.py`
- verification path: strengthen the existing Contract gate and runtime-evolution source catalog, then close with targeted tests plus `build -> test -> contract/invariant -> hotspot`

## Conclusion
- The repository already had a good planning-time and research-time source posture, but it was still too easy to change high-drift host/protocol/reference surfaces without fresh same-diff source evidence.
- This slice adds a narrow fail-closed Contract gate that only fires on named high-drift surfaces and requires explicit official-source review, primary-reference review, local-runtime evidence review, and a recorded source decision.
- The runtime-evolution required source catalog now also hard-requires the newly added official local-shelf repos `mcp-inspector` and `anthropic-claude-plugins-official`, so future dry-run evolution reviews cannot silently drop them.

## Source Review
reference_required_review:
- changed_surface_paths:
  - `docs/architecture/reference-required-change-policy.json`
  - `docs/architecture/runtime-evolution-policy.json`
  - `scripts/evaluate-runtime-evolution.py`
  - `scripts/verify-reference-required-changes.py`
  - `scripts/verify-repo.ps1`
- official_sources_reviewed:
  - `https://github.com/modelcontextprotocol/inspector`
  - `https://github.com/anthropics/claude-plugins-official`
  - `https://developers.openai.com/codex/guides/agents-md`
  - `https://developers.openai.com/codex/app/features`
- primary_references_reviewed:
  - `D:\CODE\external\ai-coding-runtime-references\README.md`
  - `D:\CODE\external\ai-coding-runtime-references\clone-results.json`
  - `docs/research/external-reference-repo-one-page-overview.md`
  - `docs/research/external-reference-repo-tiering.md`
  - `docs/research/external-reference-repos-index.md`
- local_runtime_evidence_reviewed:
  - `docs/change-evidence/20260503-ai-feature-source-catalog-coverage.md`
  - `docs/change-evidence/20260609-reference-shelf-official-additions.md`
  - `docs/architecture/planning-status.json`
- source_decision:
  - Keep enforcement narrow and fail-closed: only named high-drift host/protocol/reference surfaces trigger the new gate, and they must ship with fresh same-diff evidence rather than relying on chat-only rationale or stale historical review.

## Pre-Change Review
pre_change_review:
- control_repo_manifest_and_rule_sources: checked current `AGENTS.md`, existing `verify-pre-change-review.py`, `verify-repo.ps1`, and the architecture/doc indexes before adding a new Contract guard so the control repo stays the canonical landing point.
- user_level_deployed_rule_files: no user-level deployed rule files are changed by this slice.
- target_repo_deployed_rule_files: no target-repo deployed rule files are changed by this slice.
- target_repo_gate_scripts_and_ci: only the control-repo Contract gate is tightened; target-repo gate commands and CI are unchanged.
- target_repo_repo_profile: target repo profiles are unchanged.
- target_repo_readme_and_operator_docs: only control-repo documentation indexes are updated to expose the new policy and evidence path; no operator workflow or target-repo README contract is changed.
- current_official_tool_loading_docs: the existing official tool-loading posture remains anchored in `docs/architecture/current-source-compatibility-policy.json`; this slice adds a narrower same-diff evidence requirement rather than changing loading semantics.
- drift-integration decision: integrate the new guard into the existing Contract gate and change-evidence workflow instead of introducing a separate process or a parallel evidence location.

## Changes
- Added `docs/architecture/reference-required-change-policy.json` to define:
  - the exact high-drift surfaces that require mandatory source evidence
  - the required source categories
  - the mandatory evidence tokens and same-diff evidence location
- Added `scripts/verify-reference-required-changes.py` to:
  - inspect git-changed paths
  - detect guarded surfaces
  - require a changed evidence file under `docs/change-evidence/`
  - fail if required source-review tokens are missing or the evidence omits the guarded paths
- Wired the new verifier into `scripts/verify-repo.ps1` under the Contract gate.
- Added `tests/runtime/test_reference_required_changes.py` to cover missing evidence, incomplete evidence, unrelated changes, and gate wiring.
- Expanded the runtime-evolution required source catalog to include:
  - `mcp-inspector`
  - `anthropic-claude-plugins-official`
- Updated architecture/docs indexes so the new policy is discoverable without creating another planning truth layer.
- Updated root/docs/plans/backlog entrypoints so the hard source gate is visible before someone reads the verifier implementation.

## Verification
- `python -m unittest tests.runtime.test_reference_required_changes`
- `python -m unittest tests.runtime.test_runtime_evolution`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `git diff --check`

## Risk
- risk_level: `low`
- reason: policy, verifier, tests, and documentation-only tightening; no provider/account mutation, target-repo sync, credential rewrite, push, or merge.
- compatibility: ordinary repo changes stay outside this gate unless they touch named high-drift surfaces; the new enforcement is additive and same-diff evidence based.

## Rollback
- Revert:
  - `docs/architecture/reference-required-change-policy.json`
  - `docs/architecture/runtime-evolution-policy.json`
  - `scripts/evaluate-runtime-evolution.py`
  - `scripts/verify-reference-required-changes.py`
  - `scripts/verify-repo.ps1`
  - `tests/runtime/test_reference_required_changes.py`
  - `tests/runtime/test_runtime_evolution.py`
  - `docs/README.md`
  - `docs/architecture/README.md`
  - `docs/change-evidence/20260609-reference-required-change-enforcement.md`
  - `docs/change-evidence/README.md`
- Re-run the hard-gate order after rollback.
