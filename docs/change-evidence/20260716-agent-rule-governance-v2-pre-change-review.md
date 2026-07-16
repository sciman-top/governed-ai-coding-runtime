# Agent Rule Governance v2 Pre-Change Review

## Scope

- `issue_id`: `agent-rule-governance-v2-state-semantics`
- `risk`: medium; the verifier and Contract gate change which target state is
  authoritative for release validation.
- `rollback`: revert the v2 state-semantics commit. The complete pre-migration
  tree is also preserved at `archive/runtime-v1-20260716`.

## pre_change_review

- `control_repo_manifest_and_rule_sources`: reviewed `rules/manifest.json`,
  both global rule sources, the target coordination manifest, its schema, and
  the exact target CI workflow hash. This slice does not change rule content,
  versions, target membership, or sync destinations.
- `user_level_deployed_rule_files`: verified protected global sync with
  `python scripts/sync-agent-rules.py --scope All --fail-on-change`; both
  managed copies remain at zero drift. No apply was performed.
- `repo_local_gate_scripts_and_ci`: compared the existing Contract gate,
  target verifier, target workflow template, aggregate workflow, and focused
  tests. The local Contract now audits `origin/main --require-all`; isolated CI
  layouts continue to use the explicit workspace-root override.
- `repo_local_repo_profile`: confirmed the control repository itself is not a
  managed target and all nine target repository paths remain explicit. Target
  business gates are not changed or replaced.
- `repo_local_readme_and_operator_docs`: reviewed the current README, docs
  index, architecture, PRD, and 9.57 evidence. Their runtime-era product claims
  are scheduled for the later product-truth slice, not silently reinterpreted
  in this code change.
- `current_official_tool_loading_docs`: checked current OpenAI Codex
  `AGENTS.md` discovery and Anthropic Claude Code memory/settings guidance.
  Neither host requires moving a target worktree to audit a committed rule
  snapshot.
- `drift-integration decision`: treat the checked-out workspace and a named Git
  revision as distinct data sources. Resolve the revision to a commit SHA,
  read rule blobs without checkout, reject unsafe revision strings, preserve
  workspace dirty observations only in workspace mode, and expose the selected
  state in JSON.

## Verification

- `python -m unittest tests.runtime.test_verify_target_project_rules`
- `python scripts/verify-target-project-rules.py --git-ref origin/main --require-all`
- `python scripts/verify-target-project-rules.py --require-all` remains an
  intentional workspace-state probe and currently reports local drift.

## reference_required_review

- `changed_surface_paths`: `scripts/verify-target-project-rules.py`,
  `scripts/verify-repo.ps1`, and their focused tests.
- `official_sources_reviewed`: OpenAI Codex `AGENTS.md` discovery and advanced
  configuration documentation; Anthropic Claude Code memory, settings,
  permissions, and hooks documentation.
- `primary_references_reviewed`: the repository-owned target verifier,
  coordination schema, exact target workflow template, current 9.57 release
  evidence, and the nine target repositories' existing `origin/main` refs.
- `local_runtime_evidence_reviewed`: workspace audit reproduced 8/9 failures;
  Git-ref audit passed 9/9 without moving worktrees; focused tests passed.
- `source_decision`: keep the target-owned rule model and add only a safe Git
  object data source plus explicit status metadata. Do not introduce a daemon,
  database, provider integration, target checkout, or implicit fetch.

## State Boundary

- `default_branch_effective`: determined from the configured Git ref without
  moving or cleaning target worktrees.
- `workspace_effective`: determined from files in each current worktree and
  reported separately.
- `host_loaded` and `hosted_accepted`: not claimed by this static verifier.

## reference_basis_review

- `changed_surface_paths`: `scripts/verify-repo.ps1` changes the local release
  gate, while `scripts/verify-target-project-rules.py` adds the revision-backed
  source used by that gate.
- `reference_basis_surface_ids`: `release-gate-and-ci-boundaries`.
- `required_local_reference_ids_reviewed`: `openai-codex`,
  `anthropic-claude-code-action`, and `github-copilot-cli`. Codex establishes
  the native project-rule/loading boundary; Claude Code Action and Copilot CLI
  were checked only to confirm that hosted or third-party execution surfaces
  do not justify moving local target worktrees or becoming this repository's
  release authority.
- `reference_adoption_decision`: adopt immutable-revision audit, explicit state
  labels, fail-closed resolution, and CI/workspace separation. Reject hosted
  agent execution, provider credentials, implicit fetch, automatic checkout,
  and a parallel workflow runtime.
