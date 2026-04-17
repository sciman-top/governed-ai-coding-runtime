"""Delivery handoff package primitives."""

from dataclasses import dataclass
from typing import Literal

from governed_ai_coding_runtime_contracts.verification_runner import VerificationArtifact


ValidationStatus = Literal["fully_validated", "partially_validated"]


@dataclass(frozen=True, slots=True)
class HandoffPackage:
    task_id: str
    changed_files: list[str]
    verification_artifact: VerificationArtifact
    validation_status: ValidationStatus
    risk_notes: list[str]
    replay_references: list[str]


def build_handoff_package(
    task_id: str,
    changed_files: list[str],
    verification_artifact: VerificationArtifact,
    risk_notes: list[str],
    replay_references: list[str],
) -> HandoffPackage:
    _required_string(task_id, "task_id")
    if not changed_files:
        msg = "changed_files is required"
        raise ValueError(msg)
    validation_status = _validation_status(verification_artifact)
    if _has_failed_or_interrupted_result(verification_artifact) and not replay_references:
        msg = "failed or interrupted handoffs require replay_references"
        raise ValueError(msg)
    return HandoffPackage(
        task_id=task_id,
        changed_files=changed_files,
        verification_artifact=verification_artifact,
        validation_status=validation_status,
        risk_notes=risk_notes,
        replay_references=replay_references,
    )


def _validation_status(artifact: VerificationArtifact) -> ValidationStatus:
    expected_gates = artifact.gate_order
    if artifact.mode == "full" and all(artifact.results.get(gate) == "pass" for gate in expected_gates):
        return "fully_validated"
    return "partially_validated"


def _has_failed_or_interrupted_result(artifact: VerificationArtifact) -> bool:
    failed_states = {"fail", "failed", "interrupted", "not_run"}
    return any(result in failed_states for result in artifact.results.values())


def _required_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()
