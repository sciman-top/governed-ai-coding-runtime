from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import re
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))

from governed_ai_coding_runtime_contracts.target_repo_speed_kpi import export_target_repo_speed_kpi


DEFAULT_RUNS_ROOT = ROOT / "docs" / "change-evidence" / "target-repo-runs"
_RUN_FILE_PATTERN = re.compile(r"^(?P<target>.+?)-(?P<flow>onboard|daily)(?:-[a-z0-9]+)?-(?P<stamp>\d{14})\.json$")


def _load_runs(target: str, runs_root: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for path in sorted(runs_root.glob(f"{target}-*.json")):
        match = _RUN_FILE_PATTERN.match(path.name)
        if not match:
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        entries.append(
            {
                "path": path,
                "flow": match.group("flow"),
                "stamp": match.group("stamp"),
                "timestamp": datetime.strptime(match.group("stamp"), "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc),
                "payload": payload,
            }
        )
    return entries


def _extract_metrics(entry: dict[str, Any]) -> dict[str, Any]:
    payload = entry["payload"]
    runtime_payload = payload.get("runtime_check", {}).get("payload", {})
    status = runtime_payload.get("status", {})
    summary = runtime_payload.get("summary", {})
    verify_attachment = runtime_payload.get("verify_attachment", {})
    request_gate = runtime_payload.get("request_gate", {})
    request_gate_payload = request_gate.get("payload", {}) if isinstance(request_gate, dict) else {}
    problem_trace = runtime_payload.get("problem_trace", {})
    attachments = status.get("attachments", []) if isinstance(status, dict) else []
    first_attachment = attachments[0] if attachments else {}
    codex_capability = status.get("codex_capability", {}) if isinstance(status, dict) else {}

    evidence_refs: list[str] = []
    for candidate in [
        verify_attachment.get("evidence_link"),
        request_gate_payload.get("evidence_link"),
        request_gate.get("policy_decision_ref"),
    ]:
        if isinstance(candidate, str) and candidate.strip():
            evidence_refs.append(candidate)
    if isinstance(problem_trace, dict):
        for candidate in problem_trace.get("evidence_refs", []):
            if isinstance(candidate, str) and candidate.strip():
                evidence_refs.append(candidate)
    result_artifact_refs = verify_attachment.get("result_artifact_refs", {})
    if isinstance(result_artifact_refs, dict):
        for candidate in result_artifact_refs.values():
            if isinstance(candidate, str) and candidate.strip():
                evidence_refs.append(candidate)

    gate_results = verify_attachment.get("results")
    if not isinstance(gate_results, dict):
        gate_results = request_gate_payload.get("results", {})
    if not isinstance(gate_results, dict):
        gate_results = {}

    completeness_checks = {
        "status": bool(status),
        "summary": bool(summary),
        "verify_attachment": bool(verify_attachment),
        "policy_decision_ref": isinstance(request_gate.get("policy_decision_ref"), str),
        "evidence_link": isinstance(verify_attachment.get("evidence_link"), str),
    }
    present_count = sum(1 for item in completeness_checks.values() if item)
    completeness_ratio = round(present_count / len(completeness_checks), 4)

    return {
        "run_ref": entry["path"].name,
        "flow": entry["flow"],
        "timestamp_utc": entry["timestamp"].isoformat(),
        "overall_status": str(payload.get("overall_status") or summary.get("overall_status") or "unknown"),
        "attachment_health": summary.get("attachment_health"),
        "binding_state": first_attachment.get("binding_state"),
        "required_entrypoint_policy_present": bool(first_attachment.get("required_entrypoint_policy")),
        "entrypoint_policy_mode": summary.get("entrypoint_policy_mode")
        or first_attachment.get("required_entrypoint_policy", {}).get("current_mode"),
        "codex_capability_status": codex_capability.get("status"),
        "adapter_tier": codex_capability.get("adapter_tier") or request_gate_payload.get("session_identity", {}).get("adapter_tier"),
        "flow_kind": codex_capability.get("flow_kind") or request_gate_payload.get("session_identity", {}).get("flow_kind"),
        "gate_order": verify_attachment.get("gate_order") or request_gate_payload.get("gate_order") or [],
        "gate_results": gate_results,
        "problem_flag": bool(problem_trace.get("has_problem")) if isinstance(problem_trace, dict) else False,
        "failure_signature": problem_trace.get("failure_signature") if isinstance(problem_trace, dict) else None,
        "evidence_ref_count": len(dict.fromkeys(evidence_refs)),
        "evidence_complete": completeness_ratio >= 0.8,
        "evidence_completeness_ratio": completeness_ratio,
        "evidence_refs": list(dict.fromkeys(evidence_refs)),
    }


def _decision_for(after_metrics: dict[str, Any], kpi_record: dict[str, Any]) -> tuple[str, list[dict[str, Any]]]:
    backlog_candidates: list[dict[str, Any]] = []

    if after_metrics["codex_capability_status"] not in {"ready", None}:
        backlog_candidates.append(
            {
                "candidate_id": "target-repo-reuse-host-capability-gap",
                "disposition": "adjust",
                "reason": "Latest target run still depends on degraded host capability posture.",
                "current_posture": {
                    "codex_capability_status": after_metrics.get("codex_capability_status"),
                    "adapter_tier": after_metrics.get("adapter_tier"),
                    "flow_kind": after_metrics.get("flow_kind"),
                },
                "remediation_boundary": {
                    "allowed_interim_tiers": ["process_bridge", "manual_handoff"],
                    "required_recovery_evidence": "fresh target run with codex_capability_status=ready and adapter_tier=native_attach",
                    "claim_guard": "do not claim native_attach recovery until a fresh target repo run proves it",
                },
                "evidence_refs": after_metrics["evidence_refs"],
            }
        )

    if not after_metrics["evidence_complete"]:
        backlog_candidates.append(
            {
                "candidate_id": "target-repo-reuse-evidence-completeness-gap",
                "disposition": "adjust",
                "reason": "Effect report evidence completeness dropped below the required threshold.",
                "evidence_refs": after_metrics["evidence_refs"],
            }
        )

    if after_metrics["overall_status"] != "pass":
        backlog_candidates.append(
            {
                "candidate_id": "target-repo-reuse-after-run-failed",
                "disposition": "retire",
                "reason": "Latest target run is not passing after inherited controls and allowed overrides were applied.",
                "evidence_refs": after_metrics["evidence_refs"],
            }
        )

    if (kpi_record.get("problem_run_rate") or 0.0) > 0:
        backlog_candidates.append(
            {
                "candidate_id": "target-repo-reuse-historical-problem-trace",
                "disposition": "adjust",
                "reason": "Rolling KPI window still records problem runs that must stay tracked as backlog candidates.",
                "closure_boundary": {
                    "current_success_claim": "latest run may pass while historical problem traces remain open",
                    "close_when": "rolling KPI window ages out or supersedes the last problem trace under the documented retention rule",
                    "claim_guard": "do not collapse historical failures into the current pass-state claim",
                },
                "evidence_refs": [ref for ref in [kpi_record.get("latest_problem_evidence_ref")] if isinstance(ref, str)],
            }
        )

    if after_metrics["overall_status"] == "pass" and not backlog_candidates:
        return "promote", backlog_candidates
    if after_metrics["overall_status"] == "pass":
        return "adjust", backlog_candidates
    return "retire", backlog_candidates


def build_effect_report(*, target: str, runs_root: Path = DEFAULT_RUNS_ROOT, output_path: Path | None = None) -> dict[str, Any]:
    entries = _load_runs(target, runs_root)
    if len(entries) < 2:
        raise ValueError(f"at least two run files are required for target {target}: {runs_root}")

    entries.sort(key=lambda item: item["timestamp"])
    baseline_entry = entries[0]
    after_entry = entries[-1]
    baseline_metrics = _extract_metrics(baseline_entry)
    after_metrics = _extract_metrics(after_entry)

    kpi_snapshot = export_target_repo_speed_kpi(target_repo_runs_root=runs_root, window_kind="rolling", window_size=5)
    kpi_record = next((asdict(record) for record in kpi_snapshot.records if record.target == target), None)
    if kpi_record is None:
        raise ValueError(f"rolling KPI record not found for target {target}")

    decision, backlog_candidates = _decision_for(after_metrics, kpi_record)
    historical_problem_trace_policy = {
        "window_kind": "rolling",
        "window_size": 5,
        "keep_backlog_candidate_when_problem_run_rate_gt": 0.0,
        "close_when": "problem_run_rate == 0 and no latest_problem_run_ref remains inside the active rolling window",
        "claim_guard": "do not collapse historical failures into the current pass-state claim",
    }
    report = {
        "schema_version": "1.0",
        "report_kind": "target_repo_reuse_effect_feedback",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": target,
        "runs_root": str(runs_root),
        "baseline_run_ref": baseline_entry["path"].name,
        "after_run_ref": after_entry["path"].name,
        "baseline_metrics": baseline_metrics,
        "after_metrics": after_metrics,
        "rolling_kpi": kpi_record,
        "decision": decision,
        "backlog_candidates": backlog_candidates,
        "historical_problem_trace_policy": historical_problem_trace_policy,
        "comparison": {
            "overall_status_changed": baseline_metrics["overall_status"] != after_metrics["overall_status"],
            "adapter_tier_changed": baseline_metrics["adapter_tier"] != after_metrics["adapter_tier"],
            "entrypoint_policy_added": (not baseline_metrics["required_entrypoint_policy_present"])
            and after_metrics["required_entrypoint_policy_present"],
            "evidence_completeness_delta": round(
                after_metrics["evidence_completeness_ratio"] - baseline_metrics["evidence_completeness_ratio"], 4
            ),
        },
        "verifier_ref": "python scripts/verify-target-repo-reuse-effect-report.py",
    }

    resolved_output = output_path or (runs_root / f"effect-report-{target}.json")
    resolved_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an operator-facing target repo reuse effect feedback report.")
    parser.add_argument("--target", required=True)
    parser.add_argument("--runs-root", default=str(DEFAULT_RUNS_ROOT))
    parser.add_argument("--output")
    args = parser.parse_args()

    report = build_effect_report(
        target=args.target,
        runs_root=Path(args.runs_root).resolve(strict=False),
        output_path=Path(args.output).resolve(strict=False) if args.output else None,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
