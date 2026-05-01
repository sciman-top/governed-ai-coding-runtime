from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_SRC = ROOT / "scripts"
if str(SCRIPTS_SRC) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_SRC))
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))

from governed_ai_coding_runtime_contracts.claude_code_adapter import (
    ClaudeCodeProbeCommand,
    ClaudeCodeSurfaceProbe,
    build_claude_code_adapter_trial_result,
    claude_code_adapter_trial_to_dict,
    claude_code_capability_readiness_to_dict,
    claude_code_probe_to_dict,
    probe_claude_code_surface,
    summarize_claude_code_capability_readiness,
)
from lib.claude_local import claude_status
from lib.codex_local import codex_status


REQUIRED_DOCS = (
    "docs/product/host-feedback-loop.md",
    "docs/product/host-feedback-loop.zh-CN.md",
    "docs/product/adapter-conformance-parity-matrix.md",
    "docs/quickstart/ai-coding-usage-guide.md",
    "docs/quickstart/ai-coding-usage-guide.zh-CN.md",
)

REQUIRED_GLOBAL_TARGETS = (
    ("codex", ".codex/AGENTS.md"),
    ("claude", ".claude/CLAUDE.md"),
)
TARGET_RUN_STALE_AFTER_HOURS = 168
TARGET_RUN_FILE_RE = re.compile(r"^(?P<repo>.+?)-(?P<kind>daily(?:-[^-]+)?|onboard)-(?P<stamp>\d{14})\.json$")


@dataclass(frozen=True)
class FeedbackDimension:
    dimension_id: str
    status: str
    summary: str
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimension_id": self.dimension_id,
            "status": self.status,
            "summary": self.summary,
            "details": self.details,
        }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize Codex/Claude host feedback surfaces, rule distribution, and target-run evidence."
    )
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-markdown", default=None, help="Optional markdown output path.")
    parser.add_argument("--assert-minimum", action="store_true", help="Fail if the minimum feedback surface is incomplete.")
    parser.add_argument("--max-target-runs", type=int, default=5, help="Maximum number of target run summaries to include.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root)
    payload = build_host_feedback_summary(repo_root=repo_root, max_target_runs=args.max_target_runs)

    if args.write_markdown:
        output = Path(args.write_markdown)
        if not output.is_absolute():
            output = repo_root / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_markdown_report(payload), encoding="utf-8")
        payload["markdown_report"] = output.resolve(strict=False).as_posix()

    if args.assert_minimum:
        failures = validate_minimum_feedback_surface(payload)
        payload["minimum_surface_failures"] = failures
        if failures:
            print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))
            return 1

    print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))
    return 0


def build_host_feedback_summary(*, repo_root: Path, max_target_runs: int = 5) -> dict[str, Any]:
    resolved_root = repo_root.resolve(strict=False)
    generated_at = datetime.now(timezone.utc)
    docs_dimension = _build_docs_dimension(resolved_root)
    rules_dimension = _build_rules_dimension(resolved_root)
    hosts_dimension = _build_hosts_dimension()
    parity_dimension = _build_parity_dimension(resolved_root)
    claude_workload_dimension = _build_claude_workload_dimension(resolved_root)
    target_runs_dimension = _build_target_runs_dimension(resolved_root, max_target_runs=max_target_runs, generated_at=generated_at)

    dimensions = [
        docs_dimension,
        rules_dimension,
        hosts_dimension,
        parity_dimension,
        claude_workload_dimension,
        target_runs_dimension,
    ]
    status = _aggregate_status(dimensions)
    recommendations = _build_recommendations(dimensions)
    summary = {
        "dimensions_ok": sum(1 for item in dimensions if item.status == "ok"),
        "dimensions_attention": sum(1 for item in dimensions if item.status == "attention"),
        "dimensions_fail": sum(1 for item in dimensions if item.status == "fail"),
        "latest_target_repos": [item["repo_id"] for item in target_runs_dimension.details.get("latest_runs", [])],
        "codex_host_status": hosts_dimension.details["codex"].get("status"),
        "claude_host_status": hosts_dimension.details["claude"].get("status"),
        "claude_workload_status": claude_workload_dimension.details.get("readiness", {}).get("status"),
        "claude_adapter_tier": claude_workload_dimension.details.get("readiness", {}).get("adapter_tier"),
        "target_run_freshness": target_runs_dimension.details.get("freshness_status"),
        "rule_manifest_revision": rules_dimension.details.get("sync_revision"),
    }
    return {
        "status": status,
        "generated_at": generated_at.isoformat(),
        "repo_root": resolved_root.as_posix(),
        "summary": summary,
        "dimensions": [item.to_dict() for item in dimensions],
        "recommendations": recommendations,
    }


