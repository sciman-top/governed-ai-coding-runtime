from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
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

from governed_ai_coding_runtime_contracts.operator_ui import render_runtime_snapshot_html, write_runtime_snapshot_html
from governed_ai_coding_runtime_contracts.runtime_status import RuntimeStatusStore, runtime_snapshot_to_dict
from lib.claude_local import claude_status, switch_provider
from lib.codex_local import codex_status, switch_auth_profile


ALLOWED_ACTIONS = {
    "targets": {"operator_action": "Targets", "timeout_seconds": 300},
    "readiness": {"operator_action": "Readiness", "timeout_seconds": 1800},
    "rules_dry_run": {"operator_action": "RulesDryRun", "timeout_seconds": 600},
    "rules_apply": {"operator_action": "RulesApply", "timeout_seconds": 900},
    "governance_baseline_all": {"operator_action": "GovernanceBaselineAll", "timeout_seconds": 1800},
    "daily_all": {"operator_action": "DailyAll", "timeout_seconds": 1800},
    "apply_all_features": {"operator_action": "ApplyAllFeatures", "timeout_seconds": 2400},
}

CODEX_STATUS_CACHE_TTL_SECONDS = 10.0
CLAUDE_STATUS_CACHE_TTL_SECONDS = 15.0
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
    written = write_runtime_snapshot_html(snapshot, output, language=args.lang, target_options=load_target_ids())
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
                snapshot = RuntimeStatusStore(ROOT / ".runtime" / "tasks", ROOT).snapshot()
                html = render_runtime_snapshot_html(snapshot, language=language, interactive=True, target_options=load_target_ids())
                self._send_text(html, content_type="text/html; charset=utf-8")
                return
            if parsed.path == "/api/status":
                snapshot = RuntimeStatusStore(ROOT / ".runtime" / "tasks", ROOT).snapshot()
                self._send_json(runtime_snapshot_to_dict(snapshot))
                return
            if parsed.path == "/api/targets":
                self._send_json({"targets": load_target_ids()})
                return
            if parsed.path == "/api/codex/status":
                result = load_codex_status()
                status = HTTPStatus.OK if result.get("status") == "ok" else HTTPStatus.INTERNAL_SERVER_ERROR
                self._send_json(result, status=status)
                return
            if parsed.path == "/api/claude/status":
                result = load_claude_status()
                status = HTTPStatus.OK if result.get("status") == "ok" else HTTPStatus.INTERNAL_SERVER_ERROR
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
            self.end_headers()
            self.wfile.write(body)

        def _send_json(self, payload: dict, *, status: HTTPStatus = HTTPStatus.OK) -> None:
            self._send_text(
                json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
                content_type="application/json; charset=utf-8",
                status=status,
            )

    return OperatorUiHandler


def load_codex_status(*, refresh_online: bool = False) -> dict:
    if refresh_online:
        invalidate_status_cache("codex")
        return _load_status_payload("codex", lambda: codex_status(refresh_online=True))
    return _load_status_cached("codex", ttl_seconds=CODEX_STATUS_CACHE_TTL_SECONDS, loader=lambda: codex_status(refresh_online=False))


def load_claude_status() -> dict:
    return _load_status_cached("claude", ttl_seconds=CLAUDE_STATUS_CACHE_TTL_SECONDS, loader=claude_status)


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


def run_operator_action(payload: dict) -> dict:
    action_id = _string(payload.get("action"), "")
    action = ALLOWED_ACTIONS.get(action_id)
    if action is None:
        return {"action": action_id, "exit_code": 2, "elapsed_seconds": 0, "output": "unsupported action"}

    language = _normalize_language(_string(payload.get("language"), "zh-CN"))
    mode = _choice(_string(payload.get("mode"), "quick"), {"quick", "full", "l1", "l2", "l3"}, "quick")
    target = _string(payload.get("target"), "__all__") or "__all__"
    known_targets = set(load_target_ids())
    if target not in {"__all__", "all", "*"} and known_targets and target not in known_targets:
        return {"action": action_id, "exit_code": 2, "elapsed_seconds": 0, "output": f"unsupported target: {target}"}
    target_parallelism = _int_range(payload.get("target_parallelism"), minimum=1, maximum=16, default=1)
    milestone_tag = _string(payload.get("milestone_tag"), "milestone") or "milestone"
    fail_fast = bool(payload.get("fail_fast", False))
    dry_run = bool(payload.get("dry_run", False))

    command = [
        "pwsh",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(ROOT / "scripts" / "operator.ps1"),
        "-Action",
        action["operator_action"],
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
    if dry_run:
        command.append("-DryRun")

    started = time.monotonic()
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=action["timeout_seconds"],
        )
        output = "\n".join(segment for segment in [completed.stdout.rstrip(), completed.stderr.rstrip()] if segment)
        exit_code = completed.returncode
    except subprocess.TimeoutExpired as exc:
        output = "\n".join(segment for segment in [exc.stdout or "", exc.stderr or "", f"timed out after {action['timeout_seconds']}s"] if segment)
        exit_code = 124
    except OSError as exc:
        output = str(exc)
        exit_code = 127
    elapsed = round(time.monotonic() - started, 3)
    return {
        "action": action_id,
        "command": command,
        "elapsed_seconds": elapsed,
        "exit_code": exit_code,
        "output": output,
    }


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


if __name__ == "__main__":
    raise SystemExit(main())
