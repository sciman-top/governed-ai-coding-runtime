#!/usr/bin/env python3
"""Verify core principles are machine-enforced by active docs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "docs" / "architecture" / "core-principles-policy.json"
TEXT_EXTENSIONS = {".md", ".json", ".py", ".ps1", ".yaml", ".yml", ".txt"}

REQUIRED_PRINCIPLES = {
    "efficiency_first",
    "codex_claude_cooperation_hosts",
    "no_host_competition",
    "claude_third_party_provider_boundary",
    "external_mechanism_selective_absorption",
    "governance_hub_reusable_contract_final_state",
    "controlled_evolution_portfolio_lifecycle",
    "automation_first_outer_ai_intelligent_evolution",
    "no_automatic_mutation_without_review",
    "evidence_and_rollback_required",
    "context_budget_and_instruction_minimalism",
    "least_privilege_tool_credential_boundary",
    "measured_effect_feedback_over_claims",
    "hard_gate_order",
}

REQUIRED_PORTFOLIO_OUTCOMES = {
    "add",
    "keep",
    "improve",
    "merge",
    "deprecate",
    "retire",
    "delete_candidate",
}

REQUIRED_OUTER_AI_ALLOWED_ACTIONS = {
    "source_collection",
    "experience_extraction",
    "knowledge_candidate_generation",
    "skill_candidate_generation",
    "evolution_proposal_generation",
    "candidate_evaluation",
    "effect_feedback_analysis",
}

REQUIRED_OUTER_AI_FORBIDDEN_EFFECTIVE_ACTIONS = {
    "active_policy_mutation",
    "skill_enablement",
    "target_repo_sync",
    "push",
    "merge",
    "reviewed_evidence_deletion",
    "active_gate_deletion",
}

REQUIRED_OUTER_AI_CONTROLS = {
    "structured_candidate",
    "risk_gate",
    "machine_gate",
    "evidence_ref",
    "rollback_ref",
    "human_review_for_high_risk",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    args = parser.parse_args(argv)

    try:
        result = assert_core_principles(
            repo_root=Path(args.repo_root),
            policy_path=Path(args.policy),
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


def assert_core_principles(*, repo_root: Path, policy_path: Path) -> dict[str, object]:
    result = inspect_core_principles(repo_root=repo_root, policy_path=policy_path)
    failures: list[str] = []
    if result["missing_principles"]:
        failures.append("missing core principles: " + ", ".join(result["missing_principles"]))
    if result["missing_portfolio_outcomes"]:
        failures.append("missing portfolio outcomes: " + ", ".join(result["missing_portfolio_outcomes"]))
    if result["missing_outer_ai_allowed_actions"]:
        failures.append("missing outer AI allowed actions: " + ", ".join(result["missing_outer_ai_allowed_actions"]))
    if result["missing_outer_ai_forbidden_effective_actions"]:
        failures.append(
            "missing outer AI forbidden effective actions: "
            + ", ".join(result["missing_outer_ai_forbidden_effective_actions"])
        )
    if result["missing_outer_ai_required_controls"]:
        failures.append("missing outer AI required controls: " + ", ".join(result["missing_outer_ai_required_controls"]))
    if result["outer_ai_automatic_trigger_allowed"] is not True:
        failures.append("outer AI automatic trigger must be explicitly allowed")
    if result["missing_doc_refs"]:
        failures.append("missing doc refs: " + ", ".join(result["missing_doc_refs"]))
    if result["missing_evidence_refs"]:
        failures.append("missing evidence refs: " + ", ".join(result["missing_evidence_refs"]))
    if result["forbidden_pattern_hits"]:
        failures.append("forbidden active source patterns found: " + ", ".join(result["forbidden_pattern_hits"]))
    if result["non_enforced_principles"]:
        failures.append("non-enforced principles: " + ", ".join(result["non_enforced_principles"]))

    if failures:
        raise ValueError("; ".join(failures))
    return result


def inspect_core_principles(*, repo_root: Path, policy_path: Path) -> dict[str, object]:
    resolved_root = repo_root.resolve(strict=False)
    policy = _load_policy(policy_path)
    principle_ids = {item["principle_id"] for item in policy["principles"]}
    portfolio_outcomes = set(policy["capability_portfolio_outcomes"])
    outer_ai_controls = policy["outer_ai_evolution_controls"]
    outer_ai_allowed_actions = set(outer_ai_controls["allowed_automatic_actions"])
    outer_ai_forbidden_effective_actions = set(outer_ai_controls["forbidden_automatic_effective_actions"])
    outer_ai_required_controls = set(outer_ai_controls["required_controls"])

    missing_principles = sorted(REQUIRED_PRINCIPLES - principle_ids)
    missing_portfolio_outcomes = sorted(REQUIRED_PORTFOLIO_OUTCOMES - portfolio_outcomes)
    missing_outer_ai_allowed_actions = sorted(REQUIRED_OUTER_AI_ALLOWED_ACTIONS - outer_ai_allowed_actions)
    missing_outer_ai_forbidden_effective_actions = sorted(
        REQUIRED_OUTER_AI_FORBIDDEN_EFFECTIVE_ACTIONS - outer_ai_forbidden_effective_actions
    )
    missing_outer_ai_required_controls = sorted(REQUIRED_OUTER_AI_CONTROLS - outer_ai_required_controls)
    non_enforced_principles = sorted(
        item["principle_id"]
        for item in policy["principles"]
        if item["required"] is not True or item["machine_gate"] != "verify-core-principles"
    )
    missing_doc_refs = _collect_missing_doc_refs(resolved_root, policy["required_doc_refs"])
    missing_evidence_refs = _collect_missing_files(resolved_root, policy["evidence_refs"])
    forbidden_pattern_hits = _collect_forbidden_pattern_hits(resolved_root, policy["forbidden_active_patterns"])

    return {
        "status": "pass",
        "policy_path": policy_path.resolve(strict=False).as_posix(),
        "policy_id": policy["policy_id"],
        "policy_status": policy["status"],
        "principle_ids": sorted(principle_ids),
        "portfolio_outcomes": sorted(portfolio_outcomes),
        "outer_ai_automatic_trigger_allowed": outer_ai_controls["automatic_trigger_allowed"],
        "outer_ai_allowed_actions": sorted(outer_ai_allowed_actions),
        "outer_ai_forbidden_effective_actions": sorted(outer_ai_forbidden_effective_actions),
        "outer_ai_required_controls": sorted(outer_ai_required_controls),
        "missing_principles": missing_principles,
        "missing_portfolio_outcomes": missing_portfolio_outcomes,
        "missing_outer_ai_allowed_actions": missing_outer_ai_allowed_actions,
        "missing_outer_ai_forbidden_effective_actions": missing_outer_ai_forbidden_effective_actions,
        "missing_outer_ai_required_controls": missing_outer_ai_required_controls,
        "non_enforced_principles": non_enforced_principles,
        "missing_doc_refs": missing_doc_refs,
        "missing_evidence_refs": missing_evidence_refs,
        "forbidden_pattern_hits": forbidden_pattern_hits,
    }


def _load_policy(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"core principles policy is not readable: {path} ({exc})") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"core principles policy is invalid JSON: {path} ({exc.msg})") from exc

    if not isinstance(payload, dict):
        raise ValueError("core principles policy must be a JSON object")
    for field in ("schema_version", "policy_id", "status", "rollback_ref"):
        _require_string(payload, field)
    if payload["status"] not in {"observe", "enforced", "waived"}:
        raise ValueError("core principles status is invalid")
    _validate_principles(payload.get("principles"))
    payload["capability_portfolio_outcomes"] = _require_string_list(
        payload.get("capability_portfolio_outcomes"),
        "capability_portfolio_outcomes",
    )
    _validate_outer_ai_evolution_controls(payload.get("outer_ai_evolution_controls"))
    _validate_doc_refs(payload.get("required_doc_refs"), "required_doc_refs")
    _validate_forbidden_patterns(payload.get("forbidden_active_patterns"))
    payload["evidence_refs"] = _require_string_list(payload.get("evidence_refs"), "evidence_refs")
    return payload


def _validate_principles(value: object) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError("principles must be a non-empty list")
    seen: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"principles[{index}] must be an object")
        for field in ("principle_id", "category", "summary", "enforcement_level", "machine_gate", "rollback_ref"):
            _require_string(item, field, prefix=f"principles[{index}]")
        if item.get("required") is not True:
            raise ValueError(f"principles[{index}].required must be true")
        principle_id = item["principle_id"]
        if principle_id in seen:
            raise ValueError(f"duplicate principle_id: {principle_id}")
        seen.add(principle_id)
        if item["enforcement_level"] not in {"docs_gate", "contract_gate", "runtime_gate"}:
            raise ValueError(f"principles[{index}].enforcement_level is invalid")


def _validate_doc_refs(value: object, field_name: str) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field_name} must be a non-empty list")
    for index, ref in enumerate(value):
        if not isinstance(ref, dict):
            raise ValueError(f"{field_name}[{index}] must be an object")
        _require_string(ref, "path", prefix=f"{field_name}[{index}]")
        _require_string(ref, "contains", prefix=f"{field_name}[{index}]")


def _validate_outer_ai_evolution_controls(value: object) -> None:
    if not isinstance(value, dict):
        raise ValueError("outer_ai_evolution_controls must be an object")
    if value.get("automatic_trigger_allowed") is not True:
        raise ValueError("outer_ai_evolution_controls.automatic_trigger_allowed must be true")
    value["allowed_automatic_actions"] = _require_string_list(
        value.get("allowed_automatic_actions"),
        "outer_ai_evolution_controls.allowed_automatic_actions",
    )
    value["forbidden_automatic_effective_actions"] = _require_string_list(
        value.get("forbidden_automatic_effective_actions"),
        "outer_ai_evolution_controls.forbidden_automatic_effective_actions",
    )
    value["required_controls"] = _require_string_list(
        value.get("required_controls"),
        "outer_ai_evolution_controls.required_controls",
    )


def _validate_forbidden_patterns(value: object) -> None:
    if not isinstance(value, list) or not value:
        raise ValueError("forbidden_active_patterns must be a non-empty list")
    for index, guard in enumerate(value):
        if not isinstance(guard, dict):
            raise ValueError(f"forbidden_active_patterns[{index}] must be an object")
        _require_string(guard, "pattern", prefix=f"forbidden_active_patterns[{index}]")
        _require_string_list(guard.get("scan_roots"), f"forbidden_active_patterns[{index}].scan_roots")


def _collect_missing_doc_refs(repo_root: Path, refs: list[dict]) -> list[str]:
    missing: list[str] = []
    for ref in refs:
        path = repo_root / ref["path"]
        if not path.exists():
            missing.append(f"{ref['path']}:missing")
            continue
        text = path.read_text(encoding="utf-8")
        if ref["contains"] not in text:
            missing.append(f"{ref['path']}:missing-token")
    return missing


def _collect_missing_files(repo_root: Path, refs: list[str]) -> list[str]:
    return sorted(ref for ref in refs if not (repo_root / ref).exists())


def _collect_forbidden_pattern_hits(repo_root: Path, guards: list[dict]) -> list[str]:
    hits: list[str] = []
    for guard in guards:
        pattern = guard["pattern"]
        for path in _iter_scan_files(repo_root, guard["scan_roots"]):
            if path.name == "core-principles-policy.json":
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if pattern in text:
                hits.append(f"{path.relative_to(repo_root).as_posix()}::{pattern}")
    return sorted(hits)


def _iter_scan_files(repo_root: Path, scan_roots: list[str]):
    for root_ref in scan_roots:
        root = repo_root / root_ref
        if root.is_file():
            if root.suffix.lower() in TEXT_EXTENSIONS:
                yield root
            continue
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in {".git", ".pytest_cache", ".runtime"} for part in path.parts):
                continue
            if path.suffix.lower() in TEXT_EXTENSIONS:
                yield path


def _require_string(payload: dict, field: str, *, prefix: str | None = None) -> str:
    value = payload.get(field)
    label = f"{prefix}.{field}" if prefix else field
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    return value


def _require_string_list(value: object, field_name: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field_name} must be a non-empty list")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{field_name} must contain non-empty strings")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
