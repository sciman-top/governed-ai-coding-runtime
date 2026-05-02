from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _expand_path(value: str, *, repo_root: Path) -> Path:
    code_root = repo_root.parent
    runtime_state_base = repo_root / ".runtime" / "attachments"
    expanded = (
        value.replace("${repo_root}", str(repo_root))
        .replace("${code_root}", str(code_root))
        .replace("${runtime_state_base}", str(runtime_state_base))
    )
    return Path(expanded).resolve(strict=False)


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _command_text(entry: Any) -> str:
    if isinstance(entry, dict):
        return str(entry.get("command") or "").strip()
    return str(entry or "").strip()


def _gate_ids(entry: Any, fallback: str) -> set[str]:
    if isinstance(entry, dict):
        aliases = entry.get("satisfies_gate_ids")
        if aliases:
            return {str(item).strip() for item in _as_list(aliases) if str(item).strip()}
        gate_id = str(entry.get("id") or fallback).strip()
        return {gate_id} if gate_id else {fallback}
    return {fallback}


def _timeout(entry: Any, profile_default: int) -> int:
    if isinstance(entry, dict) and entry.get("timeout_seconds") is not None:
        try:
            return int(entry["timeout_seconds"])
        except (TypeError, ValueError):
            return 0
    return profile_default


