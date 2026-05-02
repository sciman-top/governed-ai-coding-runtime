from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from json import JSONDecodeError
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
    profile_patch_candidates: list[dict[str, Any]] = []
    deleted_files: list[dict[str, str]] = []
    patched_shared_files: list[dict[str, str]] = []
    patched_profile_files: list[dict[str, str]] = []
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
            if not item.get("shared_ownership_evidence"):
                blocked.append(
                    {
                        "path": path,
                        "reason": "shared_patch_requires_ownership_evidence",
                        "classification": "shared_or_field_owned",
                        "management_mode": mode,
                    }
                )
                continue
            source = item.get("source")
            if not isinstance(source, str) or not source.strip():
                blocked.append({"path": path, "reason": "shared_source_missing"})
                continue
            source_file = source_path(source, repo_root=ROOT)
            if not source_file.exists():
                blocked.append({"path": path, "reason": "shared_source_not_found", "source": str(source_file)})
                continue
            actual, actual_error = _load_json_for_uninstall(target_path)
            if actual_error is not None:
                blocked.append({"path": path, "reason": "invalid_json", "source": str(target_path), "error": actual_error})
                continue
            overlay, overlay_error = _load_json_for_uninstall(source_file)
            if overlay_error is not None:
                blocked.append({"path": path, "reason": "shared_source_invalid_json", "source": str(source_file), "error": overlay_error})
                continue
            patched = _remove_json_overlay(actual, overlay)
            if patched == actual:
                missing.append({"path": path, "reason": "shared_overlay_absent"})
                continue
            record = {"path": path, "management_mode": mode, "source": str(source_file)}
            shared_patch_candidates.append(record)
            record["patched_content"] = patched
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
        delete_candidates.append(asset)

    for item in baseline.get("generated_managed_files", []):
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            continue
        path = normalize_relative_text(item["path"])
        target_path = repo_relative_path(root, path)
        asset = classify_asset(
            target_repo=root,
            repo_root=ROOT,
            relative_path=path,
            active_entry=None,
            generated_entry=item,
            retired_entry=None,
        )
        if not asset.get("exists"):
            missing.append({"path": path, "reason": asset.get("reason", "missing_generated_file")})
            continue
        if asset["classification"] != "active_managed":
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
        delete_candidates.append(asset)

    profile_patch = _build_profile_patch(target_repo=root, baseline=baseline)
    if profile_patch["status"] == "candidate":
        profile_patch_candidates.append(profile_patch)
    elif profile_patch["status"] == "missing":
        missing.append({"path": profile_patch["path"], "reason": profile_patch["reason"]})
    elif profile_patch["status"] == "blocked":
        blocked.append(
            {
                "path": profile_patch["path"],
                "reason": profile_patch["reason"],
                "classification": "shared_or_field_owned",
            }
        )

    if apply and not blocked:
        for record in shared_patch_candidates:
            path = record["path"]
            target_path = repo_relative_path(root, path)
            backup_path = _backup_file(target_path=target_path, backup_root=resolved_backup_root, relative_path=path)
            target_path.write_text(
                json.dumps(record["patched_content"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            patched_shared_files.append(
                {
                    "path": path,
                    "backup_path": str(backup_path),
                    "rollback": f"copy {backup_path} back to {target_path}",
                }
            )
        for asset in delete_candidates:
            target_path = repo_relative_path(root, asset["path"])
            backup_path = _backup_file(target_path=target_path, backup_root=resolved_backup_root, relative_path=asset["path"])
            target_path.unlink()
            deleted_files.append(
                {
                    "path": asset["path"],
                    "backup_path": str(backup_path),
                    "target_sha256": str(asset.get("target_sha256", "")),
                    "rollback": f"copy {backup_path} back to {target_path}",
                }
            )
        for record in profile_patch_candidates:
            target_path = Path(record["absolute_path"])
            backup_path = _backup_file(target_path=target_path, backup_root=resolved_backup_root, relative_path=record["path"])
            target_path.write_text(
                json.dumps(record["patched_content"], ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            patched_profile_files.append(
                {
                    "path": record["path"],
                    "backup_path": str(backup_path),
                    "removed_fields": record["removed_fields"],
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
            "profile_patch_candidates": len(profile_patch_candidates),
            "deleted": len(deleted_files),
            "shared_patched": len(patched_shared_files),
            "profile_patched": len(patched_profile_files),
            "blocked": len(blocked),
            "missing": len(missing),
        },
        "delete_candidates": delete_candidates,
        "shared_patch_candidates": [_public_record(record) for record in shared_patch_candidates],
        "profile_patch_candidates": [_public_record(record) for record in profile_patch_candidates],
        "deleted_files": deleted_files,
        "patched_shared_files": patched_shared_files,
        "patched_profile_files": patched_profile_files,
        "blocked_files": blocked,
        "missing_files": missing,
        "modified": bool(deleted_files or patched_shared_files or patched_profile_files),
    }
    return payload, (2 if blocked else 0)


def _backup_file(*, target_path: Path, backup_root: Path, relative_path: str) -> Path:
    backup_path = backup_root / relative_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(target_path, backup_path)
    return backup_path


def _build_profile_patch(*, target_repo: Path, baseline: dict[str, Any]) -> dict[str, Any]:
    path = ".governed-ai/repo-profile.json"
    ownership = baseline.get("repo_profile_field_ownership")
    if ownership is None:
        return {"status": "missing", "path": path, "reason": "repo_profile_ownership_absent"}
    if not isinstance(ownership, dict):
        return {"status": "blocked", "path": path, "reason": "repo_profile_ownership_invalid"}
    fields = set(_string_list(ownership.get("baseline_override_fields"))) | set(_string_list(ownership.get("derived_runtime_fields")))
    if not fields:
        return {"status": "missing", "path": path, "reason": "repo_profile_owned_fields_absent"}
    target_path = repo_relative_path(target_repo, path)
    if not target_path.exists():
        return {"status": "missing", "path": path, "reason": "repo_profile_missing"}
    actual, actual_error = _load_json_for_uninstall(target_path)
    if actual_error is not None:
        return {"status": "blocked", "path": path, "reason": "repo_profile_invalid_json", "error": actual_error}
    if not isinstance(actual, dict):
        return {"status": "blocked", "path": path, "reason": "repo_profile_not_object"}
    removed_fields = sorted(field for field in fields if field in actual)
    if not removed_fields:
        return {"status": "missing", "path": path, "reason": "repo_profile_owned_fields_absent"}
    patched = dict(actual)
    for field in removed_fields:
        patched.pop(field, None)
    return {
        "status": "candidate",
        "path": path,
        "absolute_path": str(target_path),
        "removed_fields": removed_fields,
        "patched_content": patched,
        "evidence_refs": ["current_baseline.repo_profile_field_ownership"],
    }


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str) and item.strip()]


def _load_json_for_uninstall(path: Path) -> tuple[Any, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except JSONDecodeError as exc:
        return None, f"{exc.msg}: line {exc.lineno} column {exc.colno}"
    except OSError as exc:
        return None, str(exc)


def _public_record(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if key not in {"patched_content", "absolute_path"}}


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
