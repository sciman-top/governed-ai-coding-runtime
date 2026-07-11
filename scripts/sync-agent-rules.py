from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST_PATH = ROOT / "rules" / "manifest.json"


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"json object required: {path}")
    return data


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _expand_template(value: str, variables: dict[str, str]) -> str:
    expanded = value
    for key, raw in variables.items():
        expanded = expanded.replace("${" + key + "}", raw)
    return expanded


def _validate_manifest(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        raise ValueError("manifest.entries must be a non-empty list")

    seen: set[str] = set()
    validated: list[dict[str, Any]] = []
    for index, raw in enumerate(entries):
        if not isinstance(raw, dict):
            raise ValueError(f"manifest.entries[{index}] must be an object")
        entry = dict(raw)
        entry_id = entry.get("id")
        scope = entry.get("scope")
        tool = entry.get("tool")
        source = entry.get("source")
        target_path = entry.get("target_path")
        version = entry.get("version") or manifest.get("default_version")

        if not isinstance(entry_id, str) or not entry_id.strip():
            raise ValueError(f"manifest.entries[{index}].id must be a non-empty string")
        if entry_id in seen:
            raise ValueError(f"duplicate manifest entry id: {entry_id}")
        seen.add(entry_id)
        if scope != "global":
            raise ValueError(
                "target-repo/project rule distribution was retired; manifest entries must all use scope=global"
            )
        if tool not in {"codex", "claude"}:
            raise ValueError(f"manifest.entries[{index}].tool must be codex or claude")
        if not isinstance(version, str) or not version.strip():
            raise ValueError(f"manifest.entries[{index}].version must be a non-empty string")
        if not isinstance(source, str) or not source.strip():
            raise ValueError(f"manifest.entries[{index}].source must be a non-empty string")
        if not isinstance(target_path, str) or not target_path.strip():
            raise ValueError(f"manifest.entries[{index}].target_path must be a non-empty string")
        if "target_repo_id" in entry:
            raise ValueError(
                "target-repo/project rule distribution was retired; target_repo_id is no longer supported"
            )
        entry["version"] = version
        validated.append(entry)
    return validated


def _resolve_source_path(raw_path: str) -> Path:
    source = Path(raw_path)
    if not source.is_absolute():
        source = ROOT / source
    resolved = source.resolve(strict=False)
    try:
        resolved.relative_to(ROOT.resolve(strict=False))
    except ValueError as exc:
        raise ValueError(f"source path must stay inside this repo: {raw_path}") from exc
    return resolved


def _extract_rule_version(text: str) -> str | None:
    patterns = (
        r"GlobalUser/(?:AGENTS|CLAUDE)\.md v([0-9][0-9A-Za-z_.-]*)",
        r"\*\*版本\*\*:\s*([0-9][0-9A-Za-z_.-]*)",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def _version_tuple(value: str | None) -> tuple[int, ...] | None:
    if not value:
        return None
    parts = re.findall(r"\d+", value)
    if not parts:
        return None
    return tuple(int(part) for part in parts)


def _compare_versions(left: str | None, right: str | None) -> int | None:
    left_tuple = _version_tuple(left)
    right_tuple = _version_tuple(right)
    if left_tuple is None or right_tuple is None:
        return None
    width = max(len(left_tuple), len(right_tuple))
    left_tuple = left_tuple + (0,) * (width - len(left_tuple))
    right_tuple = right_tuple + (0,) * (width - len(right_tuple))
    return (left_tuple > right_tuple) - (left_tuple < right_tuple)


def _backup_existing(target_path: Path, backup_root: Path, target_text: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    anchor = target_path.anchor
    drive = target_path.drive.replace(":", "") if target_path.drive else "relative"
    safe_parts = [drive]
    for part in target_path.parts:
        if part in {target_path.drive, target_path.root, anchor, "\\", "/"}:
            continue
        safe_parts.append(part.replace(":", "_"))
    backup_path = backup_root / timestamp / Path(*safe_parts)
    if backup_path.resolve(strict=False) == target_path.resolve(strict=False):
        raise ValueError(f"backup path resolves to target path: {target_path}")
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    backup_path.write_text(target_text, encoding="utf-8")
    return backup_path


def _plan_entry(
    *,
    entry: dict[str, Any],
    target_path: Path,
    source_path: Path,
    source_text: str,
    apply: bool,
    force: bool,
    backup_root: Path,
) -> dict[str, Any]:
    source_hash = _sha256_text(source_text)
    source_version = _extract_rule_version(source_text) or entry["version"]
    result: dict[str, Any] = {
        "id": entry["id"],
        "scope": entry["scope"],
        "tool": entry["tool"],
        "version": entry["version"],
        "source": str(source_path),
        "target_path": str(target_path),
        "source_sha256": source_hash,
        "source_version": source_version,
    }

    if not target_path.exists():
        result["status"] = "created" if apply else "would_create"
        if apply:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(source_text, encoding="utf-8")
        return result

    target_text = target_path.read_text(encoding="utf-8")
    target_hash = _sha256_text(target_text)
    target_version = _extract_rule_version(target_text)
    result["target_sha256"] = target_hash
    result["target_version"] = target_version

    if target_hash == source_hash:
        result["status"] = "skipped_same_hash"
        return result

    comparison = _compare_versions(target_version, source_version)
    if not force and target_version == source_version:
        result["status"] = "blocked_same_version_drift"
        result["reason"] = "target has the same rule version but different content"
        return result
    if not force and comparison is not None and comparison > 0:
        result["status"] = "blocked_target_newer"
        result["reason"] = "target rule version is newer than the manifest source"
        return result
    if not force and target_version is None:
        result["status"] = "blocked_missing_target_version"
        result["reason"] = "target has no detectable rule version; use --force after review"
        return result

    result["status"] = "updated" if apply else "would_update"
    if apply:
        backup_path = _backup_existing(target_path, backup_root, target_text)
        result["backup_path"] = str(backup_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(source_text, encoding="utf-8")
    return result


def _scope_matches(selected_scope: str) -> bool:
    if selected_scope not in {"all", "global"}:
        raise ValueError(f"unknown scope: {selected_scope}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run or apply managed global agent rule files.")
    parser.add_argument("--scope", choices=("All", "Global", "all", "global"), default="All")
    parser.add_argument("--apply", action="store_true", help="Write global target files. Default is dry-run.")
    parser.add_argument("--force", action="store_true", help="Allow overwriting same-version drift or unknown-version targets.")
    parser.add_argument("--fail-on-change", action="store_true", help="Return non-zero when dry-run detects create/update drift.")
    parser.add_argument("--manifest-path", default=str(DEFAULT_MANIFEST_PATH))
    parser.add_argument("--user-profile", default=os.environ.get("USERPROFILE") or str(Path.home()))
    args = parser.parse_args()

    manifest_path = Path(args.manifest_path).resolve(strict=False)
    user_profile = Path(args.user_profile).resolve(strict=False)

    if not manifest_path.exists():
        raise SystemExit(f"manifest file not found: {manifest_path}")

    manifest = _load_json(manifest_path)
    entries = _validate_manifest(manifest)

    backup_root_raw = manifest.get("backup_policy", {}).get("root", "docs/change-evidence/rule-sync-backups")
    backup_root = Path(str(backup_root_raw))
    if not backup_root.is_absolute():
        backup_root = ROOT / backup_root
    variables = {
        "user_profile": str(user_profile),
    }

    selected_scope = args.scope.lower()
    _scope_matches(selected_scope)
    results: list[dict[str, Any]] = []
    for entry in entries:
        source_path = _resolve_source_path(str(entry["source"]))
        if not source_path.exists():
            raise SystemExit(f"source rule file not found: {source_path}")
        source_text = source_path.read_text(encoding="utf-8")
        target_path = Path(_expand_template(str(entry["target_path"]), variables)).resolve(strict=False)
        results.append(
            _plan_entry(
                entry=entry,
                target_path=target_path,
                source_path=source_path,
                source_text=source_text,
                apply=args.apply,
                force=args.force,
                backup_root=backup_root,
            )
        )

    blocked = [item for item in results if str(item["status"]).startswith("blocked_")]
    changed = [
        item
        for item in results
        if item["status"] in {"would_create", "would_update", "created", "updated"}
    ]
    status = "blocked" if blocked else ("applied" if args.apply and changed else ("dry_run_changes" if changed else "pass"))
    output = {
        "status": status,
        "mode": "apply" if args.apply else "dry-run",
        "force": args.force,
        "manifest_path": str(manifest_path),
        "scope": selected_scope,
        "entry_count": len(results),
        "changed_count": len(changed),
        "blocked_count": len(blocked),
        "results": results,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    if blocked:
        return 2
    if args.fail_on_change and changed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
