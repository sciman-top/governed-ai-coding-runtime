"""Attached target-repo write governance bridge."""

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path

from governed_ai_coding_runtime_contracts.approval import ApprovalLedger
from governed_ai_coding_runtime_contracts.file_guard import atomic_write_text, validate_file_component
from governed_ai_coding_runtime_contracts.policy_decision import PolicyDecision
from governed_ai_coding_runtime_contracts.repo_attachment import validate_light_pack
from governed_ai_coding_runtime_contracts.repo_profile import load_repo_profile
from governed_ai_coding_runtime_contracts.workspace import allocate_workspace
from governed_ai_coding_runtime_contracts.write_policy import resolve_write_policy
from governed_ai_coding_runtime_contracts.write_tool_runner import (
    WriteToolRequest,
    govern_write_request,
    policy_decision_from_write_denial,
    policy_decision_from_write_governance,
)


_APPROVALS_DIR = "approvals"


@dataclass(frozen=True, slots=True)
class AttachedWriteGovernanceResult:
    repo_id: str
    binding_id: str
    task_id: str
    target_path: str
    write_tier: str
    governance_status: str
    policy_decision: PolicyDecision
    approval_id: str | None = None
    task_state: str | None = None
    reason: str | None = None
    preflight_blocked: bool = False
    remediation_hint: str | None = None
    suggested_target_path: str | None = None
    allowed_write_scopes: tuple[str, ...] = ()


def govern_attached_write_request(
    *,
    attachment_root: str | Path,
    attachment_runtime_state_root: str | Path,
    task_id: str,
    tool_name: str,
    target_path: str,
    tier: str,
    rollback_reference: str,
    session_identity: dict | None = None,
) -> AttachedWriteGovernanceResult:
    attachment_root_path = Path(attachment_root)
    runtime_state_root_path = Path(attachment_runtime_state_root)
    attachment = validate_light_pack(
        target_repo_root=str(attachment_root_path),
        light_pack_path=str(attachment_root_path / ".governed-ai" / "light-pack.json"),
        runtime_state_root=str(runtime_state_root_path),
    )
    profile = load_repo_profile(attachment.repo_profile_path)
    write_policy = resolve_write_policy(profile)
    approval_ledger = ApprovalLedger()
    allocation = allocate_workspace(task_id, profile)

    write_allow_scopes = _write_allow_scopes(profile)
    try:
        governance = govern_write_request(
            WriteToolRequest(
                task_id=task_id,
                tool_name=tool_name,
                target_path=target_path,
                tier=tier,
                rollback_reference=rollback_reference,
            ),
            allocation,
            write_policy,
            approval_ledger,
        )
    except ValueError as exc:
        reason_text = str(exc)
        preflight_blocked = (
            "outside allowed scopes" in reason_text
            or "blocked by policy" in reason_text
            or "target_path must be a relative path" in reason_text
        )
        suggested_target_path = _suggest_target_path(write_allow_scopes)
        remediation_hint = None
        if preflight_blocked:
            if suggested_target_path:
                remediation_hint = (
                    f"choose a path within write_allow scopes ({', '.join(write_allow_scopes)}) "
                    f"for example: {suggested_target_path}"
                )
            else:
                remediation_hint = "choose a path within declared write_allow scopes"
        denied = policy_decision_from_write_denial(
            task_id=task_id,
            tool_name=tool_name,
            target_path=target_path,
            tier=tier,
            reason=reason_text,
        )
        return AttachedWriteGovernanceResult(
            repo_id=profile.repo_id,
            binding_id=attachment.binding.binding_id,
            task_id=task_id,
            target_path=target_path,
            write_tier=tier,
            governance_status="denied",
            policy_decision=denied,
            reason=reason_text,
            preflight_blocked=preflight_blocked,
            remediation_hint=remediation_hint,
            suggested_target_path=suggested_target_path,
            allowed_write_scopes=write_allow_scopes,
        )

    policy_decision = policy_decision_from_write_governance(governance)
    if governance.approval_id:
        _persist_approval_request(
            runtime_state_root=runtime_state_root_path,
            approval_id=governance.approval_id,
            task_id=task_id,
            tool_name=tool_name,
            target_path=target_path,
            tier=tier,
            reason=f"{tier} write requires approval for {target_path}",
            session_identity=session_identity,
        )
    return AttachedWriteGovernanceResult(
        repo_id=profile.repo_id,
        binding_id=attachment.binding.binding_id,
        task_id=task_id,
        target_path=target_path,
        write_tier=tier,
        governance_status=governance.status,
        policy_decision=policy_decision,
        approval_id=governance.approval_id,
        task_state=governance.task_state,
        preflight_blocked=False,
        remediation_hint=None,
        suggested_target_path=None,
        allowed_write_scopes=write_allow_scopes,
    )


def _write_allow_scopes(profile: object) -> tuple[str, ...]:
    path_policies = getattr(profile, "path_policies", None)
    if not isinstance(path_policies, dict):
        return ()
    write_allow = path_policies.get("write_allow")
    if not isinstance(write_allow, list):
        return ()
    normalized: list[str] = []
    for item in write_allow:
        if isinstance(item, str) and item.strip():
            normalized.append(item.strip())
    return tuple(normalized)


def _suggest_target_path(write_allow_scopes: tuple[str, ...]) -> str | None:
    for scope in write_allow_scopes:
        normalized = scope.replace("\\", "/").strip()
        if not normalized:
            continue
        if normalized.endswith("/**"):
            return f"{normalized[:-3]}/runtime-preflight-retry.txt"
        if normalized.endswith("/*"):
            return f"{normalized[:-2]}/runtime-preflight-retry.txt"
        if normalized == "**/*":
            return "docs/runtime-preflight-retry.txt"
        if "*" not in normalized and "?" not in normalized:
            return normalized.rstrip("/") + "/runtime-preflight-retry.txt"
    return "docs/runtime-preflight-retry.txt"


def _persist_approval_request(
    *,
    runtime_state_root: Path,
    approval_id: str,
    task_id: str,
    tool_name: str,
    target_path: str,
    tier: str,
    reason: str,
    session_identity: dict | None = None,
) -> None:
    approvals_root = runtime_state_root / _APPROVALS_DIR
    approvals_root.mkdir(parents=True, exist_ok=True)
    normalized_approval_id = validate_file_component(approval_id, "approval_id")
    record_path = approvals_root / f"{normalized_approval_id}.json"
    record = {
        "approval_id": normalized_approval_id,
        "task_id": task_id,
        "tool_name": tool_name,
        "target_path": target_path,
        "tier": tier,
        "reason": reason,
        "status": "pending",
        "decided_by": None,
        "requested_at": datetime.now(UTC).isoformat(),
        "decided_at": None,
    }
    if session_identity is not None:
        record["session_identity"] = session_identity
    atomic_write_text(record_path, json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
