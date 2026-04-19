"""Structured evidence model for multi-repo onboarding trials."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Literal

from governed_ai_coding_runtime_contracts.artifact_store import LocalArtifactStore
from governed_ai_coding_runtime_contracts.attached_write_governance import govern_attached_write_request
from governed_ai_coding_runtime_contracts.repo_attachment import inspect_attachment_posture, validate_light_pack
from governed_ai_coding_runtime_contracts.repo_profile import load_repo_profile
from governed_ai_coding_runtime_contracts.verification_runner import (
    build_repo_profile_verification_plan,
    run_verification_plan,
)


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
    doctor_status: str = "not_run"
    write_probe_status: str = "skipped"


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
    doctor_status: str = "not_run",
    write_probe_status: str = "skipped",
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
        doctor_status=_required_string(doctor_status, "doctor_status"),
        write_probe_status=_required_string(write_probe_status, "write_probe_status"),
    )


def run_multi_repo_trial(
    *,
    adapter_id: str,
    adapter_tier: str,
    unsupported_capabilities: list[str],
    trial_id: str = "multi-repo-trial",
    repo_profile_paths: list[str] | None = None,
    attachment_roots: list[str] | None = None,
    attachment_runtime_state_roots: list[str] | None = None,
    execute_write_probe: bool = False,
) -> MultiRepoTrialRun:
    if attachment_roots:
        return _run_attached_repo_trial(
            trial_id=trial_id,
            adapter_id=adapter_id,
            adapter_tier=adapter_tier,
            unsupported_capabilities=unsupported_capabilities,
            attachment_roots=attachment_roots,
            attachment_runtime_state_roots=attachment_runtime_state_roots or [],
            execute_write_probe=execute_write_probe,
        )
    return _run_profile_trial(
        trial_id=trial_id,
        adapter_id=adapter_id,
        adapter_tier=adapter_tier,
        unsupported_capabilities=unsupported_capabilities,
        repo_profile_paths=repo_profile_paths or [],
    )


def _run_profile_trial(
    *,
    trial_id: str,
    adapter_id: str,
    adapter_tier: str,
    unsupported_capabilities: list[str],
    repo_profile_paths: list[str],
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
                doctor_status="profile_validated",
                write_probe_status="skipped",
            )
        )
    return MultiRepoTrialRun(
        trial_id=normalized_trial_id,
        total_repos=len(records),
        records=records,
    )


def _run_attached_repo_trial(
    *,
    trial_id: str,
    adapter_id: str,
    adapter_tier: str,
    unsupported_capabilities: list[str],
    attachment_roots: list[str],
    attachment_runtime_state_roots: list[str],
    execute_write_probe: bool,
) -> MultiRepoTrialRun:
    normalized_trial_id = _required_string(trial_id, "trial_id")
    runtime_root_map = _runtime_root_map(attachment_roots, attachment_runtime_state_roots)
    records: list[MultiRepoTrialRecord] = []

    for attachment_root in attachment_roots:
        root_path = Path(_required_string(attachment_root, "attachment_root"))
        runtime_root = runtime_root_map.get(attachment_root) or (root_path.parent / "runtime-state" / root_path.name)
        posture = inspect_attachment_posture(
            target_repo_root=str(root_path),
            runtime_state_root=str(runtime_root),
        )
        repo_id = posture.repo_id or root_path.name
        repo_trial_id = f"{normalized_trial_id}-{repo_id}"
        base_ref = f"artifacts/{repo_trial_id}"
        doctor_status = posture.binding_state

        if posture.binding_state != "healthy":
            records.append(
                build_multi_repo_trial_record(
                    trial_id=repo_trial_id,
                    repo_id=repo_id,
                    repo_binding_id=posture.binding_id or f"binding-{repo_id}",
                    attachment_posture=posture.binding_state,
                    adapter_id=adapter_id,
                    adapter_tier=adapter_tier,
                    unsupported_capabilities=unsupported_capabilities,
                    approval_friction="observe_only",
                    gate_failures=["attachment_doctor"],
                    replay_quality="insufficient",
                    evidence_refs=[f"{base_ref}/evidence/attachment-posture.json"],
                    verification_refs=[f"{base_ref}/verification-output/not-run.txt"],
                    handoff_refs=[f"{base_ref}/handoff/not-run.json"],
                    follow_ups=[
                        {
                            "category": "onboarding_generic",
                            "summary": posture.reason or "repair attachment posture before trial",
                        }
                    ],
                    doctor_status=doctor_status,
                    write_probe_status="skipped",
                )
            )
            continue

        attachment = validate_light_pack(
            target_repo_root=str(root_path),
            light_pack_path=str(root_path / ".governed-ai" / "light-pack.json"),
            runtime_state_root=str(runtime_root),
        )
        profile = load_repo_profile(attachment.repo_profile_path)
        run_id = f"{repo_id}-trial"
        plan = build_repo_profile_verification_plan(
            "quick",
            profile_raw=profile.raw,
            task_id=repo_trial_id,
            run_id=run_id,
        )
        artifact_store = LocalArtifactStore(runtime_root)
        verification = run_verification_plan(
            plan,
            artifact_store=artifact_store,
            execute_gate=lambda gate: _execute_gate(gate.command, cwd=root_path),
        )
        gate_failures = [gate for gate, result in verification.results.items() if result != "pass"]
        handoff = artifact_store.write_json(
            task_id=repo_trial_id,
            run_id=run_id,
            kind="handoff",
            label="trial-loop",
            payload={
                "repo_id": profile.repo_id,
                "binding_id": attachment.binding.binding_id,
                "gate_failures": gate_failures,
            },
        )
        evidence_refs = [verification.evidence_link]
        write_probe_status = "skipped"
        follow_ups = _follow_ups_for_profile(profile.compatibility_signals)

        if execute_write_probe:
            try:
                governance = govern_attached_write_request(
                    attachment_root=str(root_path),
                    attachment_runtime_state_root=str(runtime_root),
                    task_id=repo_trial_id,
                    tool_name="write_file",
                    target_path="docs/.trial-write-probe.txt",
                    tier="medium",
                    rollback_reference="git checkout -- docs/.trial-write-probe.txt",
                )
                write_probe_status = governance.governance_status
                evidence_refs.append(governance.policy_decision.evidence_ref)
                if governance.governance_status in {"paused", "denied"}:
                    follow_ups.append(
                        {
                            "category": "adapter_generic",
                            "summary": f"write probe status is {governance.governance_status}",
                        }
                    )
            except ValueError as exc:
                write_probe_status = "failed"
                follow_ups.append({"category": "repo_specific", "summary": str(exc)})

        if gate_failures:
            follow_ups.append(
                {
                    "category": "repo_specific",
                    "summary": "fix failing verification gates before expanding trial coverage",
                }
            )
        replay_quality: ReplayQuality = "replay_ready" if not gate_failures else "needs_follow_up"
        selected_tier = posture.adapter_preference or adapter_tier
        records.append(
            build_multi_repo_trial_record(
                trial_id=repo_trial_id,
                repo_id=profile.repo_id,
                repo_binding_id=attachment.binding.binding_id,
                attachment_posture=posture.binding_state,
                adapter_id=adapter_id,
                adapter_tier=selected_tier,
                unsupported_capabilities=unsupported_capabilities,
                approval_friction=_approval_friction_for_profile(profile.rollout_posture),
                gate_failures=gate_failures,
                replay_quality=replay_quality,
                evidence_refs=evidence_refs,
                verification_refs=list(verification.result_artifact_refs.values()),
                handoff_refs=[handoff.relative_path],
                follow_ups=follow_ups,
                doctor_status=doctor_status,
                write_probe_status=write_probe_status,
            )
        )

    return MultiRepoTrialRun(
        trial_id=normalized_trial_id,
        total_repos=len(records),
        records=records,
    )


def _runtime_root_map(attachment_roots: list[str], runtime_roots: list[str]) -> dict[str, Path]:
    if not runtime_roots:
        return {}
    mapping: dict[str, Path] = {}
    for index, attachment_root in enumerate(attachment_roots):
        if index >= len(runtime_roots):
            break
        mapping[attachment_root] = Path(_required_string(runtime_roots[index], "attachment_runtime_state_root"))
    return mapping


def _execute_gate(command: str, *, cwd: Path) -> tuple[int, str]:
    completed = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd,
        check=False,
    )
    output = "\n".join(part for part in [completed.stdout, completed.stderr] if part).strip()
    return completed.returncode, output


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