def validate_minimum_feedback_surface(payload: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    dimensions = {item["dimension_id"]: item for item in payload.get("dimensions", []) if isinstance(item, dict)}

    docs = dimensions.get("docs")
    if not docs:
        failures.append("missing docs dimension")
    elif docs["details"].get("missing_docs"):
        failures.append("missing feedback guide docs: " + ", ".join(docs["details"]["missing_docs"]))

    rules = dimensions.get("rules")
    if not rules:
        failures.append("missing rules dimension")
    else:
        if not rules["details"].get("manifest_exists"):
            failures.append("rules manifest missing")
        expected_tools = [tool for tool, _suffix in REQUIRED_GLOBAL_TARGETS]
        present_tools = rules["details"].get("required_global_tools_present") or []
        missing_tools = [tool for tool in expected_tools if tool not in present_tools]
        if missing_tools:
            failures.append("manifest missing required global tools: " + ", ".join(missing_tools))

    parity = dimensions.get("parity")
    if not parity:
        failures.append("missing parity dimension")
    elif parity["details"].get("missing_hosts"):
        failures.append("parity matrix missing hosts: " + ", ".join(parity["details"]["missing_hosts"]))

    claude_workload = dimensions.get("claude_workload")
    if not claude_workload:
        failures.append("missing claude workload dimension")
    elif claude_workload["details"].get("readiness", {}).get("status") == "blocked":
        failures.append("claude workload probe is blocked")

    target_runs = dimensions.get("target_runs")
    if not target_runs:
        failures.append("missing target-runs dimension")
    else:
        if target_runs["details"].get("total_run_files", 0) < 1:
            failures.append("no target repo run evidence found")
        if not target_runs["details"].get("latest_runs"):
            failures.append("no latest target repo summaries extracted")

    return failures


def render_markdown_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Host Feedback Summary",
        "",
        "## Goal",
        "- Give one repeatable feedback surface for Codex and Claude host entrypoints, rule distribution, parity posture, and target-run evidence.",
        "",
        "## Snapshot",
        f"- Generated at: `{payload['generated_at']}`",
        f"- Overall status: `{payload['status']}`",
        f"- Rule manifest revision: `{summary.get('rule_manifest_revision') or 'unknown'}`",
        f"- Codex host status: `{summary.get('codex_host_status') or 'unknown'}`",
        f"- Claude host status: `{summary.get('claude_host_status') or 'unknown'}`",
        f"- Claude workload status: `{summary.get('claude_workload_status') or 'unknown'}`",
        f"- Claude adapter tier: `{summary.get('claude_adapter_tier') or 'unknown'}`",
        f"- Latest target repos: `{', '.join(summary.get('latest_target_repos') or []) or 'none'}`",
        "",
        "## Dimensions",
    ]
    for item in payload["dimensions"]:
        lines.extend(
            [
                f"### {item['dimension_id']}",
                f"- Status: `{item['status']}`",
                f"- Summary: {item['summary']}",
                "```json",
                json.dumps(item["details"], ensure_ascii=False, indent=2, sort_keys=True),
                "```",
                "",
            ]
        )

    lines.extend(
        [
            "## Recommendations",
            *(f"- {recommendation}" for recommendation in payload.get("recommendations", [])),
            "",
            "## Verification",
            "- `python scripts/host-feedback-summary.py --assert-minimum`",
            "- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action FeedbackReport`",
            "- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`",
            "",
            "## Rollback",
            "- Remove or revert the new feedback summary script, docs, and operator wiring if they regress the existing operator workflow.",
        ]
    )
    return "\n".join(lines)


