from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CHANGE_EVIDENCE_ROOT = ROOT / "docs" / "change-evidence"
DEFAULT_INDEX_PATH = CHANGE_EVIDENCE_ROOT / "evidence-index.json"
KEEP_TARGET_RUN_FILES = {
    "kpi-latest.json",
    "kpi-rolling.json",
    "summary-latest.json",
    "summary-active-targets-latest.json",
    "summary-active-targets-rows-20260422191507.json",
    "summary-active-targets-20260422191507.json",
    "summary-allowedscope.json",
    "summary-github-vps.json",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a dry-run archive index for docs/change-evidence.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-index", action="store_true")
    args = parser.parse_args()

    payload = build_change_evidence_archive_index(repo_root=Path(args.repo_root))
    if args.write_index:
        DEFAULT_INDEX_PATH.write_text(json.dumps(payload["index"], ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    elif args.dry_run:
        print(f"archive candidates: {payload['dry_run']['summary']['candidate_file_count']} files")
    else:
        print(json.dumps(payload["index"], ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def build_change_evidence_archive_index(*, repo_root: Path) -> dict[str, Any]:
    root = repo_root.resolve(strict=False)
    change_root = root / "docs" / "change-evidence"
    payload = {
        "dry_run": _build_dry_run(root, change_root),
        "index": _build_index(root, change_root),
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
            "archive_semantics": "Historical snapshots, old screenshots, rule-sync backups, and superseded raw run payloads become archive candidates once a later task adds move manifests and rollback.",
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
    groups = [
        _directory_group(root, change_root / "snapshots", "historical_snapshots"),
        _directory_group(root, change_root / "rule-sync-backups", "rule_sync_backups"),
        _target_run_group(root, change_root / "target-repo-runs"),
        _pattern_group(root, change_root, "docs_operator_ui_screenshots", "operator-ui*.png"),
        _root_pattern_group(root, "root_operator_ui_screenshots", "operator-ui-*.png"),
    ]
    return [group for group in groups if group["candidate_file_count"] > 0]


def _directory_group(root: Path, directory: Path, group_name: str) -> dict[str, Any]:
    files = [path for path in sorted(directory.rglob("*")) if path.is_file()] if directory.exists() else []
    return _group_payload(root, group_name, files)


def _pattern_group(root: Path, directory: Path, group_name: str, pattern: str) -> dict[str, Any]:
    files = [path for path in sorted(directory.glob(pattern)) if path.is_file()] if directory.exists() else []
    return _group_payload(root, group_name, files)


def _root_pattern_group(root: Path, group_name: str, pattern: str) -> dict[str, Any]:
    files = [path for path in sorted(root.glob(pattern)) if path.is_file()]
    return _group_payload(root, group_name, files)


def _target_run_group(root: Path, directory: Path) -> dict[str, Any]:
    if not directory.exists():
        return _group_payload(root, "target_repo_raw_runs", [])
    files: list[Path] = []
    for path in sorted(directory.glob("*.json")):
        if path.name in KEEP_TARGET_RUN_FILES:
            continue
        if "-daily-" in path.name or "-onboard-" in path.name or "effect-report-" in path.name:
            files.append(path)
    return _group_payload(root, "target_repo_raw_runs", files)


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


if __name__ == "__main__":
    raise SystemExit(main())
