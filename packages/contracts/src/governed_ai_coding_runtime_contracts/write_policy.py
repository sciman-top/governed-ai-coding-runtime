"""Write risk policy defaults resolved from repo profiles."""

from dataclasses import dataclass
from typing import Any


_VALID_TIERS = {"low", "medium", "high"}


@dataclass(frozen=True, slots=True)
class WritePolicy:
    default_write_tier: str
    medium_requires_approval: bool
    high_requires_explicit_approval: bool

    def requires_approval(self, tier: str) -> bool:
        normalized_tier = _normalize_tier(tier)
        if normalized_tier == "low":
            return False
        if normalized_tier == "medium":
            return self.medium_requires_approval
        return True

    def approval_mode(self, tier: str) -> str:
        normalized_tier = _normalize_tier(tier)
        if normalized_tier == "low":
            return "auto"
        if normalized_tier == "medium":
            return "approval" if self.medium_requires_approval else "auto"
        if self.high_requires_explicit_approval:
            return "explicit"
        msg = "high-tier writes must require explicit approval"
        raise ValueError(msg)


def resolve_write_policy(repo_profile: Any) -> WritePolicy:
    raw = getattr(repo_profile, "raw", None)
    if not isinstance(raw, dict):
        msg = "repo_profile.raw is required"
        raise ValueError(msg)
    risk_defaults = raw.get("risk_defaults", {})
    approval_defaults = raw.get("approval_defaults", {})
    default_write_tier = _normalize_tier(risk_defaults.get("default_write_tier", "medium"))
    high_requires_explicit_approval = approval_defaults.get("high_requires_explicit_approval", True)
    if high_requires_explicit_approval is not True:
        msg = "high_requires_explicit_approval must be true"
        raise ValueError(msg)
    return WritePolicy(
        default_write_tier=default_write_tier,
        medium_requires_approval=approval_defaults.get("medium_write_requires_approval", True) is True,
        high_requires_explicit_approval=True,
    )


def _normalize_tier(tier: str) -> str:
    if not isinstance(tier, str):
        msg = "write tier must be a string"
        raise ValueError(msg)
    normalized = tier.strip().lower()
    if normalized not in _VALID_TIERS:
        msg = f"unsupported write tier: {tier}"
        raise ValueError(msg)
    return normalized
