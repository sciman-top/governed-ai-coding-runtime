from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import re


_RUN_FILE_PATTERN = re.compile(r"^(?P<target>.+?)-(?P<flow>onboard|daily)(?:-[a-z0-9]+)?-(?P<stamp>\d{14})\.json$")
_DERIVED_FILE_PATTERN = re.compile(r"^(summary-|kpi-).+\.json$")


@dataclass(frozen=True, slots=True)
class RunEntry:
    target: str
    timestamp: datetime
    path: Path


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prune old target-repo run evidence files.")
    parser.add_argument(
        "--runs-root",
        default=str(Path(__file__).resolve().parents[1] / "docs" / "change-evidence" / "target-repo-runs"),
        help="Directory containing target-repo run evidence JSON files.",
    )
    parser.add_argument("--keep-days", type=int, default=30, help="Keep runs newer than now-keep-days.")
    parser.add_argument(
        "--keep-latest-per-target",
        type=int,
        default=30,
        help="Keep latest N runs per target regardless of age.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Only report delete candidates without deleting files.")
    return parser


def prune_target_repo_runs(
    *,
    runs_root: str | Path,
    keep_days: int,
    keep_latest_per_target: int,
    dry_run: bool,
) -> tuple[dict, int]:
    if keep_days < 0:
        raise ValueError("keep_days must be >= 0")
    if keep_latest_per_target < 0:
        raise ValueError("keep_latest_per_target must be >= 0")

    root = Path(runs_root).resolve(strict=False)
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    if not root.exists():
        payload = {
            "runs_root": str(root),
            "status": "pass",
            "reason": "runs_root_missing",
            "now_utc": now_iso,
            "keep_days": keep_days,
            "keep_latest_per_target": keep_latest_per_target,
            "dry_run": dry_run,
            "summary": {
                "total_run_files": 0,
                "kept": 0,
                "delete_candidates": 0,
                "deleted": 0,
                "failed_deletions": 0,
                "derived_files_preserved": 0,
            },
            "targets": [],
            "deleted_files": [],
            "failed_deletions": [],
        }
        return payload, 0

    entries, derived_files = _collect_entries(root)
    keep_paths = _build_keep_set(entries=entries, now=now, keep_days=keep_days, keep_latest_per_target=keep_latest_per_target)

    by_target: dict[str, dict[str, int]] = {}
    kept_entries: list[RunEntry] = []
    delete_entries: list[RunEntry] = []
    for entry in entries:
        target_stats = by_target.setdefault(
            entry.target,
            {
                "total": 0,
                "kept": 0,
                "delete_candidates": 0,
                "deleted": 0,
            },
        )
        target_stats["total"] += 1
        if entry.path in keep_paths:
            kept_entries.append(entry)
            target_stats["kept"] += 1
        else:
            delete_entries.append(entry)
            target_stats["delete_candidates"] += 1

    deleted_files: list[str] = []
    failed_deletions: list[dict[str, str]] = []
    if not dry_run:
        for entry in delete_entries:
            try:
                entry.path.unlink()
                deleted_files.append(entry.path.name)
                by_target[entry.target]["deleted"] += 1
            except OSError as exc:
                failed_deletions.append({"file": entry.path.name, "error": str(exc)})

    status = "pass" if not failed_deletions else "fail"
    reason = "ok" if status == "pass" else "delete_failed"
    payload = {
        "runs_root": str(root),
        "status": status,
        "reason": reason,
        "now_utc": now_iso,
        "keep_days": keep_days,
        "keep_latest_per_target": keep_latest_per_target,
        "dry_run": dry_run,
        "summary": {
            "total_run_files": len(entries),
            "kept": len(kept_entries),
            "delete_candidates": len(delete_entries),
            "deleted": len(deleted_files),
            "failed_deletions": len(failed_deletions),
            "derived_files_preserved": len(derived_files),
        },
        "targets": _target_rows(by_target),
        "deleted_files": sorted(deleted_files),
        "failed_deletions": failed_deletions,
    }
    return payload, (0 if status == "pass" else 1)


def _collect_entries(root: Path) -> tuple[list[RunEntry], list[Path]]:
    entries: list[RunEntry] = []
    derived_files: list[Path] = []
    for path in sorted(root.glob("*.json")):
        match = _RUN_FILE_PATTERN.match(path.name)
        if match:
            entries.append(
                RunEntry(
                    target=match.group("target"),
                    timestamp=_parse_stamp(match.group("stamp")),
                    path=path,
                )
            )
            continue
        if _DERIVED_FILE_PATTERN.match(path.name):
            derived_files.append(path)
    return entries, derived_files


def _build_keep_set(
    *,
    entries: list[RunEntry],
    now: datetime,
    keep_days: int,
    keep_latest_per_target: int,
) -> set[Path]:
    keep_paths: set[Path] = set()
    if keep_days > 0:
        cutoff = now - timedelta(days=keep_days)
        for entry in entries:
            if entry.timestamp >= cutoff:
                keep_paths.add(entry.path)

    if keep_latest_per_target > 0:
        grouped: dict[str, list[RunEntry]] = {}
        for entry in entries:
            grouped.setdefault(entry.target, []).append(entry)
        for per_target_entries in grouped.values():
            sorted_entries = sorted(per_target_entries, key=lambda item: item.timestamp, reverse=True)
            for entry in sorted_entries[:keep_latest_per_target]:
                keep_paths.add(entry.path)
    return keep_paths


def _target_rows(by_target: dict[str, dict[str, int]]) -> list[dict]:
    rows: list[dict] = []
    for target in sorted(by_target):
        stats = by_target[target]
        rows.append(
            {
                "target": target,
                "total": stats["total"],
                "kept": stats["kept"],
                "delete_candidates": stats["delete_candidates"],
                "deleted": stats["deleted"],
            }
        )
    return rows


def _parse_stamp(stamp: str) -> datetime:
    return datetime.strptime(stamp, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    payload, exit_code = prune_target_repo_runs(
        runs_root=args.runs_root,
        keep_days=args.keep_days,
        keep_latest_per_target=args.keep_latest_per_target,
        dry_run=bool(args.dry_run),
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
