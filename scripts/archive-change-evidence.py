from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CHANGE_EVIDENCE_ROOT = ROOT / "docs" / "change-evidence"
DEFAULT_INDEX_PATH = CHANGE_EVIDENCE_ROOT / "evidence-index.json"
DEFAULT_ARCHIVE_ROOT = CHANGE_EVIDENCE_ROOT / "archive" / "change-evidence"
DEFAULT_MANIFEST_ROOT = CHANGE_EVIDENCE_ROOT / "archive" / "change-evidence-manifests"
LATEST_OPERATOR_UI_SCREENSHOTS = {
    "operator-ui-current-runtime.png",
    "operator-ui-current-codex.png",
    "operator-ui-current-claude.png",
    "operator-ui-current-feedback.png",
    "operator-ui-current-mobile.png",
}
MILESTONE_OPERATOR_UI_SCREENSHOTS = {
    "operator-ui-overview-button-aligned.png",
    "operator-ui-v2-workbench.png",
    "operator-ui-live-8770-after-stale-fix.png",
    "operator-ui-run-entry-desktop-20260502.png",
    "operator-ui-run-entry-mobile-20260502.png",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a dry-run archive index for docs/change-evidence.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-index", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--archive-root", default="")
    parser.add_argument("--manifest-root", default="")
    args = parser.parse_args()

    if args.dry_run and args.apply:
        parser.error("--dry-run and --apply are mutually exclusive")

    payload = build_change_evidence_archive_index(
        repo_root=Path(args.repo_root),
        apply=bool(args.apply),
        archive_root=Path(args.archive_root) if args.archive_root else None,
        manifest_root=Path(args.manifest_root) if args.manifest_root else None,
    )
    if args.write_index:
        DEFAULT_INDEX_PATH.write_text(json.dumps(payload["index"], ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    elif args.dry_run:
        print(f"archive candidates: {payload['dry_run']['summary']['candidate_file_count']} files")
    else:
        print(json.dumps(payload["index"], ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def build_change_evidence_archive_index(
    *,
    repo_root: Path,
    apply: bool = False,
    archive_root: Path | None = None,
    manifest_root: Path | None = None,
) -> dict[str, Any]:
    root = repo_root.resolve(strict=False)
    change_root = root / "docs" / "change-evidence"
    resolved_archive_root = _resolve_archive_path(root, archive_root, DEFAULT_ARCHIVE_ROOT)
    resolved_manifest_root = _resolve_archive_path(root, manifest_root, DEFAULT_MANIFEST_ROOT)
    payload = {
        "dry_run": _build_dry_run(root, change_root),
        "index": _build_index(root, change_root),
        "apply": _apply_archive_moves(
            root=root,
            change_root=change_root,
            archive_root=resolved_archive_root,
            manifest_root=resolved_manifest_root,
        )
        if apply
        else {
            "mode": "dry_run",
            "moved_file_count": 0,
            "rollback_ref": "No archive moves were requested.",
        },
    }
    return payload


def _build_index(root: Path, change_root: Path) -> dict[str, Any]:
    latest_md = _latest_markdown_entries(change_root, limit=12)
    latest_json = [
        "docs/change-evidence/repo-slimming-surface-audit.json",
        "docs/change-evidence/repo-map-context-artifact.json",
        "docs/change-evidence/runtime-test-speed-latest.json",
        "docs/change-evidence/target-repo-runs/kpi-latest.json",
        "docs/change-evidence/target-repo-runs/kpi-rolling.json",
        "docs/change-evidence/target-repo-runs/summary-latest.json",
        "docs/change-evidence/target-repo-runs/summary-active-targets-latest.json",
    ]
    latest_json = [path for path in latest_json if (root / path).exists()]
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "index_kind": "change_evidence_archive_index",
        "current_policy": {
            "current_semantics": "Latest authoritative evidence, latest summaries, active plan companions, and machine-readable latest pointers stay easy to find.",
        "archive_semantics": "Historical snapshots, old screenshots, and rule-sync backups become archive candidates once a later task adds move manifests and rollback. Target-repo run JSON remains active evidence and is pruned only through the target-run retention tool.",
            "move_authorization": "No file movement is authorized by this index.",
        },
        "current_refs": {
            "latest_markdown_entries": latest_md,
            "latest_machine_readable_refs": latest_json,
        },
        "archive_candidate_groups": _archive_candidate_groups(root, change_root),
    }


def _build_dry_run(root: Path, change_root: Path) -> dict[str, Any]:
    groups = _archive_candidate_groups(root, change_root)
    total_files = sum(int(group["candidate_file_count"]) for group in groups)
    total_bytes = sum(int(group["candidate_byte_count"]) for group in groups)
    return {
        "mode": "dry_run",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "candidate_group_count": len(groups),
            "candidate_file_count": total_files,
            "candidate_byte_count": total_bytes,
            "candidate_megabytes": round(total_bytes / (1024 * 1024), 2),
        },
        "candidate_groups": groups,
        "rollback_ref": "Dry-run only; no files were moved or deleted.",
    }


def _archive_candidate_groups(root: Path, change_root: Path) -> list[dict[str, Any]]:
    candidates = _archive_candidate_files(root, change_root)
    groups = [
        _group_payload(root, group_name, files)
        for group_name, files in candidates.items()
    ]
    return [group for group in groups if group["candidate_file_count"] > 0]


def _archive_candidate_files(root: Path, change_root: Path) -> dict[str, list[Path]]:
    return {
        "historical_snapshots": _directory_files(change_root / "snapshots"),
        "rule_sync_backups": _directory_files(change_root / "rule-sync-backups"),
        "docs_operator_ui_screenshots": _operator_ui_screenshot_files(change_root, root_level=False),
        "root_operator_ui_screenshots": _operator_ui_screenshot_files(root, root_level=True),
    }


def _directory_files(directory: Path) -> list[Path]:
    return [path for path in sorted(directory.rglob("*")) if path.is_file()] if directory.exists() else []


def _operator_ui_screenshot_files(directory: Path, *, root_level: bool) -> list[Path]:
    if not directory.exists():
        return []
    keep_names = LATEST_OPERATOR_UI_SCREENSHOTS | MILESTONE_OPERATOR_UI_SCREENSHOTS
    return [
        path
        for path in sorted(directory.glob("operator-ui*.png" if not root_level else "operator-ui-*.png"))
        if path.is_file() and path.name not in keep_names
    ]


def _group_payload(root: Path, group_name: str, files: list[Path]) -> dict[str, Any]:
    total_bytes = sum(path.stat().st_size for path in files)
    return {
        "group": group_name,
        "candidate_file_count": len(files),
        "candidate_byte_count": total_bytes,
        "candidate_megabytes": round(total_bytes / (1024 * 1024), 2),
        "sample_paths": [path.relative_to(root).as_posix() for path in files[:12]],
    }


def _latest_markdown_entries(change_root: Path, *, limit: int) -> list[str]:
    entries = [
        path
        for path in sorted(change_root.glob("*.md"), reverse=True)
        if path.is_file() and path.name != "README.md"
    ]
    return [path.relative_to(change_root.parent.parent).as_posix() for path in entries[:limit]]


def _apply_archive_moves(*, root: Path, change_root: Path, archive_root: Path, manifest_root: Path) -> dict[str, Any]:
    candidates = _archive_candidate_files(root, change_root)
    all_files = [(group_name, path) for group_name, files in candidates.items() for path in files]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_archive_root = archive_root / stamp
    manifest_path = manifest_root / f"{stamp}.json"
    moved_files: list[dict[str, str]] = []

    if all_files:
        run_archive_root.mkdir(parents=True, exist_ok=True)
        manifest_root.mkdir(parents=True, exist_ok=True)

    for group_name, source in all_files:
        relative_source = source.relative_to(root).as_posix()
        destination = run_archive_root / relative_source
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source), str(destination))
        moved_files.append(
            {
                "group": group_name,
                "source": relative_source,
                "destination": destination.relative_to(root).as_posix(),
            }
        )

    manifest_payload = {
        "schema_version": "1.0",
        "kind": "change_evidence_archive_manifest",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(root),
        "archive_root": run_archive_root.relative_to(root).as_posix(),
        "rollback_instructions": "Rollback by moving each destination file back to its source path recorded in this manifest.",
        "moved_files": moved_files,
    }
    manifest_root.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return {
        "mode": "apply",
        "archive_root": run_archive_root.relative_to(root).as_posix(),
        "manifest_path": manifest_path.relative_to(root).as_posix(),
        "moved_file_count": len(moved_files),
        "moved_files": moved_files,
        "rollback_ref": manifest_payload["rollback_instructions"],
    }


def _resolve_archive_path(root: Path, value: Path | None, default: Path) -> Path:
    if value is None:
        return default
    if value.is_absolute():
        return value.resolve(strict=False)
    return (root / value).resolve(strict=False)


if __name__ == "__main__":
    raise SystemExit(main())
