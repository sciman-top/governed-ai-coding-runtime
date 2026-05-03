from __future__ import annotations

import argparse
from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import shutil
import subprocess
import sys
import time
from urllib.parse import parse_qs, urlparse
import webbrowser
from pathlib import Path
from threading import Lock

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
SCRIPTS_SRC = ROOT / "scripts"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))
if str(SCRIPTS_SRC) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_SRC))

from governed_ai_coding_runtime_contracts.operator_ui import render_runtime_snapshot_html
from governed_ai_coding_runtime_contracts.runtime_status import RuntimeStatusStore, runtime_snapshot_to_dict
from lib.claude_local import claude_home, claude_status, optimize_claude_local, provider_profiles_path, settings_path, switch_provider
from lib.codex_local import codex_status, delete_auth_profile, switch_auth_profile, sync_active_auth_snapshot


def _load_host_feedback_summary_builder():
    path = ROOT / "scripts" / "host-feedback-summary.py"
    module_name = "host_feedback_summary_script"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load host feedback summary script: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module.build_host_feedback_summary


build_host_feedback_summary = _load_host_feedback_summary_builder()


ALLOWED_ACTIONS = {
    "targets": {"operator_action": "Targets", "run_alias": "targets", "timeout_seconds": 300},
    "fast_feedback": {"operator_action": "FastFeedback", "run_alias": "fast", "timeout_seconds": 900},
    "readiness": {"operator_action": "Readiness", "run_alias": "readiness", "timeout_seconds": 1800},
    "rules_dry_run": {"operator_action": "RulesDryRun", "run_alias": "rules-check", "timeout_seconds": 600},
    "rules_apply": {"operator_action": "RulesApply", "run_alias": "rules-apply", "timeout_seconds": 900},
    "governance_baseline_all": {"operator_action": "GovernanceBaselineAll", "run_alias": "governance-baseline", "timeout_seconds": 1800, "allow_multi_target": True},
    "daily_all": {"operator_action": "DailyAll", "run_alias": "daily", "timeout_seconds": 1800, "allow_multi_target": True},
    "apply_all_features": {
        "operator_action": "ApplyAllFeatures",
        "run_alias": "apply-all",
        "timeout_seconds": 2400,
        "allow_multi_target": True,
        "managed_asset_removal_apply": True,
        "managed_asset_removal_default": True,
    },
    "cleanup_targets": {
        "operator_action": "CleanupTargets",
        "run_alias": "cleanup-targets",
        "timeout_seconds": 1800,
        "allow_multi_target": True,
        "managed_asset_removal": True,
    },
    "uninstall_governance": {
        "operator_action": "UninstallGovernance",
        "run_alias": "uninstall-governance",
        "timeout_seconds": 1800,
        "allow_multi_target": True,
        "managed_asset_removal": True,
    },
    "feedback_report": {"operator_action": "FeedbackReport", "run_alias": "feedback", "timeout_seconds": 600},
    "evolution_review": {"operator_action": "EvolutionReview", "run_alias": "evolution-review", "timeout_seconds": 900},
    "experience_review": {"operator_action": "ExperienceReview", "run_alias": "experience-review", "timeout_seconds": 900},
    "evolution_materialize": {"operator_action": "EvolutionMaterialize", "run_alias": "evolution-materialize", "timeout_seconds": 900},
    "core_principle_materialize": {"operator_action": "CorePrincipleMaterialize", "run_alias": "core-principle", "timeout_seconds": 900},
}