def _build_docs_dimension(repo_root: Path) -> FeedbackDimension:
    missing = [path for path in REQUIRED_DOCS if not (repo_root / path).exists()]
    status = "ok" if not missing else "fail"
    summary = "feedback guide docs are present" if not missing else "feedback guide docs are incomplete"
    return FeedbackDimension(
        dimension_id="docs",
        status=status,
        summary=summary,
        details={
            "required_docs": list(REQUIRED_DOCS),
            "missing_docs": missing,
        },
    )


def _build_rules_dimension(repo_root: Path) -> FeedbackDimension:
    manifest_path = repo_root / "rules" / "manifest.json"
    details: dict[str, Any] = {
        "manifest_path": manifest_path.as_posix(),
        "manifest_exists": manifest_path.exists(),
        "sync_revision": None,
        "default_version": None,
        "global_entries": [],
        "required_global_tools_present": [],
        "missing_global_targets": [],
    }
    if not manifest_path.exists():
        return FeedbackDimension("rules", "fail", "rule manifest is missing", details)

    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = payload.get("entries", [])
    details["sync_revision"] = payload.get("sync_revision")
    details["default_version"] = payload.get("default_version")
    details["global_entries"] = [
        {
            "id": entry.get("id"),
            "tool": entry.get("tool"),
            "target_path": entry.get("target_path"),
        }
        for entry in entries
        if isinstance(entry, dict) and entry.get("scope") == "global"
    ]
    global_tools = {entry["tool"] for entry in details["global_entries"] if isinstance(entry.get("tool"), str)}
    details["required_global_tools_present"] = [tool for tool, _suffix in REQUIRED_GLOBAL_TARGETS if tool in global_tools]
    missing_targets: list[str] = []
    for tool, suffix in REQUIRED_GLOBAL_TARGETS:
        expected = Path.home() / suffix
        if not expected.exists():
            missing_targets.append(f"{tool}:{expected.as_posix()}")
    details["missing_global_targets"] = missing_targets
    status = "ok" if not missing_targets else "attention"
    summary = "manifest-backed rule distribution is present"
    if missing_targets:
        summary = "manifest exists but some synchronized global targets are missing"
    return FeedbackDimension("rules", status, summary, details)


def _build_hosts_dimension() -> FeedbackDimension:
    codex = _safe_host_status(codex_status)
    claude = _safe_host_status(claude_status)
    codex_health = _host_health(
        loader_status=codex.get("status"),
        config_status=_nested_value(codex, "config", "status"),
        command_exit_code=_nested_value(codex, "login_status", "exit_code"),
    )
    claude_health = _host_health(
        loader_status=claude.get("status"),
        config_status=_nested_value(claude, "config", "status"),
        command_exit_code=_nested_value(claude, "command", "exit_code"),
        mcp_exit_code=_nested_value(claude, "mcp", "exit_code"),
    )
    status = "ok" if codex_health == "ok" and claude_health == "ok" else "attention"
    summary = "both host entrypoint snapshots are healthy" if status == "ok" else "one or more host snapshots need attention"
    return FeedbackDimension(
        dimension_id="hosts",
        status=status,
        summary=summary,
        details={
            "codex": {
                "status": codex.get("status"),
                "health": codex_health,
                "active_account": _active_codex_account_label(codex),
                "config_status": _nested_value(codex, "config", "status"),
                "login_exit_code": _nested_value(codex, "login_status", "exit_code"),
                "login_summary": _nested_value(codex, "login_status", "summary"),
            },
            "claude": {
                "status": claude.get("status"),
                "health": claude_health,
                "active_provider": _nested_value(claude, "active_provider", "name"),
                "config_status": _nested_value(claude, "config", "status"),
                "command_exit_code": _nested_value(claude, "command", "exit_code"),
                "command_summary": _nested_value(claude, "command", "summary"),
                "mcp_exit_code": _nested_value(claude, "mcp", "exit_code"),
                "mcp_summary": _nested_value(claude, "mcp", "summary"),
            },
        },
    )


