"""Repository profile domain model placeholders for TDD."""

from dataclasses import dataclass
from pathlib import Path
import json

from governed_ai_coding_runtime_contracts.entrypoint_policy import normalize_required_entrypoint_policy


@dataclass(slots=True)
class RepoProfile:
    repo_id: str
    primary_language: str
    path_policies: dict
    rollout_posture: dict
    compatibility_signals: list[dict]
    required_entrypoint_policy: dict
    interaction_profile: dict
    learning_assistance_policy: dict
    workflow_governance_policy: dict
    raw: dict

    @classmethod
    def from_dict(cls, raw: dict) -> "RepoProfile":
        repo_id = _required_string(raw, "repo_id")
        primary_language = _required_string(raw, "primary_language")
        rollout_posture = raw.get("rollout_posture")
        if not isinstance(rollout_posture, dict):
            msg = "rollout_posture is required"
            raise ValueError(msg)
        path_policies = raw.get("path_policies")
        if not isinstance(path_policies, dict):
            msg = "path_policies is required"
            raise ValueError(msg)
        if not path_policies.get("read_allow"):
            msg = "path_policies.read_allow requires at least one scope"
            raise ValueError(msg)
        if not raw.get("tool_allowlist"):
            msg = "tool_allowlist requires at least one tool"
            raise ValueError(msg)
        for command_group in ("build_commands", "test_commands"):
            if not raw.get(command_group):
                msg = f"{command_group} requires at least one command"
                raise ValueError(msg)
        if not (raw.get("contract_commands") or raw.get("invariant_commands")):
            msg = "contract or invariant command is required"
            raise ValueError(msg)
        _validate_additional_gate_commands(raw.get("additional_gate_commands", []))
        compatibility_signals = raw.get("compatibility_signals", [])
        if not isinstance(compatibility_signals, list):
            msg = "compatibility_signals must be a list"
            raise ValueError(msg)
        required_entrypoint_policy = normalize_required_entrypoint_policy(
            raw.get("required_entrypoint_policy")
        )
        interaction_profile = _normalize_interaction_profile(raw.get("interaction_profile", {}))
        learning_assistance_policy = _normalize_learning_assistance_policy(
            raw.get("learning_assistance_policy", {})
        )
        workflow_governance_policy = _normalize_workflow_governance_policy(
            raw.get("workflow_governance_policy")
        )
        normalized_raw = dict(raw)
        normalized_raw["required_entrypoint_policy"] = required_entrypoint_policy
        normalized_raw["interaction_profile"] = interaction_profile
        normalized_raw["learning_assistance_policy"] = learning_assistance_policy
        normalized_raw["workflow_governance_policy"] = workflow_governance_policy
        return cls(
            repo_id=repo_id,
            primary_language=primary_language,
            path_policies=path_policies,
            rollout_posture=rollout_posture,
            compatibility_signals=compatibility_signals,
            required_entrypoint_policy=required_entrypoint_policy,
            interaction_profile=interaction_profile,
            learning_assistance_policy=learning_assistance_policy,
            workflow_governance_policy=workflow_governance_policy,
            raw=normalized_raw,
        )

    def command_ids(self, group: str) -> list[str]:
        command_key = f"{group}_commands"
        commands = self.raw.get(command_key, [])
        return [command["id"] for command in commands]


def load_repo_profile(path: str | Path) -> RepoProfile:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return RepoProfile.from_dict(raw)


