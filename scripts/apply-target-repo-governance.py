from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

from lib.target_repo_speed_profile import (
    apply_speed_profile_policy,
    as_command_list,
    normalize_speed_profile_policy,
    normalize_target_test_slice,
)


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASELINE_PATH = ROOT / "docs" / "targets" / "target-repo-governance-baseline.json"
DEFAULT_QUICK_TEST_RECOMMENDATION_RELATIVE_PATH = ".governed-ai/quick-test-slice.recommendation.json"
DEFAULT_QUICK_TEST_PROMPT_RELATIVE_PATH = ".governed-ai/quick-test-slice.prompt.md"
OUTER_AI_QUICK_TEST_INSTRUCTION = (
    "Read the target repo .governed-ai/quick-test-slice.prompt.md, inspect the test structure, "
    "and write .governed-ai/quick-test-slice.recommendation.json with status=ready and a safe "
    "quick_test_command, or status=skip when no safe fast slice exists. Do not modify the full "
    "test command."
)


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
    speed_policy = baseline.get("target_repo_speed_profile_policy")
    if speed_policy is not None:
        normalize_speed_profile_policy(speed_policy)
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


def _load_outer_ai_test_slice_recommendation(
    *,
    target_repo: Path,
    recommendation_path_arg: str | None = None,
) -> tuple[dict[str, Any] | None, str, str | None]:
    recommendation_path = (
        Path(recommendation_path_arg).resolve(strict=False)
        if recommendation_path_arg
        else target_repo / DEFAULT_QUICK_TEST_RECOMMENDATION_RELATIVE_PATH
    )
    if not recommendation_path.exists():
        return None, "none", str(recommendation_path)

    raw = _load_json(recommendation_path)
    status = str(raw.get("status") or "").strip().lower()
    if status and status not in {"ready", "skip"}:
        raise ValueError("quick test slice recommendation status must be ready or skip")
    if status == "skip":
        return None, "recommendation_file_skip", str(recommendation_path)

    slice_config = normalize_target_test_slice(
        command=raw.get("quick_test_command"),
        reason=raw.get("quick_test_reason"),
        timeout_seconds=raw.get("quick_test_timeout_seconds"),
    )
    if slice_config is None:
        raise ValueError("quick test slice recommendation must define quick_test_command when status is ready")
    return slice_config, "recommendation_file", str(recommendation_path)


def _write_outer_ai_test_slice_prompt(
    *,
    target_repo: Path,
    profile: dict[str, Any],
    prompt_path_arg: str | None = None,
    check_only: bool,
) -> tuple[str, str | None]:
    prompt_path = (
        Path(prompt_path_arg).resolve(strict=False)
        if prompt_path_arg
        else target_repo / DEFAULT_QUICK_TEST_PROMPT_RELATIVE_PATH
    )
    test_commands = as_command_list(profile.get("test_commands"))
    contract_commands = as_command_list(profile.get("contract_commands"))
    invariant_commands = as_command_list(profile.get("invariant_commands"))
    full_test = test_commands[0]["command"] if test_commands else ""
    full_contract = contract_commands[0]["command"] if contract_commands else ""
    full_invariant = invariant_commands[0]["command"] if invariant_commands else ""
    prompt = f"""# Quick Test Slice Recommendation Prompt

You are reviewing a target repository for a safe daily fast-test slice.

Target repo: `{target_repo}`
Repo id: `{profile.get("repo_id", "")}`
Primary language: `{profile.get("primary_language", "")}`
Full test command: `{full_test}`
Full contract command: `{full_contract}`
Full invariant command: `{full_invariant}`

Task:
1. Inspect the target repo test structure, markers/categories, and existing fast/smoke scripts.
2. Recommend a `quick_test_command` only if it is deterministic, materially faster than the full test command, and representative of daily coding risk.
3. Do not weaken full/release gates. The full test command must remain unchanged.
4. If no safe slice exists, emit `status=skip`.

Write this JSON to `.governed-ai/quick-test-slice.recommendation.json`:

```json
{{
  "schema_version": "1.0",
  "status": "ready",
  "quick_test_command": "<command>",
  "quick_test_reason": "<short reason>",
  "quick_test_timeout_seconds": 180
}}
```

Use this skip form when no safe slice is justified:

```json
{{
  "schema_version": "1.0",
  "status": "skip",
  "quick_test_reason": "No safe target-specific quick test slice found."
}}
```
"""
    if check_only:
        return "prompt_available", str(prompt_path)
    prompt_path.parent.mkdir(parents=True, exist_ok=True)
    existing = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else None
    if existing != prompt:
        prompt_path.write_text(prompt, encoding="utf-8")
    return "prompt_written", str(prompt_path)


def _catalog_gate_entry(gate_id: str, command: str) -> dict[str, Any] | None:
    normalized = " ".join(str(command or "").strip().split())
    if not normalized:
        return None
    return {"id": gate_id, "command": normalized, "required": True}


