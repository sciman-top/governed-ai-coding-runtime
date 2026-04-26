"""Runtime read model for CLI-first operator visibility."""

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path

from governed_ai_coding_runtime_contracts.maintenance_policy import (
    MaintenancePolicyStatus,
    load_maintenance_policy_status,
)
from governed_ai_coding_runtime_contracts.repo_attachment import inspect_attachment_posture
from governed_ai_coding_runtime_contracts.task_store import FileTaskStore, TaskRecord


@dataclass(frozen=True, slots=True)
class RuntimeTaskStatus:
    task_id: str
    current_state: str
    goal: str
    rollback_ref: str | None
    active_run_id: str | None
    workspace_root: str | None
    approval_ids: list[str]
    artifact_refs: list[str]
    evidence_refs: list[str]
    verification_refs: list[str]
    interaction_posture: str | None = None
    latest_task_restatement: str | None = None
    interaction_budget_status: str | None = None
    clarification_active: bool = False
    latest_compression_action: str | None = None
    outstanding_observation_items_count: int | None = None


@dataclass(frozen=True, slots=True)
class RuntimeAttachmentStatus:
    repo_id: str | None
    binding_id: str | None
    binding_state: str
    light_pack_path: str
    adapter_preference: str | None
    gate_profile: str | None
    reason: str | None
    remediation: str | None
    fail_closed: bool
    context_pack_summary: dict | None = None
    provenance_summary: dict | None = None


@dataclass(frozen=True, slots=True)
class RuntimeSnapshot:
    total_tasks: int
    maintenance: MaintenancePolicyStatus
    tasks: list[RuntimeTaskStatus]
    attachments: list[RuntimeAttachmentStatus] = field(default_factory=list)
    runtime_root: str | None = None
    persistence_backend: str = "filesystem"


def runtime_snapshot_to_dict(snapshot: RuntimeSnapshot) -> dict:
    return asdict(snapshot)


def runtime_snapshot_from_dict(raw: dict) -> RuntimeSnapshot:
    if not isinstance(raw, dict):
        msg = "runtime snapshot payload must be an object"
        raise ValueError(msg)
    maintenance_raw = raw.get("maintenance")
    if not isinstance(maintenance_raw, dict):
        msg = "maintenance is required"
        raise ValueError(msg)
    tasks_raw = raw.get("tasks")
    if not isinstance(tasks_raw, list):
        msg = "tasks must be a list"
        raise ValueError(msg)
    attachments_raw = raw.get("attachments", [])
    if not isinstance(attachments_raw, list):
        msg = "attachments must be a list"
        raise ValueError(msg)
    total_tasks = raw.get("total_tasks")
    if not isinstance(total_tasks, int):
        msg = "total_tasks must be an integer"
        raise ValueError(msg)
    return RuntimeSnapshot(
        total_tasks=total_tasks,
        maintenance=MaintenancePolicyStatus(
            stage=_required_string(maintenance_raw.get("stage"), "maintenance.stage"),
            compatibility_policy_ref=_optional_string(
                maintenance_raw.get("compatibility_policy_ref"),
                "maintenance.compatibility_policy_ref",
            ),
            upgrade_policy_ref=_optional_string(maintenance_raw.get("upgrade_policy_ref"), "maintenance.upgrade_policy_ref"),
            triage_policy_ref=_optional_string(maintenance_raw.get("triage_policy_ref"), "maintenance.triage_policy_ref"),
            deprecation_policy_ref=_optional_string(
                maintenance_raw.get("deprecation_policy_ref"),
                "maintenance.deprecation_policy_ref",
            ),
            retirement_policy_ref=_optional_string(
                maintenance_raw.get("retirement_policy_ref"),
                "maintenance.retirement_policy_ref",
            ),
        ),
        tasks=[_runtime_task_status_from_dict(item) for item in tasks_raw],
        attachments=[_runtime_attachment_status_from_dict(item) for item in attachments_raw],
        runtime_root=_optional_string(raw.get("runtime_root"), "runtime_root"),
        persistence_backend=_required_string(raw.get("persistence_backend", "filesystem"), "persistence_backend"),
    )


