from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECOMMENDATION_ROOT = ROOT / "docs" / "change-evidence" / "self-evolution-recommendations"
DEFAULT_ARTIFACT_ROOT = ROOT / "docs" / "change-evidence" / "self-evolution-promotions"

_UNSET = object()
_BLOCKING_SELECTOR_ACTIONS = {
    "repair_gate_first",
    "refresh_evidence_first",
    "wait_for_host_capability_recovery",
    "owner_directed_scope_required",
}
_LANES = [
    ("policy_mutation", "automatic_policy_mutation", "Review a policy proposal, then run full gates before any policy mutation."),
    ("skill_enablement", "automatic_skill_enablement", "Keep skill candidates disabled until promotion evidence and rollback refs are attached."),
    ("target_repo_sync", "automatic_target_repo_sync", "Sync target repos only through explicit governed operator actions."),
    ("push_or_merge", "automatic_push_or_merge", "Push or merge only after human review, branch evidence, and release gates."),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan governed promotion for self-evolution recommendations.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--recommendation", default=None, help="Recommendation artifact path; defaults to latest.")
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
        result = plan_self_evolution_promotion(
            repo_root=Path(args.repo_root),
            recommendation_path=Path(args.recommendation) if args.recommendation else None,
            as_of=as_of,
            write_artifacts=args.write_artifacts,
            artifact_root=Path(args.artifact_root),
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def plan_self_evolution_promotion(
    *,
    repo_root: Path,
    recommendation_path: Path | None = None,
    as_of: dt.date | None = None,
    write_artifacts: bool = False,
    artifact_root: Path | None = None,
    recommendation_override: Any = _UNSET,
) -> dict:
    root = repo_root.resolve(strict=False)
    today = as_of or dt.date.today()
    recommendation, source_path = _resolve_recommendation(
        root=root,
        recommendation_path=recommendation_path,
        recommendation_override=recommendation_override,
    )
    if recommendation is None:
        result = _missing_recommendation_report(as_of=today)
    else:
        result = _build_promotion_report(
            recommendation=recommendation,
            recommendation_source_path=source_path,
            repo_root=root,
            as_of=today,
        )

    if write_artifacts:
        result["artifact_refs"] = _write_artifact(root=artifact_root or DEFAULT_ARTIFACT_ROOT, result=result, as_of=today)
    return result


def _resolve_recommendation(
    *,
    root: Path,
    recommendation_path: Path | None,
    recommendation_override: Any,
) -> tuple[dict | None, Path | None]:
    if recommendation_override is not _UNSET:
        if recommendation_override is None:
            return None, None
        return dict(recommendation_override), None

    path = recommendation_path or _latest_recommendation_path(root=root)
    if path is None:
        return None, None
    resolved = path if path.is_absolute() else root / path
    if not resolved.exists():
        raise ValueError(f"self-evolution recommendation artifact does not exist: {path}")
    payload = json.loads(resolved.read_text(encoding="utf-8"))
    if payload.get("artifact_type") != "self_evolution_recommendation_report":
        raise ValueError("recommendation artifact must have artifact_type=self_evolution_recommendation_report")
    return payload, resolved.resolve(strict=False)


def _latest_recommendation_path(*, root: Path) -> Path | None:
    candidates = sorted((root / "docs" / "change-evidence" / "self-evolution-recommendations").glob("*-self-evolution-recommendations.json"))
    return candidates[-1].resolve(strict=False) if candidates else None


def _missing_recommendation_report(*, as_of: dt.date) -> dict:
    return {
        "schema_version": "0.1-draft",
        "artifact_type": "self_evolution_promotion_controller_report",
        "status": "missing_recommendation",
        "as_of": as_of.isoformat(),
        "promotion_stage": "missing_recommendation",
        "recommended_next_action": "run_self_evolution_recommend",
        "selector_next_action": None,
        "selector_why": "self-evolution recommendation artifact is missing",
        "effective_change_allowed": False,
        "control_lanes": _build_control_lanes(
            promotion_stage="missing_recommendation",
            selector_next_action=None,
            selector_why="self-evolution recommendation artifact is missing",
            guards=_default_guards(),
        ),
        "trigger_model": _trigger_model(prerequisite="SelfEvolutionRecommend"),
        "guards": _default_guards(),
        "source_recommendation_path": None,
        "rollback": "Delete the generated promotion controller artifact. No active runtime behavior is changed.",
        "artifact_refs": {},
    }


def _build_promotion_report(
    *,
    recommendation: dict,
    recommendation_source_path: Path | None,
    repo_root: Path,
    as_of: dt.date,
) -> dict:
    selector_next_action = recommendation.get("selector_next_action")
    selector_why = recommendation.get("selector_why")
    materialization_blocked = bool(recommendation.get("materialization_blocked"))
    guards = _normalize_guards(recommendation.get("guards") or {})
    selector_blocked = selector_next_action in _BLOCKING_SELECTOR_ACTIONS or materialization_blocked
    if selector_blocked:
        status = "blocked"
        promotion_stage = "blocked_by_selector"
    elif guards.get("requires_human_review_before_effective_change", True):
        status = "ready_for_review"
        promotion_stage = "review_required"
    else:
        status = "pass"
        promotion_stage = "proposal_only"

    return {
        "schema_version": "0.1-draft",
        "artifact_type": "self_evolution_promotion_controller_report",
        "status": status,
        "as_of": as_of.isoformat(),
        "promotion_stage": promotion_stage,
        "recommended_next_action": _recommended_next_action(
            promotion_stage=promotion_stage,
            selector_next_action=selector_next_action,
            recommendation=recommendation,
        ),
        "selector_next_action": selector_next_action,
        "selector_why": selector_why,
        "source_recommendation_path": _display_path(path=recommendation_source_path, root=repo_root),
        "effective_change_allowed": False,
        "control_lanes": _build_control_lanes(
            promotion_stage=promotion_stage,
            selector_next_action=selector_next_action,
            selector_why=selector_why,
            guards=guards,
        ),
        "trigger_model": _trigger_model(prerequisite="SelfEvolutionRecommend"),
        "guards": guards,
        "commands": {
            "refresh_recommendation": "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action SelfEvolutionRecommend",
            "plan_promotion": "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action SelfEvolutionPromotionPlan",
            "materialize_candidate": "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action EvolutionMaterialize",
            "target_sync": "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action ApplyAllFeatures",
            "push_or_merge": "manual review/PR only",
        },
        "rollback": "Delete the generated promotion controller artifact. No policy, skill, target repo, push, or merge state is changed.",
        "artifact_refs": {},
    }


def _build_control_lanes(
    *,
    promotion_stage: str,
    selector_next_action: object,
    selector_why: object,
    guards: dict,
) -> list[dict]:
    lanes: list[dict] = []
    for lane_id, guard_key, default_instruction in _LANES:
        automatic_enabled = bool(guards.get(guard_key, False))
        if promotion_stage in {"blocked_by_selector", "missing_recommendation"}:
            status = "blocked"
            reason = (
                f"selector_next_action={selector_next_action or 'missing'} blocks effective changes. "
                f"{selector_why or default_instruction}"
            )
            next_action = str(selector_next_action or "run_self_evolution_recommend")
        else:
            status = "review_required"
            reason = "requires_human_review_before_effective_change=true. " + default_instruction
            next_action = "attach_promotion_evidence_and_review"
        lanes.append(
            {
                "lane": lane_id,
                "status": status,
                "automatic_enabled": automatic_enabled,
                "guard_key": guard_key,
                "reason": reason,
                "next_action": next_action,
            }
        )
    return lanes


def _recommended_next_action(*, promotion_stage: str, selector_next_action: object, recommendation: dict) -> str:
    if promotion_stage == "blocked_by_selector":
        return "report_only_until_" + str(selector_next_action or "selector_recovers")
    if promotion_stage == "review_required":
        return "review_promotion_evidence_before_effective_change"
    return str(recommendation.get("recommended_next_action") or "no_change_recommended")


def _trigger_model(*, prerequisite: str) -> dict:
    return {
        "recommended_operator_action": "SelfEvolutionPromotionPlan",
        "recommended_operator_action_command": "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action SelfEvolutionPromotionPlan",
        "prerequisite_operator_action": prerequisite,
        "proactive_operator_triggers": ["SelfEvolutionRecommend", "FeedbackReport", "DailyAll"],
        "automatic_effective_change": False,
    }


def _normalize_guards(value: dict) -> dict:
    guards = _default_guards()
    for key in guards:
        if key in value:
            guards[key] = bool(value[key])
    return guards


def _default_guards() -> dict:
    return {
        "automatic_policy_mutation": False,
        "automatic_skill_enablement": False,
        "automatic_target_repo_sync": False,
        "automatic_push_or_merge": False,
        "requires_human_review_before_effective_change": True,
    }


def _write_artifact(*, root: Path, result: dict, as_of: dt.date) -> dict[str, str]:
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{as_of.strftime('%Y%m%d')}-self-evolution-promotion-controller.json"
    refs = {"json": path.resolve(strict=False).as_posix()}
    payload = dict(result)
    payload["artifact_refs"] = refs
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return refs


def _display_path(*, path: Path | None, root: Path) -> str | None:
    if path is None:
        return None
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.resolve(strict=False).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
