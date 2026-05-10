#!/usr/bin/env python3
"""Trace Cockpit Tools Codex account switching side effects.

The script is intentionally read-only unless --out is supplied. It snapshots the
Cockpit state files, Codex config/auth files, Codex history buckets, and recent
Cockpit switch log lines. In watch mode, run it first, switch in Cockpit Tools,
then inspect the before/after summary to see exactly which actor changed what.
"""

from __future__ import annotations

import argparse
import copy
import datetime as _dt
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from contextlib import closing
from pathlib import Path
from typing import Any


SECRET_KEY_RE = re.compile(
    r"(api[_-]?key|access[_-]?token|refresh[_-]?token|id[_-]?token|secret|password|authorization|bearer)",
    re.IGNORECASE,
)
IMPORTANT_LOG_RE = re.compile(
    r"(\[Codex切号\]|\[AG Close\]|\[Codex Start\]|Codex Auth|默认实例绑定账号|自动重启指定应用|taskkill|OPENAI_API_KEY)",
    re.IGNORECASE,
)


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def default_cockpit_home() -> Path:
    return Path.home() / ".antigravity_cockpit"


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_meta(path: Path) -> dict[str, Any]:
    try:
        stat = path.stat()
    except FileNotFoundError:
        return {"exists": False}
    return {
        "exists": True,
        "size": stat.st_size,
        "mtime": stat.st_mtime,
        "mtime_iso": _dt.datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
        "sha256": sha256_file(path),
    }


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except Exception as exc:  # pragma: no cover - diagnostic path
        return {"_read_error": f"{type(exc).__name__}: {exc}"}


def read_text(path: Path, max_chars: int = 300_000) -> str | None:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return None
    return text[:max_chars]


def redact(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for key, child in value.items():
            if SECRET_KEY_RE.search(str(key)):
                out[key] = "<redacted>" if child not in (None, "", []) else child
            else:
                out[key] = redact(child)
        return out
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, str):
        if value.startswith(("sk-", "sess-", "eyJ")) or len(value) > 120:
            return "<redacted>"
    return value


def compact_toml_values(text: str | None) -> dict[str, Any]:
    if text is None:
        return {"exists": False}
    keys = [
        "model_provider",
        "openai_base_url",
        "forced_login_method",
        "approval_policy",
        "sandbox_mode",
        "project_doc_max_bytes",
    ]
    result: dict[str, Any] = {"exists": True}
    for line in text.splitlines():
        if re.match(r"\s*\[.+\]\s*$", line):
            break
        for key in keys:
            match = re.match(rf"\s*{re.escape(key)}\s*=\s*(.+?)\s*$", line)
            if match:
                result[key] = match.group(1).strip().strip('"')
    provider_blocks: dict[str, dict[str, Any]] = {}
    current_provider: str | None = None
    for line in text.splitlines():
        provider_match = re.match(r'\s*\[model_providers\."?([^"\]]+)"?\]\s*$', line)
        if provider_match:
            current_provider = provider_match.group(1)
            provider_blocks.setdefault(current_provider, {})
            continue
        section_match = re.match(r"\s*\[.+\]\s*$", line)
        if section_match:
            current_provider = None
            continue
        if current_provider and "=" in line:
            key, raw = line.split("=", 1)
            key = key.strip()
            if key in {"name", "base_url", "wire_api", "env_key"}:
                provider_blocks[current_provider][key] = raw.strip().strip('"')
    if provider_blocks:
        result["model_providers"] = provider_blocks
    return result


def summarize_auth(auth: Any) -> dict[str, Any]:
    if not isinstance(auth, dict):
        return {"exists": auth is not None, "shape": type(auth).__name__}
    return {
        "auth_mode": auth.get("auth_mode") or auth.get("mode"),
        "has_openai_api_key": bool(auth.get("OPENAI_API_KEY") or auth.get("openai_api_key")),
        "has_tokens": bool(auth.get("tokens") or auth.get("access_token") or auth.get("refresh_token")),
        "base_url": auth.get("base_url") or auth.get("api_base_url") or auth.get("OPENAI_BASE_URL"),
        "provider": auth.get("provider") or auth.get("api_provider"),
        "keys": sorted(auth.keys()),
    }


