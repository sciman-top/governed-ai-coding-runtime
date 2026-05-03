from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG_PATH = ROOT / "docs" / "targets" / "target-repos-catalog.json"
DEFAULT_MANIFEST_PATH = ROOT / "rules" / "manifest.json"


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"json object required: {path}")
    return data


def _expand_template(value: str, variables: dict[str, str]) -> str:
    expanded = value
    for key, raw in variables.items():
        expanded = expanded.replace("${" + key + "}", raw)
    return expanded


def _repo_relative_path(raw_path: str) -> str:
    path = Path(raw_path)
    if path.is_absolute() or any(part == ".." for part in path.parts):
        raise ValueError(f"project target path must be repo-relative: {raw_path}")
    return path.as_posix()


def _catalog_targets(path: Path) -> dict[str, dict[str, Any]]:
    catalog = _load_json(path)
    targets = catalog.get("targets")
    if not isinstance(targets, dict) or not targets:
        raise ValueError("target catalog must define a non-empty targets object")
    return targets


def _target_roots(
    *,
    catalog_path: Path,
    repo_root: Path,
    code_root: Path,
    runtime_state_base: Path,
) -> dict[str, Path]:
    variables = {
        "repo_root": str(repo_root),
        "code_root": str(code_root),
        "runtime_state_base": str(runtime_state_base),
    }
    roots: dict[str, Path] = {}
    for target_id, target_config in _catalog_targets(catalog_path).items():
        attachment_root = target_config.get("attachment_root")
        if not isinstance(attachment_root, str) or not attachment_root.strip():
            raise ValueError(f"target '{target_id}' missing attachment_root")
        roots[target_id] = Path(_expand_template(attachment_root, variables)).resolve(strict=False)
    return roots


def _managed_rule_paths(manifest_path: Path) -> dict[str, set[str]]:
    manifest = _load_json(manifest_path)
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        raise ValueError("manifest.entries must be a list")

    result: dict[str, set[str]] = {}
    for index, raw in enumerate(entries):
        if not isinstance(raw, dict):
            raise ValueError(f"manifest.entries[{index}] must be an object")
        if raw.get("scope") != "project":
            continue
        target_id = raw.get("target_repo_id")
        target_path = raw.get("target_path")
        if not isinstance(target_id, str) or not target_id.strip():
            raise ValueError(f"manifest.entries[{index}].target_repo_id is required")
        if not isinstance(target_path, str) or not target_path.strip():
            raise ValueError(f"manifest.entries[{index}].target_path is required")
        result.setdefault(target_id, set()).add(_repo_relative_path(target_path))
    return result


def _git_status_entries(repo: Path) -> tuple[int, list[dict[str, str]], str]:
    completed = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain=v1", "--untracked-files=all"],
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        return completed.returncode, [], completed.stderr.strip() or completed.stdout.strip()

    entries: list[dict[str, str]] = []
    for raw_line in completed.stdout.splitlines():
        if not raw_line:
            continue
        status = raw_line[:2]
        raw_path = raw_line[3:] if len(raw_line) > 3 else ""
        path = raw_path.split(" -> ", 1)[-1].replace("\\", "/")
        entries.append({"status": status, "path": path})
    return 0, entries, ""


def _change_category(target_id: str, path: str, managed_rule_paths: set[str]) -> str:
    normalized = path.replace("\\", "/")
    if normalized in managed_rule_paths:
        return "managed_rule_file"
    if normalized == ".governed-ai/repo-profile.json":
        return "managed_repo_profile"
    if normalized.startswith(".governed-ai/managed-files/"):
        return "managed_file_provenance"
    if normalized.startswith(".governed-ai/"):
        return "governance_local_state"
    if target_id == "self-runtime":
        return "control_repo_current_change"
    return "target_local_unrelated"


