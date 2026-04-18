"""Maintenance policy read model for runtime-facing operator surfaces."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class MaintenancePolicyStatus:
    stage: str
    compatibility_policy_ref: str | None
    upgrade_policy_ref: str | None
    triage_policy_ref: str | None
    deprecation_policy_ref: str | None
    retirement_policy_ref: str | None


def load_maintenance_policy_status(repo_root: Path) -> MaintenancePolicyStatus:
    compatibility_policy = _relative_if_exists(
        repo_root,
        repo_root / "docs" / "product" / "runtime-compatibility-and-upgrade-policy.md",
    )
    maintenance_policy = _relative_if_exists(
        repo_root,
        repo_root / "docs" / "product" / "maintenance-deprecation-and-retirement-policy.md",
    )

    stage = "completed" if compatibility_policy and maintenance_policy else "missing"
    return MaintenancePolicyStatus(
        stage=stage,
        compatibility_policy_ref=compatibility_policy,
        upgrade_policy_ref=compatibility_policy,
        triage_policy_ref=maintenance_policy,
        deprecation_policy_ref=maintenance_policy,
        retirement_policy_ref=maintenance_policy,
    )


def _relative_if_exists(repo_root: Path, path: Path) -> str | None:
    if not path.exists():
        return None
    return path.relative_to(repo_root).as_posix()