def summarize_cockpit(cockpit_home: Path) -> dict[str, Any]:
    config = read_json(cockpit_home / "config.json")
    accounts = read_json(cockpit_home / "codex_accounts.json")
    instances = read_json(cockpit_home / "codex_instances.json")
    providers = read_json(cockpit_home / "codex_model_providers.json")

    current_account_id = None
    if isinstance(accounts, dict):
        current_account_id = (
            accounts.get("current")
            or accounts.get("currentAccountId")
            or accounts.get("current_account_id")
            or accounts.get("activeAccountId")
        )
    account_detail = read_json(cockpit_home / "codex_accounts" / f"{current_account_id}.json") if current_account_id else None

    launch_flags: dict[str, Any] = {}
    if isinstance(config, dict):
        for key in [
            "codex_launch_on_switch",
            "codex_restart_specified_app_on_switch",
            "codex_specified_app_path",
            "codex_app_launch_mode",
        ]:
            if key in config:
                launch_flags[key] = config.get(key)

    default_instance: Any = None
    if isinstance(instances, dict):
        default_instance = (
            instances.get("defaultSettings")
            or instances.get("default")
            or instances.get("default_settings")
            or instances
        )

    provider_summary: dict[str, Any] = {}
    if isinstance(providers, dict):
        raw_providers = providers.get("providers") if isinstance(providers.get("providers"), dict) else providers
        for key, value in raw_providers.items():
            if isinstance(value, dict):
                provider_summary[str(key)] = {
                    "name": value.get("name"),
                    "base_url": value.get("base_url") or value.get("baseUrl") or value.get("apiBaseUrl"),
                    "wire_api": value.get("wire_api") or value.get("wireApi"),
                }

    return redact(
        {
            "current_account_id": current_account_id,
            "current_account": account_detail,
            "launch_flags": launch_flags,
            "default_instance": default_instance,
            "model_providers": provider_summary,
        }
    )


def summarize_state_db(state_db: Path) -> dict[str, Any]:
    if not state_db.exists():
        return {"exists": False}
    try:
        uri = f"file:{state_db.as_posix()}?mode=ro&immutable=1"
        with closing(sqlite3.connect(uri, uri=True)) as conn:
            conn.row_factory = sqlite3.Row
            tables = {
                row[0]
                for row in conn.execute("select name from sqlite_master where type='table'")
            }
            summary: dict[str, Any] = {"exists": True, "tables": sorted(tables)}
            if "threads" in tables:
                columns = {row[1] for row in conn.execute("pragma table_info(threads)")}
                if "model_provider" in columns:
                    summary["threads_by_model_provider"] = [
                        dict(row)
                        for row in conn.execute(
                            "select coalesce(model_provider, '<null>') as model_provider, count(*) as count "
                            "from threads group by coalesce(model_provider, '<null>') order by count desc"
                        )
                    ]
                if "cwd" in columns:
                    summary["threads_by_cwd_top"] = [
                        dict(row)
                        for row in conn.execute(
                            "select coalesce(cwd, '<null>') as cwd, count(*) as count "
                            "from threads group by coalesce(cwd, '<null>') order by count desc limit 8"
                        )
                    ]
            return summary
    except Exception as exc:  # pragma: no cover - diagnostic path
        return {"exists": True, "read_error": f"{type(exc).__name__}: {exc}"}


def recent_cockpit_events(cockpit_home: Path, max_lines: int = 80) -> list[str]:
    logs_dir = cockpit_home / "logs"
    if not logs_dir.exists():
        return []
    candidates = sorted(logs_dir.glob("app.log*"), key=lambda p: p.stat().st_mtime if p.exists() else 0)
    events: list[str] = []
    for path in candidates[-4:]:
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for line in lines:
            if IMPORTANT_LOG_RE.search(line):
                events.append(f"{path.name}: {line}")
    return events[-max_lines:]


def process_snapshot() -> list[dict[str, Any]]:
    if os.name != "nt":
        return []
    script = (
        "Get-Process | Where-Object { $_.ProcessName -match 'codex|cockpit' } | "
        "Select-Object Id,ProcessName,StartTime,Path | ConvertTo-Json -Compress"
    )
    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )
    except Exception:
        return []
    if completed.returncode != 0 or not completed.stdout.strip():
        return []
    try:
        parsed = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return []
    if isinstance(parsed, dict):
        return [redact(parsed)]
    if isinstance(parsed, list):
        return redact(parsed)
    return []


def guard_status_snapshot() -> dict[str, Any]:
    if os.name != "nt":
        return {"platform": os.name, "available": False}
    script = r"""
$task = Get-ScheduledTask -TaskName codex-cockpit-switch-guard -ErrorAction SilentlyContinue
$processes = @(
  Get-CimInstance Win32_Process |
    Where-Object {
      $_.CommandLine -and
      $_.CommandLine.Contains('codex-cockpit-switch-guard.py') -and
      $_.Name -match '^(python|python3)(\.exe)?$'
    } |
    Select-Object ProcessId,Name,CreationDate
)
[pscustomobject]@{
  task_state = if ($task) { [string]$task.State } else { 'not_installed' }
  healthy = $processes.Count -gt 0
  process_count = $processes.Count
  process_ids = @($processes | ForEach-Object { $_.ProcessId })
} | ConvertTo-Json -Compress
"""
    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", script],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=10,
        )
    except Exception as exc:
        return {"platform": os.name, "available": False, "error": f"{type(exc).__name__}: {exc}"}
    if completed.returncode != 0 or not completed.stdout.strip():
        return {
            "platform": os.name,
            "available": False,
            "exit_code": completed.returncode,
            "stderr": completed.stderr[-1000:],
        }
    try:
        parsed = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"platform": os.name, "available": False, "stdout": completed.stdout[-1000:]}
    if isinstance(parsed, dict):
        return redact(parsed)
    return {"platform": os.name, "available": False, "shape": type(parsed).__name__}


