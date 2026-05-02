from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


TEXT_SUFFIXES = {
    ".bat",
    ".cmd",
    ".json",
    ".md",
    ".ps1",
    ".psm1",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
SKIP_PARTS = {".git", ".runtime", ".worktrees", "bin", "node_modules", "obj", "packages"}


def load_json_object(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"json object required: {path}")
    return data


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_sha256(value: Any) -> str:
    text = str(value or "").strip()
    if text.lower().startswith("sha256:"):
        text = text.split(":", 1)[1].strip()
    return text.lower()


def repo_relative_path(repo_root: Path, raw_path: str) -> Path:
    raw = Path(raw_path)
    if raw.is_absolute():
        raise ValueError(f"target path must be repo-relative: {raw_path}")
    if any(part == ".." for part in raw.parts):
        raise ValueError(f"target path must not contain '..': {raw_path}")
    root = repo_root.resolve(strict=False)
    candidate = (root / raw).resolve(strict=False)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"target path escapes target repo: {raw_path}") from exc
    return candidate


def normalize_relative_text(path: str | Path) -> str:
    text = Path(path).as_posix()
    while text.startswith("./"):
        text = text[2:]
    return text


def source_path(raw_path: str, *, repo_root: Path) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path.resolve(strict=False)
    return (repo_root / path).resolve(strict=False)


def read_text_if_exists(path: Path) -> str | None:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def deep_merge_json(base: Any, overlay: Any) -> Any:
    if isinstance(base, dict) and isinstance(overlay, dict):
        merged = dict(base)
        for key, value in overlay.items():
            merged[key] = deep_merge_json(merged.get(key), value)
        return merged
    return overlay


