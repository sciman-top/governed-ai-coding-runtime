from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
from typing import Any

from lib.target_repo_managed_assets import (
    classify_asset,
    load_json_object,
    normalize_relative_text,
    repo_relative_path,
    source_path,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE_PATH = ROOT / "docs" / "targets" / "target-repo-governance-baseline.json"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Uninstall governed-ai-coding-runtime governance assets from a target repo.")
    parser.add_argument("--target-repo", required=True, help="Target repository root.")
    parser.add_argument("--baseline-path", default=str(DEFAULT_BASELINE_PATH), help="Governance baseline JSON path.")
    parser.add_argument(
        "--backup-root",
        help="Directory for backups before deletion or patching. Defaults to <target-repo>/.governed-ai/backups/uninstall/<timestamp>.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Only report uninstall plan.")
    parser.add_argument("--apply", action="store_true", help="Apply safe deletes and shared-file patches.")
    return parser


def uninstall_target_repo_governance(
    *,
    target_repo: Path,
    baseline: dict[str, Any],
    backup_root: Path | None,
    dry_run: bool,
    apply: bool,
) -> tuple[dict[str, Any], int]:
    if dry_run and apply:
        raise ValueError("--dry-run and --apply are mutually exclusive")
    root = target_repo.resolve(strict=False)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    resolved_backup_root = (
        backup_root.resolve(strict=False)
        if backup_root is not None
        else root / ".governed-ai" / "backups" / "uninstall" / timestamp
    )
    delete_candidates: list[dict[str, Any]] = []
    shared_patch_candidates: list[dict[str, Any]] = []
    deleted_files: list[dict[str, str]] = []
    patched_shared_files: list[dict[str, str]] = []
    blocked: list[dict[str, Any]] = []
    missing: list[dict[str, str]] = []

    for item in baseline.get("required_managed_files", []):
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            continue
        path = normalize_relative_text(item["path"])
        mode = str(item.get("management_mode", "block_on_drift"))
        target_path = repo_relative_path(root, path)
        if mode == "json_merge":
            if not target_path.exists():
                missing.append({"path": path, "reason": "missing_shared_file"})
                continue
            source = item.get("source")
            if not isinstance(source, str) or not source.strip():
                blocked.append({"path": path, "reason": "shared_source_missing"})
                continue
            source_file = source_path(source, repo_root=ROOT)
            if not source_file.exists():
                blocked.append({"path": path, "reason": "shared_source_not_found", "source": str(source_file)})
                continue
            actual = json.loads(target_path.read_text(encoding="utf-8"))
            overlay = json.loads(source_file.read_text(encoding="utf-8"))
            patched = _remove_json_overlay(actual, overlay)
            if patched == actual:
                missing.append({"path": path, "reason": "shared_overlay_absent"})
                continue
            record = {"path": path, "management_mode": mode, "source": str(source_file)}
            shared_patch_candidates.append(record)
            if apply:
                backup_path = _backup_file(target_path=target_path, backup_root=resolved_backup_root, relative_path=path)
                target_path.write_text(json.dumps(patched, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                patched_shared_files.append(
                    {
                        "path": path,
                        "backup_path": str(backup_path),
                        "rollback": f"copy {backup_path} back to {target_path}",
                    }
                )
            continue

        asset = classify_asset(
            target_repo=root,
            repo_root=ROOT,
            relative_path=path,
            active_entry=item,
            generated_entry=None,
            retired_entry=None,
        )
        if not asset.get("exists"):
            missing.append({"path": path, "reason": "missing"})
            continue
        if asset["classification"] != "active_managed":
            blocked.append({"path": path, "reason": asset["reason"], "classification": asset["classification"]})
            continue
        delete_candidates.append(asset)
        if apply:
            backup_path = _backup_file(target_path=target_path, backup_root=resolved_backup_root, relative_path=path)
            target_path.unlink()
            deleted_files.append(
                {
                    "path": path,
                    "backup_path": str(backup_path),
                    "target_sha256": str(asset.get("target_sha256", "")),
                    "rollback": f"copy {backup_path} back to {target_path}",
                }
            )

    for item in baseline.get("generated_managed_files", []):
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            continue
        path = normalize_relative_text(item["path"])
        target_path = repo_relative_path(root, path)
        if not target_path.exists():
            missing.append({"path": path, "reason": "missing_generated_file"})
            continue
        record = {
            "path": path,
            "classification": "active_managed",
            "reason": "generated_managed_file",
            "generator": str(item.get("generator", "")),
        }
        delete_candidates.append(record)
        if apply:
            backup_path = _backup_file(target_path=target_path, backup_root=resolved_backup_root, relative_path=path)
            target_path.unlink()
            deleted_files.append(
                {
                    "path": path,
                    "backup_path": str(backup_path),
                    "target_sha256": "",
                    "rollback": f"copy {backup_path} back to {target_path}",
                }
            )

    status = "blocked" if blocked else "pass"
    payload = {
        "target_repo": str(root),
        "status": status,
        "reason": "blocked_uninstall_files" if blocked else "ok",
        "dry_run": bool(dry_run or not apply),
        "apply": bool(apply),
        "backup_root": str(resolved_backup_root),
        "summary": {
            "delete_candidates": len(delete_candidates),
            "shared_patch_candidates": len(shared_patch_candidates),
            "deleted": len(deleted_files),
            "shared_patched": len(patched_shared_files),
            "blocked": len(blocked),
            "missing": len(missing),
        },
        "delete_candidates": delete_candidates,
        "shared_patch_candidates": shared_patch_candidates,
        "deleted_files": deleted_files,
        "patched_shared_files": patched_shared_files,
        "blocked_files": blocked,
        "missing_files": missing,
        "modified": bool(deleted_files or patched_shared_files),
    }
    return payload, (2 if blocked else 0)


def _backup_file(*, target_path: Path, backup_root: Path, relative_path: str) -> Path:
    backup_path = backup_root / relative_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target_path, backup_path)
    return backup_path


def _remove_json_overlay(actual: Any, overlay: Any) -> Any:
    if isinstance(actual, dict) and isinstance(overlay, dict):
        result = dict(actual)
        for key, overlay_value in overlay.items():
            if key not in result:
                continue
            new_value = _remove_json_overlay(result[key], overlay_value)
            if new_value is _DELETE:
                result.pop(key, None)
            else:
                result[key] = new_value
        return result
    if isinstance(actual, list) and isinstance(overlay, list):
        result = list(actual)
        for overlay_item in overlay:
            result = [item for item in result if item != overlay_item]
        return result
    if actual == overlay:
        return _DELETE
    return actual


class _DeleteSentinel:
    pass


_DELETE = _DeleteSentinel()


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    apply = bool(args.apply)
    dry_run = bool(args.dry_run or not apply)
    baseline = load_json_object(Path(args.baseline_path).resolve(strict=False))
    payload, exit_code = uninstall_target_repo_governance(
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