def _apply_catalog_profile_facts(
    profile: dict[str, Any],
    *,
    repo_id: str | None = None,
    display_name: str | None = None,
    primary_language: str | None = None,
    build_command: str | None = None,
    test_command: str | None = None,
    contract_command: str | None = None,
) -> tuple[dict[str, Any], list[str]]:
    updated = copy.deepcopy(profile)
    changed_fields: list[str] = []
    for field_name, value in (
        ("repo_id", repo_id),
        ("display_name", display_name),
        ("primary_language", primary_language),
    ):
        normalized = str(value or "").strip()
        if normalized and updated.get(field_name) != normalized:
            updated[field_name] = normalized
            changed_fields.append(field_name)

    for group_name, gate_id, command in (
        ("build_commands", "build", build_command),
        ("test_commands", "test", test_command),
        ("contract_commands", "contract", contract_command),
    ):
        entry = _catalog_gate_entry(gate_id, command or "")
        if entry is None:
            continue
        expected_group = [entry]
        if updated.get(group_name) != expected_group:
            updated[group_name] = expected_group
            changed_fields.append(group_name)

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
    parser.add_argument("--repo-id", help="Catalog repo id to sync into the target repo profile.")
    parser.add_argument("--display-name", help="Catalog display name to sync into the target repo profile.")
    parser.add_argument("--primary-language", help="Catalog primary language to sync into the target repo profile.")
    parser.add_argument("--build-command", help="Catalog build gate command to sync into build_commands.")
    parser.add_argument("--test-command", help="Catalog test gate command to sync into test_commands.")
    parser.add_argument("--contract-command", help="Catalog contract gate command to sync into contract_commands.")
    parser.add_argument("--quick-test-command", help="Target-specific quick test slice command for fast gates.")
    parser.add_argument("--quick-test-reason", help="Short reason for the quick test slice command.")
    parser.add_argument("--quick-test-timeout-seconds", type=int, help="Timeout override for the quick test slice command.")
    parser.add_argument(
        "--quick-test-skip-reason",
        help="Catalog-level reason that no target-specific quick test slice should be generated.",
    )
    parser.add_argument(
        "--quick-test-recommendation-path",
        help=(
            "Optional outer-AI recommendation JSON. Defaults to "
            f"{DEFAULT_QUICK_TEST_RECOMMENDATION_RELATIVE_PATH} when present."
        ),
    )
    parser.add_argument(
        "--quick-test-prompt-path",
        help=(
            "Optional output path for the outer-AI quick-test recommendation prompt. Defaults to "
            f"{DEFAULT_QUICK_TEST_PROMPT_RELATIVE_PATH}."
        ),
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
    target_test_slice = normalize_target_test_slice(
        command=args.quick_test_command,
        reason=args.quick_test_reason,
        timeout_seconds=args.quick_test_timeout_seconds,
    )
    quick_test_skip_reason = str(args.quick_test_skip_reason or "").strip()
    if target_test_slice is not None and quick_test_skip_reason:
        parser.error("--quick-test-command and --quick-test-skip-reason are mutually exclusive")

    quick_test_slice_source = "argument" if target_test_slice is not None else "none"
    if target_test_slice is None and quick_test_skip_reason:
        quick_test_slice_source = "argument_skip"
    recommendation_path = None
    if quick_test_slice_source == "none":
        target_test_slice, quick_test_slice_source, recommendation_path = _load_outer_ai_test_slice_recommendation(
            target_repo=target_repo,
            recommendation_path_arg=args.quick_test_recommendation_path,
        )
    outer_ai_action = "none"
    quick_test_prompt_path = None
    overrides = baseline["required_profile_overrides"]
    updated_profile, changed_catalog_fields = _apply_catalog_profile_facts(
        profile,
        repo_id=args.repo_id,
        display_name=args.display_name,
        primary_language=args.primary_language,
        build_command=args.build_command,
        test_command=args.test_command,
        contract_command=args.contract_command,
    )
    updated_profile, changed_fields = _apply_profile_overrides(profile=updated_profile, overrides=overrides)
    if quick_test_slice_source == "none":
        outer_ai_action, quick_test_prompt_path = _write_outer_ai_test_slice_prompt(
            target_repo=target_repo,
            profile=updated_profile,
            prompt_path_arg=args.quick_test_prompt_path,
            check_only=args.check_only,
        )
    if {"build_commands", "test_commands", "contract_commands"}.intersection(changed_catalog_fields):
        updated_profile.pop("quick_gate_commands", None)
        updated_profile.pop("full_gate_commands", None)
    updated_profile, changed_speed_profile_fields = apply_speed_profile_policy(
        profile=updated_profile,
        policy=baseline.get("target_repo_speed_profile_policy"),
        target_test_slice=target_test_slice,
    )
    changed_managed_files = _sync_managed_files(
        target_repo=target_repo,
        baseline_path=baseline_path,
        managed_files=baseline.get("required_managed_files", []),
        check_only=args.check_only,
    )

    status = "pass"
    if changed_catalog_fields or changed_fields or changed_speed_profile_fields or changed_managed_files:
        status = "drift" if args.check_only else "applied"

    if not args.check_only and (changed_catalog_fields or changed_fields or changed_speed_profile_fields):
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
        "changed_catalog_fields": changed_catalog_fields,
        "changed_fields": changed_fields,
        "changed_speed_profile_fields": changed_speed_profile_fields,
        "changed_managed_files": changed_managed_files,
        "quick_test_slice_source": quick_test_slice_source,
        "quick_test_skip_reason": quick_test_skip_reason if quick_test_slice_source.endswith("_skip") else "",
        "quick_test_recommendation_path": recommendation_path,
        "outer_ai_action": outer_ai_action,
        "quick_test_prompt_path": quick_test_prompt_path,
        "outer_ai_instruction": OUTER_AI_QUICK_TEST_INSTRUCTION if outer_ai_action in {"prompt_written", "prompt_available"} else "",
        "check_only": args.check_only,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))

    if args.check_only and (changed_catalog_fields or changed_fields or changed_speed_profile_fields or changed_managed_files):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
