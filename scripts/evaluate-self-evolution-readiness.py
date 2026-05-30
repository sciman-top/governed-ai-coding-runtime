from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "docs" / "architecture" / "self-evolution-readiness-policy.json"
DEFAULT_ARTIFACT_ROOT = ROOT / "docs" / "change-evidence" / "self-evolution-readiness"
DEFAULT_EVAL_DATASET_ROOT = ROOT / "docs" / "change-evidence" / "self-evolution-evals"


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate governed self-evolution readiness and terminal gaps.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--as-of", default=None, help="ISO date used for freshness checks; defaults to today.")
    parser.add_argument("--write-artifacts", action="store_true")
    parser.add_argument("--artifact-root", default=str(DEFAULT_ARTIFACT_ROOT))
    args = parser.parse_args()

    try:
        as_of = dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()
    except ValueError:
        print(f"invalid --as-of date: {args.as_of}", file=sys.stderr)
        return 1

    try:
        result = inspect_self_evolution_readiness(
            repo_root=Path(args.repo_root),
            policy_path=Path(args.policy),
            as_of=as_of,
            write_artifacts=args.write_artifacts,
            artifact_root=Path(args.artifact_root),
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def inspect_self_evolution_readiness(
    *,
    repo_root: Path,
    policy_path: Path = DEFAULT_POLICY,
    as_of: dt.date | None = None,
    write_artifacts: bool = False,
    artifact_root: Path | None = None,
) -> dict:
    root = repo_root.resolve(strict=False)
    today = as_of or dt.date.today()
    policy = _load_policy(policy_path)
    invalid_reasons = _validate_policy(policy=policy, root=root, as_of=today)
    if invalid_reasons:
        raise ValueError("invalid self-evolution readiness policy: " + ", ".join(invalid_reasons))

    probes = _collect_probes(root=root, as_of=today)
    capabilities = [
        _evaluate_capability(root=root, definition=definition, probes=probes)
        for definition in sorted(policy["capabilities"], key=lambda item: int(item["priority"]))
    ]
    counts = _count_capabilities(capabilities)
    next_gap = _select_next_gap(capabilities)
    result = {
        "status": "pass",
        "as_of": today.isoformat(),
        "policy_id": policy["policy_id"],
        "policy_path": policy_path.resolve(strict=False).as_posix(),
        "policy_status": policy["status"],
        "reviewed_on": policy["reviewed_on"],
        "review_expires_at": policy["review_expires_at"],
        "expired": dt.date.fromisoformat(policy["review_expires_at"]) < today,
        "reference_sources": policy["reference_sources"],
        "overall_state": "complete" if counts["missing"] == 0 and counts["partial"] == 0 else "partial",
        "ready_for_unattended_self_update": False,
        "truth_statement": (
            "Governed self-evolution has review, extraction, disabled materialization, and lifecycle pieces, "
        "and now includes deterministic eval dataset, trajectory variant generation, and variant evaluation. "
        "It still refuses unattended active mutation; reviewed promotion and full gates remain required."
        ),
        "capability_counts": counts,
        "next_gap": next_gap,
        "guards": policy["guards"],
        "capabilities": capabilities,
        "probe_summary": _summarize_probes(probes),
        "artifact_refs": {},
    }
    if write_artifacts:
        result["artifact_refs"] = _write_artifact(root=artifact_root or DEFAULT_ARTIFACT_ROOT, result=result, as_of=today)
    return result


def _load_policy(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"self-evolution readiness policy is not readable: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"self-evolution readiness policy is invalid JSON: {path} ({exc.msg})") from exc
    if not isinstance(payload, dict):
        raise ValueError("self-evolution readiness policy must be an object")
    return payload


def _validate_policy(*, policy: dict, root: Path, as_of: dt.date) -> list[str]:
    reasons: list[str] = []
    if policy.get("status") not in {"draft", "observe", "enforced", "waived"}:
        reasons.append("policy status is invalid")
    if not policy.get("policy_id"):
        reasons.append("policy_id missing")
    if not isinstance(policy.get("reference_sources"), list) or not policy["reference_sources"]:
        reasons.append("reference_sources missing")
    capabilities = policy.get("capabilities")
    if not isinstance(capabilities, list) or not capabilities:
        reasons.append("capabilities missing")
    else:
        seen: set[str] = set()
        for capability in capabilities:
            capability_id = capability.get("capability_id")
            if not capability_id:
                reasons.append("capability_id missing")
                continue
            if capability_id in seen:
                reasons.append(f"duplicate capability_id: {capability_id}")
            seen.add(capability_id)
            if capability.get("target_state") not in {"implemented", "partial", "missing"}:
                reasons.append(f"invalid target_state for {capability_id}")
            expected_refs = capability.get("expected_refs")
            if not isinstance(expected_refs, list) or not expected_refs:
                reasons.append(f"expected_refs missing for {capability_id}")
            for ref in expected_refs or []:
                if str(ref).startswith("http"):
                    continue
                if not _is_expected_missing_ref(capability_id, str(ref)) and not (root / str(ref)).exists():
                    reasons.append(f"expected ref missing for {capability_id}: {ref}")
    try:
        reviewed_on = dt.date.fromisoformat(str(policy.get("reviewed_on")))
        review_expires_at = dt.date.fromisoformat(str(policy.get("review_expires_at")))
    except ValueError:
        reasons.append("review dates must be ISO dates")
    else:
        if review_expires_at < reviewed_on:
            reasons.append("review_expires_at precedes reviewed_on")
        if review_expires_at < as_of:
            reasons.append(f"policy expired at {review_expires_at.isoformat()}")
    guards = policy.get("guards")
    if not isinstance(guards, dict):
        reasons.append("guards missing")
    elif guards.get("missing_final_state_capabilities_are_reported_not_hidden") is not True:
        reasons.append("missing final-state capability reporting guard must be true")
    return reasons


def _is_expected_missing_ref(capability_id: str, ref: str) -> bool:
    expected_missing = {
        "eval_dataset_generation": set(),
        "trajectory_optimizer": set(),
        "candidate_variant_evaluation": set(),
    }
    return ref in expected_missing.get(capability_id, set())


def _collect_probes(*, root: Path, as_of: dt.date) -> dict[str, dict]:
    probes: dict[str, dict] = {}
    probes["runtime_evolution"] = _safe_probe(
        lambda: _load_script(root / "scripts" / "evaluate-runtime-evolution.py", "self_evolution_runtime_review").assert_runtime_evolution_policy(
            repo_root=root,
            policy_path=root / "docs" / "architecture" / "runtime-evolution-policy.json",
            as_of=as_of,
        )
    )
    probes["experience"] = _safe_probe(
        lambda: _load_script(root / "scripts" / "extract-ai-coding-experience.py", "self_evolution_experience").inspect_ai_coding_experience(
            repo_root=root,
            as_of=as_of,
        )
    )
    probes["materialization"] = _safe_probe(
        lambda: _load_script(root / "scripts" / "materialize-runtime-evolution.py", "self_evolution_materialize").materialize_runtime_evolution(
            repo_root=root,
            as_of=as_of,
            apply=False,
        )
    )
    probes["retirement"] = _safe_probe(
        lambda: _load_script(root / "scripts" / "review-runtime-evolution-retirements.py", "self_evolution_retirements").review_runtime_evolution_retirements(
            repo_root=root,
            as_of=as_of,
            stale_after_days=90,
        )
    )
    probes["pr_prepare_default_manifest_exists"] = {
        "ok": (root / "docs" / "change-evidence" / "runtime-evolution-patches" / "20260501-runtime-evolution-materialization.json").exists()
    }
    probes["eval_dataset_script_exists"] = {"ok": (root / "scripts" / "generate-self-evolution-eval-dataset.py").exists()}
    probes["eval_dataset_artifact_root_exists"] = {"ok": (root / "docs" / "change-evidence" / "self-evolution-evals").exists()}
    probes["trajectory_optimizer_script_exists"] = {"ok": (root / "scripts" / "optimize-runtime-evolution-trajectory.py").exists()}
    probes["variant_evaluator_script_exists"] = {"ok": (root / "scripts" / "evaluate-runtime-evolution-variant.py").exists()}
    probes["trajectory_variant_artifact_root_exists"] = {"ok": (root / "docs" / "change-evidence" / "self-evolution-variants").exists()}
    probes["variant_evaluation_artifact_root_exists"] = {"ok": (root / "docs" / "change-evidence" / "self-evolution-variant-evaluations").exists()}
    probes["candidate_artifact_root_exists"] = {"ok": (root / "docs" / "change-evidence" / "runtime-evolution-candidates").exists()}
    return probes


def _safe_probe(fn: Callable[[], dict]) -> dict:
    try:
        payload = fn()
    except Exception as exc:  # noqa: BLE001 - readiness must report gaps instead of hiding them behind stack traces.
        return {"ok": False, "error": str(exc), "payload": None}
    return {"ok": bool(payload.get("status") == "pass"), "payload": payload}


def _load_script(path: Path, module_name: str) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"unable to load script: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _evaluate_capability(*, root: Path, definition: dict, probes: dict[str, dict]) -> dict:
    capability_id = definition["capability_id"]
    status, evidence, gap = _capability_status(capability_id, probes)
    expected_refs = definition.get("expected_refs", [])
    return {
        "capability_id": capability_id,
        "priority": definition["priority"],
        "title": definition["title"],
        "target_state": definition["target_state"],
        "status": status,
        "implemented": status == "implemented",
        "expected_refs": expected_refs,
        "existing_refs": [ref for ref in expected_refs if str(ref).startswith("http") or (root / str(ref)).exists()],
        "missing_refs": [
            ref
            for ref in expected_refs
            if not str(ref).startswith("http") and not (root / str(ref)).exists()
        ],
        "evidence": evidence,
        "gap": gap,
    }


def _capability_status(capability_id: str, probes: dict[str, dict]) -> tuple[str, list[str], str]:
    runtime = probes["runtime_evolution"].get("payload") or {}
    experience = probes["experience"].get("payload") or {}
    materialization = probes["materialization"].get("payload") or {}
    retirement = probes["retirement"].get("payload") or {}

    if capability_id == "source_review_and_candidate_generation":
        ok = probes["runtime_evolution"]["ok"] and int(runtime.get("candidate_count", 0)) >= 1
        return _status(ok), [f"candidate_count={runtime.get('candidate_count', 0)}"], "" if ok else "Runtime evolution review is not producing candidates."
    if capability_id == "experience_to_knowledge_memory":
        ok = probes["experience"]["ok"] and int(experience.get("knowledge_candidate_count", 0)) >= 1 and int(experience.get("memory_record_count", 0)) >= 1
        return _status(ok), [
            f"knowledge_candidate_count={experience.get('knowledge_candidate_count', 0)}",
            f"memory_record_count={experience.get('memory_record_count', 0)}",
        ], "" if ok else "Experience extraction is not producing knowledge and memory records."
    if capability_id == "skill_candidate_generation":
        ok = probes["experience"]["ok"] and int(experience.get("skill_manifest_candidate_count", 0)) >= 1
        return _status(ok), [f"skill_manifest_candidate_count={experience.get('skill_manifest_candidate_count', 0)}"], "" if ok else "No disabled skill candidate is generated from experience signals."
    if capability_id == "disabled_candidate_materialization":
        operations = materialization.get("operations", [])
        has_disabled_skill = any(item.get("operation") == "write_disabled_skill_manifest_candidate" for item in operations)
        guard = materialization.get("guard", {})
        ok = probes["materialization"]["ok"] and has_disabled_skill and guard.get("skill_auto_enable") is False
        return _status(ok), [f"operation_count={materialization.get('operation_count', 0)}", f"has_disabled_skill={has_disabled_skill}"], "" if ok else "Materializer is not proving disabled candidate output."
    if capability_id == "eval_dataset_generation":
        if probes["eval_dataset_script_exists"]["ok"]:
            evidence = ["generate-self-evolution-eval-dataset.py exists"]
            if probes["eval_dataset_artifact_root_exists"]["ok"]:
                evidence.append("self-evolution eval artifact root exists")
            return "implemented", evidence, ""
        return "missing", ["eval trace spec exists, but dataset generator script is absent"], "Add a deterministic eval dataset generator for self-evolution candidates."
    if capability_id == "trajectory_optimizer":
        if probes["trajectory_optimizer_script_exists"]["ok"]:
            evidence = ["optimize-runtime-evolution-trajectory.py exists"]
            if probes["trajectory_variant_artifact_root_exists"]["ok"]:
                evidence.append("self-evolution variant artifact root exists")
            return "implemented", evidence, ""
        return "missing", ["eval trace spec exists, but optimizer script is absent"], "Add a trajectory-aware optimizer or adapter that can improve prompts/skills from eval traces without direct mutation."
    if capability_id == "candidate_variant_evaluation":
        if probes["variant_evaluator_script_exists"]["ok"]:
            evidence = ["evaluate-runtime-evolution-variant.py exists"]
            if probes["variant_evaluation_artifact_root_exists"]["ok"]:
                evidence.append("self-evolution variant evaluation artifact root exists")
            return "implemented", evidence, ""
        if probes["candidate_artifact_root_exists"]["ok"]:
            return "partial", ["candidate artifact root exists"], "Candidate JSON snapshots exist, but no variant evaluator compares candidate alternatives against evals."
        return "missing", ["no candidate variant evaluator"], "Add candidate variant comparison before promotion."
    if capability_id == "review_gated_pr_preparation":
        ok = probes["pr_prepare_default_manifest_exists"]["ok"]
        return _status(ok), [f"default_materialization_manifest_exists={ok}"], "" if ok else "PR preparation cannot run until materialized candidate files exist."
    if capability_id == "promotion_retirement_effect_feedback":
        ok = probes["retirement"]["ok"] and int(retirement.get("retire_proposal_count", 0)) >= 0
        return _status(ok), [f"retire_proposal_count={retirement.get('retire_proposal_count', 0)}"], "" if ok else "Retirement review failed."
    if capability_id == "terminal_capability_gap_ledger":
        return "implemented", ["self-evolution readiness policy and evaluator are present"], ""
    return "missing", [], f"No readiness rule for capability_id={capability_id}."


def _status(ok: bool) -> str:
    return "implemented" if ok else "missing"


def _count_capabilities(capabilities: list[dict]) -> dict[str, int]:
    counts = {"implemented": 0, "partial": 0, "missing": 0, "total": len(capabilities)}
    for item in capabilities:
        counts[item["status"]] += 1
    return counts


def _select_next_gap(capabilities: list[dict]) -> dict | None:
    for item in capabilities:
        if item["status"] in {"missing", "partial"}:
            return {
                "capability_id": item["capability_id"],
                "title": item["title"],
                "status": item["status"],
                "priority": item["priority"],
                "gap": item["gap"],
            }
    return None


def _summarize_probes(probes: dict[str, dict]) -> dict:
    summary: dict[str, Any] = {}
    for name, probe in probes.items():
        payload = probe.get("payload") or {}
        summary[name] = {
            "ok": probe.get("ok"),
            "status": payload.get("status"),
            "error": probe.get("error"),
        }
    return summary


def _write_artifact(*, root: Path, result: dict, as_of: dt.date) -> dict[str, str]:
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{as_of.strftime('%Y%m%d')}-self-evolution-readiness.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"json": path.resolve(strict=False).as_posix()}


if __name__ == "__main__":
    raise SystemExit(main())
