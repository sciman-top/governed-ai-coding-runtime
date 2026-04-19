"""Read-only operator query helpers for attachment-scoped runtime visibility."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path

from governed_ai_coding_runtime_contracts.repo_attachment import inspect_attachment_posture
from governed_ai_coding_runtime_contracts.task_store import FileTaskStore, TaskRecord, TaskRunRecord


@dataclass(frozen=True, slots=True)
class OperatorPostureSummary:
    repo_id: str | None
    binding_id: str | None
    binding_state: str
    adapter_preference: str | None
    gate_profile: str | None
    reason: str | None
    remediation: str | None
    fail_closed: bool


@dataclass(frozen=True, slots=True)
class OperatorQueryResult:
    task_id: str
    repo_binding_id: str
    run_id: str | None
    task_found: bool
    current_state: str | None
    active_run_id: str | None
    approval_ids: list[str]
    approval_refs: list[str]
    evidence_refs: list[str]
    artifact_refs: list[str]
    verification_refs: list[str]
    handoff_refs: list[str]
    replay_refs: list[str]
    posture_summary: OperatorPostureSummary | None
    read_only: bool = True

    def to_dict(self) -> dict:
        payload = asdict(self)
        if self.posture_summary is None:
            payload["posture_summary"] = None
        return payload


def query_operator_attachment_surface(
    *,
    task_root: str | Path,
    task_id: str,
    repo_binding_id: str,
    run_id: str | None = None,
    attachment_root: str | Path | None = None,
    attachment_runtime_state_root: str | Path | None = None,
) -> OperatorQueryResult:
    normalized_task_id = _required_string(task_id, "task_id")
    normalized_binding_id = _required_string(repo_binding_id, "repo_binding_id")
    normalized_run_id = _optional_string(run_id, "run_id")

    record: TaskRecord | None = None
    store = FileTaskStore(Path(task_root))
    try:
        record = store.load(normalized_task_id)
    except FileNotFoundError:
        record = None

    selected_runs = _selected_runs(record, run_id=normalized_run_id)
    run_approval_ids = _dedupe_preserve_order(
        [approval_id for run in selected_runs for approval_id in run.approval_ids if approval_id]
    )
    scan = _scan_runtime_state(
        task_id=normalized_task_id,
        run_id=normalized_run_id,
        runtime_state_root=Path(attachment_runtime_state_root) if attachment_runtime_state_root else None,
    )
    approval_ids = _dedupe_preserve_order(run_approval_ids + scan["approval_ids"])

    evidence_refs = _dedupe_preserve_order(
        [ref for run in selected_runs for ref in run.evidence_refs if ref] + scan["evidence_refs"]
    )
    artifact_refs = _dedupe_preserve_order(
        [ref for run in selected_runs for ref in run.artifact_refs if ref] + scan["artifact_refs"]
    )
    verification_refs = _dedupe_preserve_order(
        [ref for run in selected_runs for ref in run.verification_refs if ref] + scan["verification_refs"]
    )
    handoff_refs = _dedupe_preserve_order(
        [ref for ref in evidence_refs + artifact_refs if "handoff" in ref] + scan["handoff_refs"]
    )
    replay_refs = _dedupe_preserve_order(
        [ref for ref in evidence_refs + artifact_refs if "replay" in ref] + scan["replay_refs"]
    )
    approval_refs = _dedupe_preserve_order(scan["approval_refs"])

    return OperatorQueryResult(
        task_id=normalized_task_id,
        repo_binding_id=normalized_binding_id,
        run_id=normalized_run_id,
        task_found=record is not None,
        current_state=record.current_state if record else None,
        active_run_id=record.active_run_id if record else None,
        approval_ids=approval_ids,
        approval_refs=approval_refs,
        evidence_refs=evidence_refs,
        artifact_refs=artifact_refs,
        verification_refs=verification_refs,
        handoff_refs=handoff_refs,
        replay_refs=replay_refs,
        posture_summary=_posture_summary(
            attachment_root=attachment_root,
            attachment_runtime_state_root=attachment_runtime_state_root,
        ),
        read_only=True,
    )


def _posture_summary(
    *,
    attachment_root: str | Path | None,
    attachment_runtime_state_root: str | Path | None,
) -> OperatorPostureSummary | None:
    if attachment_root is None or attachment_runtime_state_root is None:
        return None
    posture = inspect_attachment_posture(
        target_repo_root=str(attachment_root),
        runtime_state_root=str(attachment_runtime_state_root),
    )
    return OperatorPostureSummary(
        repo_id=posture.repo_id,
        binding_id=posture.binding_id,
        binding_state=posture.binding_state,
        adapter_preference=posture.adapter_preference,
        gate_profile=posture.gate_profile,
        reason=posture.reason,
        remediation=posture.remediation,
        fail_closed=posture.fail_closed,
    )


def _selected_runs(record: TaskRecord | None, *, run_id: str | None) -> list[TaskRunRecord]:
    if record is None:
        return []
    if run_id is None:
        return list(record.run_history)
    return [run for run in record.run_history if run.run_id == run_id]


def _scan_runtime_state(*, task_id: str, run_id: str | None, runtime_state_root: Path | None) -> dict[str, list[str]]:
    empty = {
        "approval_ids": [],
        "approval_refs": [],
        "artifact_refs": [],
        "evidence_refs": [],
        "verification_refs": [],
        "handoff_refs": [],
        "replay_refs": [],
    }
    if runtime_state_root is None or not runtime_state_root.exists():
        return empty

    approvals_root = runtime_state_root / "approvals"
    for path in sorted(approvals_root.glob("*.json")) if approvals_root.exists() else []:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if raw.get("task_id") != task_id:
            continue
        approval_id = raw.get("approval_id")
        if isinstance(approval_id, str) and approval_id.strip():
            empty["approval_ids"].append(approval_id.strip())
            empty["approval_refs"].append(path.as_posix())

    artifacts_root = runtime_state_root / "artifacts" / task_id
    if artifacts_root.exists():
        candidate_runs = [run_id] if run_id else [path.name for path in artifacts_root.iterdir() if path.is_dir()]
        for run in candidate_runs:
            run_root = artifacts_root / run
            if not run_root.exists():
                continue
            for file_path in sorted(run_root.rglob("*.json")) + sorted(run_root.rglob("*.txt")):
                relative_ref = file_path.relative_to(runtime_state_root).as_posix()
                if "/evidence/" in relative_ref:
                    empty["evidence_refs"].append(relative_ref)
                elif "/verification-output/" in relative_ref:
                    empty["verification_refs"].append(relative_ref)
                else:
                    empty["artifact_refs"].append(relative_ref)
                if "/handoff/" in relative_ref:
                    empty["handoff_refs"].append(relative_ref)
                if "/replay/" in relative_ref:
                    empty["replay_refs"].append(relative_ref)

    return {key: _dedupe_preserve_order(values) for key, values in empty.items()}


def _required_string(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()


def _optional_string(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    return _required_string(value, field_name)


def _dedupe_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered
