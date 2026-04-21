# Repo Profile Spec

## Status
Draft

## Purpose
Define the per-repository configuration inherited by governed sessions.

## Required Fields
- repo_id
- display_name
- primary_language
- repo_root_locator
- rollout_posture
- build_commands
- test_commands
- lint_commands
- typecheck_commands
- risk_defaults
- approval_defaults
- tool_allowlist
- path_policies
- branch_policy
- delivery_format

## Optional Fields
- repo_map_strategy
- quick_gate_commands
- full_gate_commands
- task_lifecycle
- extra_eval_suites
- context_files
- reviewer_handoff_template
- compatibility_signals
- interaction_profile

## Inheritance Model
1. platform defaults
2. repo profile inherited values
3. bounded repo override

## Override Rules
Repo profiles may override:
- command entrypoints
- timeouts
- allowed low-risk tools
- optional eval suites
- delivery templates
- bounded interaction defaults

Repo profiles may not override:
- evidence minimum fields
- high-risk approval requirements
- control registry semantics
- rollback reference requirement
- clarification hard caps
- hard budget stop semantics
- explicit degrade behavior
- canonical gate order

## Rollout Posture
- `current_mode`: currently active execution posture for this repo
- `target_mode`: desired posture once compatibility and evidence are strong enough
- `promotion_condition_ref`: optional link to the promotion rule or runbook

Valid posture values:
- observe
- advisory
- enforced

## Compatibility Signals
Each signal records:
- capability
- status
- degrade_to
- reason

Signal `status` values:
- full_support
- partial_support
- unsupported

## Task Lifecycle
Repos may declare local persistence hints for the Foundation task store:
- `persistence_kind`
- `store_root`
- `supports_pause_resume`
- `supports_retry_timeout`
- `artifact_root`
- `replay_root`

## Interaction Profile
Repos may declare bounded collaboration defaults through `interaction_profile`.

Supported fields:
- `default_mode`
- `term_explain_style`
- `default_checklist_kind`
- `compaction_preference`
- `summary_template`
- `handoff_teaching_notes`

These defaults tune how a repo prefers guidance to be phrased, but they do not weaken the shared clarification, budget, or approval boundaries.

## Verification
A repo profile is valid only if:
- all required commands are present or explicitly marked not applicable
- all path policies compile into deterministic allow/deny checks
- quick and full gates have unambiguous command order
- rollout posture uses a supported governance posture name
- compatibility degrade behavior is explicit whenever support is partial or unsupported
- interaction defaults stay bounded and do not redefine hard clarification or stop-on-budget behavior
- managed workspaces and runtime-local storage roots stay on one machine in the first Full Runtime stage
