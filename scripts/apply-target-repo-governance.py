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

    status = "pass"
    if changed_fields:
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
        "check_only": args.check_only,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))

    if args.check_only and changed_fields:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