def snapshot(codex_home: Path, cockpit_home: Path) -> dict[str, Any]:
    tracked_files = {
        "cockpit_config": cockpit_home / "config.json",
        "cockpit_accounts": cockpit_home / "codex_accounts.json",
        "cockpit_instances": cockpit_home / "codex_instances.json",
        "cockpit_model_providers": cockpit_home / "codex_model_providers.json",
        "codex_config": codex_home / "config.toml",
        "codex_auth": codex_home / "auth.json",
        "codex_cockpit_auth_projection": codex_home / ".cockpit_codex_auth.json",
        "codex_state_db": codex_home / "state_5.sqlite",
    }
    return {
        "timestamp": _dt.datetime.now().isoformat(timespec="seconds"),
        "paths": {
            "codex_home": str(codex_home),
            "cockpit_home": str(cockpit_home),
        },
        "files": {name: {"path": str(path), **file_meta(path)} for name, path in tracked_files.items()},
        "cockpit": summarize_cockpit(cockpit_home),
        "codex": {
            "config": compact_toml_values(read_text(codex_home / "config.toml")),
            "auth": summarize_auth(read_json(codex_home / "auth.json")),
            "cockpit_auth_projection": redact(read_json(codex_home / ".cockpit_codex_auth.json")),
            "state_db": summarize_state_db(codex_home / "state_5.sqlite"),
        },
        "processes": process_snapshot(),
        "guard_status": guard_status_snapshot(),
        "recent_cockpit_events": recent_cockpit_events(cockpit_home),
    }


def classify_changes(before: dict[str, Any], after: dict[str, Any]) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []
    before_files = before.get("files", {})
    after_files = after.get("files", {})
    for name, meta_after in after_files.items():
        meta_before = before_files.get(name, {})
        if meta_before.get("sha256") != meta_after.get("sha256") or meta_before.get("mtime") != meta_after.get("mtime"):
            changes.append(
                {
                    "file": name,
                    "path": meta_after.get("path"),
                    "before": {
                        "exists": meta_before.get("exists"),
                        "mtime_iso": meta_before.get("mtime_iso"),
                        "sha256": meta_before.get("sha256"),
                    },
                    "after": {
                        "exists": meta_after.get("exists"),
                        "mtime_iso": meta_after.get("mtime_iso"),
                        "sha256": meta_after.get("sha256"),
                    },
                }
            )
    return changes


