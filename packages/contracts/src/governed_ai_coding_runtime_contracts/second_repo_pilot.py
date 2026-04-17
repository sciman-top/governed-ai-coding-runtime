"""Second-repo reuse pilot contract primitives."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from governed_ai_coding_runtime_contracts.repo_profile import load_repo_profile


CompatibilityStatus = Literal["compatible", "compatible_with_gaps", "incompatible"]

_KERNEL_REQUIRED_KEYS = {
    "approval_defaults",
    "branch_policy",
    "delivery_format",
    "path_policies",
    "risk_defaults",
    "tool_allowlist",
}


@dataclass(frozen=True, slots=True)
class SecondRepoPilotResult:
    primary_repo_id: str
    second_repo_id: str
    same_kernel_semantics: bool
    kernel_fork_required: bool
    profile_differences: list[str]


@dataclass(frozen=True, slots=True)
class AdapterCompatibilityResult:
    adapter_id: str
    compatibility_status: CompatibilityStatus
    gaps: list[str]


def run_second_repo_reuse_pilot(
    primary_profile_path: str | Path,
    second_profile_path: str | Path,
) -> SecondRepoPilotResult:
    primary = load_repo_profile(primary_profile_path)
    second = load_repo_profile(second_profile_path)
    primary_keys = set(primary.raw)
    second_keys = set(second.raw)
    same_kernel_semantics = _KERNEL_REQUIRED_KEYS.issubset(primary_keys) and _KERNEL_REQUIRED_KEYS.issubset(second_keys)
    profile_differences = [
        key
        for key in sorted(primary_keys | second_keys)
        if primary.raw.get(key) != second.raw.get(key)
    ]
    kernel_only_differences = {"task_lifecycle", "verification_order", "approval_state_machine"}
    kernel_fork_required = any(key in kernel_only_differences for key in profile_differences)
    return SecondRepoPilotResult(
        primary_repo_id=primary.repo_id,
        second_repo_id=second.repo_id,
        same_kernel_semantics=same_kernel_semantics,
        kernel_fork_required=kernel_fork_required,
        profile_differences=profile_differences,
    )


def generic_process_adapter_declaration() -> dict:
    return {
        "adapter_id": "generic.process.cli",
        "display_name": "Generic Process CLI",
        "product_family": "generic_process",
        "lifecycle_status": "experimental",
        "invocation_mode": "non_interactive_cli",
        "auth_ownership": "unsupported",
        "workspace_control": "external_workspace",
        "event_visibility": "logs_only",
        "mutation_model": "git_diff",
        "continuation_model": "stateless",
        "evidence_model": "command_log",
        "supported_governance_modes": ["observe_only", "advisory"],
        "minimum_required_runtime_controls": [
            "task_intake",
            "repo_profile_resolution",
            "verification_runner",
            "delivery_handoff",
        ],
        "unsupported_capability_behavior": "degrade_to_advisory",
        "compatibility_notes": "Generic process agents need stricter post-run evidence because event visibility is logs-only.",
    }


def classify_adapter_compatibility(adapter: dict) -> AdapterCompatibilityResult:
    gaps: list[str] = []
    if adapter.get("event_visibility") == "logs_only":
        gaps.append("logs_only_event_visibility")
    if adapter.get("auth_ownership") == "unsupported":
        gaps.append("unsupported_auth_ownership")
    status: CompatibilityStatus = "compatible_with_gaps" if gaps else "compatible"
    return AdapterCompatibilityResult(
        adapter_id=adapter["adapter_id"],
        compatibility_status=status,
        gaps=gaps,
    )
