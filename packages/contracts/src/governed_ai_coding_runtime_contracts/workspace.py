"""Isolated workspace allocation primitives."""

from dataclasses import dataclass
from pathlib import PurePosixPath
import re
from typing import Any


_WORKSPACE_PREFIX = ".governed-workspaces"
_SAFE_SEGMENT = re.compile(r"[^A-Za-z0-9._-]+")


@dataclass(frozen=True, slots=True)
class WorkspaceAllocation:
    task_id: str
    repo_id: str
    run_id: str
    attempt_id: str
    workspace_root: str
    path_policies: dict


def allocate_workspace(
    task_id: str,
    repo_profile: Any,
    workspace_root: str | None = None,
    *,
    run_id: str | None = None,
    attempt_id: str | None = None,
) -> WorkspaceAllocation:
    normalized_task_id = _safe_segment(_required_string(task_id, "task_id"))
    repo_id = _required_string(getattr(repo_profile, "repo_id", ""), "repo_id")
    path_policies = getattr(repo_profile, "path_policies", None)
    if not isinstance(path_policies, dict):
        msg = "repo_profile.path_policies is required"
        raise ValueError(msg)
    normalized_run_id = _safe_segment(run_id or f"{normalized_task_id}-run")
    normalized_attempt_id = _safe_segment(attempt_id or f"{normalized_task_id}-attempt-1")

    root = workspace_root or f"{_WORKSPACE_PREFIX}/{repo_id}/{normalized_task_id}/{normalized_run_id}"
    normalized_root = _normalize_workspace_root(root)
    return WorkspaceAllocation(
        task_id=task_id,
        repo_id=repo_id,
        run_id=normalized_run_id,
        attempt_id=normalized_attempt_id,
        workspace_root=normalized_root,
        path_policies=path_policies,
    )


def validate_write_path(allocation: WorkspaceAllocation, target_path: str) -> bool:
    path = _normalize_relative_path(target_path)
    for pattern in allocation.path_policies.get("blocked", []):
        if _matches(path, pattern):
            msg = f"write path is blocked by policy: {target_path}"
            raise ValueError(msg)
    for pattern in allocation.path_policies.get("write_allow", []):
        if _matches(path, pattern):
            return True
    msg = f"write path is outside allowed scopes: {target_path}"
    raise ValueError(msg)


def _normalize_workspace_root(workspace_root: str) -> str:
    root = workspace_root.replace("\\", "/").strip()
    if not root:
        msg = "workspace_root is required"
        raise ValueError(msg)
    if ":" in root or root.startswith("/") or ".." in PurePosixPath(root).parts:
        msg = "workspace_root must be an isolated relative workspace path"
        raise ValueError(msg)
    if not (root == _WORKSPACE_PREFIX or root.startswith(f"{_WORKSPACE_PREFIX}/")):
        msg = f"workspace_root must be under {_WORKSPACE_PREFIX}"
        raise ValueError(msg)
    return root


def _normalize_relative_path(target_path: str) -> PurePosixPath:
    raw_path = _required_string(target_path, "target_path").replace("\\", "/").lstrip("/")
    path = PurePosixPath(raw_path)
    if path.is_absolute() or ".." in path.parts or ":" in raw_path:
        msg = f"target_path must be a relative path: {target_path}"
        raise ValueError(msg)
    return path


def _matches(path: PurePosixPath, pattern: str) -> bool:
    normalized_pattern = pattern.replace("\\", "/")
    return path.match(normalized_pattern)


def _required_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()


def _safe_segment(value: str) -> str:
    return _SAFE_SEGMENT.sub("-", value).strip("-") or "task"
