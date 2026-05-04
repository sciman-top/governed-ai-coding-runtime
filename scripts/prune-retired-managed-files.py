from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil

from lib.target_repo_managed_assets import (
    inspect_managed_assets,
    load_json_object,
    normalize_relative_text,
    repo_relative_path,
    sha256_text,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE_PATH = ROOT / "docs" / "targets" / "target-repo-governance-baseline.json"
OPERATION_TYPE = "retired_managed_files_cleanup"
DELETION_POLICY = "delete_only_registered_hash_matched_unreferenced_retired_managed_files"


def _candidate_proof(*, backup_required: bool, backup_written: bool) -> dict[str, bool]:
    return {
        "baseline_registered": True,
        "path_bounded": True,
        "target_sha256_matches_previous_sha256": True,
        "no_active_references": True,
        "backup_required": bool(backup_required),
        "backup_written": bool(backup_written),
    }


def _safety_contract() -> dict[str, object]:
    return {
        "operation_type": OPERATION_TYPE,
        "deletion_policy": DELETION_POLICY,
        "delete_requires": [
            "baseline_registered",
            "path_bounded",
            "target_sha256_matches_previous_sha256",
            "no_active_references",
            "backup_written",
            "deletion_time_sha256_recheck",
        ],
        "rollback_manifest": "backup_root/manifest.json",
    }


def _target_sha256(path: Path) -> str:
    try:
        return f"sha256:{sha256_text(path.read_text(encoding='utf-8', errors='replace'))}"
    except OSError:
        return ""


def _write_manifest(*, payload: dict, manifest_path: Path) -> None:
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prune retired runtime-managed files from a target repository.")
    parser.add_argument("--target-repo", required=True, help="Target repository root.")
    parser.add_argument("--baseline-path", default=str(DEFAULT_BASELINE_PATH), help="Governance baseline JSON path.")
    parser.add_argument(
        "--backup-root",
        help="Directory for backups before deletion. Defaults to <target-repo>/.governed-ai/backups/retired-managed-files/<timestamp>.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Only report delete candidates.")
    parser.add_argument("--apply", action="store_true", help="Delete safe retired managed candidates.")
    return parser


def prune_retired_managed_files(
    *,
    target_repo: Path,
    baseline: dict,
    backup_root: Path | None,
    dry_run: bool,
    apply: bool,
) -> tuple[dict, int]:
    if dry_run and apply:
        raise ValueError("--dry-run and --apply are mutually exclusive")
    root = target_repo.resolve(strict=False)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    resolved_backup_root = (
        backup_root.resolve(strict=False)
        if backup_root is not None
        else root / ".governed-ai" / "backups" / "retired-managed-files" / timestamp
    )
    inventory = inspect_managed_assets(target_repo=root, baseline=baseline, repo_root=ROOT)
    candidates: list[dict] = []
    blocked: list[dict] = []
    deleted: list[dict] = []
    missing: list[dict] = []
    if inventory.get("status") != "pass":
        for error in inventory.get("reference_scan_errors", []):
            if not isinstance(error, dict):
                continue
            blocked.append(
                {
                    "path": str(error.get("path", "")),
                    "reason": str(error.get("reason", "reference_scan_unreadable")),
                    "classification": "reference_scan_error",
                    "error": str(error.get("error", "")),
                }
            )

    retired_paths = {
        normalize_relative_text(str(item.get("path", "")))
        for item in baseline.get("retired_managed_files", [])
        if isinstance(item, dict)
    }
    assets = [asset for asset in inventory["assets"] if asset["path"] in retired_paths]
    for asset in assets:
        path = asset["path"]
        if not asset.get("exists"):
            missing.append({"path": path, "reason": "missing"})
            continue
        if asset["classification"] != "retired_managed_candidate":
            blocked.append({"path": path, "reason": asset["reason"], "classification": asset["classification"]})
            continue
        if asset.get("referenced_by"):
            blocked.append(
                {
                    "path": path,
                    "reason": "active_references",
                    "classification": asset["classification"],
                    "referenced_by": asset["referenced_by"],
                }
            )
            continue
        candidates.append(
            asset
            | {
                "proof": _candidate_proof(
                    backup_required=bool(asset.get("backup_required")),
                    backup_written=False,
                )
            }
        )

    if apply and not blocked:
        for asset in candidates:
            target_path = repo_relative_path(root, asset["path"])
            backup_path = resolved_backup_root / asset["path"]
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target_path, backup_path)
            current_sha256 = _target_sha256(target_path)
            if current_sha256 != asset.get("target_sha256"):
                blocked.append(
                    {
                        "path": asset["path"],
                        "reason": "target_changed_before_delete",
                        "classification": asset.get("classification", ""),
                        "expected_sha256": asset.get("target_sha256", ""),
                        "actual_sha256": current_sha256,
                        "backup_path": str(backup_path),
                    }
                )
                asset["proof"]["backup_written"] = True
                break
            target_path.unlink()
            asset["proof"]["backup_written"] = True
            deleted.append(
                {
                    "path": asset["path"],
                    "backup_path": str(backup_path),
                    "target_sha256": asset.get("target_sha256", ""),
                    "proof": dict(asset["proof"]),
                    "rollback": f"copy {backup_path} back to {target_path}",
                }
            )

    status = "blocked" if blocked else "pass"
    manifest_required = bool(apply and (deleted or any("backup_path" in item for item in blocked)))
    manifest_path = resolved_backup_root / "manifest.json" if manifest_required else None
    payload = {
        "operation_type": OPERATION_TYPE,
        "deletion_policy": DELETION_POLICY,
        "safety_contract": _safety_contract(),
        "target_repo": str(root),
        "status": status,
        "reason": "blocked_retired_files" if blocked else "ok",
        "dry_run": bool(dry_run or not apply),
        "apply": bool(apply),
        "backup_root": str(resolved_backup_root),
        "manifest_path": str(manifest_path) if manifest_path is not None else "",
        "summary": {
            "retired_files": len(assets),
            "delete_candidates": len(candidates),
            "deleted": len(deleted),
            "blocked": len(blocked),
            "missing": len(missing),
        },
        "delete_candidates": candidates,
        "deleted_files": deleted,
        "blocked_files": blocked,
        "missing_files": missing,
        "modified": bool(deleted),
    }
    if manifest_path is not None:
        _write_manifest(payload=payload, manifest_path=manifest_path)
    return payload, (2 if blocked else 0)


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    apply = bool(args.apply)
    dry_run = bool(args.dry_run or not apply)
    baseline = load_json_object(Path(args.baseline_path).resolve(strict=False))
    payload, exit_code = prune_retired_managed_files(
        target_repo=Path(args.target_repo),
        baseline=baseline,
        backup_root=Path(args.backup_root) if args.backup_root else None,
        dry_run=dry_run,
        apply=apply,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
