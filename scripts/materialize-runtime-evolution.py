from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTRACTOR_PATH = ROOT / "scripts" / "extract-ai-coding-experience.py"
DEFAULT_MANIFEST_ROOT = Path("docs/change-evidence/runtime-evolution-patches")
DEFAULT_PROPOSAL_ROOT = Path("docs/change-evidence/runtime-evolution-proposals")
DEFAULT_PROMOTION_ROOT = Path("docs/change-evidence/runtime-evolution-promotions")
DEFAULT_SKILL_ROOT = Path("skills/candidates")


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize reviewed runtime evolution candidates.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--as-of", default=None, help="ISO date used for generated files; defaults to today.")
    parser.add_argument("--apply", action="store_true", help="Write proposal and disabled skill candidate files.")
    args = parser.parse_args()

    try:
        as_of = dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()
    except ValueError:
        print(f"invalid --as-of date: {args.as_of}", file=sys.stderr)
        return 1

    try:
        result = materialize_runtime_evolution(repo_root=Path(args.repo_root), as_of=as_of, apply=args.apply)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def materialize_runtime_evolution(*, repo_root: Path, as_of: dt.date | None = None, apply: bool = False) -> dict:
    root = repo_root.resolve(strict=False)
    today = as_of or dt.date.today()
    extractor = _load_extractor()
    review = extractor.inspect_ai_coding_experience(repo_root=root, as_of=today)
    if review.get("invalid_reasons"):
        raise ValueError("cannot materialize invalid experience review: " + ", ".join(review["invalid_reasons"]))

    operations = _build_operations(root=root, review=review, as_of=today)
    invalid_reasons = _validate_operations(operations)
    if invalid_reasons:
        raise ValueError("invalid runtime evolution materialization: " + ", ".join(invalid_reasons))

    written_files: list[str] = []
    if apply:
        for operation in operations:
            path = root / operation["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(operation["content"], encoding="utf-8")
            written_files.append(operation["path"])

    result = {
        "status": "pass",
        "as_of": today.isoformat(),
        "mode": "apply" if apply else "dry_run",
        "mutation_allowed": apply,
        "guard": {
            "direct_main_update": False,
            "policy_auto_apply": False,
            "skill_auto_enable": False,
            "requires_human_review_before_enable": True,
        },
        "operation_count": len(operations),
        "operations": [_operation_summary(operation) for operation in operations],
        "written_files": written_files,
    }
    return result


def _load_extractor():
    spec = importlib.util.spec_from_file_location("extract_ai_coding_experience_script", EXTRACTOR_PATH)
    if spec is None or spec.loader is None:
        raise ValueError(f"unable to load extractor: {EXTRACTOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["extract_ai_coding_experience_script_for_materializer"] = module
    spec.loader.exec_module(module)
    return module


def _build_operations(*, root: Path, review: dict, as_of: dt.date) -> list[dict]:
    operations: list[dict] = []
    promotion_entries: list[dict] = []
    for proposal in review["proposals"]:
        proposal_path = DEFAULT_PROPOSAL_ROOT / f"{proposal['proposal_id']}.json"
        operations.append(
            {
                "operation": "write_controlled_proposal",
                "path": proposal_path.as_posix(),
                "content": json.dumps(proposal, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                "risk": proposal["risk_posture"],
            }
        )
        promotion_entries.append(_build_promotion_entry_for_proposal(proposal=proposal, path=proposal_path))

    for skill in review["skill_manifest_candidates"]:
        slug = skill["skill_id"].replace("skill.", "", 1)
        skill_dir = DEFAULT_SKILL_ROOT / slug
        manifest_path = skill_dir / "skill-manifest.json"
        skill_doc_path = skill_dir / "SKILL.md"
        operations.append(
            {
                "operation": "write_disabled_skill_manifest_candidate",
                "path": manifest_path.as_posix(),
                "content": json.dumps(skill, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                "risk": skill["risk_tier"],
            }
        )
        promotion_entries.append(_build_promotion_entry_for_skill(skill=skill, manifest_path=manifest_path))
        operations.append(
            {
                "operation": "write_skill_candidate_readme",
                "path": skill_doc_path.as_posix(),
                "content": _render_skill_doc(skill),
                "risk": skill["risk_tier"],
            }
        )

    manifest = {
        "schema_version": "0.1-draft",
        "generated_on": as_of.isoformat(),
        "source_review": "scripts/operator.ps1 -Action ExperienceReview",
        "mutation_guard": {
            "policy_auto_apply": False,
            "skill_auto_enable": False,
            "target_repo_sync": False,
        },
        "operation_paths": [operation["path"] for operation in operations],
        "rollback": "Delete the generated proposal and skills/candidates files from this manifest; no enabled runtime behavior is changed.",
    }
    manifest_path = DEFAULT_MANIFEST_ROOT / f"{as_of.strftime('%Y%m%d')}-runtime-evolution-materialization.json"
    operations.append(
        {
            "operation": "write_materialization_manifest",
            "path": manifest_path.as_posix(),
            "content": json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            "risk": "low",
        }
    )

    promotion_manifest = {
        "schema_version": "0.1-draft",
        "lifecycle_id": f"runtime-evolution-promotion-{as_of.isoformat()}",
        "generated_on": as_of.isoformat(),
        "source_review": "scripts/operator.ps1 -Action ExperienceReview",
        "entries": promotion_entries,
        "retirement_guard": {
            "candidate_cleanup_only": True,
            "preserve_evidence_history": True,
            "reviewed_asset_delete": False,
        },
        "rollback_ref": "Delete generated candidate files and this lifecycle manifest; no enabled runtime behavior is changed.",
    }
    promotion_manifest_path = DEFAULT_PROMOTION_ROOT / f"{as_of.strftime('%Y%m%d')}-runtime-evolution-promotion-lifecycle.json"
    operations.append(
        {
            "operation": "write_promotion_lifecycle_manifest",
            "path": promotion_manifest_path.as_posix(),
            "content": json.dumps(promotion_manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            "risk": "low",
        }
    )
    return operations


def _render_skill_doc(skill: dict) -> str:
    capabilities = "\n".join(f"- {item}" for item in skill["capabilities"])
    contracts = "\n".join(f"- `{item}`" for item in skill["compatibility"].get("required_contracts", []))
    return (
        f"# {skill['display_name']}\n\n"
        "## Status\n"
        "- Candidate only.\n"
        "- `default_enabled=false`.\n"
        "- Do not install or enable without human review and project gates.\n\n"
        "## Description\n"
        f"{skill['description']}\n\n"
        "## Capabilities\n"
        f"{capabilities}\n\n"
        "## Required Contracts\n"
        f"{contracts}\n\n"
        "## Rollback\n"
        "Delete this candidate directory. No runtime behavior is enabled by this file.\n"
    )


def _build_promotion_entry_for_proposal(*, proposal: dict, path: Path) -> dict:
    return {
        "asset_id": proposal["proposal_id"],
        "asset_kind": proposal["proposal_category"],
        "status": "disabled",
        "materialized_path": path.as_posix(),
        "enabled_by_default": False,
        "review_required": proposal["human_review"]["required"],
        "promotion_evidence_refs": proposal["source_refs"],
        "promotion_gate_refs": [
            "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime",
            "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract",
        ],
        "effect_metric_refs": [
            "docs/specs/learning-efficiency-metrics-spec.md",
            "docs/specs/interaction-evidence-spec.md",
        ],
        "rollback_ref": proposal["rollback_ref"],
    }


def _build_promotion_entry_for_skill(*, skill: dict, manifest_path: Path) -> dict:
    return {
        "asset_id": skill["skill_id"],
        "asset_kind": "skill",
        "status": "disabled",
        "materialized_path": manifest_path.as_posix(),
        "enabled_by_default": bool(skill.get("default_enabled")),
        "review_required": True,
        "promotion_evidence_refs": [skill["provenance"]["source"]],
        "promotion_gate_refs": [
            "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime",
            "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract",
        ],
        "effect_metric_refs": [
            "docs/specs/learning-efficiency-metrics-spec.md",
            "docs/specs/skill-manifest-spec.md",
        ],
        "rollback_ref": "Delete this candidate manifest and directory. No runtime behavior is enabled by this file.",
    }


def _validate_operations(operations: list[dict]) -> list[str]:
    reasons: list[str] = []
    if not operations:
        reasons.append("no operations")
    for operation in operations:
        path = operation.get("path", "")
        if not isinstance(path, str) or not path.strip():
            reasons.append("operation path missing")
        if Path(path).is_absolute() or ".." in Path(path).parts:
            reasons.append(f"unsafe operation path: {path}")
        if not operation.get("content"):
            reasons.append(f"operation content missing: {path}")
        if operation.get("operation") == "write_disabled_skill_manifest_candidate":
            payload = json.loads(operation["content"])
            if payload.get("default_enabled") is not False:
                reasons.append(f"skill candidate must stay disabled: {path}")
            if payload.get("risk_tier") == "high":
                reasons.append(f"high-risk skill candidate cannot be materialized automatically: {path}")
    return reasons


def _operation_summary(operation: dict) -> dict:
    return {
        "operation": operation["operation"],
        "path": operation["path"],
        "risk": operation["risk"],
    }


if __name__ == "__main__":
    raise SystemExit(main())