def _build_parity_dimension(repo_root: Path) -> FeedbackDimension:
    path = repo_root / "docs" / "product" / "adapter-conformance-parity-matrix.md"
    details = {"path": path.as_posix(), "exists": path.exists(), "missing_hosts": []}
    if not path.exists():
        return FeedbackDimension("parity", "fail", "adapter parity matrix is missing", details)
    text = path.read_text(encoding="utf-8")
    missing_hosts = [host for host in ("Codex", "Claude Code") if host not in text]
    details["missing_hosts"] = missing_hosts
    status = "ok" if not missing_hosts else "fail"
    summary = "Codex and Claude parity posture is documented" if status == "ok" else "parity matrix is missing required host rows"
    return FeedbackDimension("parity", status, summary, details)


def _build_claude_workload_dimension(repo_root: Path) -> FeedbackDimension:
    details: dict[str, Any] = {
        "probe_source": "live_claude_code_adapter_probe",
        "probe": None,
        "readiness": None,
        "trial": None,
    }
    try:
        probe = probe_claude_code_surface(cwd=repo_root)
        readiness = summarize_claude_code_capability_readiness(probe)
        trial = build_claude_code_adapter_trial_result(
            repo_id="governed-ai-coding-runtime",
            task_id="host-feedback-claude-code-probe",
            binding_id="binding-claude-code",
            native_attach_available=probe.native_attach_available,
            process_bridge_available=probe.process_bridge_available,
            settings_available=probe.settings_available,
            hooks_available=probe.hooks_available,
            session_id_available=probe.session_id_available,
            structured_events_available=probe.structured_events_available,
            evidence_export_available=probe.evidence_export_available,
            resume_available=probe.resume_available,
            run_id="host-feedback-live-probe",
            probe=probe,
        )
    except Exception as exc:
        details["error"] = str(exc)
        return FeedbackDimension(
            "claude_workload",
            "fail",
            "Claude Code workload probe failed",
            details,
        )

    details["probe"] = claude_code_probe_to_dict(probe)
    details["readiness"] = claude_code_capability_readiness_to_dict(readiness)
    details["trial"] = claude_code_adapter_trial_to_dict(trial)

    if readiness.status == "ready":
        status = "ok"
        summary = "Claude Code workload adapter probe is ready"
    elif readiness.status == "degraded":
        status = "attention"
        summary = "Claude Code workload adapter probe is degraded but usable"
    else:
        status = "fail"
        summary = "Claude Code workload adapter probe is blocked"
    return FeedbackDimension("claude_workload", status, summary, details)


def _build_target_runs_dimension(repo_root: Path, *, max_target_runs: int, generated_at: datetime) -> FeedbackDimension:
    evidence_root = repo_root / "docs" / "change-evidence" / "target-repo-runs"
    details: dict[str, Any] = {
        "path": evidence_root.as_posix(),
        "exists": evidence_root.exists(),
        "total_run_files": 0,
        "latest_runs": [],
        "degraded_latest_runs": [],
        "skipped_files": [],
        "freshness_status": "unknown",
        "stale_after_hours": TARGET_RUN_STALE_AFTER_HOURS,
    }
    if not evidence_root.exists():
        return FeedbackDimension("target_runs", "fail", "target repo run evidence directory is missing", details)

    files = sorted(evidence_root.glob("*.json"))
    details["total_run_files"] = len(files)
    grouped: dict[str, list[Path]] = defaultdict(list)
    for path in files:
        parsed = _parse_target_run_file(path)
        if parsed is None:
            details["skipped_files"].append({"file_name": path.name, "reason": "not a target daily/onboard run artifact"})
            continue
        grouped[parsed["repo_id"]].append(path)

    latest_runs: list[dict[str, Any]] = []
    for repo_id, paths in grouped.items():
        selected = max(paths, key=_target_run_sort_key)
        try:
            latest_runs.append(_summarize_target_run(repo_id, selected, generated_at=generated_at))
        except ValueError as exc:
            details["skipped_files"].append({"file_name": selected.name, "reason": str(exc)})
    latest_runs.sort(key=lambda item: item.get("run_stamp") or item["file_name"], reverse=True)
    details["latest_runs"] = latest_runs[:max_target_runs]
    details["degraded_latest_runs"] = [
        {
            "repo_id": item["repo_id"],
            "file_name": item["file_name"],
            "codex_capability_status": item.get("codex_capability_status"),
            "adapter_tier": item.get("adapter_tier"),
            "flow_kind": item.get("flow_kind"),
            "recovery_evidence_rule": "fresh target run with codex_capability_status=ready and adapter_tier=native_attach",
            "claim_guard": "do not claim native_attach recovery until a fresh target repo run proves it",
        }
        for item in latest_runs[:max_target_runs]
        if item.get("codex_capability_status") not in {"ready", None}
    ]
    stale_runs = [
        item
        for item in latest_runs
        if isinstance(item.get("age_hours"), (int, float)) and item["age_hours"] > TARGET_RUN_STALE_AFTER_HOURS
    ]
    details["stale_latest_runs"] = [
        {"repo_id": item["repo_id"], "file_name": item["file_name"], "age_hours": item["age_hours"]}
        for item in stale_runs[:max_target_runs]
    ]
    if latest_runs:
        details["freshness_status"] = "stale" if stale_runs else "fresh"

    if not latest_runs:
        status = "fail"
        summary = "no target-run evidence found"
    elif stale_runs:
        status = "attention"
        summary = f"latest target-run evidence is stale for {len(stale_runs)} repos"
    else:
        status = "ok"
        summary = f"fresh target-run evidence summarized for {len(latest_runs)} repos"
    return FeedbackDimension("target_runs", status, summary, details)


