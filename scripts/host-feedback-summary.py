from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
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


GUIDE_PATH_ZH = "docs/product/host-feedback-loop.zh-CN.md"
GUIDE_PATH_EN = "docs/product/host-feedback-loop.md"
PARITY_PATH = "docs/product/adapter-conformance-parity-matrix.md"

REQUIRED_DOCS = (
    GUIDE_PATH_EN,
    GUIDE_PATH_ZH,
    PARITY_PATH,
    "docs/quickstart/ai-coding-usage-guide.md",
    "docs/quickstart/ai-coding-usage-guide.zh-CN.md",
)

REQUIRED_GLOBAL_TARGETS = (
    ("codex", ".codex/AGENTS.md"),
    ("claude", ".claude/CLAUDE.md"),
)
HOST_FEEDBACK_FIXTURE_ENV = "GACR_HOST_FEEDBACK_FIXTURE"
HOST_FEEDBACK_FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "host-feedback"
HOST_FEEDBACK_FIXTURE_SHAPE = {
    "schema_version": str,
    "fixture_id": str,
    "acceptance_scope": str,
    "global_target_presence": {"codex": bool, "claude": bool},
    "codex_status": {
        "login_status": {"exit_code": int, "summary": str},
        "config": {"status": str},
        "active_account": {"account_label": str},
    },
    "claude_status": {
        "active_provider": {"name": str},
        "config": {"status": str},
        "command": {"exit_code": int, "summary": str},
        "mcp": {"exit_code": int, "summary": str},
    },
    "claude_probe": {
        "claude_cli_available": bool,
        "version": (str, type(None)),
        "native_attach_available": bool,
        "process_bridge_available": bool,
        "settings_available": bool,
        "hooks_available": bool,
        "session_id_available": bool,
        "structured_events_available": bool,
        "evidence_export_available": bool,
        "resume_available": bool,
        "live_session_id": (str, type(None)),
        "live_resume_id": (str, type(None)),
        "reason": str,
        "failure_stage": (str, type(None)),
        "remediation_hint": (str, type(None)),
        "probe_commands": [{"cmd": str, "exit_code": int, "key_output": str, "timestamp": str}],
    },
}


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


@dataclass(frozen=True)
class HostFeedbackInputs:
    mode: str
    acceptance_scope: str
    fixture_id: str | None = None
    fixture_ref: str | None = None
    fixture_sha256: str | None = None
    global_target_presence: dict[str, bool] | None = None
    codex_status_payload: dict[str, Any] | None = None
    claude_status_payload: dict[str, Any] | None = None
    claude_probe: ClaudeCodeSurfaceProbe | None = None

    def provenance(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "acceptance_scope": self.acceptance_scope,
            "hosted_acceptance": False,
            "fixture_id": self.fixture_id,
            "fixture_ref": self.fixture_ref,
            "fixture_sha256": self.fixture_sha256,
        }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize Codex/Claude host feedback surfaces, global rule distribution, and repo-local parity posture."
    )
    parser.add_argument("--repo-root", default=str(ROOT))
    parser.add_argument("--write-markdown", default=None, help="Optional markdown output path.")
    parser.add_argument("--assert-minimum", action="store_true", help="Fail if the minimum feedback surface is incomplete.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    repo_root = Path(args.repo_root)
    try:
        payload = build_host_feedback_summary(repo_root=repo_root)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    if args.write_markdown:
        output = Path(args.write_markdown)
        if not output.is_absolute():
            output = repo_root / output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render_markdown_report(payload), encoding="utf-8")
        payload["report_path"] = output.resolve(strict=False).as_posix()

    if args.assert_minimum:
        failures = validate_minimum_feedback_surface(payload)
        payload["minimum_surface_failures"] = failures
        if failures:
            print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))
            return 1

    print(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True))
    return 0