def expected_managed_text(*, source_text: str, actual_text: str | None, management_mode: str) -> str:
    if management_mode in {"replace", "block_on_drift"} or actual_text is None:
        return source_text
    if management_mode != "json_merge":
        return source_text
    source_json = json.loads(source_text)
    actual_json = json.loads(actual_text)
    merged = deep_merge_json(actual_json, source_json)
    return json.dumps(merged, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def collect_candidate_paths(target_repo: Path, explicit_paths: list[str], baseline: dict[str, Any]) -> list[str]:
    paths: set[str] = {normalize_relative_text(path) for path in explicit_paths if str(path).strip()}
    if explicit_paths:
        return sorted(paths)
    for item in baseline.get("required_managed_files", []):
        if isinstance(item, dict) and isinstance(item.get("path"), str):
            paths.add(normalize_relative_text(item["path"]))
    for item in baseline.get("generated_managed_files", []):
        if isinstance(item, dict) and isinstance(item.get("path"), str):
            paths.add(normalize_relative_text(item["path"]))
    for item in baseline.get("retired_managed_files", []):
        if isinstance(item, dict) and isinstance(item.get("path"), str):
            paths.add(normalize_relative_text(item["path"]))
    for folder in (".governed-ai", ".claude"):
        root = target_repo / folder
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file():
                paths.add(path.relative_to(target_repo).as_posix())
    return sorted(paths)


def inspect_managed_assets(
    *,
    target_repo: Path,
    baseline: dict[str, Any],
    repo_root: Path,
    candidate_paths: list[str] | None = None,
) -> dict[str, Any]:
    root = target_repo.resolve(strict=False)
    explicit = candidate_paths or []
    candidates = collect_candidate_paths(root, explicit, baseline)
    active_entries = {
        normalize_relative_text(str(item["path"])): item
        for item in baseline.get("required_managed_files", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    generated_entries = {
        normalize_relative_text(str(item["path"])): item
        for item in baseline.get("generated_managed_files", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }
    retired_entries = {
        normalize_relative_text(str(item["path"])): item
        for item in baseline.get("retired_managed_files", [])
        if isinstance(item, dict) and isinstance(item.get("path"), str)
    }

    assets = []
    counts: dict[str, int] = {}
    for relative in candidates:
        asset = classify_asset(
            target_repo=root,
            repo_root=repo_root,
            relative_path=relative,
            active_entry=active_entries.get(relative),
            generated_entry=generated_entries.get(relative),
            retired_entry=retired_entries.get(relative),
        )
        counts[asset["classification"]] = counts.get(asset["classification"], 0) + 1
        assets.append(asset)

    return {
        "target_repo": str(root),
        "status": "pass",
        "modified": False,
        "summary": counts,
        "assets": assets,
    }


def classify_asset(
    *,
    target_repo: Path,
    repo_root: Path,
    relative_path: str,
    active_entry: dict[str, Any] | None,
    generated_entry: dict[str, Any] | None,
    retired_entry: dict[str, Any] | None,
) -> dict[str, Any]:
    target_path = repo_relative_path(target_repo, relative_path)
    actual_text = read_text_if_exists(target_path)
    target_sha = sha256_text(actual_text) if actual_text is not None else ""
    base: dict[str, Any] = {
        "path": normalize_relative_text(relative_path),
        "exists": actual_text is not None,
        "target_sha256": f"sha256:{target_sha}" if target_sha else "",
        "classification": "target_owned",
        "reason": "no_runtime_managed_evidence",
        "evidence_refs": [],
        "referenced_by": find_references(target_repo=target_repo, relative_path=relative_path),
    }
    if active_entry is not None:
        source = active_entry.get("source")
        if not isinstance(source, str) or not source.strip():
            return base | {"classification": "unknown", "reason": "active_managed_source_missing"}
        source_file = source_path(source, repo_root=repo_root)
        if not source_file.exists():
            return base | {"classification": "unknown", "reason": "active_managed_source_not_found", "source": str(source_file)}
        source_text = source_file.read_text(encoding="utf-8")
        management_mode = str(active_entry.get("management_mode", "block_on_drift"))
        expected = expected_managed_text(source_text=source_text, actual_text=actual_text, management_mode=management_mode)
        expected_sha = sha256_text(expected)
        classification = "active_managed" if actual_text is not None and sha256_text(actual_text) == expected_sha else "managed_drifted"
        reason = "expected_content_matches" if classification == "active_managed" else "expected_content_differs"
        return base | {
            "classification": classification,
            "reason": reason,
            "management_mode": management_mode,
            "source": str(source_file),
            "source_sha256": f"sha256:{sha256_text(source_text)}",
            "expected_sha256": f"sha256:{expected_sha}",
            "evidence_refs": ["current_baseline.required_managed_files"],
        }
    if generated_entry is not None:
        expected_hash = normalize_sha256(generated_entry.get("expected_sha256") or generated_entry.get("source_sha256"))
        if not expected_hash:
            return base | {
                "classification": "managed_unverified",
                "reason": "generated_managed_hash_missing",
                "generator": str(generated_entry.get("generator", "")),
                "management_mode": str(generated_entry.get("management_mode", "block_on_drift")),
                "evidence_refs": ["current_baseline.generated_managed_files"],
            }
        if actual_text is None:
            return base | {
                "classification": "managed_drifted",
                "reason": "generated_managed_file_missing",
                "generator": str(generated_entry.get("generator", "")),
                "management_mode": str(generated_entry.get("management_mode", "block_on_drift")),
                "expected_sha256": f"sha256:{expected_hash}",
                "evidence_refs": ["current_baseline.generated_managed_files"],
            }
        matches = target_sha == expected_hash
        return base | {
            "classification": "active_managed" if matches else "managed_drifted",
            "reason": "generated_hash_matches" if matches else "generated_hash_differs",
            "generator": str(generated_entry.get("generator", "")),
            "management_mode": str(generated_entry.get("management_mode", "block_on_drift")),
            "expected_sha256": f"sha256:{expected_hash}",
            "evidence_refs": ["current_baseline.generated_managed_files"],
        }
    if retired_entry is not None:
        expected_hash = retired_expected_hash(retired_entry, repo_root=repo_root)
        if not expected_hash:
            return base | {"classification": "unknown", "reason": "retired_managed_hash_missing"}
        if actual_text is None:
            return base | {
                "classification": "retired_managed_candidate",
                "reason": "retired_file_missing",
                "expected_sha256": f"sha256:{expected_hash}",
                "evidence_refs": ["current_baseline.retired_managed_files"],
            }
        matches = target_sha == expected_hash
        return base | {
            "classification": "retired_managed_candidate" if matches else "managed_drifted",
            "reason": "previous_hash_matches" if matches else "target_content_differs_from_retired_hash",
            "expected_sha256": f"sha256:{expected_hash}",
            "retire_reason": str(retired_entry.get("retire_reason", "")),
            "replacement": str(retired_entry.get("replacement", "")),
            "safe_delete_when": retired_entry.get("safe_delete_when", []),
            "backup_required": bool(retired_entry.get("backup_required")),
            "evidence_refs": ["current_baseline.retired_managed_files"],
        }
    return base


def retired_expected_hash(entry: dict[str, Any], *, repo_root: Path) -> str:
    raw_hash = normalize_sha256(entry.get("previous_sha256"))
    if raw_hash:
        return raw_hash
    previous_source = entry.get("previous_source")
    if isinstance(previous_source, str) and previous_source.strip():
        path = source_path(previous_source, repo_root=repo_root)
        if path.exists():
            return sha256_text(path.read_text(encoding="utf-8"))
    return ""


def find_references(*, target_repo: Path, relative_path: str) -> list[str]:
    needle = normalize_relative_text(relative_path)
    refs: list[str] = []
    for path in target_repo.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(target_repo)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        rel_text = rel.as_posix()
        if rel_text == needle:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if needle in text or needle.replace("/", "\\") in text:
            refs.append(rel_text)
    return sorted(refs)
