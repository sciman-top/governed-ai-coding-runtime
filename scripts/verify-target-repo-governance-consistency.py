from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG_PATH = ROOT / "docs" / "targets" / "target-repos-catalog.json"
DEFAULT_BASELINE_PATH = ROOT / "docs" / "targets" / "target-repo-governance-baseline.json"


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


def _validate_baseline(path: Path) -> tuple[str, dict[str, Any]]:
    baseline = _load_json(path)
    sync_revision = baseline.get("sync_revision")
    overrides = baseline.get("required_profile_overrides")
    if not isinstance(sync_revision, str) or not sync_revision.strip():
        raise ValueError("baseline.sync_revision must be a non-empty string")
    if not isinstance(overrides, dict) or not overrides:
        raise ValueError("baseline.required_profile_overrides must be a non-empty object")
    return sync_revision, overrides


def _load_targets(catalog_path: Path) -> dict[str, dict[str, Any]]:
    catalog = _load_json(catalog_path)
    targets = catalog.get("targets")
    if not isinstance(targets, dict) or not targets:
        raise ValueError("target catalog must define a non-empty targets object")
    validated: dict[str, dict[str, Any]] = {}
    for key, value in targets.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("target catalog key must be a non-empty string")
        if not isinstance(value, dict):
            raise ValueError(f"target '{key}' must be an object")
        attachment_root = value.get("attachment_root")
        if not isinstance(attachment_root, str) or not attachment_root.strip():
            raise ValueError(f"target '{key}' missing attachment_root")
        validated[key] = value
    return validated


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify governance feature consistency across all active target repos.")
    parser.add_argument("--catalog-path", default=str(DEFAULT_CATALOG_PATH))
    parser.add_argument("--baseline-path", default=str(DEFAULT_BASELINE_PATH))
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--code-root", default=None)
    parser.add_argument("--runtime-state-base", default=None)
    args = parser.parse_args()

    catalog_path = Path(args.catalog_path).resolve(strict=False)
    baseline_path = Path(args.baseline_path).resolve(strict=False)
    repo_root = Path(args.repo_root).resolve(strict=False)
    code_root = Path(args.code_root).resolve(strict=False) if args.code_root else repo_root.parent
    runtime_state_base = (
        Path(args.runtime_state_base).resolve(strict=False)
        if args.runtime_state_base
        else repo_root / ".runtime" / "attachments"
    )

    if not catalog_path.exists():
        raise SystemExit(f"catalog file not found: {catalog_path}")
    if not baseline_path.exists():
        raise SystemExit(f"baseline file not found: {baseline_path}")

    sync_revision, expected_overrides = _validate_baseline(baseline_path)
    targets = _load_targets(catalog_path)
    variables = {
        "repo_root": str(repo_root),
        "code_root": str(code_root),
        "runtime_state_base": str(runtime_state_base),
    }

    checked_targets: list[str] = []
    drift: list[dict[str, Any]] = []

    for target_name in sorted(targets.keys()):
        checked_targets.append(target_name)
        target = targets[target_name]
        attachment_root = Path(_expand_template(str(target["attachment_root"]), variables)).resolve(strict=False)
        profile_path = attachment_root / ".governed-ai" / "repo-profile.json"

        if not attachment_root.exists():
            drift.append(
                {
                    "target": target_name,
                    "reason": "target_repo_not_found",
                    "target_repo": str(attachment_root),
                    "profile_path": str(profile_path),
                }
            )
            continue

        if not profile_path.exists():
            drift.append(
                {
                    "target": target_name,
                    "reason": "repo_profile_not_found",
                    "target_repo": str(attachment_root),
                    "profile_path": str(profile_path),
                }
            )
            continue

        profile = _load_json(profile_path)
        mismatched_fields: list[str] = []
        for field_name, expected_value in expected_overrides.items():
            if profile.get(field_name) != expected_value:
                mismatched_fields.append(field_name)
        if mismatched_fields:
            drift.append(
                {
                    "target": target_name,
                    "reason": "governance_profile_drift",
                    "target_repo": str(attachment_root),
                    "profile_path": str(profile_path),
                    "mismatched_fields": mismatched_fields,
                }
            )

    status = "pass" if not drift else "fail"
    output = {
        "status": status,
        "catalog_path": str(catalog_path),
        "baseline_path": str(baseline_path),
        "sync_revision": sync_revision,
        "target_count": len(checked_targets),
        "checked_targets": checked_targets,
        "drift_count": len(drift),
        "drift": drift,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
