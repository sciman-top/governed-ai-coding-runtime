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
        normalized_raw = dict(raw)
        normalized_raw["required_entrypoint_policy"] = required_entrypoint_policy
        return cls(
            repo_id=repo_id,
            primary_language=primary_language,
            path_policies=path_policies,
            rollout_posture=rollout_posture,
            compatibility_signals=compatibility_signals,
            required_entrypoint_policy=required_entrypoint_policy,
            interaction_profile=interaction_profile,
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
