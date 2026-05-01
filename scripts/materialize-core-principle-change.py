#!/usr/bin/env python3
"""Materialize reviewable core-principle change proposals without changing active policy."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROPOSAL_ROOT = Path("docs/change-evidence/core-principle-change-proposals")
DEFAULT_PATCH_ROOT = Path("docs/change-evidence/core-principle-change-patches")
DEFAULT_REPORT_ROOT = Path("docs/change-evidence/core-principle-change-reports")
DEFAULT_PRINCIPLE_ID = "governance_hub_reusable_contract_final_state"
DEFAULT_SUMMARY = (
    "The best engineering final state is Governance Hub + Reusable Contract + "
    "Controlled Evolution loop + outer AI intelligent review/generation capability, "
    "implemented as governed controls rather than a competing host product."
)
DEFAULT_RATIONALE = (
    "Make the final-state product posture explicit in core principles so future "
    "automation and outer-AI-assisted evolution preserve the governance-center boundary."
)
ALLOWED_CHANGE_ACTIONS = {"add", "update", "deprecate", "retire", "delete_candidate"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--as-of", default=None, help="ISO date used for generated files; defaults to today.")
    parser.add_argument("--apply", action="store_true", help="Write reviewable proposal and manifest files.")
    parser.add_argument(
        "--write-dry-run-report",
        action="store_true",
        help="Write an audit-only dry-run report. Does not write proposal/manifest files or active policy.",
    )
    parser.add_argument("--change-action", default="add", choices=sorted(ALLOWED_CHANGE_ACTIONS))
    parser.add_argument("--principle-id", default=DEFAULT_PRINCIPLE_ID)
    parser.add_argument("--summary", default=DEFAULT_SUMMARY)
    parser.add_argument("--rationale", default=DEFAULT_RATIONALE)
    args = parser.parse_args(argv)

    try:
        as_of = dt.date.fromisoformat(args.as_of) if args.as_of else dt.date.today()
    except ValueError:
        print(f"invalid --as-of date: {args.as_of}", file=sys.stderr)
        return 1

    try:
        result = materialize_core_principle_change(
            repo_root=Path(args.repo_root),
            as_of=as_of,
            apply=args.apply,
            write_dry_run_report=args.write_dry_run_report,
            change_action=args.change_action,
            principle_id=args.principle_id,
            summary=args.summary,
            rationale=args.rationale,
        )
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def materialize_core_principle_change(
    *,
    repo_root: Path,
    as_of: dt.date | None = None,
    apply: bool = False,
    write_dry_run_report: bool = False,
    change_action: str = "add",
    principle_id: str = DEFAULT_PRINCIPLE_ID,
    summary: str = DEFAULT_SUMMARY,
    rationale: str = DEFAULT_RATIONALE,
) -> dict:
    root = repo_root.resolve(strict=False)
    today = as_of or dt.date.today()
    proposal = _build_proposal(
        as_of=today,
        change_action=change_action,
        principle_id=principle_id,
        summary=summary,
        rationale=rationale,
    )
    operations = _build_operations(proposal=proposal, as_of=today)
    invalid_reasons = _validate_operations(operations)
    if invalid_reasons:
        raise ValueError("invalid core principle change materialization: " + ", ".join(invalid_reasons))
    if apply and write_dry_run_report:
        raise ValueError("--write-dry-run-report cannot be combined with --apply")

    operation_summaries = [
        _operation_summary(operation=operation, repo_root=root)
        for operation in operations
    ]
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
        "operation_count": len(operations),
        "operations": operation_summaries,
        "written_files": written_files,
        "guard": _effective_change_guard(),
    }
    if write_dry_run_report:
        report_path = _dry_run_report_path(proposal=proposal, as_of=today)
        report = {
            "schema_version": "0.1-draft",
            "generated_on": today.isoformat(),
            "mode": "dry_run_report",
            "source_command": "scripts/operator.ps1 -Action CorePrincipleMaterialize -WriteCorePrincipleDryRunReport",
            "proposal_id": proposal["change_id"],
            "proposal_path": operations[0]["path"],
            "manifest_path": operations[1]["path"],
            "operations": operation_summaries,
            "guard": _effective_change_guard(),
            "rollback": "Delete this dry-run report. Proposal, manifest, and active policy files are untouched.",
        }
        report_file = root / report_path
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result["mode"] = "dry_run"
        result["dry_run_report_path"] = report_path.as_posix()
        result["written_files"] = [report_path.as_posix()]
    return result


def _build_proposal(
    *,
    as_of: dt.date,
    change_action: str,
    principle_id: str,
    summary: str,
    rationale: str,
) -> dict:
    if change_action not in ALLOWED_CHANGE_ACTIONS:
        raise ValueError(f"unsupported change_action: {change_action}")
    if not re.fullmatch(r"[a-z0-9_.-]+", principle_id):
        raise ValueError(f"invalid principle_id: {principle_id}")
    if not summary.strip():
        raise ValueError("summary is required")

    return {
        "schema_version": "0.1-draft",
        "generated_on": as_of.isoformat(),
        "change_id": f"principle.{principle_id}",
        "change_action": change_action,
        "principle_id": principle_id,
        "category": "positioning",
        "summary": summary,
        "rationale": rationale,
        "source_refs": [
            "docs/architecture/core-principles-policy.json",
            "docs/specs/core-principles-spec.md",
            "docs/plans/governance-hub-reuse-and-controlled-evolution-plan.md",
        ],
        "target_active_files": [
            "docs/architecture/core-principles-policy.json",
            "docs/specs/core-principles-spec.md",
            "scripts/verify-core-principles.py",
            "tests/runtime/test_core_principles.py",
        ],
        "required_controls": [
            "structured_candidate",
            "risk_gate",
            "machine_gate",
            "evidence_ref",
            "rollback_ref",
            "human_review_for_high_risk",
        ],
        "guard": _effective_change_guard(),
        "rollback": "Delete this proposal and its manifest; no active policy file is changed by materialization.",
    }


def _build_operations(*, proposal: dict, as_of: dt.date) -> list[dict]:
    slug = proposal["principle_id"].replace("_", "-").replace(".", "-")
    proposal_path = DEFAULT_PROPOSAL_ROOT / f"{as_of.strftime('%Y%m%d')}-{slug}.json"
    manifest_path = DEFAULT_PATCH_ROOT / f"{as_of.strftime('%Y%m%d')}-core-principle-change-materialization.json"
    operations = [
        {
            "operation": "write_core_principle_change_proposal",
            "path": proposal_path.as_posix(),
            "content": json.dumps(proposal, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            "risk": "medium",
        }
    ]
    manifest = {
        "schema_version": "0.1-draft",
        "generated_on": as_of.isoformat(),
        "source_command": "scripts/operator.ps1 -Action CorePrincipleMaterialize",
        "existing_file_behavior": "overwrite_same_candidate",
        "operation_paths": [operation["path"] for operation in operations] + [manifest_path.as_posix()],
        "operation_artifacts": [
            {
                "operation": operation["operation"],
                "path": operation["path"],
                "risk": operation["risk"],
                "sha256": _sha256_text(operation["content"]),
                "existing_file_behavior": "overwrite_same_candidate",
            }
            for operation in operations
        ],
        "guard": _effective_change_guard(),
        "rollback": "Delete files listed in operation_paths. Active core principle files are untouched by this materializer.",
    }
    operations.append(
        {
            "operation": "write_core_principle_change_manifest",
            "path": manifest_path.as_posix(),
            "content": json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            "risk": "low",
        }
    )
    return operations


def _dry_run_report_path(*, proposal: dict, as_of: dt.date) -> Path:
    slug = proposal["principle_id"].replace("_", "-").replace(".", "-")
    return DEFAULT_REPORT_ROOT / f"{as_of.strftime('%Y%m%d')}-{slug}-dry-run-report.json"


def _effective_change_guard() -> dict:
    return {
        "active_policy_auto_apply": False,
        "active_spec_auto_apply": False,
        "verifier_auto_update": False,
        "skill_auto_enable": False,
        "target_repo_sync": False,
        "push": False,
        "merge": False,
        "requires_human_review_before_effective_change": True,
    }


def _validate_operations(operations: list[dict]) -> list[str]:
    reasons: list[str] = []
    if not operations:
        reasons.append("no operations")
    for operation in operations:
        path = operation.get("path", "")
        if not isinstance(path, str) or not path.strip():
            reasons.append("operation path missing")
            continue
        path_obj = Path(path)
        if path_obj.is_absolute() or ".." in path_obj.parts:
            reasons.append(f"unsafe operation path: {path}")
        if not path.startswith("docs/change-evidence/core-principle-change-"):
            reasons.append(f"operation path must stay under core-principle change evidence roots: {path}")
        if not operation.get("content"):
            reasons.append(f"operation content missing: {path}")
    return reasons


def _operation_summary(*, operation: dict, repo_root: Path) -> dict:
    path = repo_root / operation["path"]
    return {
        "operation": operation["operation"],
        "path": operation["path"],
        "risk": operation["risk"],
        "sha256": _sha256_text(operation["content"]),
        "existing_file_behavior": "overwrite_same_candidate",
        "exists_before_write": path.exists(),
    }


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    raise SystemExit(main())