CODEX_STATUS_CACHE_TTL_SECONDS = 10.0
CLAUDE_STATUS_CACHE_TTL_SECONDS = 15.0
FEEDBACK_SUMMARY_CACHE_TTL_SECONDS = 30.0
NEXT_WORK_CACHE_TTL_SECONDS = 60.0
SERVER_STARTED_AT = time.time()
UI_RUNTIME_DIR = ROOT / ".runtime" / "operator-ui"
UI_RESTART_REQUEST_PATH = UI_RUNTIME_DIR / "restart-requested.json"
UI_RESTART_COOLDOWN_SECONDS = 20.0
UI_SOURCE_FILES = (
    ROOT / "scripts" / "serve-operator-ui.py",
    ROOT / "scripts" / "operator-ui-service.ps1",
    ROOT / "packages" / "contracts" / "src" / "governed_ai_coding_runtime_contracts" / "operator_ui.py",
    ROOT / "packages" / "contracts" / "src" / "governed_ai_coding_runtime_contracts" / "runtime_status.py",
    ROOT / "scripts" / "lib" / "codex_local.py",
    ROOT / "scripts" / "lib" / "claude_local.py",
)
_STATUS_CACHE_LOCK = Lock()
_STATUS_CACHE: dict[str, dict] = {}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the local governed runtime operator UI.")
    parser.add_argument(
        "--output",
        default=".runtime/artifacts/operator-ui/index.html",
        help="Output HTML path, relative to the repository root unless absolute.",
    )
    parser.add_argument(
        "--lang",
        choices=["zh-CN", "en"],
        default="zh-CN",
        help="UI language. Defaults to zh-CN.",
    )
    parser.add_argument("--serve", action="store_true", help="Run an interactive localhost UI server.")
    parser.add_argument("--host", default="127.0.0.1", help="Interactive server host.")
    parser.add_argument("--port", type=int, default=8766, help="Interactive server port.")
    parser.add_argument("--open", action="store_true", help="Open the generated HTML in the default browser.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.serve:
        return serve_operator_ui(host=args.host, port=args.port, language=args.lang, open_browser=args.open)

    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output
    snapshot = RuntimeStatusStore(ROOT / ".runtime" / "tasks", ROOT).snapshot()
    html = render_runtime_snapshot_html(snapshot, language=args.lang, target_options=load_target_ids())
    html = inject_next_work_panel(html, language=args.lang)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    written = output
    file_url = written.resolve().as_uri()
    payload = {
        "file_url": file_url,
        "language": args.lang,
        "maintenance_stage": snapshot.maintenance.stage,
        "output_path": written.relative_to(ROOT).as_posix(),
        "total_tasks": snapshot.total_tasks,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    if args.open:
        webbrowser.open(file_url)
    return 0


def serve_operator_ui(*, host: str, port: int, language: str, open_browser: bool) -> int:
    server = ThreadingHTTPServer((host, port), _build_handler(default_language=language))
    url = f"http://{host}:{port}/?lang={language}"
    payload = {"url": url, "language": language, "status": "serving"}
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        return 0
    finally:
        server.server_close()
    return 0


def _build_handler(*, default_language: str):
    class OperatorUiHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path in {"/", "/index.html"}:
                params = parse_qs(parsed.query)
                language = _normalize_language(params.get("lang", [default_language])[0])
                if is_operator_ui_process_stale():
                    restart_state = maybe_request_operator_ui_restart(language=language, host=host, port=port)
                    self._send_text(
                        render_stale_service_html(language, restart_state=restart_state),
                        content_type="text/html; charset=utf-8",
                        status=HTTPStatus.CONFLICT,
                    )
                    return
                snapshot = RuntimeStatusStore(ROOT / ".runtime" / "tasks", ROOT).snapshot()
                html = render_runtime_snapshot_html(snapshot, language=language, interactive=True, target_options=load_target_ids())
                html = inject_next_work_panel(html, language=language)
                self._send_text(html, content_type="text/html; charset=utf-8")
                return
            if parsed.path == "/api/status":
                snapshot = RuntimeStatusStore(ROOT / ".runtime" / "tasks", ROOT).snapshot()
                self._send_json(runtime_snapshot_to_dict(snapshot))
                return
            if parsed.path == "/api/ui-process":
                self._send_json(operator_ui_process_status())
                return
            if parsed.path == "/api/targets":
                self._send_json({"targets": load_target_ids()})
                return
            if parsed.path == "/api/codex/status":
                params = parse_qs(parsed.query)
                result = load_codex_status(refresh_if_stale=_truthy(params.get("refresh_if_stale", [""])[0]))
                status = HTTPStatus.OK if result.get("status") == "ok" else HTTPStatus.INTERNAL_SERVER_ERROR
                self._send_json(result, status=status)
                return
            if parsed.path == "/api/claude/status":
                result = load_claude_status()
                status = HTTPStatus.OK if result.get("status") == "ok" else HTTPStatus.INTERNAL_SERVER_ERROR
                self._send_json(result, status=status)
                return
            if parsed.path == "/api/claude/file":
                params = parse_qs(parsed.query)
                result = read_claude_local_file(params.get("kind", [""])[0])
                status = HTTPStatus.OK if "content" in result else HTTPStatus.BAD_REQUEST
                self._send_json(result, status=status)
                return
            if parsed.path == "/api/feedback/summary":
                params = parse_qs(parsed.query)
                if _truthy(params.get("refresh", [""])[0]):
                    invalidate_status_cache("feedback")
                result = load_feedback_summary()
                status = HTTPStatus.OK if result.get("status") != "error" else HTTPStatus.INTERNAL_SERVER_ERROR
                self._send_json(result, status=status)
                return
            if parsed.path == "/api/next-work":
                params = parse_qs(parsed.query)
                if _truthy(params.get("refresh", [""])[0]):
                    invalidate_status_cache("next_work")
                result = load_next_work_summary()
                status = HTTPStatus.OK if result.get("status") != "error" else HTTPStatus.INTERNAL_SERVER_ERROR
                self._send_json(result, status=status)
                return
            if parsed.path == "/api/file":
                params = parse_qs(parsed.query)
                requested = params.get("path", [""])[0]
                result = read_repo_file(requested)
                status = HTTPStatus.OK if "content" in result else HTTPStatus.BAD_REQUEST
                self._send_json(result, status=status)
                return
            self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)

        def do_POST(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path != "/api/run":
                if parsed.path == "/api/codex/switch":
                    result = run_codex_switch(self._read_json_body())
                    status = HTTPStatus.OK if result.get("status") == "ok" else HTTPStatus.BAD_REQUEST
                    self._send_json(result, status=status)
                    return
                if parsed.path == "/api/codex/sync-active":
                    result = run_codex_sync_active(self._read_json_body())
                    status = HTTPStatus.OK if result.get("status") == "ok" else HTTPStatus.BAD_REQUEST
                    self._send_json(result, status=status)
                    return
                if parsed.path == "/api/codex/delete":
                    result = run_codex_delete(self._read_json_body())
                    status = HTTPStatus.OK if result.get("status") == "ok" else HTTPStatus.BAD_REQUEST
                    self._send_json(result, status=status)
                    return
                if parsed.path == "/api/codex/refresh":
                    result = load_codex_status(refresh_online=True)
                    status = HTTPStatus.OK if result.get("status") == "ok" else HTTPStatus.INTERNAL_SERVER_ERROR
                    self._send_json(result, status=status)
                    return
                if parsed.path == "/api/claude/switch":
                    result = run_claude_switch(self._read_json_body())
                    status = HTTPStatus.OK if result.get("status") == "ok" else HTTPStatus.BAD_REQUEST
                    self._send_json(result, status=status)
                    return
                if parsed.path == "/api/claude/optimize":
                    result = run_claude_optimize(self._read_json_body())
                    status = HTTPStatus.OK if result.get("status") in {"ok", "dry_run"} else HTTPStatus.BAD_REQUEST
                    self._send_json(result, status=status)
                    return
                self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
                return
            payload = self._read_json_body()
            if "_json_error" in payload:
                self._send_json({"error": payload["_json_error"]}, status=HTTPStatus.BAD_REQUEST)
                return
            result = run_operator_action(payload)
            if result.get("exit_code") == 0:
                status = HTTPStatus.OK
            elif result.get("exit_code") == 2:
                status = HTTPStatus.BAD_REQUEST
            else:
                status = HTTPStatus.INTERNAL_SERVER_ERROR
            self._send_json(result, status=status)

        def _read_json_body(self) -> dict:
            length = int(self.headers.get("content-length", "0") or "0")
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError as exc:
                return {"_json_error": f"invalid JSON: {exc}"}
            return payload

        def log_message(self, format: str, *args: object) -> None:
            return

        def _send_text(self, text: str, *, content_type: str, status: HTTPStatus = HTTPStatus.OK) -> None:
            body = text.encode("utf-8")
            self.send_response(int(status))
            self.send_header("content-type", content_type)
            self.send_header("content-length", str(len(body)))
            self.send_header("cache-control", "no-store, max-age=0")
            self.send_header("pragma", "no-cache")
            self.send_header("expires", "0")
            self.send_header("x-governed-runtime-ui-stale", "true" if is_operator_ui_process_stale() else "false")
            self.end_headers()
            self.wfile.write(body)

        def _send_json(self, payload: dict, *, status: HTTPStatus = HTTPStatus.OK) -> None:
            self._send_text(
                json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
                content_type="application/json; charset=utf-8",
                status=status,
            )

    return OperatorUiHandler


def operator_ui_source_last_write_epoch() -> float:
    latest = 0.0
    for path in UI_SOURCE_FILES:
        try:
            latest = max(latest, path.stat().st_mtime)
        except FileNotFoundError:
            continue
    return latest


def is_operator_ui_process_stale() -> bool:
    source_last_write = operator_ui_source_last_write_epoch()
    return bool(source_last_write and source_last_write > SERVER_STARTED_AT + 0.5)


def operator_ui_process_status() -> dict:
    source_last_write = operator_ui_source_last_write_epoch()
    stale = is_operator_ui_process_stale()
    restart_state = load_operator_ui_restart_state()
    if not stale and UI_RESTART_REQUEST_PATH.exists():
        try:
            UI_RESTART_REQUEST_PATH.unlink()
        except OSError:
            pass
        restart_state = None
    return {
        "status": "ok",
        "stale": stale,
        "process_started_at": epoch_to_iso(SERVER_STARTED_AT),
        "source_last_write_utc": epoch_to_iso(source_last_write) if source_last_write else None,
        "source_files": [path.relative_to(ROOT).as_posix() for path in UI_SOURCE_FILES],
        "restart_request": restart_state,
    }


def render_stale_service_html(language: str, *, restart_state: dict | None = None) -> str:
    status = operator_ui_process_status()
    command = "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Start -UiLanguage zh-CN -Port 8770"
    if language == "en":
        title = "Operator UI service is stale"
        message = "The running UI process is older than the UI source files, so this page refuses to serve stale content."
        action = "A managed restart has been requested automatically. This page will retry shortly."
        manual = "If it still does not recover, run the managed service entrypoint manually:"
    else:
        title = "Operator UI 服务已过期"
        message = "当前运行中的 UI 进程早于 UI 源文件，本页已拒绝继续展示旧内容。"
        action = "已经自动请求受管重启；本页会稍后自动重试。"
        manual = "若仍未恢复，再手动执行受管服务入口："
    restart_requested_at = ""
    restart_error = ""
    if isinstance(restart_state, dict):
        restart_requested_at = escape(str(restart_state.get("requested_at") or ""))
        restart_error = escape(str(restart_state.get("error") or ""))
    return f"""<!doctype html>
<html lang="{escape(language)}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
  <meta http-equiv="refresh" content="3">
  <style>
    body {{ margin: 0; min-height: 100vh; display: grid; place-items: center; background: #f6f4ef; color: #1f2933; font-family: "Segoe UI", "Microsoft YaHei", sans-serif; }}
    main {{ width: min(760px, calc(100vw - 40px)); background: #fffdfa; border: 1px solid #ded7c8; border-radius: 8px; box-shadow: 0 20px 60px rgba(39, 33, 24, .14); padding: 28px; }}
    h1 {{ margin: 0 0 12px; font-size: 28px; line-height: 1.2; }}
    p {{ margin: 10px 0; line-height: 1.7; }}
    code {{ display: block; overflow-x: auto; margin-top: 14px; padding: 14px; background: #1f2933; color: #f8f3e7; border-radius: 6px; }}
    dl {{ display: grid; grid-template-columns: max-content 1fr; gap: 8px 14px; margin: 18px 0 0; font-size: 14px; }}
    dt {{ color: #6b7280; }}
    dd {{ margin: 0; }}
  </style>
</head>
<body>
  <main>
    <h1>{escape(title)}</h1>
    <p>{escape(message)}</p>
    <p>{escape(action)}</p>
    <p>{escape(manual)}</p>
    <code>{escape(command)}</code>
    <dl>
      <dt>stale</dt><dd>{str(status["stale"]).lower()}</dd>
      <dt>process_started_at</dt><dd>{escape(str(status["process_started_at"]))}</dd>
      <dt>source_last_write_utc</dt><dd>{escape(str(status["source_last_write_utc"]))}</dd>
      <dt>restart_requested_at</dt><dd>{restart_requested_at or '-'}</dd>
      <dt>restart_error</dt><dd>{restart_error or '-'}</dd>
    </dl>
  </main>
</body>
</html>"""


def load_codex_status(*, refresh_online: bool = False, refresh_if_stale: bool = False) -> dict:
    if refresh_online or refresh_if_stale:
        invalidate_status_cache("codex")
        return _load_status_payload(
            "codex",
            lambda: codex_status(refresh_online=refresh_online, refresh_if_stale=refresh_if_stale),
        )
    return _load_status_cached("codex", ttl_seconds=CODEX_STATUS_CACHE_TTL_SECONDS, loader=lambda: codex_status(refresh_online=False))


def load_claude_status() -> dict:
    return _load_status_cached("claude", ttl_seconds=CLAUDE_STATUS_CACHE_TTL_SECONDS, loader=claude_status)


def load_feedback_summary() -> dict:
    payload = _load_status_cached("feedback", ttl_seconds=FEEDBACK_SUMMARY_CACHE_TTL_SECONDS, loader=_build_feedback_summary)
    if payload.get("status") == "ok" and "overall_status" in payload:
        payload["status"] = payload.get("overall_status") or "pass"
    return payload


def _build_feedback_summary() -> dict:
    try:
        payload = build_host_feedback_summary(repo_root=ROOT, max_target_runs=5)
    except Exception as exc:  # pragma: no cover - defensive boundary for localhost UI
        return {"status": "error", "error": str(exc)}
    payload["overall_status"] = payload.get("status") or "pass"
    markdown_path = ROOT / ".runtime" / "artifacts" / "host-feedback-summary" / "latest.md"
    payload["report_path"] = (
        markdown_path.relative_to(ROOT).as_posix() if markdown_path.exists() else None
    )
    payload["guide_path"] = "docs/product/host-feedback-loop.zh-CN.md"
    payload["guide_path_en"] = "docs/product/host-feedback-loop.md"
    return payload


def _load_next_work_module():
    path = ROOT / "scripts" / "select-next-work.py"
    module_name = "select_next_work_script"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load next-work selector: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_next_work_summary() -> dict:
    payload = _load_status_cached("next_work", ttl_seconds=NEXT_WORK_CACHE_TTL_SECONDS, loader=_build_next_work_summary)
    if payload.get("status") == "ok" and "policy_status" in payload:
        payload["status"] = "pass"
    return payload


def _build_next_work_summary() -> dict:
    module = _load_next_work_module()
    payload = module.inspect_next_work_selection(
        repo_root=ROOT,
        policy_path=ROOT / "docs" / "architecture" / "autonomous-next-work-selection-policy.json",
        ltp_policy_path=ROOT / "docs" / "architecture" / "ltp-autonomous-promotion-policy.json",
    )

    next_action = str(payload.get("next_action", "unknown"))
    if next_action == "repair_gate_first":
        blocked_actions = [
            "daily_all",
            "apply_all_features",
            "cleanup_targets",
            "uninstall_governance",
            "evolution_materialize",
        ]
        ui_status = "action_required"
    elif next_action == "refresh_evidence_first":
        blocked_actions = ["apply_all_features", "evolution_materialize"]
        ui_status = "action_required"
    elif next_action == "wait_for_host_capability_recovery":
        blocked_actions = ["apply_all_features", "evolution_materialize"]
        ui_status = "attention"
    elif next_action == "owner_directed_scope_required":
        blocked_actions = ["apply_all_features", "evolution_materialize"]
        ui_status = "action_required"
    elif next_action == "promote_ltp":
        blocked_actions = []
        ui_status = "attention"
    else:
        blocked_actions = []
        ui_status = "healthy"

    payload["status"] = payload.get("status") or "pass"
    payload["ui_status"] = ui_status
    payload["safe_next_action"] = next_action
    payload["blocked_actions"] = blocked_actions
    return payload


def inject_next_work_panel(html: str, *, language: str) -> str:
    marker = "<!-- NEXT_WORK_PANEL -->"
    if marker not in html:
        return html
    panel = render_next_work_panel(language=language)
    return html.replace(marker, panel, 1)


def render_next_work_panel(*, language: str) -> str:
    is_zh = not language.lower().startswith("en")
    title = "下一步选择" if is_zh else "Next Work Selector"
    caption = "把当前建议、阻断和推荐动作放在执行输出下面，便于直接决定下一步。" if is_zh else "Keep the current recommendation, blockers, and suggested action directly under the output panel."
    summary = "加载中" if is_zh else "Loading"
    recommendation = "AI 推荐: 正在刷新" if is_zh else "AI recommended: refreshing"
    state_line = "状态: loading" if is_zh else "Status: loading"
    reason = ""
    escape_json = escape(json.dumps({"status": "loading"}, ensure_ascii=False, indent=2, sort_keys=True))
    return "\n".join(
        [
            "<section class='panel section' id='next-work-panel'>",
            f"<h2>{title}</h2>",
            f"<p class='meta'>{caption}</p>",
            "<div class='policy-grid'>",
            f"<div class='policy-card'><strong>{'动作' if is_zh else 'Action'}</strong><span id='next-work-action'>{summary}</span></div>",
            f"<div class='policy-card'><strong>{'建议' if is_zh else 'Recommendation'}</strong><span id='next-work-recommendation'>{recommendation}</span></div>",
            f"<div class='policy-card'><strong>{'判定' if is_zh else 'State'}</strong><span id='next-work-state'>{state_line}</span></div>",
            "</div>",
            f"<p class='meta' id='next-work-why'>{reason}</p>" if reason else "<p class='meta' id='next-work-why'></p>",
            "<div id='next-work-cache-state' class='status-line'></div>",
            f"<button type='button' data-next-work-refresh='1'>{'刷新 next-work' if is_zh else 'Refresh next-work'}</button>",
            f"<details><summary>{'查看 selector JSON' if is_zh else 'View selector JSON'}</summary><pre id='next-work-json' class='output'>{escape_json}</pre></details>",
            "</section>",
        ]
    )


def run_codex_switch(payload: dict) -> dict:
    if "_json_error" in payload:
        return {"status": "error", "error": payload["_json_error"]}
    name = _string(payload.get("name"), "")
    dry_run = bool(payload.get("dry_run", False))
    try:
        result = switch_auth_profile(name, dry_run=dry_run)
    except Exception as exc:  # pragma: no cover - defensive boundary for localhost UI
        return {"status": "error", "error": str(exc)}
    if result.get("status") == "ok" and result.get("changed"):
        invalidate_status_cache("codex")
    return result


def run_codex_sync_active(payload: dict) -> dict:
    if "_json_error" in payload:
        return {"status": "error", "error": payload["_json_error"]}
    name = _string(payload.get("name"), "") or None
    dry_run = bool(payload.get("dry_run", False))
    try:
        result = sync_active_auth_snapshot(target_name=name, dry_run=dry_run)
    except Exception as exc:  # pragma: no cover - defensive boundary for localhost UI
        return {"status": "error", "error": str(exc)}
    if result.get("status") == "ok" and result.get("changed"):
        invalidate_status_cache("codex")
    return result


def run_codex_delete(payload: dict) -> dict:
    if "_json_error" in payload:
        return {"status": "error", "error": payload["_json_error"]}
    name = _string(payload.get("name"), "")
    dry_run = bool(payload.get("dry_run", False))
    try:
        result = delete_auth_profile(name, dry_run=dry_run)
    except Exception as exc:  # pragma: no cover - defensive boundary for localhost UI
        return {"status": "error", "error": str(exc)}
    if result.get("status") == "ok" and result.get("changed"):
        invalidate_status_cache("codex")
    return result


def run_claude_switch(payload: dict) -> dict:
    if "_json_error" in payload:
        return {"status": "error", "error": payload["_json_error"]}
    name = _string(payload.get("name"), "")
    dry_run = bool(payload.get("dry_run", False))
    try:
        result = switch_provider(name, dry_run=dry_run)
    except Exception as exc:  # pragma: no cover - defensive boundary for localhost UI
        return {"status": "error", "error": str(exc)}
    if result.get("status") == "ok" and result.get("changed"):
        invalidate_status_cache("claude")
    return result


def run_claude_optimize(payload: dict) -> dict:
    if "_json_error" in payload:
        return {"status": "error", "error": payload["_json_error"]}
    provider = _string(payload.get("provider"), "bigmodel-glm") or "bigmodel-glm"
    apply = bool(payload.get("apply", False))
    try:
        result = optimize_claude_local(provider_name=provider, apply=apply)
    except Exception as exc:  # pragma: no cover - defensive boundary for localhost UI
        return {"status": "error", "error": str(exc)}
    invalidate_status_cache("claude")
    return result


def invalidate_status_cache(kind: str | None = None) -> None:
    with _STATUS_CACHE_LOCK:
        if kind is None:
            _STATUS_CACHE.clear()
            return
        _STATUS_CACHE.pop(kind, None)


def _load_status_cached(kind: str, *, ttl_seconds: float, loader) -> dict:
    now = time.time()
    with _STATUS_CACHE_LOCK:
        cached = _STATUS_CACHE.get(kind)
        if cached and now - float(cached.get("loaded_at", 0.0)) <= ttl_seconds:
            return dict(cached["payload"])
    payload = _load_status_payload(kind, loader)
    with _STATUS_CACHE_LOCK:
        _STATUS_CACHE[kind] = {"loaded_at": now, "payload": dict(payload)}
    return payload


def _load_status_payload(kind: str, loader) -> dict:
    try:
        payload = loader()
    except Exception as exc:  # pragma: no cover - defensive boundary for localhost UI
        return {"status": "error", "error": str(exc), "cache_kind": kind}
    payload["status"] = "ok"
    payload["cache_kind"] = kind
    payload["cached_at"] = datetime_now_iso()
    return payload


def datetime_now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def epoch_to_iso(epoch_seconds: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(epoch_seconds))


def load_operator_ui_restart_state() -> dict | None:
    if not UI_RESTART_REQUEST_PATH.exists():
        return None
    try:
        payload = json.loads(UI_RESTART_REQUEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def save_operator_ui_restart_state(payload: dict) -> None:
    try:
        UI_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
        UI_RESTART_REQUEST_PATH.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    except OSError:
        return


def maybe_request_operator_ui_restart(*, language: str, host: str, port: int) -> dict:
    now = time.time()
    state = load_operator_ui_restart_state() or {}
    requested_epoch = float(state.get("requested_epoch", 0.0) or 0.0)
    if requested_epoch and now - requested_epoch < UI_RESTART_COOLDOWN_SECONDS:
        return dict(state)

    payload = {
        "requested": False,
        "requested_at": datetime_now_iso(),
        "requested_epoch": now,
        "host": host,
        "port": port,
        "language": language,
    }
    pwsh = shutil.which("pwsh")
    if not pwsh:
        payload["error"] = "pwsh not found"
        save_operator_ui_restart_state(payload)
        return payload

    command = [
        pwsh,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(ROOT / "scripts" / "operator-ui-service.ps1"),
        "-Action",
        "Restart",
        "-UiLanguage",
        language,
        "-HostAddress",
        host,
        "-Port",
        str(port),
    ]
    try:
        subprocess.Popen(
            command,
            cwd=str(ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except OSError as exc:
        payload["error"] = str(exc)
        save_operator_ui_restart_state(payload)
        return payload

    payload["requested"] = True
    payload["command"] = command
    save_operator_ui_restart_state(payload)
    return payload


def run_operator_action(payload: dict) -> dict:
    action_id = _string(payload.get("action"), "")
    action = ALLOWED_ACTIONS.get(action_id)
    if action is None:
        return {"action": action_id, "exit_code": 2, "elapsed_seconds": 0, "output": "unsupported action"}

    language = _normalize_language(_string(payload.get("language"), "zh-CN"))
    mode = _choice(_string(payload.get("mode"), "quick"), {"quick", "full", "l1", "l2", "l3"}, "quick")
    known_targets = set(load_target_ids())
    target_values, target_error = _target_values_from_payload(payload, known_targets=known_targets)
    if target_error:
        return {"action": action_id, "exit_code": 2, "elapsed_seconds": 0, "output": target_error}
    if len(target_values) > 1 and not action.get("allow_multi_target"):
        return {
            "action": action_id,
            "exit_code": 2,
            "elapsed_seconds": 0,
            "output": f"multiple targets are not supported for action: {action_id}",
            "targets": target_values,
        }
    target_parallelism = _int_range(payload.get("target_parallelism"), minimum=1, maximum=16, default=1)
    milestone_tag = _string(payload.get("milestone_tag"), "milestone") or "milestone"
    fail_fast = bool(payload.get("fail_fast", False))
    dry_run = bool(payload.get("dry_run", False))
    apply_managed_asset_removal = bool(
        payload.get("apply_managed_asset_removal", bool(action.get("managed_asset_removal_default", False)))
    ) and not dry_run

    started = time.monotonic()
    per_target: list[dict] = []
    for target_value in target_values:
        command = _build_operator_command(
            action=action,
            language=language,
            target=target_value,
            mode=mode,
            target_parallelism=target_parallelism,
            milestone_tag=milestone_tag,
            fail_fast=fail_fast,
            dry_run=dry_run,
            apply_managed_asset_removal=apply_managed_asset_removal,
        )
        result = _run_operator_command(command, timeout_seconds=int(action["timeout_seconds"]))
        result["target"] = target_value
        per_target.append(result)
        if target_value == "__all__" or (fail_fast and int(result["exit_code"]) != 0):
            break

    elapsed = round(time.monotonic() - started, 3)
    exit_codes = [int(item["exit_code"]) for item in per_target]
    exit_code = next((code for code in exit_codes if code != 0), 0)
    if len(per_target) == 1:
        single = per_target[0]
        return {
            "action": action_id,
            "command": single["command"],
            "elapsed_seconds": elapsed,
            "exit_code": exit_code,
            "output": single["output"],
            "target": single["target"],
            "targets": target_values,
            "apply_managed_asset_removal": apply_managed_asset_removal,
        }
    output = "\n\n".join(
        "\n".join(
            [
                f"===== target: {item['target']} =====",
                f"command: {_command_for_display(item['command'])}",
                f"exit_code: {item['exit_code']}",
                f"elapsed_seconds: {item['elapsed_seconds']}",
                "",
                str(item["output"]),
            ]
        )
        for item in per_target
    )
    return {
        "action": action_id,
        "commands": [item["command"] for item in per_target],
        "elapsed_seconds": elapsed,
        "exit_code": exit_code,
        "output": output,
        "targets": [item["target"] for item in per_target],
        "apply_managed_asset_removal": apply_managed_asset_removal,
    }


def _target_values_from_payload(payload: dict, *, known_targets: set[str]) -> tuple[list[str], str | None]:
    raw_targets = payload.get("targets")
    values: list[str] = []
    if isinstance(raw_targets, list):
        values = [str(item).strip() for item in raw_targets if str(item).strip()]
    elif isinstance(raw_targets, str) and raw_targets.strip():
        values = [part.strip() for part in raw_targets.split(",") if part.strip()]
    else:
        values = [_string(payload.get("target"), "__all__") or "__all__"]

    normalized: list[str] = []
    for value in values:
        if value in {"__all__", "all", "*"}:
            return ["__all__"], None
        if known_targets and value not in known_targets:
            return [], f"unsupported target: {value}"
        if value not in normalized:
            normalized.append(value)
    if not normalized:
        return [], "no target selected"
    return normalized, None


def _build_operator_command(
    *,
    action: dict,
    language: str,
    target: str,
    mode: str,
    target_parallelism: int,
    milestone_tag: str,
    fail_fast: bool,
    dry_run: bool,
    apply_managed_asset_removal: bool,
) -> list[str]:
    command = [
        "pwsh",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(ROOT / "run.ps1"),
        action.get("run_alias") or action["operator_action"],
        "-UiLanguage",
        language,
        "-Target",
        target,
        "-Mode",
        mode,
        "-TargetParallelism",
        str(target_parallelism),
        "-MilestoneTag",
        milestone_tag,
    ]
    if fail_fast:
        command.append("-FailFast")
    if dry_run and not action.get("managed_asset_removal"):
        command.append("-DryRun")
    if apply_managed_asset_removal and (
        action.get("managed_asset_removal") or action.get("managed_asset_removal_apply")
    ):
        command.append("-ApplyManagedAssetRemoval")
    return command


def _run_operator_command(command: list[str], *, timeout_seconds: int) -> dict:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
        )
        output = "\n".join(segment for segment in [completed.stdout.rstrip(), completed.stderr.rstrip()] if segment)
        exit_code = completed.returncode
    except subprocess.TimeoutExpired as exc:
        output = "\n".join(segment for segment in [exc.stdout or "", exc.stderr or "", f"timed out after {timeout_seconds}s"] if segment)
        exit_code = 124
    except OSError as exc:
        output = str(exc)
        exit_code = 127
    return {
        "command": command,
        "elapsed_seconds": round(time.monotonic() - started, 3),
        "exit_code": exit_code,
        "output": output,
    }


def _command_for_display(command: list[str]) -> str:
    return " ".join(f'"{part}"' if any(ch.isspace() for ch in part) else part for part in command)


def read_repo_file(requested: str) -> dict:
    if not requested.strip():
        return {"error": "path is required"}
    root = ROOT.resolve()
    path = (root / requested).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return {"error": "path escapes repository root"}
    if not path.exists() or not path.is_file():
        return {"path": requested, "error": "file not found"}
    try:
        return {
            "path": path.relative_to(root).as_posix(),
            "content": path.read_text(encoding="utf-8", errors="replace"),
        }
    except OSError as exc:
        return {"path": requested, "error": str(exc)}


def read_claude_local_file(kind: str) -> dict:
    normalized = _string(kind, "")
    home = claude_home()
    path_map = {
        "settings": settings_path(home),
        "profiles": provider_profiles_path(home),
        "switcher": home / "scripts" / "Switch-ClaudeProvider.ps1",
    }
    path = path_map.get(normalized)
    if path is None:
        return {"error": f"unsupported Claude local file kind: {normalized}"}
    if not path.exists() or not path.is_file():
        return {"error": f"file not found: {path}"}
    try:
        return {"path": str(path), "content": path.read_text(encoding="utf-8", errors="replace")}
    except OSError as exc:
        return {"path": str(path), "error": str(exc)}


def load_target_ids() -> list[str]:
    catalog_path = ROOT / "docs" / "targets" / "target-repos-catalog.json"
    try:
        payload = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    targets = payload.get("targets", {})
    if not isinstance(targets, dict):
        return []
    return sorted(str(name) for name in targets.keys())


def _normalize_language(value: str) -> str:
    return "en" if value.lower().startswith("en") else "zh-CN"


def _choice(value: str, allowed: set[str], default: str) -> str:
    return value if value in allowed else default


def _int_range(value: object, *, minimum: int, maximum: int, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, parsed))


def _string(value: object, default: str) -> str:
    if isinstance(value, str):
        return value.strip()
    return default


def _truthy(value: object) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


if __name__ == "__main__":
    raise SystemExit(main())
