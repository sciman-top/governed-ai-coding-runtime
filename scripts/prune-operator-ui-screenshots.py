from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CHANGE_EVIDENCE_ROOT = ROOT / "docs" / "change-evidence"
DEFAULT_ARCHIVE_ROOT = DEFAULT_CHANGE_EVIDENCE_ROOT / "archive" / "operator-ui-screenshots"
DEFAULT_MANIFEST_ROOT = DEFAULT_CHANGE_EVIDENCE_ROOT / "archive" / "operator-ui-screenshot-prune-manifests"
LATEST_ROOT_NAMES = {
    "operator-ui-current-runtime.png",
    "operator-ui-current-codex.png",
    "operator-ui-current-claude.png",
    "operator-ui-current-feedback.png",
    "operator-ui-current-mobile.png",
}
MILESTONE_NAMES = {
    "operator-ui-overview-button-aligned.png",
    "operator-ui-v2-workbench.png",
    "operator-ui-live-8770-after-stale-fix.png",
    "operator-ui-run-entry-desktop-20260502.png",
    "operator-ui-run-entry-mobile-20260502.png",
}


@dataclass(frozen=True, slots=True)
class ScreenshotEntry:
    category: str
    relative_path: str
    path: Path
    size_bytes: int


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Classify and prune operator UI screenshots with manifest-backed archive moves.")
    parser.add_argument(
        "--repo-root",
        default=str(ROOT),
        help="Repository root used to resolve screenshot locations.",
    )
    parser.add_argument(
        "--archive-root",
        default="",
        help="Archive directory for apply mode. Defaults to docs/change-evidence/archive/operator-ui-screenshots.",
    )
    parser.add_argument(
        "--manifest-root",
        default="",
        help="Manifest directory for apply mode. Defaults to docs/change-evidence/archive/operator-ui-screenshot-prune-manifests.",
    )
    parser.add_argument("--json", action="store_true", help="Accepted for CLI parity; output is JSON in all modes.")
    parser.add_argument("--dry-run", action="store_true", help="Report classification without moving files.")
    parser.add_argument("--apply", action="store_true", help="Move archive candidates into the archive root and write a manifest.")
    return parser


def manage_operator_ui_screenshots(
    *,
    repo_root: str | Path,
    archive_root: str | Path | None = None,
    manifest_root: str | Path | None = None,
    dry_run: bool,
    apply: bool,
) -> tuple[dict, int]:
    if dry_run and apply:
        raise ValueError("dry_run and apply are mutually exclusive")

    root = Path(repo_root).resolve(strict=False)
    change_root = root / "docs" / "change-evidence"
    archive_dir = _resolve_optional_path(
        value=archive_root,
        default=(change_root / "archive" / "operator-ui-screenshots"),
        repo_root=root,
    )
    manifest_dir = _resolve_optional_path(
        value=manifest_root,
        default=(change_root / "archive" / "operator-ui-screenshot-prune-manifests"),
        repo_root=root,
    )
    entries = _collect_entries(root, change_root)
    latest_entries = [entry for entry in entries if entry.category == "latest"]
    milestone_entries = [entry for entry in entries if entry.category == "milestone"]
    archive_candidates = [entry for entry in entries if entry.category == "archive_candidate"]

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    archive_run_dir = archive_dir / stamp
    manifest_path = manifest_dir / f"{stamp}.json"
    moved_files: list[dict[str, str]] = []

    if apply:
        archive_run_dir.mkdir(parents=True, exist_ok=True)
        manifest_dir.mkdir(parents=True, exist_ok=True)
        for entry in archive_candidates:
            destination = archive_run_dir / entry.relative_path.replace("/", "__")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(entry.path), str(destination))
            moved_files.append(
                {
                    "source": entry.relative_path,
                    "destination": destination.relative_to(root).as_posix(),
                }
            )
        manifest_payload = {
            "schema_version": "1.0",
            "kind": "operator_ui_screenshot_prune_manifest",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "repo_root": str(root),
            "archive_root": archive_run_dir.relative_to(root).as_posix(),
            "rollback_instructions": "Rollback by moving each destination file back to its source path recorded in this manifest.",
            "moved_files": moved_files,
        }
        manifest_path.write_text(json.dumps(manifest_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    payload = {
        "repo_root": str(root),
        "status": "pass",
        "reason": "ok",
        "mode": "apply" if apply else "dry_run",
        "apply_requested": apply,
        "dry_run": dry_run or not apply,
        "retention_policy": {
            "latest_semantics": "Root operator-ui-current-*.png files are the latest operator-facing screenshots.",
            "milestone_semantics": "Named milestone screenshots remain in place to document major UI checkpoints and current entrypoint UX.",
            "archive_candidate_semantics": "Historical operator UI screenshots outside latest/milestone sets should move behind archive manifests before removal from the active work surface.",
            "apply_requires": ["--apply", "archive manifest", "rollback instructions"],
        },
        "summary": {
            "total_screenshots": len(entries),
            "total_size_bytes": sum(entry.size_bytes for entry in entries),
            "latest_count": len(latest_entries),
            "latest_size_bytes": sum(entry.size_bytes for entry in latest_entries),
            "milestone_count": len(milestone_entries),
            "milestone_size_bytes": sum(entry.size_bytes for entry in milestone_entries),
            "archive_candidate_count": len(archive_candidates),
            "archive_candidate_size_bytes": sum(entry.size_bytes for entry in archive_candidates),
            "moved_count": len(moved_files),
        },
        "latest": [_entry_row(entry) for entry in latest_entries],
        "milestones": [_entry_row(entry) for entry in milestone_entries],
        "archive_candidates": [_entry_row(entry) for entry in archive_candidates],
        "archive_plan": {
            "archive_root": archive_run_dir.relative_to(root).as_posix(),
            "manifest_path": manifest_path.relative_to(root).as_posix(),
            "rollback_instructions": "Move archived screenshots back to their original relative paths using the manifest if this retention decision is rejected.",
        },
        "moved_files": moved_files,
    }
    return payload, 0


def _resolve_optional_path(*, value: str | Path | None, default: Path, repo_root: Path) -> Path:
    if value is None:
        return default
    raw = str(value).strip()
    if not raw:
        return default
    path = Path(raw)
    if not path.is_absolute():
        path = repo_root / path
    return path.resolve(strict=False)


def _collect_entries(root: Path, change_root: Path) -> list[ScreenshotEntry]:
    entries: list[ScreenshotEntry] = []
    for path in sorted(change_root.glob("*operator-ui*.png")):
        if path.is_file():
            entries.append(_build_entry(root, path))
    for path in sorted(root.glob("operator-ui-*.png")):
        if path.is_file():
            entries.append(_build_entry(root, path))
    return entries


def _build_entry(root: Path, path: Path) -> ScreenshotEntry:
    relative_path = path.relative_to(root).as_posix()
    name = path.name
    if name in LATEST_ROOT_NAMES:
      category = "latest"
    elif name in MILESTONE_NAMES:
      category = "milestone"
    else:
      category = "archive_candidate"
    return ScreenshotEntry(
        category=category,
        relative_path=relative_path,
        path=path,
        size_bytes=path.stat().st_size,
    )


def _entry_row(entry: ScreenshotEntry) -> dict[str, str | int]:
    return {
        "path": entry.relative_path,
        "size_bytes": entry.size_bytes,
    }


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    payload, exit_code = manage_operator_ui_screenshots(
        repo_root=args.repo_root,
        archive_root=args.archive_root,
        manifest_root=args.manifest_root,
        dry_run=bool(args.dry_run),
        apply=bool(args.apply),
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