def _load_report(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _get_path(payload: dict[str, Any], path: str) -> Any:
    value: Any = payload
    for part in path.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def _history_distribution(snapshot_payload: dict[str, Any]) -> str:
    rows = _get_path(snapshot_payload, "codex.state_db.threads_by_model_provider")
    if not isinstance(rows, list):
        return ""
    parts: list[str] = []
    for row in rows:
        if isinstance(row, dict):
            parts.append(f"{row.get('model_provider')}:{row.get('count')}")
    return ",".join(parts)


COMPARE_FIELDS = {
    "guard.healthy": "guard_status.healthy",
    "guard.process_count": "guard_status.process_count",
    "guard.task_state": "guard_status.task_state",
    "cockpit.current_account_id": "cockpit.current_account_id",
    "cockpit.codex_launch_on_switch": "cockpit.launch_flags.codex_launch_on_switch",
    "cockpit.codex_restart_specified_app_on_switch": "cockpit.launch_flags.codex_restart_specified_app_on_switch",
    "cockpit.codex_specified_app_path": "cockpit.launch_flags.codex_specified_app_path",
    "cockpit.default.bindAccountId": "cockpit.default_instance.bindAccountId",
    "cockpit.default.followLocalAccount": "cockpit.default_instance.followLocalAccount",
    "cockpit.default.lastPid": "cockpit.default_instance.lastPid",
    "codex.config.model_provider": "codex.config.model_provider",
    "codex.config.openai_base_url": "codex.config.openai_base_url",
    "codex.config.forced_login_method": "codex.config.forced_login_method",
    "codex.auth.auth_mode": "codex.auth.auth_mode",
    "codex.auth.has_openai_api_key": "codex.auth.has_openai_api_key",
    "codex.auth.has_tokens": "codex.auth.has_tokens",
    "codex.auth.base_url": "codex.auth.base_url",
    "codex.auth.provider": "codex.auth.provider",
}


def summarize_report(report: dict[str, Any], path: Path | None = None) -> dict[str, Any]:
    after = report.get("after", {})
    summary = {
        "path": str(path) if path else None,
        "label": report.get("label"),
        "timestamp": after.get("timestamp"),
        "history_threads_by_provider": _history_distribution(after),
        "changed_files_within_watch": [item.get("file") for item in report.get("changed_files", [])],
    }
    for name, source_path in COMPARE_FIELDS.items():
        summary[name] = _get_path(after, source_path)
    return summary


def compare_reports(paths: list[Path]) -> dict[str, Any]:
    reports = [_load_report(path) for path in paths]
    summaries = [summarize_report(report, path) for report, path in zip(reports, paths)]
    transitions: list[dict[str, Any]] = []
    for index in range(1, len(summaries)):
        before = summaries[index - 1]
        after = summaries[index]
        field_changes = []
        for key in [*COMPARE_FIELDS.keys(), "history_threads_by_provider"]:
            if before.get(key) != after.get(key):
                field_changes.append({"field": key, "before": before.get(key), "after": after.get(key)})

        before_files = reports[index - 1].get("after", {}).get("files", {})
        after_files = reports[index].get("after", {}).get("files", {})
        file_changes = []
        for name, file_after in after_files.items():
            file_before = before_files.get(name, {})
            if file_before.get("sha256") != file_after.get("sha256"):
                file_changes.append(
                    {
                        "file": name,
                        "before_mtime": file_before.get("mtime_iso"),
                        "after_mtime": file_after.get("mtime_iso"),
                        "before_sha256": file_before.get("sha256"),
                        "after_sha256": file_after.get("sha256"),
                    }
                )

        transitions.append(
            {
                "from": before.get("path"),
                "to": after.get("path"),
                "from_label": before.get("label"),
                "to_label": after.get("label"),
                "field_changes": field_changes,
                "file_changes": file_changes,
            }
        )

    return {
        "schema_version": 1,
        "record_count": len(paths),
        "records": summaries,
        "transitions": transitions,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Trace Cockpit Tools <-> Codex App/CLI switching side effects.")
    parser.add_argument("--codex-home", type=Path, default=default_codex_home())
    parser.add_argument("--cockpit-home", type=Path, default=default_cockpit_home())
    parser.add_argument("--watch-seconds", type=float, default=0.0, help="Poll tracked files for this many seconds.")
    parser.add_argument("--poll-interval", type=float, default=0.5)
    parser.add_argument("--label", help="Human-readable label for this record, for example before-restart.")
    parser.add_argument("--out", type=Path, help="Write JSON report to this path.")
    parser.add_argument("--compare", type=Path, nargs="+", help="Compare two or more saved record JSON files.")
    parser.add_argument("--json", action="store_true", help="Emit JSON to stdout.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.compare:
        if len(args.compare) < 2:
            raise SystemExit("--compare requires at least two record JSON files")
        report = compare_reports(args.compare)
        text = json.dumps(report, ensure_ascii=False, indent=2)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(text + "\n", encoding="utf-8")
        if args.json or not args.out:
            print(text)
        return 0

    before = snapshot(args.codex_home, args.cockpit_home)
    events: list[dict[str, Any]] = []
    last_files = copy.deepcopy(before["files"])

    if args.watch_seconds > 0:
        deadline = time.time() + args.watch_seconds
        while time.time() < deadline:
            time.sleep(max(0.05, args.poll_interval))
            current = snapshot(args.codex_home, args.cockpit_home)
            for name, meta in current["files"].items():
                old = last_files.get(name, {})
                if old.get("mtime") != meta.get("mtime") or old.get("sha256") != meta.get("sha256"):
                    events.append(
                        {
                            "timestamp": current["timestamp"],
                            "file": name,
                            "path": meta.get("path"),
                            "old_mtime_iso": old.get("mtime_iso"),
                            "new_mtime_iso": meta.get("mtime_iso"),
                        }
                    )
            last_files = copy.deepcopy(current["files"])

    after = snapshot(args.codex_home, args.cockpit_home)
    report = {
        "schema_version": 1,
        "label": args.label,
        "watch_seconds": args.watch_seconds,
        "before": before,
        "after": after,
        "change_events": events,
        "changed_files": classify_changes(before, after),
        "interpretation": [
            "cockpit_* changes are Cockpit Tools state writes",
            "codex_auth changes affect Codex App/CLI login projection",
            "codex_config changes affect provider/profile projection",
            "codex_state_db changes affect history visibility buckets",
        ],
    }

    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    if args.json or not args.out:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
