"""Read-only governed tool request validation."""

from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Any

_READONLY_SIDE_EFFECTS = {"none", "filesystem_read", "network_read"}


@dataclass(slots=True)
class ToolRequest:
    tool_name: str
    side_effect_class: str
    target_path: str


@dataclass(slots=True)
class ReadOnlySessionSummary:
    repo_id: str
    accepted_count: int
    tool_names: list[str]


def validate_readonly_request(request: ToolRequest, repo_profile: Any) -> bool:
    if request.tool_name not in repo_profile.raw.get("tool_allowlist", []):
        msg = f"tool is not allowlisted: {request.tool_name}"
        raise ValueError(msg)
    if request.side_effect_class not in _READONLY_SIDE_EFFECTS:
        msg = f"side effect is not read-only: {request.side_effect_class}"
        raise ValueError(msg)
    if not _is_allowed_path(request.target_path, repo_profile.path_policies):
        msg = f"path is outside read scope: {request.target_path}"
        raise ValueError(msg)
    return True


def run_readonly_session(
    requests: list[ToolRequest],
    repo_profile: Any,
) -> ReadOnlySessionSummary:
    for request in requests:
        validate_readonly_request(request, repo_profile)
    return ReadOnlySessionSummary(
        repo_id=repo_profile.repo_id,
        accepted_count=len(requests),
        tool_names=[request.tool_name for request in requests],
    )


def _is_allowed_path(target_path: str, path_policies: dict) -> bool:
    normalized = target_path.replace("\\", "/").lstrip("/")
    path = PurePosixPath(normalized)

    for blocked in path_policies.get("blocked", []):
        if path.match(blocked):
            return False

    return any(path.match(pattern) for pattern in path_policies.get("read_allow", []))
