"""Structured evidence model for multi-repo onboarding trials."""

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from governed_ai_coding_runtime_contracts.repo_profile import load_repo_profile


FollowUpCategory = Literal["repo_specific", "onboarding_generic", "adapter_generic", "contract_generic"]
ReplayQuality = Literal["replay_ready", "needs_follow_up", "insufficient"]

_FOLLOW_UP_CATEGORIES = {"repo_specific", "onboarding_generic", "adapter_generic", "contract_generic"}
_REPLAY_QUALITIES = {"replay_ready", "needs_follow_up", "insufficient"}
_ADAPTER_TIERS = {"native_attach", "process_bridge", "manual_handoff"}


@dataclass(frozen=True, slots=True)
class MultiRepoTrialFollowUp:
    category: FollowUpCategory
    summary: str


@dataclass(frozen=True, slots=True)
class MultiRepoTrialRecord:
    trial_id: str
    repo_id: str
    repo_binding_id: str
    attachment_posture: str
    adapter_id: str
    adapter_tier: str
    unsupported_capabilities: list[str]
    approval_friction: str
    gate_failures: list[str]
    replay_quality: ReplayQuality
    evidence_refs: list[str]
    verification_refs: list[str]
    handoff_refs: list[str]
    follow_ups: list[MultiRepoTrialFollowUp]


@dataclass(frozen=True, slots=True)
class MultiRepoTrialRun:
    trial_id: str
    total_repos: int
    records: list[MultiRepoTrialRecord]


def build_multi_repo_trial_record(
    *,
    trial_id: str,
    repo_id: str,
    repo_binding_id: str,
    attachment_posture: str = "profile_validated",
    adapter_id: str,
    adapter_tier: str,
    unsupported_capabilities: list[str],
    approval_friction: str,
    gate_failures: list[str],
    replay_quality: ReplayQuality,
    evidence_refs: list[str],
    verification_refs: list[str],
    handoff_refs: list[str],
    follow_ups: list[dict] | list[MultiRepoTrialFollowUp],
) -> MultiRepoTrialRecord:
    normalized_follow_ups = [_normalize_follow_up(item) for item in follow_ups]
    return MultiRepoTrialRecord(
        trial_id=_required_string(trial_id, "trial_id"),
        repo_id=_required_string(repo_id, "repo_id"),
        repo_binding_id=_required_string(repo_binding_id, "repo_binding_id"),
        attachment_posture=_required_string(attachment_posture, "attachment_posture"),
        adapter_id=_required_string(adapter_id, "adapter_id"),
        adapter_tier=_required_enum(adapter_tier, "adapter_tier", _ADAPTER_TIERS),
        unsupported_capabilities=[_required_string(item, "unsupported_capabilities[]") for item in unsupported_capabilities],
        approval_friction=_required_string(approval_friction, "approval_friction"),
        gate_failures=[_required_string(item, "gate_failures[]") for item in gate_failures],
        replay_quality=_required_enum(replay_quality, "replay_quality", _REPLAY_QUALITIES),
        evidence_refs=_required_string_list(evidence_refs, "evidence_refs"),
        verification_refs=_required_string_list(verification_refs, "verification_refs"),
        handoff_refs=_required_string_list(handoff_refs, "handoff_refs"),
        follow_ups=normalized_follow_ups,
    )


def run_multi_repo_trial(
    *,
    repo_profile_paths: list[str],
    adapter_id: str,
    adapter_tier: str,
    unsupported_capabilities: list[str],
    trial_id: str = "multi-repo-trial",
) -> MultiRepoTrialRun:
    records: list[MultiRepoTrialRecord] = []
    normalized_trial_id = _required_string(trial_id, "trial_id")
    for repo_profile_path in repo_profile_paths:
        profile = load_repo_profile(Path(repo_profile_path))
        repo_specific_trial_id = f"{normalized_trial_id}-{profile.repo_id}"
        base_ref = f"artifacts/{repo_specific_trial_id}"
        follow_ups = _follow_ups_for_profile(profile.compatibility_signals)
        records.append(
            build_multi_repo_trial_record(
                trial_id=repo_specific_trial_id,
                repo_id=profile.repo_id,
                repo_binding_id=f"binding-{profile.repo_id}",
                attachment_posture="profile_validated",
                adapter_id=adapter_id,
                adapter_tier=adapter_tier,
                unsupported_capabilities=unsupported_capabilities,
                approval_friction=_approval_friction_for_profile(profile.rollout_posture),
                gate_failures=[],
                replay_quality="replay_ready",
                evidence_refs=[f"{base_ref}/evidence/bundle.json"],
                verification_refs=[
                    f"{base_ref}/verification-output/runtime.txt",
                    f"{base_ref}/verification-output/contract.txt",
                ],
                handoff_refs=[f"{base_ref}/handoff/package.json"],
                follow_ups=follow_ups,
            )
        )
    return MultiRepoTrialRun(
        trial_id=normalized_trial_id,
        total_repos=len(records),
        records=records,
    )


def _normalize_follow_up(item: dict | MultiRepoTrialFollowUp) -> MultiRepoTrialFollowUp:
    if isinstance(item, MultiRepoTrialFollowUp):
        return item
    if not isinstance(item, dict):
        msg = "follow_ups must contain objects"
        raise ValueError(msg)
    return MultiRepoTrialFollowUp(
        category=_required_enum(item.get("category"), "follow_up.category", _FOLLOW_UP_CATEGORIES),
        summary=_required_string(item.get("summary"), "follow_up.summary"),
    )


def _follow_ups_for_profile(compatibility_signals: list[dict]) -> list[dict]:
    follow_ups: list[dict] = []
    for signal in compatibility_signals:
        status = signal.get("status")
        reason = signal.get("reason", "compatibility follow-up")
        if status == "partial_support":
            follow_ups.append({"category": "onboarding_generic", "summary": _required_string(reason, "reason")})
        elif status == "unsupported":
            follow_ups.append({"category": "adapter_generic", "summary": _required_string(reason, "reason")})
    if not follow_ups:
        follow_ups.append({"category": "repo_specific", "summary": "no additional onboarding follow-up required"})
    return follow_ups


def _approval_friction_for_profile(rollout_posture: dict) -> str:
    current_mode = rollout_posture.get("current_mode")
    if current_mode == "enforced":
        return "strict_runtime_controls"
    if current_mode == "advisory":
        return "medium_write_needs_human"
    return "observe_only"


def _required_string_list(values: list[str], field_name: str) -> list[str]:
    if not isinstance(values, list) or not values:
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return [_required_string(value, field_name) for value in values]


def _required_enum(value: str, field_name: str, valid_values: set[str]) -> str:
    normalized = _required_string(value, field_name)
    if normalized not in valid_values:
        msg = f"unsupported {field_name}: {value}"
        raise ValueError(msg)
    return normalized


def _required_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()
