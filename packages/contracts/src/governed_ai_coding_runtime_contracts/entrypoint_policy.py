"""Canonical runtime entrypoint policy helpers."""

from __future__ import annotations

from typing import Final


ENTRYPOINT_POLICY_MODES: Final[set[str]] = {
    "advisory",
    "targeted_enforced",
    "repo_wide_enforced",
}
DEFAULT_CANONICAL_ENTRYPOINTS: Final[list[str]] = [
    "runtime-flow",
    "runtime-flow-preset",
]
DEFAULT_ALLOWED_DIRECT_ENTRYPOINTS: Final[list[str]] = [
    "run-governed-task.status",
    "session-bridge.inspect_status",
    "session-bridge.inspect_evidence",
    "session-bridge.inspect_handoff",
    "verify-repo",
]
DEFAULT_TARGETED_ENFORCEMENT_SCOPES: Final[list[str]] = [
    "run_quick_gate",
    "run_full_gate",
    "verify_attachment",
    "govern_attachment_write",
    "write_request",
    "write_execute",
    "execute_attachment_write",
]
_READ_ONLY_SCOPES: Final[set[str]] = {
    "inspect_status",
    "inspect_evidence",
    "inspect_handoff",
    "status",
}


class EntrypointPolicyViolation(RuntimeError):
    """Raised when a required canonical entrypoint policy blocks a request."""

    def __init__(self, evaluation: dict) -> None:
        self.evaluation = dict(evaluation)
        super().__init__(str(self.evaluation.get("reason", "entrypoint policy blocked request")))


def default_required_entrypoint_policy() -> dict:
    return {
        "current_mode": "advisory",
        "target_mode": "repo_wide_enforced",
        "canonical_entrypoints": list(DEFAULT_CANONICAL_ENTRYPOINTS),
        "allow_direct_entrypoints": list(DEFAULT_ALLOWED_DIRECT_ENTRYPOINTS),
        "targeted_enforcement_scopes": list(DEFAULT_TARGETED_ENFORCEMENT_SCOPES),
    }


def normalize_required_entrypoint_policy(value: object) -> dict:
    policy = default_required_entrypoint_policy()
    if value is None:
        return policy
    if not isinstance(value, dict):
        msg = "required_entrypoint_policy must be an object"
        raise ValueError(msg)

    normalized = dict(policy)
    normalized["current_mode"] = _required_mode(
        value.get("current_mode", normalized["current_mode"]),
        "required_entrypoint_policy.current_mode",
    )
    normalized["target_mode"] = _required_mode(
        value.get("target_mode", normalized["target_mode"]),
        "required_entrypoint_policy.target_mode",
    )
    normalized["canonical_entrypoints"] = _required_string_list(
        value.get("canonical_entrypoints", normalized["canonical_entrypoints"]),
        "required_entrypoint_policy.canonical_entrypoints",
    )
    normalized["allow_direct_entrypoints"] = _required_string_list(
        value.get("allow_direct_entrypoints", normalized["allow_direct_entrypoints"]),
        "required_entrypoint_policy.allow_direct_entrypoints",
    )
    normalized["targeted_enforcement_scopes"] = _required_string_list(
        value.get("targeted_enforcement_scopes", normalized["targeted_enforcement_scopes"]),
        "required_entrypoint_policy.targeted_enforcement_scopes",
    )
    promotion_condition_ref = value.get("promotion_condition_ref")
    if promotion_condition_ref is not None:
        normalized["promotion_condition_ref"] = _required_string(
            promotion_condition_ref,
            "required_entrypoint_policy.promotion_condition_ref",
        )
    return normalized


def evaluate_required_entrypoint_policy(
    policy_value: object,
    *,
    entrypoint_id: str,
    scope: str,
) -> dict:
    policy = normalize_required_entrypoint_policy(policy_value)
    normalized_entrypoint_id = _required_string(entrypoint_id, "entrypoint_id")
    normalized_scope = _required_string(scope, "scope")
    canonical_entrypoints = set(policy["canonical_entrypoints"])
    allowed_direct_entrypoints = set(policy["allow_direct_entrypoints"])
    targeted_scopes = set(policy["targeted_enforcement_scopes"])
    current_mode = policy["current_mode"]
    is_canonical = normalized_entrypoint_id in canonical_entrypoints
    is_allowed_direct = normalized_entrypoint_id in allowed_direct_entrypoints
    drift_detected = not is_canonical
    blocked = False
    reason = None
    remediation_hint = None

    if current_mode == "targeted_enforced":
        if (normalized_scope in targeted_scopes) and (not is_canonical) and (not is_allowed_direct):
            blocked = True
    elif current_mode == "repo_wide_enforced":
        if (normalized_scope not in _READ_ONLY_SCOPES) and (not is_canonical) and (not is_allowed_direct):
            blocked = True

    if blocked:
        reason = (
            f"required canonical entrypoint policy blocks scope '{normalized_scope}' from "
            f"entrypoint '{normalized_entrypoint_id}' in mode '{current_mode}'"
        )
        remediation_hint = _remediation_hint(policy)

    return {
        "current_mode": current_mode,
        "target_mode": policy["target_mode"],
        "entrypoint_id": normalized_entrypoint_id,
        "scope": normalized_scope,
        "canonical_entrypoints": list(policy["canonical_entrypoints"]),
        "allow_direct_entrypoints": list(policy["allow_direct_entrypoints"]),
        "targeted_enforcement_scopes": list(policy["targeted_enforcement_scopes"]),
        "is_canonical": is_canonical,
        "is_allowed_direct": is_allowed_direct,
        "drift_detected": drift_detected,
        "blocked": blocked,
        "reason": reason,
        "remediation_hint": remediation_hint,
    }


def enforce_required_entrypoint_policy(
    policy_value: object,
    *,
    entrypoint_id: str,
    scope: str,
) -> dict:
    evaluation = evaluate_required_entrypoint_policy(
        policy_value,
        entrypoint_id=entrypoint_id,
        scope=scope,
    )
    if evaluation["blocked"]:
        raise EntrypointPolicyViolation(evaluation)
    return evaluation


def _remediation_hint(policy: dict) -> str:
    canonical = [item for item in policy["canonical_entrypoints"] if isinstance(item, str)]
    if canonical:
        joined = ", ".join(canonical)
        return f"rerun through a canonical governed entrypoint: {joined}"
    return "rerun through the canonical governed runtime flow"


def _required_mode(value: object, field_name: str) -> str:
    normalized = _required_string(value, field_name)
    if normalized not in ENTRYPOINT_POLICY_MODES:
        msg = f"unsupported {field_name}: {value}"
        raise ValueError(msg)
    return normalized


def _required_string_list(value: object, field_name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        msg = f"{field_name} must be a non-empty list"
        raise ValueError(msg)
    return [_required_string(item, field_name) for item in value]


def _required_string(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()
