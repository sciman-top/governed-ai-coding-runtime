"""Replay-oriented references for failed governed runs."""

from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256


@dataclass(frozen=True, slots=True)
class FailureSignature:
    signature_id: str
    failure_reason: str
    created_at: str


@dataclass(frozen=True, slots=True)
class ReplayReference:
    task_id: str
    run_id: str
    failure_signature: FailureSignature
    artifact_refs: list[str]
    verification_artifact_refs: list[str]
    created_at: str


def build_replay_reference(
    *,
    task_id: str,
    run_id: str,
    failure_reason: str,
    artifact_refs: list[str],
    verification_artifact_refs: list[str],
) -> ReplayReference:
    if not failure_reason.strip():
        msg = "failure_reason is required"
        raise ValueError(msg)
    created_at = datetime.now(UTC).isoformat()
    signature = FailureSignature(
        signature_id=_signature_for(task_id=task_id, run_id=run_id, failure_reason=failure_reason),
        failure_reason=failure_reason,
        created_at=created_at,
    )
    return ReplayReference(
        task_id=task_id,
        run_id=run_id,
        failure_signature=signature,
        artifact_refs=artifact_refs,
        verification_artifact_refs=verification_artifact_refs,
        created_at=created_at,
    )


def _signature_for(*, task_id: str, run_id: str, failure_reason: str) -> str:
    source = f"{task_id}:{run_id}:{failure_reason}".encode("utf-8")
    return f"failure-{sha256(source).hexdigest()[:16]}"