def _summarize_target(target_id: str, repo: Path, managed_rules: set[str]) -> dict[str, Any]:
    git_exit_code, entries, error = _git_status_entries(repo)
    if git_exit_code != 0:
        return {
            "target": target_id,
            "repo": str(repo),
            "status": "git_status_failed",
            "git_exit_code": git_exit_code,
            "error": error,
            "change_count": 0,
            "managed_change_count": 0,
            "unrelated_change_count": 0,
            "changes": [],
        }

    changes: list[dict[str, str]] = []
    counts: dict[str, int] = {}
    for entry in entries:
        category = _change_category(target_id, entry["path"], managed_rules)
        counts[category] = counts.get(category, 0) + 1
        changes.append({**entry, "category": category})

    managed_categories = {
        "managed_rule_file",
        "managed_repo_profile",
        "managed_file_provenance",
        "governance_local_state",
        "control_repo_current_change",
    }
    managed_count = sum(1 for item in changes if item["category"] in managed_categories)
    unrelated_count = sum(1 for item in changes if item["category"] == "target_local_unrelated")
    target_status = "clean" if not changes else ("attention" if unrelated_count else "managed_only")
    return {
        "target": target_id,
        "repo": str(repo),
        "status": target_status,
        "change_count": len(changes),
        "managed_change_count": managed_count,
        "unrelated_change_count": unrelated_count,
        "category_counts": counts,
        "changes": changes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify target repo worktree changes into governed vs target-local buckets.")
    parser.add_argument("--catalog-path", default=str(DEFAULT_CATALOG_PATH))
    parser.add_argument("--manifest-path", default=str(DEFAULT_MANIFEST_PATH))
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--code-root", default=None)
    parser.add_argument("--runtime-state-base", default=None)
    parser.add_argument("--target", action="append", default=[], help="Limit to one or more target repo ids.")
    parser.add_argument("--fail-on-unrelated", action="store_true", help="Return non-zero if target-local unrelated changes exist.")
    parser.add_argument("--output-path", default=None, help="Optional path for writing the JSON report.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve(strict=False)
    catalog_path = Path(args.catalog_path).resolve(strict=False)
    manifest_path = Path(args.manifest_path).resolve(strict=False)
    code_root = Path(args.code_root).resolve(strict=False) if args.code_root else repo_root.parent
    runtime_state_base = (
        Path(args.runtime_state_base).resolve(strict=False)
        if args.runtime_state_base
        else repo_root / ".runtime" / "attachments"
    )

    roots = _target_roots(
        catalog_path=catalog_path,
        repo_root=repo_root,
        code_root=code_root,
        runtime_state_base=runtime_state_base,
    )
    managed_rules_by_target = _managed_rule_paths(manifest_path)
    selected_targets = set(args.target)

    results: list[dict[str, Any]] = []
    for target_id, repo in roots.items():
        if selected_targets and target_id not in selected_targets:
            continue
        results.append(_summarize_target(target_id, repo, managed_rules_by_target.get(target_id, set())))

    if selected_targets:
        missing_targets = sorted(selected_targets - set(roots))
        if missing_targets:
            raise SystemExit(f"target repo id not found in catalog: {', '.join(missing_targets)}")

    unrelated_count = sum(int(item.get("unrelated_change_count", 0)) for item in results)
    failed_count = sum(1 for item in results if item.get("status") == "git_status_failed")
    status = "fail" if failed_count else ("attention" if unrelated_count else "pass")
    output = {
        "status": status,
        "catalog_path": str(catalog_path),
        "manifest_path": str(manifest_path),
        "target_count": len(results),
        "failed_count": failed_count,
        "unrelated_change_count": unrelated_count,
        "results": results,
    }
    output_text = json.dumps(output, ensure_ascii=False, indent=2) + "\n"
    if args.output_path:
        output_path = Path(args.output_path)
        if not output_path.is_absolute():
            output_path = ROOT / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_text, encoding="utf-8")
    print(output_text, end="")
    if failed_count:
        return 2
    if args.fail_on_unrelated and unrelated_count:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
