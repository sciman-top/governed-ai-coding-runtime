"""Repository profile domain model placeholders for TDD."""

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(slots=True)
class RepoProfile:
    repo_id: str
    primary_language: str
    path_policies: dict
    rollout_posture: dict
    compatibility_signals: list[dict]
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
        compatibility_signals = raw.get("compatibility_signals", [])
        if not isinstance(compatibility_signals, list):
            msg = "compatibility_signals must be a list"
            raise ValueError(msg)
        interaction_profile = _normalize_interaction_profile(raw.get("interaction_profile", {}))
        return cls(
            repo_id=repo_id,
            primary_language=primary_language,
            path_policies=path_policies,
            rollout_posture=rollout_posture,
            compatibility_signals=compatibility_signals,
            interaction_profile=interaction_profile,
            raw=raw,
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
