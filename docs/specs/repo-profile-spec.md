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
- gate_timeout_seconds
- quick_gate_commands
- full_gate_commands
- additional_gate_commands
- task_lifecycle
- extra_eval_suites
- context_files
- reviewer_handoff_template
- compatibility_signals
- auto_commit_policy
- interaction_profile
- learning_assistance_policy
- rule_file_coordination_policy
- windows_process_environment_policy

## Inheritance Model
1. platform defaults
2. repo profile inherited values
3. bounded repo override

## Override Rules
Repo profiles may override:
- command entrypoints
- timeouts
- per-gate `timeout_seconds`
- allowed low-risk tools
- optional eval suites
- delivery templates
- bounded interaction defaults
- bounded learning-assistance policy
- rule-file coordination details that stay repo/profile scoped
- Windows process environment guidance that stays repo/profile scoped

Repo profiles may not override:
- evidence minimum fields
- high-risk approval requirements
- control registry semantics
- rollback reference requirement
- clarification hard caps
- hard budget stop semantics
- explicit degrade behavior
- canonical gate order
- risk taxonomy
- approval state semantics

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

## Auto Commit Policy
Repos may declare optional post-gate auto-commit behavior through `auto_commit_policy`.

Supported fields:
- `enabled`
- `on` (`any_pass` / `fast_pass` / `full_pass` / `milestone`)
- `milestone_markers`
- `require_all_required_gates_pass`
- `commit_message_template`

When enabled, the runtime may stage all tracked and untracked changes and create one commit only after gate execution reaches a pass condition.
The commit message template may reference runtime placeholders such as mode, timestamp, repo id, and milestone marker.

## Interaction Profile
Repos may declare bounded collaboration defaults through `interaction_profile`.

Supported fields:
- `default_mode`
- `communication_language`
- `user_facing_output_language`
- `preserve_technical_tokens_language`
- `commit_message_language`
- `term_explain_style`
- `default_checklist_kind`
- `compaction_preference`
- `summary_template`
- `multi_option_recommendation_policy`
- `handoff_teaching_notes`
- `language_guidance`

These defaults tune how a repo prefers guidance to be phrased, but they do not weaken the shared clarification, budget, or approval boundaries.

## Learning Assistance Policy
Repos may declare low-token teaching and misunderstanding-detection behavior through `learning_assistance_policy`.

Supported fields:
- `enabled`
- `observable_signals_only`
- `require_evidence_refs`
- `trigger_on_user_correction`
- `trigger_signals`
- `restatement_triggers`
- `bug_observation_checklist`
- `max_terms_per_response`
- `max_task_restatements_per_stage`
- `max_observation_items`
- `max_clarification_questions`
- `teaching_style`
- `token_budget_policy`
- `degrade_to_handoff_on_budget_pressure`
- `guidance`

The policy must treat confusion as observable interaction evidence, not as psychological inference. Valid signals include user corrections, repeated failures, missing expected/actual/repro facts, symptom/root-cause confusion, term confusion, intent drift, and budget pressure.

Low-token teaching should explain at most one or two terms per response, prefer `definition + task role + common mistake`, and switch to checklist-first bug observation when runtime symptoms are underspecified.

## Rule File Coordination Policy
Repos may inherit or declare bounded rule-file coordination defaults through `rule_file_coordination_policy`.

Supported fields:
- `enabled`
- `global_rule_scope`
- `project_rule_scope`
- `synergy_requirement`
- `source_review_basis`
- `root_file_quality_rules`
- `pre_change_review_gate`
- `tool_specific_loading_policy`
- `progressive_disclosure`
- `missing_project_rule_behavior`
- `required_project_rule_fields`

The policy may tighten drift review and self-containment requirements, but it may not redefine global precedence, remove evidence, or replace deterministic gate enforcement.

## Windows Process Environment Policy
Repos may inherit or declare bounded Windows process normalization defaults through `windows_process_environment_policy`.

Supported fields:
- `enabled`
- `scope`
- `required_variables`
- `inherited_network_variables`
- `safe_codex_policy_source`
- `preferred_powershell_executable`
- `fallback_powershell_executable`
- `windows_powershell_escape_hatch_env`
- `required_practice`
- `runtime_runbook`
- `coding_guidance`
- `powershell_entrypoint_pattern`
- `verification_commands`

The policy may strengthen repo/operator guidance, but it may not weaken the shared approval model, gate order, or rollback requirements.

## Verification
A repo profile is valid only if:
- all required commands are present or explicitly marked not applicable
- all path policies compile into deterministic allow/deny checks
- quick and full gates have unambiguous command order
- `l1/l2/l3` layered gates preserve the canonical order within their declared scope
- gate timeout values are non-negative and `0` means no profile-provided timeout
- rollout posture uses a supported governance posture name
- compatibility degrade behavior is explicit whenever support is partial or unsupported
- interaction defaults stay bounded and do not redefine hard clarification or stop-on-budget behavior
- learning assistance stays evidence-backed, respects the clarification cap, and degrades to summaries or handoff when budget pressure is high
- inherited and repo-local override fields resolve to explicit schema paths in the inheritance matrix
- managed workspaces and runtime-local storage roots stay on one machine in the first Full Runtime stage
