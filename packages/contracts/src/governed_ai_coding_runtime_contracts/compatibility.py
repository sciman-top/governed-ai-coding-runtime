"""Compatibility posture helpers for rollout-aware runtime decisions."""

from dataclasses import dataclass
from typing import Literal


RequestedPosture = Literal["observe", "advisory", "enforced"]
SupportLevel = Literal["full_support", "partial_support", "unsupported"]
EffectivePosture = Literal["observe", "advisory", "enforced", "blocked"]

_POSTURE_ORDER = {"observe": 0, "advisory": 1, "enforced": 2}


@dataclass(frozen=True, slots=True)
class RuntimePostureResolution:
    requested_posture: RequestedPosture
    effective_posture: EffectivePosture
    support_level: SupportLevel
    degrade_reason: str


def resolve_runtime_posture(
    *,
    requested_posture: RequestedPosture,
    repo_supported_postures: list[RequestedPosture],
    compatibility_signals: list[dict],
) -> RuntimePostureResolution:
    support_level: SupportLevel = "full_support"
    effective_posture: EffectivePosture = requested_posture
    degrade_reason = ""

    if requested_posture not in repo_supported_postures:
        effective_posture = _highest_supported_posture(repo_supported_postures)
        support_level = "partial_support"
        degrade_reason = "requested posture exceeds repo-supported posture"

    for signal in compatibility_signals:
        signal_status = signal.get("status")
        if signal_status == "unsupported":
            support_level = "unsupported"
            degrade_reason = str(signal.get("reason", "unsupported capability"))
            if signal.get("degrade_to") == "fail_closed":
                effective_posture = "blocked"
            else:
                effective_posture = _coerce_posture(signal.get("degrade_to"), fallback="observe")
            break
        if signal_status == "partial_support":
            support_level = "partial_support"
            degrade_reason = str(signal.get("reason", "partial support requires degrade behavior"))
            effective_posture = _coerce_posture(signal.get("degrade_to"), fallback="advisory")

    if effective_posture != "blocked" and effective_posture in _POSTURE_ORDER:
        highest_supported = _highest_supported_posture(repo_supported_postures)
        if _POSTURE_ORDER[effective_posture] > _POSTURE_ORDER[highest_supported]:
            effective_posture = highest_supported
            if support_level == "full_support":
                support_level = "partial_support"
            if not degrade_reason:
                degrade_reason = "requested posture exceeds repo-supported posture"

    if support_level == "full_support":
        degrade_reason = ""

    return RuntimePostureResolution(
        requested_posture=requested_posture,
        effective_posture=effective_posture,
        support_level=support_level,
        degrade_reason=degrade_reason,
    )


def _highest_supported_posture(repo_supported_postures: list[RequestedPosture]) -> RequestedPosture:
    return max(repo_supported_postures, key=lambda item: _POSTURE_ORDER[item])


def _coerce_posture(value: object, *, fallback: RequestedPosture) -> EffectivePosture:
    if value in ("observe", "advisory", "enforced", "blocked"):
        return value
    return fallback