def _summarize_target_run(repo_id: str, path: Path, *, generated_at: datetime) -> dict[str, Any]:
    parsed = _parse_target_run_file(path) or {"run_kind": "", "run_stamp": ""}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("target-run payload must be an object")
    runtime_payload = _nested_value(payload, "runtime_check", "payload") or {}
    status_payload = runtime_payload.get("status") if isinstance(runtime_payload, dict) and isinstance(runtime_payload.get("status"), dict) else {}
    summary_payload = runtime_payload.get("summary") if isinstance(runtime_payload, dict) and isinstance(runtime_payload.get("summary"), dict) else {}
    live_loop = runtime_payload.get("live_loop") if isinstance(runtime_payload, dict) and isinstance(runtime_payload.get("live_loop"), dict) else {}
    write_execute = runtime_payload.get("write_execute") if isinstance(runtime_payload, dict) else None
    codex_capability = status_payload.get("codex_capability") if isinstance(status_payload, dict) and isinstance(status_payload.get("codex_capability"), dict) else {}
    return {
        "repo_id": repo_id,
        "file_name": path.name,
        "run_kind": parsed["run_kind"],
        "run_stamp": parsed["run_stamp"],
        "age_hours": _target_run_age_hours(parsed["run_stamp"], generated_at),
        "overall_status": payload.get("overall_status"),
        "flow_mode": payload.get("flow_mode"),
        "adapter_tier": codex_capability.get("adapter_tier"),
        "flow_kind": codex_capability.get("flow_kind") or summary_payload.get("flow_kind"),
        "codex_capability_status": codex_capability.get("status"),
        "closure_state": live_loop.get("closure_state"),
        "write_status": _extract_write_status(write_execute),
        "attachment_health": summary_payload.get("attachment_health"),
        "unsupported_capabilities": codex_capability.get("unsupported_capabilities") or [],
    }


def _parse_target_run_file(path: Path) -> dict[str, str] | None:
    match = TARGET_RUN_FILE_RE.match(path.name)
    if not match:
        return None
    return {
        "repo_id": match.group("repo"),
        "run_kind": match.group("kind"),
        "run_stamp": match.group("stamp"),
    }


def _target_run_sort_key(path: Path) -> tuple[str, int, str]:
    parsed = _parse_target_run_file(path)
    if parsed is None:
        return ("", 0, path.name)
    # For equal timestamps prefer daily evidence over onboard snapshots because daily carries real workload feedback.
    kind_rank = 1 if parsed["run_kind"].startswith("daily") else 0
    return (parsed["run_stamp"], kind_rank, path.name)


