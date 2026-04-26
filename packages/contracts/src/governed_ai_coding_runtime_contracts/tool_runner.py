"""Read-only and contained governed tool request validation."""

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
_REQUIRED_EXECUTABLE_TOOL_FAMILIES = {
    "file_write",
    "shell",
    "git",
    "package_manager",
    "browser_automation",
    "mcp_tool_bridge",
}
_VALID_ENVIRONMENT_POLICIES = {"minimal", "sanitized_inherited", "repo_profile_declared"}
_VALID_NETWORK_POSTURES = {"deny", "read_only", "declared_by_tool", "allowlist_required"}
_VALID_APPROVAL_CLASSES = {"auto_execute", "auto_if_reversible", "explicit_user_approval", "deny"}
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
    containment_profile: "ContainmentProfile | None" = None
    rollback_refs: list[str] | None = None


@dataclass(frozen=True, slots=True)
class ContainmentProfile:
    tool_family: str
    workspace_root: str
    allowed_path_roots: list[str]
    environment_policy: str
    network_posture: str
    timeout_seconds: float | None
    approval_class: str
    evidence_refs: list[str]
    rollback_refs: list[str]
    waiver_ref: str | None = None


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


def govern_contained_execution_request(
    *,
    tool_name: str,
    command: str,
    tier: str,
    rollback_reference: str,
    containment_profile: ContainmentProfile | None,
) -> ToolGovernanceDecision:
    normalized_tool = _required_string(tool_name, "tool_name").lower()
    expected_family = resolve_execution_tool_family(normalized_tool)
    if expected_family is None:
        return ToolGovernanceDecision(
            status="deny",
            reason=f"unclassified executable tool family: {normalized_tool}",
            requires_approval=False,
        )
    if containment_profile is None:
        return ToolGovernanceDecision(
            status="deny",
            reason=f"missing containment profile for {expected_family}",
            requires_approval=False,
        )
    try:
        validate_containment_profile(containment_profile)
    except ValueError as exc:
        return ToolGovernanceDecision(
            status="deny",
            reason=f"invalid containment profile: {exc}",
            requires_approval=False,
        )
    if containment_profile.tool_family != expected_family:
        return ToolGovernanceDecision(
            status="deny",
            reason=f"containment profile family mismatch: expected {expected_family}",
            requires_approval=False,
        )
    if containment_profile.approval_class == "deny":
        return ToolGovernanceDecision(
            status="deny",
            reason=f"containment profile denies {expected_family}",
            requires_approval=False,
        )
    if expected_family not in {"shell", "git", "package_manager"}:
        return ToolGovernanceDecision(
            status="deny",
            reason=f"execution family is declared but not currently executable: {expected_family}",
            requires_approval=False,
        )

    bounded_tool = "package" if expected_family == "package_manager" else expected_family
    decision = govern_execution_request(
        tool_name=bounded_tool,
        command=command,
        tier=tier,
        rollback_reference=rollback_reference,
    )
    decision.containment_profile = containment_profile
    decision.rollback_refs = list(containment_profile.rollback_refs)
    return decision


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


def build_containment_profile(
    *,
    tool_family: str,
    workspace_root: str,
    allowed_path_roots: list[str],
    environment_policy: str,
    network_posture: str,
    timeout_seconds: object,
    approval_class: str,
    evidence_refs: list[str],
    rollback_refs: list[str],
    waiver_ref: str | None = None,
) -> ContainmentProfile:
    profile = ContainmentProfile(
        tool_family=_required_string(tool_family, "tool_family").lower(),
        workspace_root=_required_string(workspace_root, "workspace_root"),
        allowed_path_roots=list(allowed_path_roots),
        environment_policy=_required_string(environment_policy, "environment_policy"),
        network_posture=_required_string(network_posture, "network_posture"),
        timeout_seconds=_optional_positive_number(timeout_seconds, "timeout_seconds"),
        approval_class=_required_string(approval_class, "approval_class"),
        evidence_refs=list(evidence_refs),
        rollback_refs=list(rollback_refs),
        waiver_ref=waiver_ref.strip() if isinstance(waiver_ref, str) and waiver_ref.strip() else None,
    )
    validate_containment_profile(profile)
    return profile


def validate_containment_profile(profile: ContainmentProfile) -> bool:
    if not isinstance(profile, ContainmentProfile):
        raise ValueError("profile must be a ContainmentProfile")
    if profile.tool_family not in _REQUIRED_EXECUTABLE_TOOL_FAMILIES:
        raise ValueError(f"unsupported tool_family: {profile.tool_family}")
    _required_string(profile.workspace_root, "workspace_root")
    _require_non_empty_string_list(profile.allowed_path_roots, "allowed_path_roots")
    _reject_path_traversal_roots(profile.allowed_path_roots, "allowed_path_roots")
    if profile.environment_policy not in _VALID_ENVIRONMENT_POLICIES:
        raise ValueError(f"unsupported environment_policy: {profile.environment_policy}")
    if profile.network_posture not in _VALID_NETWORK_POSTURES:
        raise ValueError(f"unsupported network_posture: {profile.network_posture}")
    if profile.approval_class not in _VALID_APPROVAL_CLASSES:
        raise ValueError(f"unsupported approval_class: {profile.approval_class}")
    _require_non_empty_string_list(profile.evidence_refs, "evidence_refs")
    _require_non_empty_string_list(profile.rollback_refs, "rollback_refs")
    if profile.timeout_seconds is not None:
        _optional_positive_number(profile.timeout_seconds, "timeout_seconds")
    return True


def validate_containment_registry(profiles: list[ContainmentProfile]) -> bool:
    declared = set()
    for profile in profiles:
        validate_containment_profile(profile)
        declared.add(profile.tool_family)
    missing = sorted(_REQUIRED_EXECUTABLE_TOOL_FAMILIES - declared)
    if missing:
        raise ValueError(f"missing containment profiles: {', '.join(missing)}")
    return True


def resolve_execution_tool_family(tool_name: str) -> str | None:
    normalized = _required_string(tool_name, "tool_name").lower()
    if normalized in {"apply_patch", "write_file", "file_write"}:
        return "file_write"
    if normalized in {"shell", "powershell", "pwsh", "cmd", "bash"}:
        return "shell"
    if normalized == "git":
        return "git"
    if normalized in {"package", "package_manager", "pip", "uv", "npm"}:
        return "package_manager"
    if normalized in {"browser", "playwright", "browser_automation"}:
        return "browser_automation"
    if normalized in {"mcp", "mcp_tool", "mcp_tool_bridge"}:
        return "mcp_tool_bridge"
    return None


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


def _optional_positive_number(value: object, field_name: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a positive number")
    if isinstance(value, (int, float)):
        numeric = float(value)
    elif isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        try:
            numeric = float(raw)
        except ValueError as exc:
            raise ValueError(f"{field_name} must be a positive number") from exc
    else:
        raise ValueError(f"{field_name} must be a positive number")
    if numeric <= 0:
        raise ValueError(f"{field_name} must be a positive number")
    return numeric


def _require_non_empty_string_list(values: object, field_name: str) -> None:
    if not isinstance(values, list) or not values:
        raise ValueError(f"{field_name} must be a non-empty list")
    for index, value in enumerate(values):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name}[{index}] must be a non-empty string")


def _reject_path_traversal_roots(values: list[str], field_name: str) -> None:
    for index, value in enumerate(values):
        path = PurePosixPath(value.replace("\\", "/"))
        if ".." in path.parts:
            raise ValueError(f"{field_name}[{index}] must not contain path traversal")