def _required_string(raw: dict, key: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        msg = f"{key} is required"
        raise ValueError(msg)
    return value


def _normalize_interaction_profile(value: object) -> dict:
    if value is None:
        return {}
    if not isinstance(value, dict):
        msg = "interaction_profile must be an object"
        raise ValueError(msg)
    normalized = dict(value)
    default_mode = normalized.get("default_mode")
    if default_mode is not None and default_mode not in {"terse", "guided", "teaching"}:
        msg = f"unsupported interaction_profile.default_mode: {default_mode}"
        raise ValueError(msg)
    compaction_preference = normalized.get("compaction_preference")
    if compaction_preference is not None and compaction_preference not in {
        "stage_summary",
        "aggressive_compaction",
        "ref_only",
    }:
        msg = f"unsupported interaction_profile.compaction_preference: {compaction_preference}"
        raise ValueError(msg)
    return normalized


def _normalize_learning_assistance_policy(value: object) -> dict:
    if value is None:
        return {}
    if not isinstance(value, dict):
        msg = "learning_assistance_policy must be an object"
        raise ValueError(msg)
    normalized = dict(value)
    enabled = normalized.get("enabled")
    if enabled is not None and not isinstance(enabled, bool):
        msg = "learning_assistance_policy.enabled must be a bool"
        raise ValueError(msg)
    boolean_fields = (
        "observable_signals_only",
        "require_evidence_refs",
        "trigger_on_user_correction",
        "degrade_to_handoff_on_budget_pressure",
    )
    for field_name in boolean_fields:
        value = normalized.get(field_name)
        if value is not None and not isinstance(value, bool):
            msg = f"learning_assistance_policy.{field_name} must be a bool"
            raise ValueError(msg)
    integer_fields = (
        "max_terms_per_response",
        "max_task_restatements_per_stage",
        "max_observation_items",
        "max_clarification_questions",
    )
    for field_name in integer_fields:
        value = normalized.get(field_name)
        if value is None:
            continue
        if not isinstance(value, int) or value < 0:
            msg = f"learning_assistance_policy.{field_name} must be a non-negative int"
            raise ValueError(msg)
    if normalized.get("max_clarification_questions", 0) > 3:
        msg = "learning_assistance_policy.max_clarification_questions must stay within clarification cap 0..3"
        raise ValueError(msg)
    if normalized.get("max_terms_per_response", 0) > 2:
        msg = "learning_assistance_policy.max_terms_per_response must stay within low-token cap 0..2"
        raise ValueError(msg)
    for field_name in ("trigger_signals", "restatement_triggers", "bug_observation_checklist"):
        entries = normalized.get(field_name)
        if entries is None:
            continue
        if not isinstance(entries, list):
            msg = f"learning_assistance_policy.{field_name} must be a list"
            raise ValueError(msg)
        for index, entry in enumerate(entries):
            if not isinstance(entry, str) or not entry.strip():
                msg = f"learning_assistance_policy.{field_name}[{index}] must be a non-empty string"
                raise ValueError(msg)
    token_policy = normalized.get("token_budget_policy")
    if token_policy is not None:
        if not isinstance(token_policy, dict):
            msg = "learning_assistance_policy.token_budget_policy must be an object"
            raise ValueError(msg)
        for field_name in ("default_explanation_budget", "default_clarification_budget"):
            value = token_policy.get(field_name)
            if value is not None and (not isinstance(value, int) or value < 0):
                msg = f"learning_assistance_policy.token_budget_policy.{field_name} must be a non-negative int"
                raise ValueError(msg)
        compression_mode = token_policy.get("compression_mode")
        if compression_mode is not None and compression_mode not in {
            "stage_summary",
            "aggressive_compaction",
            "ref_only",
        }:
            msg = f"unsupported learning_assistance_policy.token_budget_policy.compression_mode: {compression_mode}"
            raise ValueError(msg)
    return normalized


def _normalize_workflow_governance_policy(value: object) -> dict:
    if value is None:
        return {}
    if not isinstance(value, dict):
        msg = "workflow_governance_policy must be an object"
        raise ValueError(msg)

    allowed_modes = {
        "direct_fix",
        "spec_first",
        "spec_plus_review",
        "worktree_isolated_execution",
        "parallel_subagent_assist",
        "maintenance_automation",
    }
    normalized = dict(value)

    default_mode = normalized.get("default_workflow_mode")
    if not isinstance(default_mode, str) or default_mode not in allowed_modes:
        msg = "workflow_governance_policy.default_workflow_mode must be a supported workflow mode"
        raise ValueError(msg)

    allowed_workflow_modes = normalized.get("allowed_workflow_modes")
    if not isinstance(allowed_workflow_modes, list) or not allowed_workflow_modes:
        msg = "workflow_governance_policy.allowed_workflow_modes must be a non-empty list"
        raise ValueError(msg)
    cleaned_modes: list[str] = []
    for index, mode in enumerate(allowed_workflow_modes):
        if not isinstance(mode, str) or mode not in allowed_modes:
            msg = f"workflow_governance_policy.allowed_workflow_modes[{index}] must be a supported workflow mode"
            raise ValueError(msg)
        if mode not in cleaned_modes:
            cleaned_modes.append(mode)
    if default_mode not in cleaned_modes:
        msg = "workflow_governance_policy.default_workflow_mode must exist in allowed_workflow_modes"
        raise ValueError(msg)
    normalized["allowed_workflow_modes"] = cleaned_modes

    overrides = normalized.get("workflow_mode_overrides_by_risk")
    if not isinstance(overrides, dict):
        msg = "workflow_governance_policy.workflow_mode_overrides_by_risk must be an object"
        raise ValueError(msg)
    normalized_overrides: dict[str, str] = {}
    for risk in ("low", "medium", "high"):
        mode = overrides.get(risk)
        if mode is None:
            continue
        if not isinstance(mode, str) or mode not in cleaned_modes:
            msg = f"workflow_governance_policy.workflow_mode_overrides_by_risk.{risk} must be one of allowed_workflow_modes"
            raise ValueError(msg)
        normalized_overrides[risk] = mode
    normalized["workflow_mode_overrides_by_risk"] = normalized_overrides

    for field_name in ("spec_artifact_requirements",):
        entries = normalized.get(field_name)
        if not isinstance(entries, list):
            msg = f"workflow_governance_policy.{field_name} must be a list"
            raise ValueError(msg)
        for index, entry in enumerate(entries):
            if not isinstance(entry, str) or not entry.strip():
                msg = f"workflow_governance_policy.{field_name}[{index}] must be a non-empty string"
                raise ValueError(msg)

    review_requirements = normalized.get("review_requirements")
    if not isinstance(review_requirements, dict):
        msg = "workflow_governance_policy.review_requirements must be an object"
        raise ValueError(msg)
    for key, review_value in review_requirements.items():
        if not isinstance(key, str) or not key.strip():
            msg = "workflow_governance_policy.review_requirements keys must be non-empty strings"
            raise ValueError(msg)
        if not isinstance(review_value, str) or not review_value.strip():
            msg = "workflow_governance_policy.review_requirements values must be non-empty strings"
            raise ValueError(msg)

    for field_name in ("worktree_policy", "subagent_policy", "automation_policy"):
        policy = normalized.get(field_name)
        if not isinstance(policy, dict):
            msg = f"workflow_governance_policy.{field_name} must be an object"
            raise ValueError(msg)
        allow = policy.get("allow")
        if not isinstance(allow, bool):
            msg = f"workflow_governance_policy.{field_name}.allow must be a bool"
            raise ValueError(msg)
        fallback_mode = policy.get("fallback_mode")
        if not isinstance(fallback_mode, str) or fallback_mode not in cleaned_modes:
            msg = f"workflow_governance_policy.{field_name}.fallback_mode must be one of allowed_workflow_modes"
            raise ValueError(msg)

    return normalized


def _validate_additional_gate_commands(value: object) -> None:
    if value is None:
        return
    if not isinstance(value, list):
        msg = "additional_gate_commands must be a list"
        raise ValueError(msg)
    allowed_profiles = {"quick", "full", "l1", "l2", "l3", "all", "*"}
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            msg = f"additional_gate_commands[{index}] must be an object"
            raise ValueError(msg)
        _required_string(item, "id")
        _required_string(item, "command")
        profiles = item.get("profiles")
        if profiles is None:
            continue
        if not isinstance(profiles, list):
            msg = f"additional_gate_commands[{index}].profiles must be a list"
            raise ValueError(msg)
        for profile in profiles:
            if not isinstance(profile, str) or not profile.strip():
                msg = f"additional_gate_commands[{index}].profiles entries must be non-empty strings"
                raise ValueError(msg)
            if profile.strip().lower() not in allowed_profiles:
                msg = f"unsupported additional_gate_commands[{index}].profiles value: {profile}"
                raise ValueError(msg)
