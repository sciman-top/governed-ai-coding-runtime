from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_PATH = ROOT / "docs" / "change-evidence" / "repo-slimming-surface-audit.json"
TEXT_EXTENSIONS = {
    ".md",
    ".py",
    ".ps1",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".txt",
    ".sql",
}
TRANSIENT_DIRECTORY_NAMES = {
    ".git",
    ".pytest_cache",
    ".tmp",
    ".runtime",
    ".worktrees",
    ".playwright-mcp",
    "__pycache__",
    "node_modules",
    "dist",
}
LARGE_BINARY_THRESHOLD_BYTES = 200_000


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit repository size and active work-surface weight for slimming work.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    args = parser.parse_args()

    payload = audit_repo_slimming_surface(
        repo_root=Path(args.repo_root),
        output_path=Path(args.output),
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def audit_repo_slimming_surface(*, repo_root: Path, output_path: Path) -> dict[str, Any]:
    root = repo_root.resolve(strict=False)
    visible_files = _collect_visible_files(root)
    transient_inventory = _collect_transient_inventory(root)
    worktree_status = _git_status(root)

    files_by_area = _group_by_area(visible_files)
    text_files = [item for item in visible_files if item["extension"] in TEXT_EXTENSIONS]
    text_lines_total = sum(int(item["line_count"] or 0) for item in text_files)
    docs_change_evidence = files_by_area.get("docs/change-evidence")
    large_binary_evidence = [
        {
            "path": item["relative_path"],
            "bytes": item["bytes"],
            "megabytes": _round_mb(item["bytes"]),
            "extension": item["extension"] or "[none]",
            "area": item["area"],
        }
        for item in visible_files
        if _is_large_binary_evidence(item)
    ]

    payload = {
        "schema_version": "1.0",
        "report_kind": "repo_slimming_surface_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_id": root.name,
        "repo_root": str(root),
        "safety_fence": {
            "delete_mode": "forbidden_by_default",
            "archive_move_mode": "forbidden_by_default",
            "override_condition": "Task 2 or later must add dry-run proof, rollback, focused verification, and change evidence before archive movement.",
            "notes": "Task 1 is inventory-only.",
        },
        "visible_surface": {
            "excluded_directory_names": sorted(TRANSIENT_DIRECTORY_NAMES),
            "file_count": len(visible_files),
            "byte_count": sum(item["bytes"] for item in visible_files),
            "megabytes": _round_mb(sum(item["bytes"] for item in visible_files)),
        },
        "text_surface": {
            "extensions": sorted(TEXT_EXTENSIONS),
            "file_count": len(text_files),
            "line_count": text_lines_total,
        },
        "active_surface_breakdown": {
            "docs": _area_summary(files_by_area, "docs"),
            "docs_change_evidence": _area_summary(files_by_area, "docs/change-evidence"),
            "scripts": _area_summary(files_by_area, "scripts"),
            "tests": _area_summary(files_by_area, "tests"),
            "packages": _area_summary(files_by_area, "packages"),
            "schemas": _area_summary(files_by_area, "schemas"),
            "rules": _area_summary(files_by_area, "rules"),
            "apps": _area_summary(files_by_area, "apps"),
        },
        "transient_surface_breakdown": transient_inventory,
        "top_level_directories": _summaries_by_top_level(visible_files),
        "largest_files": _largest_files(visible_files, limit=25),
        "largest_text_files": _largest_text_files(text_files, limit=25),
        "large_binary_evidence": large_binary_evidence,
        "extension_summary": _extension_summary(visible_files, limit=20),
        "hotspots": {
            "likely_entrypoint_hotspots": _select_hotspots(visible_files),
            "docs_change_evidence_summary": docs_change_evidence or {"file_count": 0, "byte_count": 0, "megabytes": 0.0, "text_line_count": 0},
        },
        "out_of_scope_dirty_worktree": {
            "entry_count": len(worktree_status),
            "entries": worktree_status,
            "adoption_policy": "Existing dirty worktree entries remain out of scope unless explicitly adopted by the current slimming task.",
        },
        "comparison_keys": {
            "visible_surface_path": "visible_surface",
            "text_surface_path": "text_surface",
            "top_level_directory_path": "top_level_directories",
            "active_surface_breakdown_path": "active_surface_breakdown",
            "large_binary_evidence_path": "large_binary_evidence",
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def _collect_visible_files(root: Path) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for path in _iter_visible_files(root):
        relative_path = path.relative_to(root).as_posix()
        extension = path.suffix.lower()
        line_count = _line_count(path) if extension in TEXT_EXTENSIONS else None
        files.append(
            {
                "relative_path": relative_path,
                "bytes": path.stat().st_size,
                "extension": extension,
                "line_count": line_count,
                "top_level": _top_level(relative_path),
                "area": _classify_area(relative_path),
            }
        )
    return files


def _iter_visible_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in TRANSIENT_DIRECTORY_NAMES for part in path.relative_to(root).parts):
            continue
        yield path


def _collect_transient_inventory(root: Path) -> dict[str, dict[str, Any]]:
    summary: dict[str, dict[str, Any]] = {}
    for name in sorted(TRANSIENT_DIRECTORY_NAMES):
        matches = [path for path in root.rglob(name) if path.is_dir()]
        file_count = 0
        byte_count = 0
        for directory in matches:
            for path in directory.rglob("*"):
                if path.is_file():
                    file_count += 1
                    byte_count += path.stat().st_size
        summary[name] = {
            "directory_count": len(matches),
            "file_count": file_count,
            "byte_count": byte_count,
            "megabytes": _round_mb(byte_count),
        }
    return summary


def _git_status(root: Path) -> list[str]:
    completed = subprocess.run(
        ["git", "status", "--short"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=root,
    )
    if completed.returncode != 0:
        return [f"git-status-unavailable: {completed.stderr.strip() or completed.returncode}"]
    return [line.rstrip() for line in completed.stdout.splitlines() if line.strip()]


def _line_count(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
    except OSError:
        return 0


def _top_level(relative_path: str) -> str:
    if "/" not in relative_path:
        return relative_path
    return relative_path.split("/", 1)[0]


def _classify_area(relative_path: str) -> str:
    if relative_path.startswith("docs/change-evidence/"):
        return "docs/change-evidence"
    if relative_path.startswith("docs/"):
        return "docs"
    if relative_path.startswith("scripts/"):
        return "scripts"
    if relative_path.startswith("tests/"):
        return "tests"
    if relative_path.startswith("packages/"):
        return "packages"
    if relative_path.startswith("schemas/"):
        return "schemas"
    if relative_path.startswith("rules/"):
        return "rules"
    if relative_path.startswith("apps/"):
        return "apps"
    if relative_path.startswith(".governed-ai/"):
        return ".governed-ai"
    return "root"


def _group_by_area(files: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for item in files:
        area = str(item["area"])
        current = grouped.setdefault(
            area,
            {
                "file_count": 0,
                "byte_count": 0,
                "megabytes": 0.0,
                "text_line_count": 0,
            },
        )
        current["file_count"] += 1
        current["byte_count"] += int(item["bytes"])
        current["text_line_count"] += int(item["line_count"] or 0)
    for current in grouped.values():
        current["megabytes"] = _round_mb(int(current["byte_count"]))
    return grouped


def _area_summary(grouped: dict[str, dict[str, Any]], key: str) -> dict[str, Any]:
    return grouped.get(key, {"file_count": 0, "byte_count": 0, "megabytes": 0.0, "text_line_count": 0})


def _summaries_by_top_level(files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for item in files:
        key = str(item["top_level"])
        current = grouped.setdefault(
            key,
            {"top_level": key, "file_count": 0, "byte_count": 0, "text_line_count": 0},
        )
        current["file_count"] += 1
        current["byte_count"] += int(item["bytes"])
        current["text_line_count"] += int(item["line_count"] or 0)
    result = []
    for item in grouped.values():
        result.append(
            {
                "top_level": item["top_level"],
                "file_count": item["file_count"],
                "byte_count": item["byte_count"],
                "megabytes": _round_mb(item["byte_count"]),
                "text_line_count": item["text_line_count"],
            }
        )
    return sorted(result, key=lambda item: (-item["byte_count"], item["top_level"]))


def _largest_files(files: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    ranked = sorted(files, key=lambda item: (-int(item["bytes"]), str(item["relative_path"])))
    return [
        {
            "path": item["relative_path"],
            "bytes": item["bytes"],
            "megabytes": _round_mb(item["bytes"]),
            "area": item["area"],
            "extension": item["extension"] or "[none]",
        }
        for item in ranked[:limit]
    ]


def _largest_text_files(files: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    ranked = sorted(files, key=lambda item: (-int(item["line_count"] or 0), str(item["relative_path"])))
    return [
        {
            "path": item["relative_path"],
            "line_count": item["line_count"],
            "bytes": item["bytes"],
            "megabytes": _round_mb(item["bytes"]),
            "area": item["area"],
        }
        for item in ranked[:limit]
    ]


def _extension_summary(files: list[dict[str, Any]], *, limit: int) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for item in files:
        key = item["extension"] or "[none]"
        current = grouped.setdefault(key, {"extension": key, "file_count": 0, "byte_count": 0})
        current["file_count"] += 1
        current["byte_count"] += int(item["bytes"])
    result = []
    for item in grouped.values():
        result.append(
            {
                "extension": item["extension"],
                "file_count": item["file_count"],
                "byte_count": item["byte_count"],
                "megabytes": _round_mb(item["byte_count"]),
            }
        )
    return sorted(result, key=lambda item: (-item["byte_count"], item["extension"]))[:limit]


def _select_hotspots(files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    hotspot_candidates = {
        "run.ps1",
        "scripts/operator.ps1",
        "scripts/runtime-flow-preset.ps1",
        "scripts/verify-repo.ps1",
        "packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py",
    }
    selected = [item for item in files if item["relative_path"] in hotspot_candidates]
    return [
        {
            "path": item["relative_path"],
            "bytes": item["bytes"],
            "megabytes": _round_mb(item["bytes"]),
            "line_count": item["line_count"],
            "area": item["area"],
        }
        for item in sorted(selected, key=lambda item: str(item["relative_path"]))
    ]


def _is_large_binary_evidence(item: dict[str, Any]) -> bool:
    if int(item["bytes"]) < LARGE_BINARY_THRESHOLD_BYTES:
        return False
    if item["extension"] in TEXT_EXTENSIONS:
        return False
    return str(item["area"]) in {"docs/change-evidence", "root"}


def _round_mb(size_bytes: int) -> float:
    return round(size_bytes / (1024 * 1024), 2)


if __name__ == "__main__":
    raise SystemExit(main())
