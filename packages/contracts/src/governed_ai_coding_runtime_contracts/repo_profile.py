"""Repository profile domain model placeholders for TDD."""

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass(slots=True)
class RepoProfile:
    repo_id: str
    primary_language: str
    path_policies: dict
    raw: dict

    @classmethod
    def from_dict(cls, raw: dict) -> "RepoProfile":
        repo_id = _required_string(raw, "repo_id")
        primary_language = _required_string(raw, "primary_language")
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
        return cls(repo_id=repo_id, primary_language=primary_language, path_policies=path_policies, raw=raw)

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