class RuntimeStatusStore:
    def __init__(
        self,
        task_root: Path,
        repo_root: Path | None = None,
        attachment_roots: list[Path] | None = None,
        attachment_runtime_state_root: Path | None = None,
        runtime_root: Path | None = None,
        persistence_backend: str = "filesystem",
    ) -> None:
        self._task_root = task_root
        self._repo_root = repo_root or task_root.parent.parent
        self._attachment_roots = attachment_roots or []
        self._attachment_runtime_state_root = attachment_runtime_state_root
        self._runtime_root = runtime_root or task_root.parent
        self._persistence_backend = persistence_backend

    def snapshot(self) -> RuntimeSnapshot:
        maintenance = load_maintenance_policy_status(self._repo_root)
        attachments = self._attachment_statuses()
        if not self._task_root.exists():
            return RuntimeSnapshot(
                total_tasks=0,
                maintenance=maintenance,
                tasks=[],
                attachments=attachments,
                runtime_root=self._runtime_root.as_posix(),
                persistence_backend=self._persistence_backend,
            )

        store = FileTaskStore(self._task_root)
        tasks = [
            self._to_status(store.load(path.stem))
            for path in sorted(self._task_root.glob("*.json"))
        ]
        return RuntimeSnapshot(
            total_tasks=len(tasks),
            maintenance=maintenance,
            tasks=tasks,
            attachments=attachments,
            runtime_root=self._runtime_root.as_posix(),
            persistence_backend=self._persistence_backend,
        )

    def _to_status(self, record: TaskRecord) -> RuntimeTaskStatus:
        active_run = None
        if record.active_run_id:
            for item in record.run_history:
                if item.run_id == record.active_run_id:
                    active_run = item
                    break
        return RuntimeTaskStatus(
            task_id=record.task_id,
            current_state=record.current_state,
            goal=record.task.goal,
            rollback_ref=record.rollback_ref,
            active_run_id=record.active_run_id,
            workspace_root=record.workspace_root,
            approval_ids=active_run.approval_ids if active_run else [],
            artifact_refs=active_run.artifact_refs if active_run else [],
            evidence_refs=active_run.evidence_refs if active_run else [],
            verification_refs=active_run.verification_refs if active_run else [],
            **_interaction_projection(
                runtime_root=self._runtime_root,
                evidence_refs=active_run.evidence_refs if active_run else [],
            ),
        )

    def _attachment_statuses(self) -> list[RuntimeAttachmentStatus]:
        statuses: list[RuntimeAttachmentStatus] = []
        for attachment_root in self._attachment_roots:
            runtime_state_root = self._attachment_runtime_state_root or self._task_root.parent / "attachments" / attachment_root.name
            posture = inspect_attachment_posture(
                target_repo_root=str(attachment_root),
                runtime_state_root=str(runtime_state_root),
            )
            statuses.append(
                RuntimeAttachmentStatus(
                    repo_id=posture.repo_id,
                    binding_id=posture.binding_id,
                    binding_state=posture.binding_state,
                    light_pack_path=posture.light_pack_path,
                    adapter_preference=posture.adapter_preference,
                    gate_profile=posture.gate_profile,
                    reason=posture.reason,
                    remediation=posture.remediation,
                    fail_closed=posture.fail_closed,
                    context_pack_summary=posture.context_pack_summary,
                    provenance_summary=posture.provenance_summary,
                )
            )
        return statuses


def _runtime_task_status_from_dict(raw: dict) -> RuntimeTaskStatus:
    if not isinstance(raw, dict):
        msg = "task status entry must be an object"
        raise ValueError(msg)
    return RuntimeTaskStatus(
        task_id=_required_string(raw.get("task_id"), "task_id"),
        current_state=_required_string(raw.get("current_state"), "current_state"),
        goal=_required_string(raw.get("goal"), "goal"),
        rollback_ref=_optional_string(raw.get("rollback_ref"), "rollback_ref"),
        active_run_id=_optional_string(raw.get("active_run_id"), "active_run_id"),
        workspace_root=_optional_string(raw.get("workspace_root"), "workspace_root"),
        approval_ids=_required_string_list(raw.get("approval_ids"), "approval_ids"),
        artifact_refs=_required_string_list(raw.get("artifact_refs"), "artifact_refs"),
        evidence_refs=_required_string_list(raw.get("evidence_refs"), "evidence_refs"),
        verification_refs=_required_string_list(raw.get("verification_refs"), "verification_refs"),
        interaction_posture=_optional_string(raw.get("interaction_posture"), "interaction_posture"),
        latest_task_restatement=_optional_string(raw.get("latest_task_restatement"), "latest_task_restatement"),
        interaction_budget_status=_optional_string(
            raw.get("interaction_budget_status"),
            "interaction_budget_status",
        ),
        clarification_active=_optional_bool(raw.get("clarification_active"), "clarification_active", default=False),
        latest_compression_action=_optional_string(
            raw.get("latest_compression_action"),
            "latest_compression_action",
        ),
        outstanding_observation_items_count=_optional_int(
            raw.get("outstanding_observation_items_count"),
            "outstanding_observation_items_count",
        ),
    )


