from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET_ROOT = ROOT / "docs" / "change-evidence" / "self-evolution-evals"
DEFAULT_ARTIFACT_ROOT = ROOT / "docs" / "change-evidence" / "self-evolution-variants"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate governed self-evolution candidate variants from eval cases.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--dataset", default=None, help="Eval dataset path; defaults to latest self-evolution dataset.")
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
        result = optimize_runtime_evolution_trajectory(
            repo_root=Path(args.repo_root),
            dataset_path=Path(args.dataset) if args.dataset else None,
            as_of=as_of,
            write_artifacts=args.write_artifacts,
            artifact_root=Path(args.artifact_root),
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def optimize_runtime_evolution_trajectory(
    *,
    repo_root: Path,
    dataset_path: Path | None = None,
    as_of: dt.date | None = None,
    write_artifacts: bool = False,
    artifact_root: Path | None = None,
) -> dict:
    root = repo_root.resolve(strict=False)
    today = as_of or dt.date.today()
    dataset_file = _resolve_dataset_path(root=root, dataset_path=dataset_path)
    dataset = _load_dataset(dataset_file)
    variants = [_build_variant(case=case) for case in dataset["cases"]]
    invalid_reasons = _validate_variants(variants)
    if invalid_reasons:
        raise ValueError("invalid runtime evolution trajectory variants: " + ", ".join(invalid_reasons))

    result = {
        "schema_version": "0.1-draft",
        "artifact_type": "self_evolution_candidate_variants",
        "as_of": today.isoformat(),
        "source_dataset": dataset_file.relative_to(root).as_posix() if _is_relative_to(dataset_file, root) else dataset_file.as_posix(),
        "mutation_allowed": False,
        "variant_count": len(variants),
        "variants": variants,
        "guards": {
            "direct_policy_update": False,
            "skill_auto_enable": False,
            "target_repo_sync": False,
            "push": False,
            "merge": False,
            "requires_variant_evaluation": True,
        },
        "rollback": "Delete the generated variant artifact. No active runtime behavior is changed.",
        "artifact_refs": {},
    }
    if write_artifacts:
        result["artifact_refs"] = _write_artifact(root=artifact_root or DEFAULT_ARTIFACT_ROOT, result=result, as_of=today)
    return result


def _resolve_dataset_path(*, root: Path, dataset_path: Path | None) -> Path:
    if dataset_path:
        path = dataset_path if dataset_path.is_absolute() else root / dataset_path
        if not path.exists():
            raise ValueError(f"eval dataset does not exist: {dataset_path}")
        return path.resolve(strict=False)
    candidates = sorted((root / "docs" / "change-evidence" / "self-evolution-evals").glob("*-self-evolution-eval-dataset.json"))
    if not candidates:
        raise ValueError("no self-evolution eval dataset artifact found")
    return candidates[-1].resolve(strict=False)


def _load_dataset(path: Path) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"eval dataset is not readable: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"eval dataset is invalid JSON: {path} ({exc.msg})") from exc
    if not isinstance(payload, dict) or payload.get("artifact_type") != "self_evolution_eval_dataset":
        raise ValueError("eval dataset must have artifact_type=self_evolution_eval_dataset")
    if not isinstance(payload.get("cases"), list) or not payload["cases"]:
        raise ValueError("eval dataset must include cases")
    return payload


def _build_variant(*, case: dict) -> dict:
    case_id = case["case_id"]
    source_kind = case["source_kind"]
    strategy = _strategy_for_case(case)
    return {
        "variant_id": "variant." + case_id,
        "source_case_id": case_id,
        "source_kind": source_kind,
        "source_id": case.get("source_id"),
        "risk_level": case.get("risk_level", "medium"),
        "optimization_strategy": strategy,
        "proposed_change": _proposed_change_for_case(case),
        "expected_properties": case.get("expected_properties", []),
        "verification_refs": case.get("verification_refs", []),
        "constraints": [
            "mutation_allowed=false",
            "rollback_check_required",
            "human_review_before_effective_change",
            "runtime_and_contract_gates_before_promotion",
        ],
        "mutation_allowed": False,
        "rollback_check": case["rollback_check"],
    }


def _strategy_for_case(case: dict) -> str:
    if case["source_kind"] == "skill_candidate":
        return "tighten skill manifest promotion criteria and preserve disabled-by-default posture"
    if case["source_kind"] == "experience_proposal":
        return "turn repeated experience into a reviewable proposal with explicit source and rollback checks"
    return "turn runtime-evolution candidate evidence into a bounded promote/improve/defer decision"


def _proposed_change_for_case(case: dict) -> str:
    if case["source_kind"] == "skill_candidate":
        return "Create a reviewed skill-promotion variant that keeps default_enabled=false until gates and human review pass."
    if case["source_kind"] == "experience_proposal":
        return "Create a proposal variant that preserves human_review.required=true and adds explicit verification refs."
    return "Create a runtime-evolution decision variant that must cite source_ref, verification refs, and rollback before promotion."


def _validate_variants(variants: list[dict]) -> list[str]:
    reasons: list[str] = []
    if not variants:
        reasons.append("no variants")
    seen: set[str] = set()
    for variant in variants:
        variant_id = variant.get("variant_id")
        if not variant_id:
            reasons.append("variant_id missing")
            continue
        if variant_id in seen:
            reasons.append(f"duplicate variant_id: {variant_id}")
        seen.add(variant_id)
        if variant.get("mutation_allowed") is not False:
            reasons.append(f"variant must not allow mutation: {variant_id}")
        if not variant.get("expected_properties"):
            reasons.append(f"expected_properties missing: {variant_id}")
        if not variant.get("rollback_check"):
            reasons.append(f"rollback_check missing: {variant_id}")
    return reasons


def _write_artifact(*, root: Path, result: dict, as_of: dt.date) -> dict[str, str]:
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{as_of.strftime('%Y%m%d')}-self-evolution-variants.json"
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