def build_host_feedback_summary(*, repo_root: Path) -> dict[str, Any]:
    resolved_root = repo_root.resolve(strict=False)
    generated_at = datetime.now(timezone.utc)
    inputs = _resolve_host_feedback_inputs()
    docs_dimension = _build_docs_dimension(resolved_root)
    rules_dimension = _build_rules_dimension(resolved_root, inputs=inputs)
    hosts_dimension = _build_hosts_dimension(inputs=inputs)
    parity_dimension = _build_parity_dimension(resolved_root)
    claude_workload_dimension = _build_claude_workload_dimension(resolved_root, inputs=inputs)

    dimensions = [
        docs_dimension,
        rules_dimension,
        hosts_dimension,
        parity_dimension,
        claude_workload_dimension,
    ]
    status = _aggregate_status(dimensions)
    recommendations = _build_recommendations(dimensions)
    summary = {
        "dimensions_ok": sum(1 for item in dimensions if item.status == "ok"),
        "dimensions_attention": sum(1 for item in dimensions if item.status == "attention"),
        "dimensions_fail": sum(1 for item in dimensions if item.status == "fail"),
        "codex_host_status": hosts_dimension.details["codex"].get("status"),
        "claude_host_status": hosts_dimension.details["claude"].get("status"),
        "claude_workload_status": (claude_workload_dimension.details.get("readiness") or {}).get("status"),
        "claude_adapter_tier": (claude_workload_dimension.details.get("readiness") or {}).get("adapter_tier"),
        "rule_manifest_revision": rules_dimension.details.get("sync_revision"),
    }
    return {
        "status": status,
        "generated_at": generated_at.isoformat(),
        "repo_root": resolved_root.as_posix(),
        "input_provenance": inputs.provenance(),
        "guide_path": GUIDE_PATH_ZH,
        "guide_path_en": GUIDE_PATH_EN,
        "parity_path": PARITY_PATH,
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

    return failures


def render_markdown_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Host Feedback Summary",
        "",
        "## Goal",
        "- Give one repeatable host-only feedback surface for Codex and Claude host entrypoints, global rule distribution, and repo-local parity posture.",
        "",
        "## Snapshot",
        f"- Generated at: `{payload['generated_at']}`",
        f"- Overall status: `{payload['status']}`",
        f"- Rule manifest revision: `{summary.get('rule_manifest_revision') or 'unknown'}`",
        f"- Codex host status: `{summary.get('codex_host_status') or 'unknown'}`",
        f"- Claude host status: `{summary.get('claude_host_status') or 'unknown'}`",
        f"- Claude workload status: `{summary.get('claude_workload_status') or 'unknown'}`",
        f"- Claude adapter tier: `{summary.get('claude_adapter_tier') or 'unknown'}`",
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
            "- Remove or revert the host-only feedback summary script, docs, and operator wiring if they regress the existing operator workflow.",
        ]
    )
    return "\n".join(lines)


def _resolve_host_feedback_inputs() -> HostFeedbackInputs:
    raw_fixture_path = os.environ.get(HOST_FEEDBACK_FIXTURE_ENV, "").strip()
    if not raw_fixture_path:
        return HostFeedbackInputs(
            mode="live_host",
            acceptance_scope="repo_local_host_only",
        )

    fixture_path = Path(raw_fixture_path)
    if not fixture_path.is_absolute():
        fixture_path = ROOT / fixture_path
    fixture_path = fixture_path.resolve(strict=False)
    fixture_root = HOST_FEEDBACK_FIXTURE_ROOT.resolve(strict=False)
    try:
        fixture_ref = fixture_path.relative_to(ROOT.resolve(strict=False)).as_posix()
        fixture_path.relative_to(fixture_root)
    except ValueError as exc:
        raise ValueError(
            f"{HOST_FEEDBACK_FIXTURE_ENV} must point inside tests/fixtures/host-feedback: {fixture_path}"
        ) from exc
    if fixture_path.suffix.lower() != ".json":
        raise ValueError(f"host feedback fixture must be JSON: {fixture_ref}")

    try:
        fixture_bytes = fixture_path.read_bytes()
    except OSError as exc:
        raise ValueError(f"host feedback fixture is not readable: {fixture_ref} ({exc})") from exc
    try:
        payload = json.loads(fixture_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"host feedback fixture is invalid UTF-8 JSON: {fixture_ref} ({exc})") from exc

    fixture = _validate_host_feedback_fixture(payload, fixture_ref=fixture_ref)
    return HostFeedbackInputs(
        mode="test_fixture",
        acceptance_scope=fixture["acceptance_scope"],
        fixture_id=fixture["fixture_id"],
        fixture_ref=fixture_ref,
        fixture_sha256=hashlib.sha256(fixture_bytes).hexdigest(),
        global_target_presence=fixture["global_target_presence"],
        codex_status_payload=fixture["codex_status"],
        claude_status_payload=fixture["claude_status"],
        claude_probe=_claude_probe_from_fixture(fixture["claude_probe"], fixture_ref=fixture_ref),
    )


