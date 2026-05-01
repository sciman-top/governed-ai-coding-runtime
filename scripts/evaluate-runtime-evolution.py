from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "docs" / "architecture" / "runtime-evolution-policy.json"
DEFAULT_ARTIFACT_ROOT = ROOT / ".runtime" / "artifacts" / "runtime-evolution"
VALID_STATUS = {"draft", "observe", "enforced", "waived"}
VALID_ACTIONS = {"add", "modify", "delete", "defer", "no_action"}
VALID_RISKS = {"low", "medium", "high"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate runtime self-evolution review policy.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--as-of", default=None, help="ISO date used for freshness checks; defaults to today.")
    parser.add_argument("--write-artifacts", action="store_true", help="Write JSON and Markdown dry-run artifacts.")
    parser.add_argument("--artifact-root", default=str(DEFAULT_ARTIFACT_ROOT))
    parser.add_argument(
        "--online-source-check",
        action="store_true",
        help="Attempt lightweight online source checks; failures are recorded in dry-run output.",
    )
    args = parser.parse_args()

    try:
        as_of = dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()
    except ValueError:
        print(f"invalid --as-of date: {args.as_of}", file=sys.stderr)
        return 1

    try:
        result = assert_runtime_evolution_policy(
            repo_root=Path(args.repo_root),
            policy_path=Path(args.policy),
            as_of=as_of,
            write_artifacts=args.write_artifacts,
            artifact_root=Path(args.artifact_root),
            online_source_check=args.online_source_check,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def assert_runtime_evolution_policy(
    *,
    repo_root: Path,
    policy_path: Path,
    as_of: dt.date | None = None,
    write_artifacts: bool = False,
    artifact_root: Path | None = None,
    online_source_check: bool = False,
) -> dict:
    result = inspect_runtime_evolution_policy(
        repo_root=repo_root,
        policy_path=policy_path,
        as_of=as_of,
        write_artifacts=write_artifacts,
        artifact_root=artifact_root,
        online_source_check=online_source_check,
    )
    failures: list[str] = []
    if result["invalid_reasons"]:
        failures.append("invalid runtime evolution policy: " + ", ".join(result["invalid_reasons"]))
    if result["missing_required_refs"]:
        failures.append("missing required refs: " + ", ".join(result["missing_required_refs"]))
    if result["expired"]:
        failures.append(
            f"runtime evolution policy expired at {result['review_expires_at']}; run a fresh evolution review"
        )
    if result["candidate_count"] < 1:
        failures.append("runtime evolution review must produce at least one candidate")

    if failures:
        raise ValueError("; ".join(failures))
    return result


def inspect_runtime_evolution_policy(
    *,
    repo_root: Path,
    policy_path: Path,
    as_of: dt.date | None = None,
    write_artifacts: bool = False,
    artifact_root: Path | None = None,
    online_source_check: bool = False,
) -> dict:
    resolved_root = repo_root.resolve(strict=False)
    policy = _load_policy(policy_path)
    today = as_of or dt.date.today()
    reviewed_on = _parse_iso_date(policy["reviewed_on"], "reviewed_on")
    review_expires_at = _parse_iso_date(policy["review_expires_at"], "review_expires_at")
    if reviewed_on > review_expires_at:
        raise ValueError("reviewed_on must be on or before review_expires_at")

    review_age_days = (today - reviewed_on).days
    stale = review_age_days > int(policy["stale_after_days"])
    source_records = _build_source_records(
        policy=policy,
        repo_root=resolved_root,
        as_of=today,
        online_source_check=online_source_check,
    )
    evidence_snapshot = _build_evidence_snapshot(repo_root=resolved_root, as_of=today)
    candidates = _build_candidates(
        policy=policy,
        source_records=source_records,
        stale=stale,
        as_of=today,
        evidence_snapshot=evidence_snapshot,
    )
    invalid_reasons = _collect_invalid_reasons(policy, candidates)
    missing_required_refs = _collect_missing_required_refs(resolved_root, policy)

    result = {
        "status": "pass",
        "policy_path": policy_path.resolve(strict=False).as_posix(),
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "reviewed_on": reviewed_on.isoformat(),
        "review_expires_at": review_expires_at.isoformat(),
        "as_of": today.isoformat(),
        "stale_after_days": policy["stale_after_days"],
        "review_age_days": review_age_days,
        "stale": stale,
        "expired": policy["status"] == "enforced" and review_expires_at < today,
        "mode": "dry_run",
        "online_source_check": online_source_check,
        "mutation_allowed": False,
        "source_count": len(source_records),
        "candidate_count": len(candidates),
        "source_records": source_records,
        "evidence_snapshot": evidence_snapshot,
        "candidates": candidates,
        "invalid_reasons": invalid_reasons,
        "missing_required_refs": missing_required_refs,
        "artifact_refs": {},
    }

    if write_artifacts:
        root = artifact_root or DEFAULT_ARTIFACT_ROOT
        result["artifact_refs"] = _write_artifacts(root=root, result=result, as_of=today)

    return result


def _load_policy(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"runtime evolution policy is not readable: {path} ({exc})") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"runtime evolution policy is invalid JSON: {path} ({exc.msg})") from exc

    if not isinstance(payload, dict):
        raise ValueError("runtime evolution policy must be a JSON object")
    for field in ("policy_id", "status", "reviewed_on", "review_expires_at", "decision_claim", "rollback_ref"):
        _require_string(payload, field)
    if payload["status"] not in VALID_STATUS:
        raise ValueError("runtime evolution policy status is invalid")
    if not isinstance(payload.get("stale_after_days"), int) or payload["stale_after_days"] < 1:
        raise ValueError("stale_after_days must be a positive integer")
    for field in (
        "source_priority",
        "source_catalog",
        "candidate_actions",
        "candidate_required_fields",
        "add_or_modify_criteria",
        "delete_or_retire_criteria",
        "verification_floor",
        "invariants",
        "planned_artifacts",
    ):
        if not isinstance(payload.get(field), list) or not payload[field]:
            raise ValueError(f"{field} must be a non-empty list")
    for action in payload["candidate_actions"]:
        if action not in VALID_ACTIONS:
            raise ValueError(f"candidate action is invalid: {action}")
    if not isinstance(payload.get("risk_automation_boundaries"), dict):
        raise ValueError("risk_automation_boundaries must be an object")
    for risk in VALID_RISKS:
        _require_string(payload["risk_automation_boundaries"], risk, prefix="risk_automation_boundaries")
    return payload


def _build_source_records(
    *,
    policy: dict,
    repo_root: Path,
    as_of: dt.date,
    online_source_check: bool,
) -> list[dict]:
    records: list[dict] = []
    for item in sorted(policy["source_priority"], key=lambda value: int(value["priority"])):
        priority = int(item["priority"])
        source_type = item["source_type"]
        records.append(
            {
                "source_id": f"policy-source-{priority}",
                "source_type": source_type,
                "source_ref": source_type,
                "source_checked_on": as_of.isoformat(),
                "summary": item["use"],
                "confidence": "high" if priority <= 2 else "medium",
                "retrieval_mode": "dry_run_no_network",
            }
        )

    local_source_types = {"internal_ai_coding_experience"}
    for item in policy["source_catalog"]:
        for field in ("source_id", "source_type", "source_ref", "summary"):
            _require_string(item, field, prefix="source_catalog[]")
        source_ref = item["source_ref"]
        local_ref_exists = (repo_root / source_ref).exists() if item["source_type"] in local_source_types else None
        online_probe = (
            _probe_online_source(source_ref)
            if online_source_check and item["source_type"] not in local_source_types
            else None
        )
        records.append(
            {
                "source_id": item["source_id"],
                "source_type": item["source_type"],
                "source_ref": source_ref,
                "source_checked_on": as_of.isoformat(),
                "summary": item["summary"],
                "confidence": _source_confidence(item["source_type"], local_ref_exists),
                "retrieval_mode": (
                    "local_file_check"
                    if item["source_type"] in local_source_types
                    else "online_probe"
                    if online_source_check
                    else "dry_run_catalog"
                ),
                "local_ref_exists": local_ref_exists,
                "online_probe": online_probe,
            }
        )

    internal_refs = [
        "docs/architecture/current-source-compatibility-policy.json",
        "docs/architecture/ltp-autonomous-promotion-policy.json",
        "docs/architecture/autonomous-next-work-selection-policy.json",
        "docs/change-evidence/20260501-runtime-evolution-planning.md",
    ]
    for ref in internal_refs:
        records.append(
            {
                "source_id": "internal-" + Path(ref).stem.replace(".", "-"),
                "source_type": "internal_runtime_evidence",
                "source_ref": ref,
                "source_checked_on": as_of.isoformat(),
                "summary": "Internal policy or evidence file exists." if (repo_root / ref).exists() else "Internal file missing.",
                "confidence": "high" if (repo_root / ref).exists() else "low",
                "retrieval_mode": "local_file_check",
            }
        )
    return records


def _probe_online_source(source_ref: str) -> dict:
    request = Request(source_ref, method="GET", headers={"User-Agent": "governed-ai-coding-runtime-evolution/0.1"})
    try:
        with urlopen(request, timeout=8) as response:
            return {
                "status": "ok",
                "http_status": response.status,
                "content_type": response.headers.get("content-type", ""),
            }
    except HTTPError as exc:
        return {
            "status": "http_error",
            "http_status": exc.code,
            "error": str(exc),
        }
    except (OSError, URLError) as exc:
        return {
            "status": "platform_na",
            "reason": "online_source_unavailable",
            "error": str(exc),
        }


def _source_confidence(source_type: str, local_ref_exists: bool | None) -> str:
    if source_type == "official_doc_or_changelog":
        return "high"
    if source_type == "internal_ai_coding_experience":
        return "high" if local_ref_exists else "low"
    return "medium"


def _load_script_module(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"unable to load helper module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _build_evidence_snapshot(*, repo_root: Path, as_of: dt.date) -> dict[str, dict]:
    snapshots: dict[str, dict] = {}

    current_source_module = _load_script_module(
        repo_root / "scripts" / "verify-current-source-compatibility.py",
        "verify_current_source_compatibility_evolution",
    )
    current_source = current_source_module.inspect_current_source_compatibility(
        repo_root=repo_root,
        policy_path=repo_root / "docs" / "architecture" / "current-source-compatibility-policy.json",
        as_of=as_of,
    )
    snapshots["current_source"] = {
        "status": current_source["status"],
        "expired": bool(current_source["expired"]),
        "missing_doc_refs": list(current_source["missing_doc_refs"]),
        "missing_evidence_refs": list(current_source["missing_evidence_refs"]),
        "forbidden_pattern_hits": list(current_source["forbidden_pattern_hits"]),
        "protocols_missing_kernel_semantics": list(current_source["protocols_missing_kernel_semantics"]),
        "review_expires_at": current_source["review_expires_at"],
    }

    host_feedback_module = _load_script_module(
        repo_root / "scripts" / "host-feedback-summary.py",
        "host_feedback_summary_evolution",
    )
    host_feedback = host_feedback_module.build_host_feedback_summary(repo_root=repo_root, max_target_runs=5)
    target_runs_details = next(
        (
            item.get("details", {})
            for item in host_feedback.get("dimensions", [])
            if isinstance(item, dict) and item.get("dimension_id") == "target_runs"
        ),
        {},
    )
    snapshots["host_feedback"] = {
        "status": host_feedback["status"],
        "target_run_freshness": target_runs_details.get("freshness_status"),
        "stale_latest_runs": list(target_runs_details.get("stale_latest_runs", [])),
        "recommendation_count": len(host_feedback.get("recommendations", [])),
        "codex_host_status": host_feedback.get("summary", {}).get("codex_host_status"),
        "claude_host_status": host_feedback.get("summary", {}).get("claude_host_status"),
        "claude_workload_status": host_feedback.get("summary", {}).get("claude_workload_status"),
    }

    effect_module = _load_script_module(
        repo_root / "scripts" / "verify-target-repo-reuse-effect-report.py",
        "verify_target_repo_effect_evolution",
    )
    effect_feedback = effect_module.inspect_effect_report()
    snapshots["effect_feedback"] = {
        "status": effect_feedback["status"],
        "decision": effect_feedback.get("decision"),
        "target": effect_feedback.get("target"),
        "backlog_candidate_count": int(effect_feedback.get("backlog_candidate_count", 0)),
        "error_count": len(effect_feedback.get("errors", [])),
        "errors": list(effect_feedback.get("errors", [])),
    }

    ai_experience_module = _load_script_module(
        repo_root / "scripts" / "extract-ai-coding-experience.py",
        "extract_ai_coding_experience_evolution",
    )
    ai_experience = ai_experience_module.inspect_ai_coding_experience(repo_root=repo_root, as_of=as_of)
    snapshots["ai_coding_experience"] = {
        "status": ai_experience["status"],
        "proposal_count": int(ai_experience["proposal_count"]),
        "knowledge_candidate_count": int(ai_experience["knowledge_candidate_count"]),
        "pattern_candidate_count": int(ai_experience["pattern_candidate_count"]),
        "skill_manifest_candidate_count": int(ai_experience["skill_manifest_candidate_count"]),
        "retirement_record_count": int(ai_experience["retirement_record_count"]),
        "invalid_reasons": list(ai_experience["invalid_reasons"]),
    }

    return snapshots


def _build_candidates(
    *,
    policy: dict,
    source_records: list[dict],
    stale: bool,
    as_of: dt.date,
    evidence_snapshot: dict[str, dict],
) -> list[dict]:
    candidates: list[dict] = []
    current_source = evidence_snapshot["current_source"]
    if stale or current_source["expired"]:
        candidates.append(
            {
                "candidate_id": "EVOL-REVIEW-FRESHNESS",
                "source_type": "internal_runtime_evidence",
                "source_ref": "docs/architecture/runtime-evolution-policy.json",
                "source_checked_on": as_of.isoformat(),
                "observed_change": "Runtime evolution review or current-source compatibility review has crossed its freshness boundary.",
                "repo_impact": "Keeps self-evolution claims tied to fresh policy review instead of stale timing assumptions.",
                "proposed_action": "modify",
                "risk_level": "low",
                "evidence_required": [
                    "runtime evolution policy",
                    "current-source compatibility policy",
                    "candidate dry-run artifact",
                ],
                "acceptance_gates": policy["verification_floor"],
                "rollback_plan": policy["rollback_ref"],
                "patch_plan": [
                    {
                        "path": "docs/architecture/runtime-evolution-policy.json",
                        "operation": "refresh reviewed_on/review_expires_at only after a new review artifact exists",
                        "apply_mode": "manual_or_future_low_risk_only",
                    },
                    {
                        "path": "docs/architecture/current-source-compatibility-policy.json",
                        "operation": "refresh current-source review when official host or protocol assumptions age out",
                        "apply_mode": "manual_or_future_low_risk_only",
                    },
                ],
                "decision": "refresh_review",
            }
        )

    if (
        current_source["missing_doc_refs"]
        or current_source["missing_evidence_refs"]
        or current_source["forbidden_pattern_hits"]
        or current_source["protocols_missing_kernel_semantics"]
    ):
        candidates.append(
            {
                "candidate_id": "EVOL-SOURCE-COMPATIBILITY",
                "source_type": "official_doc_or_changelog",
                "source_ref": "docs/architecture/current-source-compatibility-policy.json",
                "source_checked_on": as_of.isoformat(),
                "observed_change": "Current-source compatibility signals missing references or forbidden claim drift in active docs.",
                "repo_impact": "Prevents stale host or protocol assumptions from silently widening runtime claims.",
                "proposed_action": "modify",
                "risk_level": "medium",
                "evidence_required": [
                    "current-source compatibility verifier output",
                    "required doc/evidence references",
                    "claim-drift remediation evidence",
                ],
                "acceptance_gates": [
                    "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs"
                ],
                "rollback_plan": "revert current-source compatibility policy or docs updates that introduced the drift",
                "patch_plan": [
                    {
                        "path": "docs/architecture/current-source-compatibility-policy.json",
                        "operation": "restore required boundary refs and review metadata",
                        "apply_mode": "manual_repair_first",
                    }
                ],
                "decision": "repair_source_compatibility",
            }
        )

    host_feedback = evidence_snapshot["host_feedback"]
    if host_feedback["status"] != "pass" or host_feedback["target_run_freshness"] == "stale":
        candidates.append(
            {
                "candidate_id": "EVOL-HOST-FEEDBACK",
                "source_type": "internal_runtime_evidence",
                "source_ref": ".runtime/artifacts/host-feedback-summary/latest.md",
                "source_checked_on": as_of.isoformat(),
                "observed_change": "Host feedback or target-run freshness shows attention-level posture.",
                "repo_impact": "Keeps self-evolution prompts aligned with real host degradation and stale target workload evidence.",
                "proposed_action": "modify",
                "risk_level": "low",
                "evidence_required": [
                    "host feedback summary",
                    "latest target repo runs",
                    "operator-facing recommendation surface",
                ],
                "acceptance_gates": [
                    "python scripts/host-feedback-summary.py --assert-minimum",
                    "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs",
                ],
                "rollback_plan": "remove host-feedback-driven candidate wiring if it misclassifies freshness or host posture",
                "patch_plan": [
                    {
                        "path": "scripts/host-feedback-summary.py",
                        "operation": "refresh host and target-run evidence before promoting new implementation work",
                        "apply_mode": "manual_or_future_low_risk_only",
                    }
                ],
                "decision": "refresh_host_feedback",
            }
        )

    effect_feedback = evidence_snapshot["effect_feedback"]
    if effect_feedback["status"] != "pass" or effect_feedback["backlog_candidate_count"] > 0:
        proposed_action = "delete" if effect_feedback.get("decision") == "retire" else "modify"
        decision = "retire_low_value_capability" if proposed_action == "delete" else "improve_target_effect_loop"
        candidates.append(
            {
                "candidate_id": "EVOL-EFFECT-FEEDBACK",
                "source_type": "internal_runtime_evidence",
                "source_ref": "docs/change-evidence/target-repo-runs/effect-report-classroomtoolkit.json",
                "source_checked_on": as_of.isoformat(),
                "observed_change": "Target repo effect feedback still carries unresolved backlog candidates or verifier errors.",
                "repo_impact": "Turns real target repo effect gaps into explicit evolution work instead of leaving them in report-only form.",
                "proposed_action": proposed_action,
                "risk_level": "medium",
                "evidence_required": [
                    "target repo reuse effect report",
                    "backlog candidates with reason and disposition",
                    "fresh daily target-run evidence",
                ],
                "acceptance_gates": policy["verification_floor"],
                "rollback_plan": "revert any follow-up change that was justified only by stale or misread target effect feedback",
                "patch_plan": [
                    {
                        "path": "docs/change-evidence/target-repo-runs/effect-report-classroomtoolkit.json",
                        "operation": "refresh effect report and translate remaining candidates into bounded follow-up work",
                        "apply_mode": "manual_or_future_low_risk_only",
                    }
                ],
                "decision": decision,
            }
        )

    ai_experience = evidence_snapshot["ai_coding_experience"]
    if ai_experience["proposal_count"] > 0 or ai_experience["retirement_record_count"] > 0:
        proposed_action = "delete" if ai_experience["retirement_record_count"] > 0 and ai_experience["proposal_count"] == 0 else "add"
        candidates.append(
            {
                "candidate_id": "EVOL-AI-EXPERIENCE",
                "source_type": "internal_ai_coding_experience",
                "source_ref": ".runtime/artifacts/ai-coding-experience/20260501-ai-coding-experience-review.json",
                "source_checked_on": as_of.isoformat(),
                "observed_change": "AI coding evidence now contains reusable proposals, knowledge candidates, or retirement signals.",
                "repo_impact": "Lets repeated AI coding patterns become governed proposals or cleanup candidates instead of hidden session-only know-how.",
                "proposed_action": proposed_action,
                "risk_level": "low",
                "evidence_required": [
                    "learning-efficiency metrics or interaction evidence",
                    "controlled improvement proposals",
                    "knowledge or skill candidate manifest",
                ],
                "acceptance_gates": [
                    "python -m unittest tests.runtime.test_runtime_evolution tests.runtime.test_learning_efficiency_metrics",
                    "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs",
                ],
                "rollback_plan": "remove generated AI-coding-experience candidates if their reuse value or verification posture regresses",
                "patch_plan": [
                    {
                        "path": "scripts/extract-ai-coding-experience.py",
                        "operation": "promote repeated signals into reviewable proposals and keep retirement candidate cleanup explicit",
                        "apply_mode": "proposal_only_until_reviewed" if proposed_action == "add" else "manual_or_future_low_risk_only",
                    }
                ],
                "decision": "promote_ai_experience_candidate" if proposed_action == "add" else "retire_low_value_candidate",
            }
        )

    if not any(record.get("retrieval_mode") == "online_probe" for record in source_records if isinstance(record, dict)):
        candidates.append(
            {
                "candidate_id": "EVOL-SOURCE-COLLECTOR",
                "source_type": "official_doc_or_changelog",
                "source_ref": "dry-run source inventory",
                "source_checked_on": as_of.isoformat(),
                "observed_change": "Official documentation source collection remains catalog-only unless the optional online probe is enabled.",
                "repo_impact": "Prevents community or stale assumptions from becoming execution rules without reviewable source evidence.",
                "proposed_action": "defer",
                "risk_level": "medium",
                "evidence_required": [
                    "source collection artifact",
                    "candidate evaluator artifact",
                    "platform_na record if online source is unavailable",
                ],
                "acceptance_gates": [
                    "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs"
                ],
                "rollback_plan": "remove the source collection candidate from the evolution dry-run output",
                "patch_plan": [
                    {
                        "path": "scripts/evaluate-runtime-evolution.py",
                        "operation": "promote source collection from probe-only to parsed source snapshots after schema is defined",
                        "apply_mode": "defer_until_scope_fenced",
                    }
                ],
                "decision": "implement_source_collector_before_online_fetch",
            }
        )

    if not candidates:
        candidates.append(
            {
                "candidate_id": "EVOL-KEEP-CURRENT",
                "source_type": "internal_runtime_evidence",
                "source_ref": "docs/architecture/runtime-evolution-policy.json",
                "source_checked_on": as_of.isoformat(),
                "observed_change": "All current evolution triggers are fresh and no higher-priority evidence requires change.",
                "repo_impact": "Keeps the evolution lane honest when there is nothing worth changing right now.",
                "proposed_action": "no_action",
                "risk_level": "low",
                "evidence_required": [
                    "fresh evolution review",
                    "fresh host feedback summary",
                    "passing target effect report",
                ],
                "acceptance_gates": policy["verification_floor"],
                "rollback_plan": policy["rollback_ref"],
                "patch_plan": [
                    {
                        "path": "docs/architecture/runtime-evolution-policy.json",
                        "operation": "keep current review window and wait for a stronger evidence trigger",
                        "apply_mode": "no_change_required",
                    }
                ],
                "decision": "review_current",
            }
        )

    if not source_records:
        candidates.append(
            {
                "candidate_id": "EVOL-999",
                "source_type": "internal_runtime_evidence",
                "source_ref": "source_records",
                "source_checked_on": as_of.isoformat(),
                "observed_change": "No source records were produced.",
                "repo_impact": "Evolution review cannot make decisions.",
                "proposed_action": "defer",
                "risk_level": "high",
                "evidence_required": ["source records"],
                "acceptance_gates": ["fix source collection before continuing"],
                "rollback_plan": "disable evolution review gate until source collection is restored",
                "patch_plan": [
                    {
                        "path": "scripts/evaluate-runtime-evolution.py",
                        "operation": "restore source record generation",
                        "apply_mode": "manual_repair_first",
                    }
                ],
                "decision": "blocked",
            }
        )
    return candidates


def _collect_invalid_reasons(policy: dict, candidates: list[dict]) -> list[str]:
    required = set(policy["candidate_required_fields"])
    reasons: list[str] = []
    for index, candidate in enumerate(candidates):
        missing = sorted(field for field in required if field not in candidate)
        if missing:
            reasons.append(f"candidates[{index}] missing {', '.join(missing)}")
        if candidate.get("proposed_action") not in VALID_ACTIONS:
            reasons.append(f"candidates[{index}].proposed_action is invalid")
        if candidate.get("risk_level") not in VALID_RISKS:
            reasons.append(f"candidates[{index}].risk_level is invalid")
    return reasons


def _collect_missing_required_refs(repo_root: Path, policy: dict) -> list[str]:
    refs = [
        "docs/architecture/runtime-evolution-policy.json",
        "docs/plans/runtime-evolution-review-plan.md",
        "docs/change-evidence/20260501-runtime-evolution-planning.md",
    ]
    missing = [ref for ref in refs if not (repo_root / ref).exists()]
    for command in policy["verification_floor"]:
        if "scripts/" not in command:
            continue
        script = command.split("scripts/", 1)[1].split()[0]
        script_ref = "scripts/" + script
        if not (repo_root / script_ref).exists():
            missing.append(script_ref)
    return sorted(set(missing))


def _write_artifacts(*, root: Path, result: dict, as_of: dt.date) -> dict[str, str]:
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / f"{as_of.strftime('%Y%m%d')}-runtime-evolution-review.json"
    md_path = root / f"{as_of.strftime('%Y%m%d')}-runtime-evolution-review.md"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(_render_markdown(result), encoding="utf-8")
    return {
        "json": json_path.resolve(strict=False).as_posix(),
        "markdown": md_path.resolve(strict=False).as_posix(),
    }


def _render_markdown(result: dict) -> str:
    candidate_lines = [
        f"- `{item['candidate_id']}`: `{item['proposed_action']}` / `{item['risk_level']}` / {item['decision']}"
        for item in result["candidates"]
    ]
    patch_lines = [
        f"- `{item['candidate_id']}`: " + "; ".join(
            f"{patch['path']} -> {patch['operation']} ({patch['apply_mode']})"
            for patch in item.get("patch_plan", [])
        )
        for item in result["candidates"]
    ]
    source_lines = [
        f"- `{item['source_id']}`: `{item['source_type']}` / `{item['retrieval_mode']}`"
        for item in result["source_records"]
    ]
    return (
        "# Runtime Evolution Review\n\n"
        "## Summary\n"
        f"- policy: `{result['policy_id']}`\n"
        f"- as_of: `{result['as_of']}`\n"
        f"- mode: `{result['mode']}`\n"
        f"- online_source_check: `{str(result['online_source_check']).lower()}`\n"
        f"- mutation_allowed: `{str(result['mutation_allowed']).lower()}`\n"
        f"- stale: `{str(result['stale']).lower()}`\n\n"
        "## Sources\n"
        + "\n".join(source_lines)
        + "\n\n## Candidates\n"
        + "\n".join(candidate_lines)
        + "\n\n## Patch Plan\n"
        + "\n".join(patch_lines)
        + "\n\n## Rollback\n"
        "- Remove generated runtime-evolution artifacts and revert the policy/script changes that introduced the candidate.\n"
    )


def _require_string(payload: dict, field: str, *, prefix: str | None = None) -> str:
    value = payload.get(field)
    if not isinstance(value, str) or not value.strip():
        name = f"{prefix}.{field}" if prefix else field
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _parse_iso_date(value: str, field_name: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be an ISO date") from exc


if __name__ == "__main__":
    raise SystemExit(main())
