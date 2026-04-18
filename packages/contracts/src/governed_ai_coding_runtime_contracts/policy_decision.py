"""Stable policy decision contract for governed execution-like actions."""

from dataclasses import dataclass
from typing import Literal


DecisionStatus = Literal["allow", "escalate", "deny"]
RiskTier = Literal["low", "medium", "high"]
DEFAULT_SCHEMA_VERSION = "1.0"

_VALID_STATUSES = {"allow", "escalate", "deny"}
_VALID_RISK_TIERS = {"low", "medium", "high"}


@dataclass(frozen=True, slots=True)
class PolicyDecision:
    schema_version: str
    task_id: str
    action_id: str
    risk_tier: RiskTier
    subject: str
    status: DecisionStatus
    decision_basis: list[str]
    evidence_ref: str
    required_approval_ref: str | None = None
    remediation_hint: str | None = None


def build_policy_decision(
    *,
    schema_version: str = DEFAULT_SCHEMA_VERSION,
    task_id: str,
    action_id: str,
    risk_tier: RiskTier,
    subject: str,
    status: DecisionStatus,
    decision_basis: list[str],
    evidence_ref: str,
    required_approval_ref: str | None = None,
    remediation_hint: str | None = None,
) -> PolicyDecision:
    normalized_status = _required_enum(status, "status", _VALID_STATUSES)
    normalized_risk_tier = _required_enum(risk_tier, "risk_tier", _VALID_RISK_TIERS)
    normalized_approval_ref = _optional_string(required_approval_ref, "required_approval_ref")
    normalized_remediation_hint = _optional_string(remediation_hint, "remediation_hint")

    if normalized_status == "allow" and normalized_approval_ref is not None:
        msg = "allow decisions may not require approval"
        raise ValueError(msg)
    if normalized_status == "escalate" and normalized_approval_ref is None:
        msg = "escalate decisions require required_approval_ref"
        raise ValueError(msg)
    if normalized_status == "deny":
        if normalized_approval_ref is not None:
            msg = "deny decisions may not carry approval intent"
            raise ValueError(msg)
        if normalized_remediation_hint is None:
            msg = "deny decisions require remediation_hint"
            raise ValueError(msg)

    return PolicyDecision(
        schema_version=_required_string(schema_version, "schema_version"),
        task_id=_required_string(task_id, "task_id"),
        action_id=_required_string(action_id, "action_id"),
        risk_tier=normalized_risk_tier,
        subject=_required_string(subject, "subject"),
        status=normalized_status,
        decision_basis=_required_basis(decision_basis),
        evidence_ref=_required_string(evidence_ref, "evidence_ref"),
        required_approval_ref=normalized_approval_ref,
        remediation_hint=normalized_remediation_hint,
    )


def is_executable_action(decision: PolicyDecision) -> bool:
    return decision.status == "allow"


def _required_basis(decision_basis: list[str]) -> list[str]:
    if not isinstance(decision_basis, list):
        msg = "decision_basis is required"
        raise ValueError(msg)
    normalized = [_required_string(item, "decision_basis entry") for item in decision_basis]
    if not normalized:
        msg = "decision_basis is required"
        raise ValueError(msg)
    return normalized


def _required_enum(value: str, field_name: str, valid_values: set[str]) -> str:
    normalized = _required_string(value, field_name).lower()
    if normalized not in valid_values:
        msg = f"unsupported {field_name}: {value}"
        raise ValueError(msg)
    return normalized


def _required_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()


def _optional_string(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} must be a non-empty string when provided"
        raise ValueError(msg)
    return value.strip()
