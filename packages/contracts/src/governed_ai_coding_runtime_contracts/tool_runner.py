"""Read-only governed tool request validation."""

from dataclasses import dataclass
import fnmatch
from pathlib import PurePosixPath
from typing import Any

from governed_ai_coding_runtime_contracts.subprocess_guard import (
    resolve_timeout_policy,
    run_subprocess,
)

_READONLY_SIDE_EFFECTS = {"none", "filesystem_read", "network_read"}
_SUPPORTED_GOVERNED_TOOLS = {"shell", "git", "package"}
_PACKAGE_DRY_RUN_HINTS = ("--dry-run", "--dryrun", "list", "check")
_DENY_TOKEN_HINTS = ("rm ", "del ", "format ", "push", "commit", "publish", "install ")


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


@dataclass(slots=True)
class ToolGovernanceDecision:
    status: str
    reason: str
    requires_approval: bool


@dataclass(slots=True)
class ToolExecutionResult:
    exit_code: int
    output: str
    timed_out: bool = False
    timeout_seconds: float | None = None
    timeout_exempt: bool = False


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


def govern_execution_request(
    *,
    tool_name: str,
    command: str,
    tier: str,
    rollback_reference: str,
) -> ToolGovernanceDecision:
    normalized_tool = _required_string(tool_name, "tool_name").lower()
    normalized_command = _required_string(command, "command")
    normalized_tier = _required_string(tier, "tier").lower()
    if normalized_tool not in _SUPPORTED_GOVERNED_TOOLS:
        return ToolGovernanceDecision(
            status="deny",
            reason=f"unsupported governed tool: {normalized_tool}",
            requires_approval=False,
        )
    if normalized_tier not in {"low", "medium", "high"}:
        return ToolGovernanceDecision(
            status="deny",
            reason=f"unsupported tool execution tier: {normalized_tier}",
            requires_approval=False,
        )
    if normalized_tier in {"medium", "high"} and not rollback_reference.strip():
        return ToolGovernanceDecision(
            status="deny",
            reason="medium and high tier tool execution requires rollback_reference",
            requires_approval=False,
        )

    bounded, reason = _is_bounded_command(normalized_tool, normalized_command)
    if not bounded:
        return ToolGovernanceDecision(status="deny", reason=reason, requires_approval=False)

    if normalized_tier in {"medium", "high"}:
        return ToolGovernanceDecision(status="escalate", reason="approval required", requires_approval=True)
    return ToolGovernanceDecision(status="allow", reason="bounded low-risk execution", requires_approval=False)


def execute_governed_command(
    *,
    command: str,
    cwd: str | None = None,
    timeout_seconds: object = None,
    timeout_exempt: bool = False,
    timeout_exempt_allowlist: list[str] | None = None,
) -> ToolExecutionResult:
    normalized_command = _required_string(command, "command")
    timeout_policy = resolve_timeout_policy(
        command_text=normalized_command,
        timeout_seconds=timeout_seconds,
        timeout_exempt=timeout_exempt,
        allowlist_patterns=timeout_exempt_allowlist,
    )
    completed = run_subprocess(
        command=normalized_command,
        shell=True,
        cwd=cwd,
        timeout_seconds=timeout_policy.timeout_seconds,
    )
    output = "\n".join(part for part in [completed.stdout, completed.stderr] if part).strip()
    return ToolExecutionResult(
        exit_code=completed.returncode,
        output=output,
        timed_out=completed.timed_out,
        timeout_seconds=timeout_policy.timeout_seconds,
        timeout_exempt=timeout_policy.timeout_exempt,
    )


def _is_allowed_path(target_path: str, path_policies: dict) -> bool:
    normalized = target_path.replace("\\", "/").lstrip("/")
    path = PurePosixPath(normalized)
    if ".." in path.parts:
        return False
    path_text = path.as_posix()

    for blocked in path_policies.get("blocked", []):
        if fnmatch.fnmatch(path_text, blocked.replace("\\", "/")):
            return False

    return any(fnmatch.fnmatch(path_text, pattern.replace("\\", "/")) for pattern in path_policies.get("read_allow", []))


def _is_bounded_command(tool_name: str, command: str) -> tuple[bool, str]:
    normalized = command.strip().lower()
    if any(token in normalized for token in _DENY_TOKEN_HINTS):
        return False, "command contains prohibited mutation token"
    if tool_name == "git":
        if normalized.startswith("git status") or normalized.startswith("git diff") or normalized.startswith("git log"):
            return True, "bounded git read command"
        return False, "git execution is limited to status/diff/log"
    if tool_name == "package":
        if any(hint in normalized for hint in _PACKAGE_DRY_RUN_HINTS):
            return True, "bounded package dry-run command"
        return False, "package execution must be dry-run or list/check only"
    if tool_name == "shell":
        if normalized.startswith("git status") or normalized.startswith("git diff"):
            return True, "bounded shell command mapped to git read flow"
        if "pip list" in normalized or "pip check" in normalized:
            return True, "bounded shell command mapped to package dry-run flow"
        return False, "shell execution is bounded to git status/diff and package list/check"
    return False, "unsupported governed tool"


def _required_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()
