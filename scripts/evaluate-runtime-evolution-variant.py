from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_VARIANT_ROOT = ROOT / "docs" / "change-evidence" / "self-evolution-variants"
DEFAULT_ARTIFACT_ROOT = ROOT / "docs" / "change-evidence" / "self-evolution-variant-evaluations"


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate governed self-evolution candidate variants.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--variants", default=None, help="Variant artifact path; defaults to latest.")
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
        result = evaluate_runtime_evolution_variants(
            repo_root=Path(args.repo_root),
            variant_path=Path(args.variants) if args.variants else None,
            as_of=as_of,
            write_artifacts=args.write_artifacts,
            artifact_root=Path(args.artifact_root),
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def evaluate_runtime_evolution_variants(
    *,
    repo_root: Path,
    variant_path: Path | None = None,
    as_of: dt.date | None = None,
    write_artifacts: bool = False,
    artifact_root: Path | None = None,
) -> dict:
    root = repo_root.resolve(strict=False)
    today = as_of or dt.date.today()
    variant_file = _resolve_variant_path(root=root, variant_path=variant_path)
    variants = _load_variants(variant_file)
    evaluations = [_evaluate_variant(variant=variant) for variant in variants["variants"]]
    invalid_reasons = _validate_evaluations(evaluations)
    if invalid_reasons:
        raise ValueError("invalid runtime evolution variant evaluation: " + ", ".join(invalid_reasons))

    selected = [item for item in evaluations if item["decision"] == "review_candidate"]
    result = {
        "schema_version": "0.1-draft",
        "artifact_type": "self_evolution_variant_evaluation",
        "as_of": today.isoformat(),
        "source_variants": variant_file.relative_to(root).as_posix() if _is_relative_to(variant_file, root) else variant_file.as_posix(),
        "mutation_allowed": False,
        "variant_count": len(evaluations),
        "review_candidate_count": len(selected),
        "evaluations": evaluations,
        "guards": {
            "direct_policy_update": False,
            "skill_auto_enable": False,
            "target_repo_sync": False,
            "auto_push_or_pr": False,
            "requires_human_review_before_effective_change": True,
        },
        "rollback": "Delete the generated variant-evaluation artifact. No active runtime behavior is changed.",
        "artifact_refs": {},
    }
    if write_artifacts:
        result["artifact_refs"] = _write_artifact(root=artifact_root or DEFAULT_ARTIFACT_ROOT, result=result, as_of=today)
    return result


def _resolve_variant_path(*, root: Path, variant_path: Path | None) -> Path:
    if variant_path:
        path = variant_path if variant_path.is_absolute() else root / variant_path
        if not path.exists():
            raise ValueError(f"variant artifact does not exist: {variant_path}")
        return path.resolve(strict=False)
    candidates = sorted((root / "docs" / "change-evidence" / "self-evolution-variants").glob("*-self-evolution-variants.json"))
    if not candidates:
        raise ValueError("no self-evolution variant artifact found")
    return candidates[-1].resolve(strict=False)


def _load_variants(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"variant artifact is not readable: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"variant artifact is invalid JSON: {path} ({exc.msg})") from exc
    if not isinstance(payload, dict) or payload.get("artifact_type") != "self_evolution_candidate_variants":
        raise ValueError("variant artifact must have artifact_type=self_evolution_candidate_variants")
    if not isinstance(payload.get("variants"), list) or not payload["variants"]:
        raise ValueError("variant artifact must include variants")
    return payload


def _evaluate_variant(*, variant: dict) -> dict:
    expected_count = len(variant.get("expected_properties", []))
    constraint_count = len(variant.get("constraints", []))
    verification_count = len(variant.get("verification_refs", []))
    score = expected_count + constraint_count + min(verification_count, 3)
    risk = variant.get("risk_level", "medium")
    decision = "review_candidate" if score >= 7 and risk in {"low", "medium"} else "improve"
    if risk == "high":
        decision = "defer"
    return {
        "variant_id": variant["variant_id"],
        "source_case_id": variant["source_case_id"],
        "risk_level": risk,
        "score": score,
        "decision": decision,
        "reasons": [
            f"expected_properties={expected_count}",
            f"constraints={constraint_count}",
            f"verification_refs={verification_count}",
            "mutation_allowed=false",
        ],
        "mutation_allowed": False,
        "required_next_step": "human_review_and_full_gates" if decision == "review_candidate" else "improve_variant_before_review",
    }


def _validate_evaluations(evaluations: list[dict]) -> list[str]:
    reasons: list[str] = []
    if not evaluations:
        reasons.append("no evaluations")
    for evaluation in evaluations:
        if evaluation.get("mutation_allowed") is not False:
            reasons.append(f"evaluation must not allow mutation: {evaluation.get('variant_id')}")
        if evaluation.get("decision") not in {"review_candidate", "improve", "defer"}:
            reasons.append(f"invalid decision: {evaluation.get('variant_id')}")
        if not evaluation.get("required_next_step"):
            reasons.append(f"required_next_step missing: {evaluation.get('variant_id')}")
    return reasons


def _write_artifact(*, root: Path, result: dict, as_of: dt.date) -> dict[str, str]:
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{as_of.strftime('%Y%m%d')}-self-evolution-variant-evaluation.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"json": path.resolve(strict=False).as_posix()}


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


if __name__ == "__main__":
    raise SystemExit(main())