def _validate_host_feedback_fixture(payload: object, *, fixture_ref: str) -> dict[str, Any]:
    _validate_fixture_shape(payload, HOST_FEEDBACK_FIXTURE_SHAPE, path="fixture", fixture_ref=fixture_ref)
    fixture = payload
    if fixture["schema_version"] != "1.0":
        raise ValueError(f"host feedback fixture schema_version must be 1.0: {fixture_ref}")
    if fixture["acceptance_scope"] != "test_only_not_hosted":
        raise ValueError(f"host feedback fixture acceptance_scope must be test_only_not_hosted: {fixture_ref}")
    return fixture


def _claude_probe_from_fixture(payload: object, *, fixture_ref: str) -> ClaudeCodeSurfaceProbe:
    probe = dict(payload)
    commands = [ClaudeCodeProbeCommand(**command) for command in probe.pop("probe_commands")]
    return ClaudeCodeSurfaceProbe(probe_commands=commands, **probe)


def _validate_fixture_shape(value: object, shape: object, *, path: str, fixture_ref: str) -> None:
    if isinstance(shape, dict):
        if not isinstance(value, dict):
            raise ValueError(f"host feedback fixture {path} must be an object: {fixture_ref}")
        missing = sorted(set(shape) - set(value))
        unexpected = sorted(set(value) - set(shape))
        if missing or unexpected:
            raise ValueError(
                f"host feedback fixture {path} keys are invalid: missing={missing}, unexpected={unexpected}: {fixture_ref}"
            )
        for key, child_shape in shape.items():
            _validate_fixture_shape(value[key], child_shape, path=f"{path}.{key}", fixture_ref=fixture_ref)
        return
    if isinstance(shape, list):
        if not isinstance(value, list) or not value:
            raise ValueError(f"host feedback fixture {path} must be a non-empty array: {fixture_ref}")
        for index, item in enumerate(value):
            _validate_fixture_shape(item, shape[0], path=f"{path}[{index}]", fixture_ref=fixture_ref)
        return

    expected_types = shape if isinstance(shape, tuple) else (shape,)
    if type(value) not in expected_types:
        names = ", ".join(expected.__name__ for expected in expected_types)
        raise ValueError(f"host feedback fixture {path} must have type {names}: {fixture_ref}")
    if isinstance(value, str) and not value.strip():
        raise ValueError(f"host feedback fixture {path} must be non-empty: {fixture_ref}")


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
            "guide_path": GUIDE_PATH_ZH,
            "guide_path_en": GUIDE_PATH_EN,
            "parity_path": PARITY_PATH,
        },
    )


