from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "docs" / "architecture" / "governance-hub-certification.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build governance hub certification with effect metrics.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    args = parser.parse_args()

    try:
        result = build_governance_hub_certification(repo_root=Path(args.repo_root), config_path=Path(args.config))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


def build_governance_hub_certification(*, repo_root: Path, config_path: Path) -> dict[str, Any]:
    repo_root = repo_root.resolve(strict=False)
    config = _load_json(config_path)
    _require_string(config, "report_output_ref")
    output_path = repo_root / config["report_output_ref"]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    missing_artifact_refs = [ref for ref in _string_list(config.get("required_artifact_refs")) if not (repo_root / ref).exists()]
    missing_host_statement_refs = _collect_missing_statement_refs(repo_root, config.get("host_statement_refs"))

    capability = _load_script(repo_root / "scripts" / "verify-capability-portfolio.py", "verify_capability_portfolio_gap139")
    current_source = _load_script(
        repo_root / "scripts" / "verify-current-source-compatibility.py",
        "verify_current_source_compatibility_gap139",
    )
    knowledge = _load_script(
        repo_root / "scripts" / "verify-knowledge-memory-lifecycle.py",
        "verify_knowledge_memory_lifecycle_gap139",
    )
    promotion = _load_script(
        repo_root / "scripts" / "verify-promotion-lifecycle.py",
        "verify_promotion_lifecycle_gap139",
    )
    evolution = _load_script(repo_root / "scripts" / "evaluate-runtime-evolution.py", "evaluate_runtime_evolution_gap139")
    experience = _load_script(repo_root / "scripts" / "extract-ai-coding-experience.py", "extract_ai_coding_experience_gap139")
    effect = _load_script(
        repo_root / "scripts" / "verify-target-repo-reuse-effect-report.py",
        "verify_target_repo_reuse_effect_gap139",
    )
    audit = _load_script(
        repo_root / "scripts" / "verify-policy-tool-credential-audit.py",
        "verify_policy_tool_credential_audit_gap139",
    )

    portfolio_result = capability.verify_capability_portfolio(repo_root=repo_root, portfolio_path=repo_root / config["portfolio_ref"])
    current_source_result = current_source.assert_current_source_compatibility(
        repo_root=repo_root,
        policy_path=repo_root / "docs" / "architecture" / "current-source-compatibility-policy.json",
        as_of=date.today(),
    )
    knowledge_result = knowledge.verify_knowledge_memory_lifecycle(repo_root=repo_root, as_of=date.today())
    promotion_result = promotion.verify_promotion_lifecycle(repo_root=repo_root, as_of=date.today())
    evolution_result = evolution.assert_runtime_evolution_policy(
        repo_root=repo_root,
        policy_path=repo_root / "docs" / "architecture" / "runtime-evolution-policy.json",
        as_of=date.today(),
        write_artifacts=False,
        artifact_root=repo_root / ".runtime" / "artifacts" / "runtime-evolution",
        online_source_check=False,
    )
    experience_result = experience.inspect_ai_coding_experience(repo_root=repo_root, as_of=date.today(), write_artifacts=False)
    effect_result = effect.inspect_effect_report(
        report_path=repo_root / config["effect_feedback_ref"],
        runs_root=repo_root / "docs" / "change-evidence" / "target-repo-runs",
    )
    audit_result = audit.inspect_policy_tool_credential_audit(repo_root=repo_root)
    raw_effect_report = _load_json(repo_root / config["effect_feedback_ref"])
    portfolio_payload = _load_json(repo_root / config["portfolio_ref"])
    audit_report_payload = _load_json(repo_root / config["policy_audit_ref"])
    repo_map_artifact = _load_json(repo_root / "docs" / "change-evidence" / "repo-map-context-artifact.json")

    outcome_counter = Counter(
        str(entry.get("lifecycle_outcome")).strip()
        for entry in portfolio_payload.get("entries", [])
        if isinstance(entry, dict) and str(entry.get("lifecycle_outcome", "")).strip()
    )
    required_outcomes = set(_string_list(config.get("required_outcomes")))
    missing_outcomes = sorted(required_outcomes - set(outcome_counter))
    special_entries_without_future_trigger = sorted(
        str(entry.get("id"))
        for entry in portfolio_payload.get("entries", [])
        if isinstance(entry, dict)
        and str(entry.get("lifecycle_outcome", "")).strip() in {"deprecate", "retire", "delete_candidate"}
        and not entry.get("future_trigger")
    )

    loop_status = {
        "review_loop": portfolio_result["status"] == "pass"
        and current_source_result["status"] == "pass"
        and audit_result["status"] == "pass",
        "knowledge_loop": knowledge_result["status"] == "pass",
        "capability_upgrade_loop": promotion_result["lifecycle_entry_count"] >= 1,
        "capability_cleanup_loop": promotion_result["retire_proposal_count"] >= 1 and bool(
            {"deprecate", "retire", "delete_candidate"} & set(outcome_counter)
        ),
        "controlled_evolution_loop": evolution_result["status"] == "pass" and evolution_result["candidate_count"] >= 1,
        "self_improvement_loop": experience_result["status"] == "pass"
        and experience_result["proposal_count"] >= 1
        and experience_result["knowledge_candidate_count"] >= 1
        and experience_result["pattern_candidate_count"] >= 1,
    }

    host_posture = {
        "codex_is_cooperation_host": True,
        "claude_code_is_cooperation_host": True,
        "claude_provider_boundary_enforced": True,
        "no_host_competition_claim": not missing_host_statement_refs,
    }

    final_answers = {
        "review_loop_executable": loop_status["review_loop"],
        "knowledge_loop_executable": loop_status["knowledge_loop"],
        "capability_upgrade_loop_executable": loop_status["capability_upgrade_loop"],
        "capability_cleanup_loop_executable": loop_status["capability_cleanup_loop"],
        "controlled_evolution_loop_executable": loop_status["controlled_evolution_loop"],
        "self_improvement_loop_executable": loop_status["self_improvement_loop"],
    }

    failures: list[str] = []
    if missing_artifact_refs:
        failures.append("missing_artifact_refs")
    if missing_host_statement_refs:
        failures.append("missing_host_statement_refs")
    if portfolio_result["status"] != "pass":
        failures.append("capability_portfolio_failed")
    if effect_result["status"] != "pass":
        failures.append("target_repo_effect_feedback_failed")
    if audit_result["status"] != "pass":
        failures.append("policy_tool_credential_audit_failed")
    if missing_outcomes:
        failures.append("missing_required_outcomes")
    if special_entries_without_future_trigger:
        failures.append("missing_future_trigger")
    if not all(loop_status.values()):
        failures.append("non_executable_loop")
    if raw_effect_report.get("decision") not in {"keep", "adjust"}:
        failures.append("effect_decision_not_certifiable")
    if not raw_effect_report.get("after_metrics", {}).get("evidence_complete", False):
        failures.append("effect_evidence_incomplete")
    if repo_map_artifact.get("decision") not in {"keep", "adjust"}:
        failures.append("repo_map_artifact_not_certifiable")
    if audit_report_payload.get("status") != "pass":
        failures.append("audit_report_payload_failed")

    result = {
        "status": "fail" if failures else "pass",
        "schema_version": config.get("schema_version"),
        "certification_id": config.get("certification_id"),
        "reviewed_on": config.get("reviewed_on"),
        "verification_command": config.get("verification_command"),
        "report_path": output_path.resolve(strict=False).as_posix(),
        "host_posture": host_posture,
        "missing_artifact_refs": missing_artifact_refs,
        "missing_host_statement_refs": missing_host_statement_refs,
        "required_outcomes": sorted(required_outcomes),
        "outcome_counts": dict(sorted(outcome_counter.items())),
        "missing_outcomes": missing_outcomes,
        "special_entries_without_future_trigger": special_entries_without_future_trigger,
        "effect_feedback": {
          "target": raw_effect_report.get("target"),
          "decision": raw_effect_report.get("decision"),
          "backlog_candidate_count": len(raw_effect_report.get("backlog_candidates", [])),
          "after_overall_status": raw_effect_report.get("after_metrics", {}).get("overall_status"),
          "after_evidence_complete": raw_effect_report.get("after_metrics", {}).get("evidence_complete"),
          "verifier_status": effect_result["status"]
        },
        "loop_status": loop_status,
        "final_answers": final_answers,
        "verifier_results": {
            "capability_portfolio": portfolio_result,
            "current_source_compatibility": current_source_result,
            "knowledge_memory_lifecycle": knowledge_result,
            "promotion_lifecycle": promotion_result,
            "runtime_evolution": evolution_result,
            "ai_coding_experience": {
                "status": experience_result["status"],
                "proposal_count": experience_result["proposal_count"],
                "knowledge_candidate_count": experience_result["knowledge_candidate_count"],
                "pattern_candidate_count": experience_result["pattern_candidate_count"],
            },
            "target_repo_effect_feedback": effect_result,
            "policy_tool_credential_audit": audit_result,
        },
        "rollback_ref": config.get("rollback_ref"),
        "invalid_reasons": failures,
    }

    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def _load_script(path: Path, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"unable to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"json file is not readable: {path} ({exc})") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"json file is invalid: {path} ({exc.msg})") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"json object required: {path}")
    return payload


def _require_string(payload: dict[str, Any], field_name: str) -> None:
    value = payload.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            result.append(text)
    return result


def _collect_missing_statement_refs(repo_root: Path, refs: object) -> list[str]:
    if not isinstance(refs, list):
        return ["host_statement_refs"]
    missing: list[str] = []
    for item in refs:
        if not isinstance(item, dict):
            missing.append("<invalid-host-statement-ref>")
            continue
        path = str(item.get("path", "")).strip()
        contains = str(item.get("contains", "")).strip()
        target = repo_root / path
        if not path or not contains or not target.exists():
            missing.append(path or "<missing-path>")
            continue
        text = target.read_text(encoding="utf-8")
        if contains not in text:
            missing.append(path)
    return missing


if __name__ == "__main__":
    raise SystemExit(main())