def _audit_group(
    *,
    target: str,
    profile: dict[str, Any],
    group_name: str,
    required_gate_ids: set[str],
    max_timeout_seconds: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    commands = _as_list(profile.get(group_name))
    default_timeout = int(profile.get("gate_timeout_seconds") or 0)
    covered_gate_ids: set[str] = set()
    command_counts: dict[str, int] = {}
    command_summaries: list[dict[str, Any]] = []
    findings: list[dict[str, Any]] = []

    for index, entry in enumerate(commands, start=1):
        command = _command_text(entry)
        gate_ids = _gate_ids(entry, f"{group_name}:{index}")
        timeout_seconds = _timeout(entry, default_timeout)
        if command:
            command_counts[command] = command_counts.get(command, 0) + 1
        covered_gate_ids.update(gate_ids)
        command_summaries.append(
            {
                "index": index,
                "command": command,
                "satisfies_gate_ids": sorted(gate_ids),
                "timeout_seconds": timeout_seconds,
            }
        )
        if not command:
            findings.append(
                {
                    "severity": "error",
                    "target": target,
                    "group": group_name,
                    "code": "empty_command",
                    "message": f"{group_name}[{index}] has no command text.",
                }
            )
        if timeout_seconds <= 0:
            findings.append(
                {
                    "severity": "error",
                    "target": target,
                    "group": group_name,
                    "code": "missing_timeout",
                    "message": f"{group_name}[{index}] has no finite timeout.",
                }
            )
        elif timeout_seconds > max_timeout_seconds:
            findings.append(
                {
                    "severity": "warn",
                    "target": target,
                    "group": group_name,
                    "code": "timeout_budget_high",
                    "message": f"{group_name}[{index}] timeout {timeout_seconds}s exceeds budget {max_timeout_seconds}s.",
                }
            )

    missing = sorted(required_gate_ids - covered_gate_ids)
    if missing:
        findings.append(
            {
                "severity": "error",
                "target": target,
                "group": group_name,
                "code": "missing_required_gate_ids",
                "message": f"{group_name} does not cover required gate ids: {', '.join(missing)}.",
                "missing_gate_ids": missing,
            }
        )

    duplicate_commands = sorted(command for command, count in command_counts.items() if count > 1)
    if duplicate_commands:
        findings.append(
            {
                "severity": "warn",
                "target": target,
                "group": group_name,
                "code": "duplicate_command_entries",
                "message": f"{group_name} has duplicate commands that should be merged with satisfies_gate_ids.",
                "duplicate_commands": duplicate_commands,
            }
        )

    summary = {
        "group": group_name,
        "command_count": len(commands),
        "covered_gate_ids": sorted(covered_gate_ids),
        "required_gate_ids": sorted(required_gate_ids),
        "missing_gate_ids": missing,
        "duplicate_command_count": len(duplicate_commands),
        "commands": command_summaries,
    }
    return summary, findings


def _result_by_target(batch_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(item.get("target")): item
        for item in batch_payload.get("results", [])
        if isinstance(item, dict) and item.get("target")
    }


def _effect_summary(serial_path: Path | None, parallel_path: Path | None) -> dict[str, Any] | None:
    if serial_path is None or parallel_path is None:
        return None
    serial = _load_json(serial_path)
    parallel = _load_json(parallel_path)
    serial_elapsed = float(serial.get("batch_elapsed_seconds") or 0)
    parallel_elapsed = float(parallel.get("batch_elapsed_seconds") or 0)
    speedup = round(serial_elapsed / parallel_elapsed, 4) if parallel_elapsed > 0 else None
    reduction = round((serial_elapsed - parallel_elapsed) / serial_elapsed, 4) if serial_elapsed > 0 else None
    serial_targets = _result_by_target(serial)
    parallel_targets = _result_by_target(parallel)
    per_target = []
    for target in sorted(set(serial_targets) | set(parallel_targets)):
        serial_result = serial_targets.get(target, {})
        parallel_result = parallel_targets.get(target, {})
        per_target.append(
            {
                "target": target,
                "serial_target_duration_ms": int(serial_result.get("target_duration_ms") or 0),
                "parallel_target_duration_ms": int(parallel_result.get("target_duration_ms") or 0),
                "serial_exit_code": serial_result.get("exit_code"),
                "parallel_exit_code": parallel_result.get("exit_code"),
            }
        )
    return {
        "serial_path": str(serial_path),
        "parallel_path": str(parallel_path),
        "serial_batch_elapsed_seconds": serial_elapsed,
        "parallel_batch_elapsed_seconds": parallel_elapsed,
        "speedup_ratio": speedup,
        "wall_time_reduction_ratio": reduction,
        "serial_failure_count": int(serial.get("failure_count") or 0),
        "parallel_failure_count": int(parallel.get("failure_count") or 0),
        "serial_batch_timed_out": bool(serial.get("batch_timed_out")),
        "parallel_batch_timed_out": bool(parallel.get("batch_timed_out")),
        "per_target": per_target,
    }


def audit(
    *,
    repo_root: Path,
    catalog_path: Path,
    quick_timeout_budget_seconds: int,
    full_timeout_budget_seconds: int,
    serial_result_path: Path | None,
    parallel_result_path: Path | None,
) -> dict[str, Any]:
    catalog = _load_json(catalog_path)
    targets = catalog.get("targets") or {}
    findings: list[dict[str, Any]] = []
    target_reports: list[dict[str, Any]] = []

    for target_name, target_config in sorted(targets.items()):
        attachment_root = _expand_path(str(target_config.get("attachment_root") or ""), repo_root=repo_root)
        profile_path = attachment_root / ".governed-ai" / "repo-profile.json"
        target_findings: list[dict[str, Any]] = []
        report: dict[str, Any] = {
            "target": target_name,
            "attachment_root": str(attachment_root),
            "profile_path": str(profile_path),
            "profile_exists": profile_path.exists(),
            "primary_language": target_config.get("primary_language"),
            "quick_slice_source": "catalog_command"
            if target_config.get("quick_test_command")
            else ("catalog_skip" if target_config.get("quick_test_skip_reason") else "missing_decision"),
        }
        if not profile_path.exists():
            target_findings.append(
                {
                    "severity": "error",
                    "target": target_name,
                    "code": "profile_missing",
                    "message": f"Target repo profile is missing: {profile_path}",
                }
            )
            report["findings"] = target_findings
            findings.extend(target_findings)
            target_reports.append(report)
            continue

        profile = _load_json(profile_path)
        quick_summary, quick_findings = _audit_group(
            target=target_name,
            profile=profile,
            group_name="quick_gate_commands",
            required_gate_ids={"test", "contract"},
            max_timeout_seconds=quick_timeout_budget_seconds,
        )
        full_summary, full_findings = _audit_group(
            target=target_name,
            profile=profile,
            group_name="full_gate_commands",
            required_gate_ids={"build", "test", "contract"},
            max_timeout_seconds=full_timeout_budget_seconds,
        )
        target_findings.extend(quick_findings)
        target_findings.extend(full_findings)

        if report["quick_slice_source"] == "missing_decision":
            target_findings.append(
                {
                    "severity": "warn",
                    "target": target_name,
                    "code": "quick_slice_decision_missing",
                    "message": "Target catalog has neither quick_test_command nor quick_test_skip_reason.",
                }
            )

        report.update(
            {
                "gate_timeout_seconds": profile.get("gate_timeout_seconds"),
                "quick_gate_summary": quick_summary,
                "full_gate_summary": full_summary,
                "findings": target_findings,
            }
        )
        findings.extend(target_findings)
        target_reports.append(report)

    effect = _effect_summary(serial_result_path, parallel_result_path)
    if effect is not None:
        if effect["serial_failure_count"] or effect["parallel_failure_count"]:
            findings.append(
                {
                    "severity": "error",
                    "code": "effect_comparison_has_failures",
                    "message": "Serial/parallel effect comparison includes failed target runs.",
                }
            )
        if effect["speedup_ratio"] is None or effect["speedup_ratio"] < 1.2:
            findings.append(
                {
                    "severity": "warn",
                    "code": "parallel_speedup_below_threshold",
                    "message": "TargetParallelism speedup is below the 1.2x advisory threshold.",
                    "speedup_ratio": effect["speedup_ratio"],
                }
            )

    error_count = sum(1 for item in findings if item.get("severity") == "error")
    warn_count = sum(1 for item in findings if item.get("severity") == "warn")
    return {
        "schema_version": "1.0",
        "report_kind": "target_repo_gate_speed_audit",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "catalog_path": str(catalog_path),
        "target_count": len(target_reports),
        "status": "pass" if error_count == 0 else "fail",
        "error_count": error_count,
        "warn_count": warn_count,
        "quick_timeout_budget_seconds": quick_timeout_budget_seconds,
        "full_timeout_budget_seconds": full_timeout_budget_seconds,
        "effect_summary": effect,
        "targets": target_reports,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit target repo quick/full gate speed profiles and effect evidence.")
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--catalog", default=str(ROOT / "docs" / "targets" / "target-repos-catalog.json"))
    parser.add_argument("--quick-timeout-budget-seconds", type=int, default=180)
    parser.add_argument("--full-timeout-budget-seconds", type=int, default=600)
    parser.add_argument("--serial-result")
    parser.add_argument("--parallel-result")
    parser.add_argument("--output")
    args = parser.parse_args()

    report = audit(
        repo_root=Path(args.repo_root).resolve(strict=False),
        catalog_path=Path(args.catalog).resolve(strict=False),
        quick_timeout_budget_seconds=args.quick_timeout_budget_seconds,
        full_timeout_budget_seconds=args.full_timeout_budget_seconds,
        serial_result_path=Path(args.serial_result).resolve(strict=False) if args.serial_result else None,
        parallel_result_path=Path(args.parallel_result).resolve(strict=False) if args.parallel_result else None,
    )
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        output_path = Path(args.output).resolve(strict=False)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
    print(
        json.dumps(
            {
                "status": report["status"],
                "target_count": report["target_count"],
                "error_count": report["error_count"],
                "warn_count": report["warn_count"],
                "output": str(Path(args.output).resolve(strict=False)) if args.output else None,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
