from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE_PATH = ROOT / "docs" / "targets" / "target-repo-governance-baseline.json"


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"json object required: {path}")
    return data


def _resolve_profile_path(target_repo: Path, profile_path_arg: str | None) -> Path:
    if profile_path_arg:
        return Path(profile_path_arg).resolve(strict=False)
    return target_repo / ".governed-ai" / "repo-profile.json"


def _normalize_baseline(path: Path) -> dict[str, Any]:
    baseline = _load_json(path)
    overrides = baseline.get("required_profile_overrides")
    if not isinstance(overrides, dict) or not overrides:
        raise ValueError("baseline.required_profile_overrides must be a non-empty object")
    sync_revision = baseline.get("sync_revision")
    if not isinstance(sync_revision, str) or not sync_revision.strip():
        raise ValueError("baseline.sync_revision must be a non-empty string")
    managed_files = baseline.get("required_managed_files", [])
    if not isinstance(managed_files, list):
        raise ValueError("baseline.required_managed_files must be a list when present")
    for index, item in enumerate(managed_files):
        if not isinstance(item, dict):
            raise ValueError(f"baseline.required_managed_files[{index}] must be an object")
        target_path = item.get("path")
        source_path = item.get("source")
        if not isinstance(target_path, str) or not target_path.strip():
            raise ValueError(f"baseline.required_managed_files[{index}].path must be a non-empty string")
        if not isinstance(source_path, str) or not source_path.strip():
            raise ValueError(f"baseline.required_managed_files[{index}].source must be a non-empty string")
    return baseline


def _apply_profile_overrides(
    profile: dict[str, Any],
    overrides: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    updated = dict(profile)
    changed_fields: list[str] = []
    for key, value in overrides.items():
        expected = copy.deepcopy(value)
        if updated.get(key) != expected:
            changed_fields.append(key)
        updated[key] = expected
    return updated, changed_fields


def _target_relative_path(target_repo: Path, raw_path: str) -> Path:
    relative = Path(raw_path)
    if relative.is_absolute():
        raise ValueError(f"managed file path must be repo-relative: {raw_path}")
    if any(part == ".." for part in relative.parts):
        raise ValueError(f"managed file path must not contain '..': {raw_path}")
    resolved = (target_repo / relative).resolve(strict=False)
    try:
        resolved.relative_to(target_repo.resolve(strict=False))
    except ValueError as exc:
        raise ValueError(f"managed file path escapes target repo: {raw_path}") from exc
    return resolved


def _source_path(baseline_path: Path, raw_path: str) -> Path:
    source = Path(raw_path)
    if not source.is_absolute():
        source = ROOT / source
    return source.resolve(strict=False)


def _sync_managed_files(
    *,
    target_repo: Path,
    baseline_path: Path,
    managed_files: list[dict[str, Any]],
    check_only: bool,
) -> list[dict[str, str]]:
    changed_files: list[dict[str, str]] = []
    for item in managed_files:
        target_path = _target_relative_path(target_repo, str(item["path"]))
        source_path = _source_path(baseline_path, str(item["source"]))
        if not source_path.exists():
            raise ValueError(f"managed file source not found: {source_path}")
        expected = source_path.read_text(encoding="utf-8")
        actual = target_path.read_text(encoding="utf-8") if target_path.exists() else None
        if actual == expected:
            continue
        changed_files.append(
            {
                "path": str(target_path.relative_to(target_repo)).replace("\\", "/"),
                "source": str(source_path),
                "reason": "missing" if actual is None else "content_drift",
            }
        )
        if not check_only:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(expected, encoding="utf-8")
    return changed_files


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply governance baseline overrides into a target repo profile.")
    parser.add_argument("--target-repo", required=True, help="Target repository root.")
    parser.add_argument(
        "--baseline-path",
        default=str(DEFAULT_BASELINE_PATH),
        help="Path to governance baseline json.",
    )
    parser.add_argument(
        "--profile-path",
        default=None,
        help="Explicit repo-profile path. Defaults to <target-repo>/.governed-ai/repo-profile.json",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Do not write files; return non-zero when drift is detected.",
    )
    args = parser.parse_args()

    target_repo = Path(args.target_repo).resolve(strict=False)
    baseline_path = Path(args.baseline_path).resolve(strict=False)
    profile_path = _resolve_profile_path(target_repo=target_repo, profile_path_arg=args.profile_path)

    if not baseline_path.exists():
        raise SystemExit(f"baseline file not found: {baseline_path}")
    if not target_repo.exists():
        raise SystemExit(f"target repo not found: {target_repo}")
    if not profile_path.exists():
        raise SystemExit(f"repo profile not found: {profile_path}")

    baseline = _normalize_baseline(baseline_path)
    profile = _load_json(profile_path)
    overrides = baseline["required_profile_overrides"]
    updated_profile, changed_fields = _apply_profile_overrides(profile=profile, overrides=overrides)
    changed_managed_files = _sync_managed_files(
        target_repo=target_repo,
        baseline_path=baseline_path,
        managed_files=baseline.get("required_managed_files", []),
        check_only=args.check_only,
    )

    status = "pass"
    if changed_fields or changed_managed_files:
        status = "drift" if args.check_only else "applied"

    if not args.check_only and changed_fields:
        profile_path.write_text(
            json.dumps(updated_profile, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    output = {
        "status": status,
        "target_repo": str(target_repo),
        "profile_path": str(profile_path),
        "baseline_path": str(baseline_path),
        "sync_revision": baseline["sync_revision"],
        "changed_fields": changed_fields,
        "changed_managed_files": changed_managed_files,
        "check_only": args.check_only,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))

    if args.check_only and (changed_fields or changed_managed_files):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