def _target_run_age_hours(stamp: str, generated_at: datetime) -> float | None:
    if not stamp:
        return None
    try:
        parsed = datetime.strptime(stamp, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    return round(max(0.0, (generated_at - parsed).total_seconds() / 3600), 2)


def _extract_write_status(write_execute: object) -> str | None:
    if not isinstance(write_execute, dict):
        return None
    if isinstance(write_execute.get("execution_status"), str):
        return str(write_execute["execution_status"])
    if isinstance(write_execute.get("status"), str):
        return str(write_execute["status"])
    return None


def _safe_host_status(loader) -> dict[str, Any]:
    try:
        payload = loader()
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
    return {"status": "ok", **payload}


def _host_health(
    *,
    loader_status: object,
    config_status: object,
    command_exit_code: object,
    mcp_exit_code: object | None = None,
) -> str:
    if loader_status != "ok":
        return "error"
    if config_status not in (None, "ok"):
        return "attention"
    for exit_code in (command_exit_code, mcp_exit_code):
        if exit_code in (None, ""):
            continue
        try:
            if int(exit_code) != 0:
                return "attention"
        except (TypeError, ValueError):
            return "attention"
    return "ok"


def _active_codex_account_label(payload: dict[str, Any]) -> str | None:
    active = payload.get("active_account")
    if isinstance(active, dict):
        label = active.get("account_label") or active.get("email") or active.get("display_name")
        if isinstance(label, str) and label.strip():
            return label.strip()
    return None


def _nested_value(payload: dict[str, Any], *keys: str) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _aggregate_status(dimensions: list[FeedbackDimension]) -> str:
    if any(item.status == "fail" for item in dimensions):
        return "fail"
    if any(item.status == "attention" for item in dimensions):
        return "attention"
    return "pass"


def _build_recommendations(dimensions: list[FeedbackDimension]) -> list[str]:
    dimension_map = {item.dimension_id: item for item in dimensions}
    recommendations: list[str] = []

    docs = dimension_map["docs"]
    if docs.details["missing_docs"]:
        recommendations.append("补齐 host feedback guide 与 AI coding quickstart 链接，避免后续只剩工具输出没有判读说明。")

    rules = dimension_map["rules"]
    if rules.details["missing_global_targets"]:
        recommendations.append("先运行 `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -Apply`，确认 Codex/Claude 全局规则副本已经真正同步。")

    hosts = dimension_map["hosts"]
    if hosts.details["codex"]["health"] != "ok":
        recommendations.append("Codex 本机状态需要关注；先核对真实 `codex` 可执行入口、登录状态和 `C:\\Users\\sciman\\.codex\\config.toml`。")
    if hosts.details["claude"]["health"] != "ok":
        recommendations.append("Claude 本机状态需要关注；先核对 `settings.json`、provider profile、`claude --version` 和 `claude mcp list`。")

    parity = dimension_map["parity"]
    if parity.details["missing_hosts"]:
        recommendations.append("补齐 adapter parity matrix 中的 Codex / Claude 行，避免后续无法明确回答双宿主是否等效。")

    claude_workload = dimension_map["claude_workload"]
    claude_readiness = claude_workload.details.get("readiness") or {}
    if claude_readiness.get("status") == "blocked":
        recommendations.append("Claude workload probe 已阻断；先修复 `claude --version` / `claude --help` 可执行入口，再重跑 FeedbackReport。")
    elif claude_readiness.get("status") == "degraded":
        recommendations.append("Claude workload probe 处于 degraded；优先补齐 managed settings/hooks、session/resume 或 structured event 能力，避免只停留在配置可用。")

    target_runs = dimension_map["target_runs"]
    if not target_runs.details["latest_runs"]:
        recommendations.append("先跑一轮 `runtime-flow-preset.ps1 -AllTargets -FlowMode daily -Json`，否则没有真实目标仓反馈可分析。")
    elif target_runs.details.get("freshness_status") == "stale":
        recommendations.append("最新 target-run evidence 已过期；先跑 `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action DailyAll -Mode quick` 刷新真实 workload 反馈。")
    elif target_runs.details.get("degraded_latest_runs"):
        recommendations.append("最新 target runs 仍存在 degraded host posture；先刷新目标仓 run 和 host feedback，并仅在 fresh evidence 同时回到 `codex_capability_status=ready` 与 `adapter_tier=native_attach` 后再宣称恢复。")
    else:
        recommendations.append("对每次功能优化，先生成 host feedback summary，再对照 latest target runs 的 `adapter_tier / closure_state / write_status` 判断是宿主问题、规则问题还是 runtime 问题。")

    return recommendations


if __name__ == "__main__":
    raise SystemExit(main())
