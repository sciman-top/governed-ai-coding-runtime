from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VARIANT_EVALUATION_ROOT = ROOT / "docs" / "change-evidence" / "self-evolution-variant-evaluations"
DEFAULT_ARTIFACT_ROOT = ROOT / "docs" / "change-evidence" / "self-evolution-recommendations"


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend the next governed self-evolution action.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--variant-evaluation", default=None, help="Variant evaluation artifact path; defaults to latest.")
    parser.add_argument("--as-of", default=None, help="ISO date used for generated records; defaults to today.")
    parser.add_argument("--write-artifacts", action="store_true")
    parser.add_argument("--artifact-root", default=str(DEFAULT_ARTIFACT_ROOT))
    args = parser.parse_args()

    try:
        as_of = dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()
    except ValueError:
        print(f"invalid --as-of date: {args.as_of}", file=sys.stderr)
        return 1

    try:
        result = recommend_self_evolution(
            repo_root=Path(args.repo_root),
            variant_evaluation_path=Path(args.variant_evaluation) if args.variant_evaluation else None,
            as_of=as_of,
            write_artifacts=args.write_artifacts,
            artifact_root=Path(args.artifact_root),
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def recommend_self_evolution(
    *,
    repo_root: Path,
    variant_evaluation_path: Path | None = None,
    as_of: dt.date | None = None,
    write_artifacts: bool = False,
    artifact_root: Path | None = None,
    next_work_override: dict | None = None,
) -> dict:
    root = repo_root.resolve(strict=False)
    today = as_of or dt.date.today()
    readiness = _inspect_readiness(root=root, as_of=today)
    variant_evaluation = _load_variant_evaluation(root=root, variant_evaluation_path=variant_evaluation_path)
    retirement = _inspect_retirements(root=root, as_of=today)
    next_work = next_work_override or _inspect_next_work(root=root, as_of=today)
    recommendations = _build_recommendations(
        readiness=readiness,
        variant_evaluation=variant_evaluation,
        retirement=retirement,
        next_work=next_work,
    )
    materialization_blocked = next_work.get("next_action") in {
        "repair_gate_first",
        "refresh_evidence_first",
        "wait_for_host_capability_recovery",
        "owner_directed_scope_required",
    }
    result = {
        "schema_version": "0.1-draft",
        "artifact_type": "self_evolution_recommendation_report",
        "status": "pass",
        "as_of": today.isoformat(),
        "mutation_allowed": False,
        "trigger_model": {
            "recommended_operator_action": "SelfEvolutionRecommend",
            "manual_trigger_command": "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action SelfEvolutionRecommend",
            "proactive_operator_triggers": [
                "FeedbackReport",
                "DailyAll",
            ],
            "cycle_steps": [
                "SelfEvolutionReadiness",
                "SelfEvolutionEvalDataset",
                "SelfEvolutionOptimize",
                "SelfEvolutionVariantEvaluate",
                "SelfEvolutionRecommend",
            ],
            "proactive_report_sources": [
                "after Readiness closeout",
                "after FeedbackReport evidence refresh",
                "daily operator automation if configured by the owner",
            ],
            "automatic_effective_change": False,
        },
        "recommended_next_action": _select_recommended_next_action(
            recommendations=recommendations,
            materialization_blocked=materialization_blocked,
            next_work=next_work,
        ),
        "materialization_blocked": materialization_blocked,
        "selector_next_action": next_work.get("next_action"),
        "selector_why": next_work.get("why"),
        "readiness_overall_state": readiness.get("overall_state"),
        "ready_for_unattended_self_update": readiness.get("ready_for_unattended_self_update"),
        "variant_review_candidate_count": int(variant_evaluation.get("review_candidate_count", 0)),
        "retire_proposal_count": int(retirement.get("retire_proposal_count", 0)),
        "recommendations": recommendations,
        "guards": {
            "automatic_policy_mutation": False,
            "automatic_skill_enablement": False,
            "automatic_target_repo_sync": False,
            "automatic_push_or_merge": False,
            "requires_human_review_before_effective_change": True,
        },
        "rollback": "Delete the generated recommendation artifact. No active runtime behavior is changed.",
        "artifact_refs": {},
    }
    if write_artifacts:
        result["artifact_refs"] = _write_artifact(root=artifact_root or DEFAULT_ARTIFACT_ROOT, result=result, as_of=today)
    return result


def _inspect_readiness(*, root: Path, as_of: dt.date) -> dict:
    module = _load_script(root / "scripts" / "evaluate-self-evolution-readiness.py", "recommend_self_evolution_readiness")
    return module.inspect_self_evolution_readiness(
        repo_root=root,
        policy_path=root / "docs" / "architecture" / "self-evolution-readiness-policy.json",
        as_of=as_of,
    )


def _inspect_retirements(*, root: Path, as_of: dt.date) -> dict:
    module = _load_script(root / "scripts" / "review-runtime-evolution-retirements.py", "recommend_self_evolution_retirements")
    return module.review_runtime_evolution_retirements(repo_root=root, as_of=as_of)


def _inspect_next_work(*, root: Path, as_of: dt.date) -> dict:
    try:
        module = _load_script(root / "scripts" / "select-next-work.py", "recommend_self_evolution_next_work")
        return module.inspect_next_work_selection(
            repo_root=root,
            policy_path=root / "docs" / "architecture" / "autonomous-next-work-selection-policy.json",
            ltp_policy_path=root / "docs" / "architecture" / "ltp-autonomous-promotion-policy.json",
            as_of=as_of,
        )
    except Exception as exc:  # noqa: BLE001 - advisory reporting should surface selector errors without hiding recommendations.
        return {"status": "error", "next_action": "refresh_evidence_first", "why": f"next-work selector error: {exc}"}


def _load_variant_evaluation(*, root: Path, variant_evaluation_path: Path | None) -> dict:
    path = _resolve_variant_evaluation_path(root=root, variant_evaluation_path=variant_evaluation_path)
    if path is None:
        return {
            "artifact_type": "self_evolution_variant_evaluation",
            "status": "missing",
            "review_candidate_count": 0,
            "evaluations": [],
            "artifact_refs": {},
        }
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"variant evaluation artifact is not readable: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"variant evaluation artifact is invalid JSON: {path} ({exc.msg})") from exc
    if payload.get("artifact_type") != "self_evolution_variant_evaluation":
        raise ValueError("variant evaluation artifact must have artifact_type=self_evolution_variant_evaluation")
    payload.setdefault("artifact_refs", {})
    payload["artifact_refs"].setdefault("json", _display_path(path=path, root=root))
    return payload


def _resolve_variant_evaluation_path(*, root: Path, variant_evaluation_path: Path | None) -> Path | None:
    if variant_evaluation_path:
        path = variant_evaluation_path if variant_evaluation_path.is_absolute() else root / variant_evaluation_path
        if not path.exists():
            raise ValueError(f"variant evaluation artifact does not exist: {variant_evaluation_path}")
        return path.resolve(strict=False)
    candidates = sorted((root / "docs" / "change-evidence" / "self-evolution-variant-evaluations").glob("*-self-evolution-variant-evaluation.json"))
    return candidates[-1].resolve(strict=False) if candidates else None


def _build_recommendations(
    *,
    readiness: dict,
    variant_evaluation: dict,
    retirement: dict,
    next_work: dict,
) -> list[dict]:
    recommendations = [
        _addition_recommendation(readiness),
        _optimization_recommendation(variant_evaluation, next_work),
        _retirement_recommendation(retirement),
    ]
    return recommendations


def _addition_recommendation(readiness: dict) -> dict:
    next_gap = readiness.get("next_gap")
    if next_gap:
        return {
            "recommendation_id": "add.self_evolution_missing_capability",
            "lane": "add",
            "decision": "implement_missing_capability",
            "priority": "P0",
            "risk_level": "medium",
            "title": f"Implement missing self-evolution capability: {next_gap.get('title')}",
            "reason": next_gap.get("gap") or "Readiness ledger reported a missing terminal capability.",
            "evidence_refs": _compact_refs([readiness.get("policy_path")]),
            "commands": ["python scripts/evaluate-self-evolution-readiness.py --write-artifacts"],
            "mutation_allowed": False,
        }
    return {
        "recommendation_id": "add.none_terminal_capabilities_complete",
        "lane": "add",
        "decision": "no_addition_recommended",
        "priority": "P3",
        "risk_level": "low",
        "title": "No new terminal self-evolution capability is currently required.",
        "reason": "The readiness ledger reports implemented=total and no next_gap.",
        "evidence_refs": _compact_refs([readiness.get("policy_path")]),
        "commands": ["python scripts/evaluate-self-evolution-readiness.py --write-artifacts"],
        "mutation_allowed": False,
    }


def _optimization_recommendation(variant_evaluation: dict, next_work: dict) -> dict:
    review_candidates = [
        item for item in variant_evaluation.get("evaluations", []) if item.get("decision") == "review_candidate"
    ]
    if review_candidates:
        return {
            "recommendation_id": "optimize.review_candidate_variants",
            "lane": "optimize",
            "decision": "review_candidate_variants",
            "priority": "P1",
            "risk_level": "medium",
            "title": "Review evaluated self-evolution variants before materialization.",
            "reason": f"{len(review_candidates)} variant(s) reached review_candidate; selector_next_action={next_work.get('next_action')}.",
            "evidence_refs": _compact_refs([variant_evaluation.get("artifact_refs", {}).get("json")]),
            "commands": [
                "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action SelfEvolutionVariantEvaluate",
                "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action EvolutionMaterialize",
            ],
            "mutation_allowed": False,
        }
    return {
        "recommendation_id": "optimize.refresh_eval_cycle",
        "lane": "optimize",
        "decision": "refresh_eval_cycle",
        "priority": "P2",
        "risk_level": "low",
        "title": "Refresh the self-evolution eval and variant cycle.",
        "reason": "No review_candidate variants are available from the latest evaluation artifact.",
        "evidence_refs": _compact_refs([variant_evaluation.get("artifact_refs", {}).get("json")]),
        "commands": [
            "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action SelfEvolutionEvalDataset",
            "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action SelfEvolutionOptimize",
            "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action SelfEvolutionVariantEvaluate",
        ],
        "mutation_allowed": False,
    }


def _retirement_recommendation(retirement: dict) -> dict:
    retire_count = int(retirement.get("retire_proposal_count", 0))
    if retire_count:
        return {
            "recommendation_id": "delete.review_retirement_proposals",
            "lane": "delete_or_retire",
            "decision": "review_retirement_proposals",
            "priority": "P1",
            "risk_level": "low",
            "title": "Review stale or duplicate evolution candidates for retirement.",
            "reason": f"{retire_count} retirement proposal(s) were generated in dry-run mode.",
            "evidence_refs": _compact_refs(
                [proposal.get("source_refs", [None])[0] for proposal in retirement.get("retire_proposals", [])]
            ),
            "commands": ["python scripts/review-runtime-evolution-retirements.py"],
            "mutation_allowed": False,
        }
    return {
        "recommendation_id": "delete.none_retirement_candidates",
        "lane": "delete_or_retire",
        "decision": "no_delete_recommended",
        "priority": "P3",
        "risk_level": "low",
        "title": "No deletion or retirement is currently recommended.",
        "reason": "Retirement review produced zero retire proposals.",
        "evidence_refs": [],
        "commands": ["python scripts/review-runtime-evolution-retirements.py"],
        "mutation_allowed": False,
    }


def _select_recommended_next_action(
    *,
    recommendations: list[dict],
    materialization_blocked: bool,
    next_work: dict,
) -> str:
    if materialization_blocked:
        return "report_only_until_" + str(next_work.get("next_action") or "selector_recovers")
    for decision in (
        "implement_missing_capability",
        "review_candidate_variants",
        "review_retirement_proposals",
        "refresh_eval_cycle",
    ):
        if any(item["decision"] == decision for item in recommendations):
            return decision
    return "no_change_recommended"


def _compact_refs(values: list[object]) -> list[str]:
    return [str(value) for value in values if isinstance(value, str) and value.strip()]


def _load_script(path: Path, module_name: str) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"unable to load script: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _write_artifact(*, root: Path, result: dict, as_of: dt.date) -> dict[str, str]:
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{as_of.strftime('%Y%m%d')}-self-evolution-recommendations.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"json": path.resolve(strict=False).as_posix()}


def _display_path(*, path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.resolve(strict=False).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
