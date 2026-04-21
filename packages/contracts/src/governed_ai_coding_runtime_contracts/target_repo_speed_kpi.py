"""Speed KPI baseline export for target-repo trial evidence."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Literal


WindowKind = Literal["latest", "rolling"]
DEFAULT_SCHEMA_VERSION = "1.0"
_RUN_FILE_PATTERN = re.compile(r"^(?P<target>.+?)-(?P<flow>onboard|daily)(?:-[a-z0-9]+)?-(?P<stamp>\d{14})\.json$")


@dataclass(frozen=True, slots=True)
class TargetRepoSpeedKpiRecord:
    target: str
    total_daily_runs: int
    onboarding_latency_seconds: int | None
    first_pass_latency_seconds: int | None
    deny_to_success_retries: int
    fallback_rate: float
    medium_risk_loop_success_ratio: float | None
    window_start_utc: str | None
    window_end_utc: str | None
    latest_evidence_ref: str | None


@dataclass(frozen=True, slots=True)
class TargetRepoSpeedKpiSnapshot:
    schema_version: str
    generated_at: str
    window_kind: WindowKind
    window_size: int
    record_count: int
    records: list[TargetRepoSpeedKpiRecord]

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "generated_at": self.generated_at,
            "window_kind": self.window_kind,
            "window_size": self.window_size,
            "record_count": self.record_count,
            "records": [asdict(record) for record in self.records],
        }


def export_target_repo_speed_kpi(
    *,
    target_repo_runs_root: str | Path,
    window_kind: WindowKind = "latest",
    window_size: int = 10,
) -> TargetRepoSpeedKpiSnapshot:
    runs_root = Path(target_repo_runs_root).resolve(strict=False)
    if not runs_root.exists():
        msg = f"target_repo_runs_root does not exist: {runs_root}"
        raise ValueError(msg)
    if window_size < 1:
        msg = "window_size must be >= 1"
        raise ValueError(msg)

    run_entries = _load_run_entries(runs_root)
    grouped = _group_by_target(run_entries)
    records: list[TargetRepoSpeedKpiRecord] = []
    for target in sorted(grouped):
        records.append(_build_record(target, grouped[target], window_kind=window_kind, window_size=window_size))

    return TargetRepoSpeedKpiSnapshot(
        schema_version=DEFAULT_SCHEMA_VERSION,
        generated_at=datetime.now(timezone.utc).isoformat(),
        window_kind=window_kind,
        window_size=window_size,
        record_count=len(records),
        records=records,
    )


def _build_record(target: str, entries: list[dict], *, window_kind: WindowKind, window_size: int) -> TargetRepoSpeedKpiRecord:
    onboard = [entry for entry in entries if entry["flow"] == "onboard"]
    daily = [entry for entry in entries if entry["flow"] == "daily"]
    daily.sort(key=lambda item: item["timestamp"])
    onboard.sort(key=lambda item: item["timestamp"])

    selected_daily = daily[-1:] if window_kind == "latest" else daily[-window_size:]
    if not selected_daily:
        return TargetRepoSpeedKpiRecord(
            target=target,
            total_daily_runs=0,
            onboarding_latency_seconds=None,
            first_pass_latency_seconds=None,
            deny_to_success_retries=0,
            fallback_rate=0.0,
            medium_risk_loop_success_ratio=None,
            window_start_utc=None,
            window_end_utc=None,
            latest_evidence_ref=None,
        )

    window_start = selected_daily[0]["timestamp"].isoformat()
    window_end = selected_daily[-1]["timestamp"].isoformat()
    fallback_runs = 0
    medium_total = 0
    medium_success = 0
    deny_to_success_retries = 0
    previous_denied = False

    for entry in selected_daily:
        if _is_fallback_run(entry["payload"]):
            fallback_runs += 1
        write_tier = _write_tier(entry["payload"])
        write_status = _write_status(entry["payload"])
        if write_tier == "medium":
            medium_total += 1
            if write_status in {"completed", "allowed", "written", "ok"}:
                medium_success += 1
        current_denied = write_status in {"denied", "deny"}
        current_success = write_status in {"completed", "allowed", "written", "ok"}
        if previous_denied and current_success:
            deny_to_success_retries += 1
        previous_denied = current_denied

    latest_daily = selected_daily[-1]
    closest_onboard = _closest_onboard(onboard, latest_daily["timestamp"])
    onboarding_latency = None
    if closest_onboard is not None:
        onboarding_latency = int((latest_daily["timestamp"] - closest_onboard["timestamp"]).total_seconds())
        if onboarding_latency < 0:
            onboarding_latency = 0

    return TargetRepoSpeedKpiRecord(
        target=target,
        total_daily_runs=len(selected_daily),
        onboarding_latency_seconds=onboarding_latency,
        first_pass_latency_seconds=onboarding_latency,
        deny_to_success_retries=deny_to_success_retries,
        fallback_rate=round(fallback_runs / len(selected_daily), 4),
        medium_risk_loop_success_ratio=(round(medium_success / medium_total, 4) if medium_total > 0 else None),
        window_start_utc=window_start,
        window_end_utc=window_end,
        latest_evidence_ref=_latest_evidence_ref(latest_daily["payload"]),
    )


def _closest_onboard(onboard: list[dict], daily_timestamp: datetime) -> dict | None:
    candidates = [entry for entry in onboard if entry["timestamp"] <= daily_timestamp]
    if not candidates:
        return onboard[-1] if onboard else None
    return candidates[-1]


def _is_fallback_run(payload: dict) -> bool:
    session_identity = _session_identity(payload)
    if session_identity is None:
        return False
    flow_kind = session_identity.get("flow_kind")
    if isinstance(flow_kind, str) and flow_kind.strip() and flow_kind != "live_attach":
        return True
    return False


def _write_tier(payload: dict) -> str | None:
    write_governance = _required_object(payload.get("runtime_check"), "runtime_check")
    if write_governance is None:
        return None
    runtime_payload = _required_object(write_governance.get("payload"), "runtime_check.payload")
    if runtime_payload is None:
        return None
    write_governance_payload = _required_object(runtime_payload.get("write_governance"), "write_governance")
    if write_governance_payload and isinstance(write_governance_payload.get("write_tier"), str):
        return write_governance_payload["write_tier"]
    write_execute_payload = _required_object(runtime_payload.get("write_execute"), "write_execute")
    if write_execute_payload and isinstance(write_execute_payload.get("write_tier"), str):
        return write_execute_payload["write_tier"]
    return None


def _write_status(payload: dict) -> str | None:
    runtime_check = _required_object(payload.get("runtime_check"), "runtime_check")
    if runtime_check is None:
        return None
    runtime_payload = _required_object(runtime_check.get("payload"), "runtime_check.payload")
    if runtime_payload is None:
        return None
    write_execute = _required_object(runtime_payload.get("write_execute"), "write_execute")
    if write_execute and isinstance(write_execute.get("execution_status"), str):
        return write_execute["execution_status"]
    write_governance = _required_object(runtime_payload.get("write_governance"), "write_governance")
    if write_governance and isinstance(write_governance.get("governance_status"), str):
        return write_governance["governance_status"]
    return None


def _latest_evidence_ref(payload: dict) -> str | None:
    runtime_check = _required_object(payload.get("runtime_check"), "runtime_check")
    if runtime_check is None:
        return None
    runtime_payload = _required_object(runtime_check.get("payload"), "runtime_check.payload")
    if runtime_payload is None:
        return None
    verify_attachment = _required_object(runtime_payload.get("verify_attachment"), "verify_attachment")
    if verify_attachment and isinstance(verify_attachment.get("evidence_link"), str):
        return verify_attachment["evidence_link"]
    return None


def _session_identity(payload: dict) -> dict | None:
    runtime_check = _required_object(payload.get("runtime_check"), "runtime_check")
    if runtime_check is None:
        return None
    runtime_payload = _required_object(runtime_check.get("payload"), "runtime_check.payload")
    if runtime_payload is None:
        return None

    request_gate = _required_object(runtime_payload.get("request_gate"), "request_gate")
    if request_gate:
        gate_payload = _required_object(request_gate.get("payload"), "request_gate.payload")
        if gate_payload:
            session_identity = _required_object(gate_payload.get("session_identity"), "session_identity")
            if session_identity is not None:
                return session_identity

    write_execute = _required_object(runtime_payload.get("write_execute"), "write_execute")
    if write_execute:
        session_identity = _required_object(write_execute.get("session_identity"), "session_identity")
        if session_identity is not None:
            return session_identity
    return None


def _load_run_entries(runs_root: Path) -> list[dict]:
    entries: list[dict] = []
    for run_file in sorted(runs_root.glob("*.json")):
        match = _RUN_FILE_PATTERN.match(run_file.name)
        if not match:
            continue
        try:
            payload = json.loads(run_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        timestamp = _stamp_to_utc(match.group("stamp"))
        entries.append(
            {
                "target": match.group("target"),
                "flow": match.group("flow"),
                "stamp": match.group("stamp"),
                "timestamp": timestamp,
                "path": run_file,
                "payload": payload,
            }
        )
    return entries


def _group_by_target(entries: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for entry in entries:
        target = entry["target"]
        grouped.setdefault(target, []).append(entry)
    return grouped


def _stamp_to_utc(stamp: str) -> datetime:
    return datetime.strptime(stamp, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)


def _required_object(value: object, _field_name: str) -> dict | None:
    if isinstance(value, dict):
        return value
    return None