def _runtime_attachment_status_from_dict(raw: dict) -> RuntimeAttachmentStatus:
    if not isinstance(raw, dict):
        msg = "attachment status entry must be an object"
        raise ValueError(msg)
    fail_closed = raw.get("fail_closed")
    if not isinstance(fail_closed, bool):
        msg = "attachment.fail_closed must be a boolean"
        raise ValueError(msg)
    return RuntimeAttachmentStatus(
        repo_id=_optional_string(raw.get("repo_id"), "repo_id"),
        binding_id=_optional_string(raw.get("binding_id"), "binding_id"),
        binding_state=_required_string(raw.get("binding_state"), "binding_state"),
        light_pack_path=_required_string(raw.get("light_pack_path"), "light_pack_path"),
        adapter_preference=_optional_string(raw.get("adapter_preference"), "adapter_preference"),
        gate_profile=_optional_string(raw.get("gate_profile"), "gate_profile"),
        reason=_optional_string(raw.get("reason"), "reason"),
        remediation=_optional_string(raw.get("remediation"), "remediation"),
        fail_closed=fail_closed,
        context_pack_summary=_optional_object(raw.get("context_pack_summary"), "context_pack_summary"),
        provenance_summary=_optional_object(raw.get("provenance_summary"), "provenance_summary"),
    )


def _required_string(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()


def _optional_string(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    return _required_string(value, field_name)


def _required_string_list(value: object, field_name: str) -> list[str]:
    if not isinstance(value, list):
        msg = f"{field_name} must be a list"
        raise ValueError(msg)
    return [_required_string(item, field_name) for item in value]


def _optional_object(value: object, field_name: str) -> dict | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        msg = f"{field_name} must be an object"
        raise ValueError(msg)
    return dict(value)


def _optional_bool(value: object, field_name: str, *, default: bool | None = None) -> bool | None:
    if value is None:
        return default
    if not isinstance(value, bool):
        msg = f"{field_name} must be a boolean"
        raise ValueError(msg)
    return value


def _optional_int(value: object, field_name: str) -> int | None:
    if value is None:
        return None
    if not isinstance(value, int):
        msg = f"{field_name} must be an integer"
        raise ValueError(msg)
    return value


def _interaction_projection(*, runtime_root: Path, evidence_refs: list[str]) -> dict[str, object]:
    empty = {
        "interaction_posture": None,
        "latest_task_restatement": None,
        "interaction_budget_status": None,
        "clarification_active": False,
        "latest_compression_action": None,
        "outstanding_observation_items_count": None,
    }
    interaction_trace = _load_latest_interaction_trace(runtime_root=runtime_root, evidence_refs=evidence_refs)
    if interaction_trace is None:
        return empty

    applied_policies = interaction_trace.get("applied_policies", [])
    task_restatements = interaction_trace.get("task_restatements", [])
    budget_snapshots = interaction_trace.get("budget_snapshots", [])
    clarification_rounds = interaction_trace.get("clarification_rounds", [])
    compression_actions = interaction_trace.get("compression_actions", [])
    observation_checklists = interaction_trace.get("observation_checklists", [])

    empty["interaction_posture"] = _last_mapping_value(applied_policies, "posture")
    empty["latest_task_restatement"] = task_restatements[-1] if task_restatements else None
    empty["interaction_budget_status"] = _last_mapping_value(budget_snapshots, "budget_status")
    empty["clarification_active"] = bool(clarification_rounds)
    empty["latest_compression_action"] = _last_mapping_value(compression_actions, "compression_mode")
    empty["outstanding_observation_items_count"] = _last_list_size(observation_checklists, "items")
    return empty


def _load_latest_interaction_trace(*, runtime_root: Path, evidence_refs: list[str]) -> dict | None:
    for evidence_ref in reversed(evidence_refs):
        candidate = runtime_root / Path(evidence_ref)
        if not candidate.exists():
            continue
        try:
            payload = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        interaction_trace = payload.get("interaction_trace")
        if isinstance(interaction_trace, dict):
            return interaction_trace
    return None


def _last_mapping_value(items: object, field_name: str) -> str | None:
    if not isinstance(items, list):
        return None
    for item in reversed(items):
        if isinstance(item, dict):
            value = item.get(field_name)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _last_list_size(items: object, field_name: str) -> int | None:
    if not isinstance(items, list):
        return None
    for item in reversed(items):
        if isinstance(item, dict):
            value = item.get(field_name)
            if isinstance(value, list):
                return len(value)
    return None