def _build_rules_dimension(repo_root: Path, *, inputs: HostFeedbackInputs) -> FeedbackDimension:
    manifest_path = repo_root / "rules" / "manifest.json"
    details: dict[str, Any] = {
        "manifest_path": manifest_path.as_posix(),
        "manifest_exists": manifest_path.exists(),
        "sync_revision": None,
        "default_version": None,
        "global_entries": [],
        "required_global_tools_present": [],
        "missing_global_targets": [],
        "target_presence_source": inputs.mode,
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
        if inputs.global_target_presence is not None:
            if not inputs.global_target_presence[tool]:
                missing_targets.append(f"{tool}:fixture-declared-absent")
        else:
            expected = Path.home() / suffix
            if not expected.exists():
                missing_targets.append(f"{tool}:{expected.as_posix()}")
    details["missing_global_targets"] = missing_targets
    status = "ok" if not missing_targets else "attention"
    summary = "manifest-backed global rule distribution is present"
    if missing_targets:
        summary = "manifest exists but some synchronized global targets are missing"
    return FeedbackDimension("rules", status, summary, details)


def _build_hosts_dimension(*, inputs: HostFeedbackInputs) -> FeedbackDimension:
    codex_loader = codex_status
    claude_loader = claude_status
    if inputs.codex_status_payload is not None:
        codex_loader = lambda: dict(inputs.codex_status_payload or {})
    if inputs.claude_status_payload is not None:
        claude_loader = lambda: dict(inputs.claude_status_payload or {})
    codex = _safe_host_status(codex_loader)
    claude = _safe_host_status(claude_loader)
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
    codex_nonblocking_config_attention = codex_health == "attention" and _nested_value(codex, "config", "status") == "attention"
    claude_nonblocking_config_attention = claude_health == "attention" and _nested_value(claude, "config", "status") == "attention"
    codex_effective_health = "ok" if codex_nonblocking_config_attention else codex_health
    claude_effective_health = "ok" if claude_nonblocking_config_attention else claude_health
    status = "ok" if codex_effective_health == "ok" and claude_effective_health == "ok" else "attention"
    summary = "both host entrypoint snapshots are healthy" if status == "ok" else "one or more host snapshots need attention"
    return FeedbackDimension(
        dimension_id="hosts",
        status=status,
        summary=summary,
        details={
            "codex": {
                "status": codex.get("status"),
                "health": codex_effective_health,
                "nonblocking_config_attention": codex_nonblocking_config_attention,
                "active_account": _active_codex_account_label(codex),
                "config_status": _nested_value(codex, "config", "status"),
                "login_exit_code": _nested_value(codex, "login_status", "exit_code"),
                "login_summary": _nested_value(codex, "login_status", "summary"),
            },
            "claude": {
                "status": claude.get("status"),
                "health": claude_effective_health,
                "nonblocking_config_attention": claude_nonblocking_config_attention,
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
    path = repo_root / PARITY_PATH
    details = {"path": path.as_posix(), "exists": path.exists(), "missing_hosts": []}
    if not path.exists():
        return FeedbackDimension("parity", "fail", "adapter parity matrix is missing", details)
    text = path.read_text(encoding="utf-8")
    missing_hosts = [host for host in ("Codex", "Claude Code") if host not in text]
    details["missing_hosts"] = missing_hosts
    status = "ok" if not missing_hosts else "fail"
    summary = "Codex and Claude parity posture is documented" if status == "ok" else "parity matrix is missing required host rows"
    return FeedbackDimension("parity", status, summary, details)


def _build_claude_workload_dimension(repo_root: Path, *, inputs: HostFeedbackInputs) -> FeedbackDimension:
    details: dict[str, Any] = {
        "probe_source": "test_fixture" if inputs.claude_probe is not None else "live_claude_code_adapter_probe",
        "probe": None,
        "readiness": None,
        "trial": None,
    }
    try:
        probe = inputs.claude_probe or probe_claude_code_surface(cwd=repo_root)
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
            run_id="host-feedback-test-fixture" if inputs.claude_probe is not None else "host-feedback-live-probe",
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
    if inputs.claude_probe is not None:
        details["trial"]["probe_source"] = "test_fixture"

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
    if any(_dimension_counts_as_attention(item) for item in dimensions):
        return "attention"
    return "pass"


def _dimension_counts_as_attention(item: FeedbackDimension) -> bool:
    if item.status != "attention":
        return False
    if item.dimension_id != "hosts":
        return True
    details = item.details if isinstance(item.details, dict) else {}
    codex = details.get("codex") if isinstance(details.get("codex"), dict) else {}
    claude = details.get("claude") if isinstance(details.get("claude"), dict) else {}
    return not bool(codex.get("nonblocking_config_attention")) and not bool(claude.get("nonblocking_config_attention"))


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

    if not recommendations:
        recommendations.append("本仓 host-only feedback 面正常；后续每次修改 host/规则/自演化链时先重跑 `FeedbackReport`，再决定是否需要更高成本 gate。")

    return recommendations


if __name__ == "__main__":
    raise SystemExit(main())
