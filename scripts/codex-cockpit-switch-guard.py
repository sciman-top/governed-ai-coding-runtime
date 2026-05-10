#!/usr/bin/env python3
"""Background guard for Cockpit Tools -> Codex state drift.

The guard does not launch, stop, or restart Codex App. It watches the local
Cockpit/Codex state files that Cockpit Tools rewrites during account/provider
switching, then runs the existing interop repair path after a short debounce.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def default_codex_home() -> Path:
    return Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex")


def default_cockpit_home() -> Path:
    return Path.home() / ".antigravity_cockpit"


def default_cc_switch_db() -> Path:
    return Path.home() / ".cc-switch" / "cc-switch.db"


def sha256_file(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(512 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tracked_paths(codex_home: Path, cockpit_home: Path) -> list[Path]:
    paths = [
        cockpit_home / "config.json",
        cockpit_home / "codex_accounts.json",
        cockpit_home / "codex_instances.json",
        cockpit_home / "codex_model_providers.json",
        codex_home / "config.toml",
        codex_home / "auth.json",
        codex_home / ".cockpit_codex_auth.json",
    ]
    accounts_dir = cockpit_home / "codex_accounts"
    if accounts_dir.exists():
        paths.extend(sorted(path for path in accounts_dir.glob("*.json") if path.is_file()))
    return paths


def fingerprint(codex_home: Path, cockpit_home: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for path in tracked_paths(codex_home, cockpit_home):
        try:
            stat = path.stat()
        except FileNotFoundError:
            result[str(path)] = {"exists": False}
            continue
        result[str(path)] = {
            "exists": True,
            "mtime": stat.st_mtime,
            "size": stat.st_size,
            "sha256": sha256_file(path),
        }
    return result


def changed_paths(before: dict[str, dict[str, Any]], after: dict[str, dict[str, Any]]) -> list[str]:
    changes: list[str] = []
    for path in sorted(set(before) | set(after)):
        if before.get(path) != after.get(path):
            changes.append(path)
    return changes


def run_interop_repair(
    *,
    repair_script: Path,
    codex_home: Path,
    cockpit_home: Path,
    cc_switch_db: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    command = [
        sys.executable,
        str(repair_script),
        "--codex-home",
        str(codex_home),
        "--cc-switch-db",
        str(cc_switch_db),
        "--cockpit-home",
        str(cockpit_home),
        "--apply",
        "--migrate-provider-bucket",
        "--quick-launch",
    ]
    started = dt.datetime.now().isoformat(timespec="seconds")
    completed = subprocess.run(
        command,
        cwd=str(repair_script.resolve().parents[1]),
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout_seconds,
        check=False,
    )
    parsed_stdout: Any = None
    try:
        parsed_stdout = json.loads(completed.stdout) if completed.stdout.strip() else None
    except json.JSONDecodeError:
        parsed_stdout = None
    return {
        "timestamp": started,
        "command": command,
        "exit_code": completed.returncode,
        "stdout_status": parsed_stdout.get("status") if isinstance(parsed_stdout, dict) else None,
        "stdout_actions": parsed_stdout.get("actions") if isinstance(parsed_stdout, dict) else None,
        "stdout": parsed_stdout if isinstance(parsed_stdout, dict) else completed.stdout[-8000:],
        "stderr": completed.stderr[-8000:],
    }


def append_log(log_path: Path, event: dict[str, Any]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Guard Cockpit Tools Codex switch drift.")
    parser.add_argument("--codex-home", type=Path, default=default_codex_home())
    parser.add_argument("--cockpit-home", type=Path, default=default_cockpit_home())
    parser.add_argument("--cc-switch-db", type=Path, default=default_cc_switch_db())
    parser.add_argument("--repair-script", type=Path, default=Path(__file__).resolve().with_name("codex-interop-check.py"))
    parser.add_argument("--interval-seconds", type=float, default=1.0)
    parser.add_argument("--debounce-seconds", type=float, default=3.0)
    parser.add_argument("--min-repair-interval-seconds", type=float, default=8.0)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--once", action="store_true", help="Run one repair pass and exit.")
    parser.add_argument("--watch", action="store_true", help="Watch files and repair on drift.")
    parser.add_argument("--log-path", type=Path, default=default_codex_home() / "log" / "codex-cockpit-switch-guard.jsonl")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.once and not args.watch:
        args.once = True

    if args.once:
        event = {
            "event": "manual_repair",
            "repair": run_interop_repair(
                repair_script=args.repair_script,
                codex_home=args.codex_home,
                cockpit_home=args.cockpit_home,
                cc_switch_db=args.cc_switch_db,
                timeout_seconds=args.timeout_seconds,
            ),
        }
        append_log(args.log_path, event)
        print(json.dumps(event, ensure_ascii=False, indent=2))
        return 0 if event["repair"]["exit_code"] == 0 else 1

    previous = fingerprint(args.codex_home, args.cockpit_home)
    last_repair_at = 0.0
    append_log(
        args.log_path,
        {
            "event": "guard_started",
            "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
            "codex_home": str(args.codex_home),
            "cockpit_home": str(args.cockpit_home),
            "repair_script": str(args.repair_script),
        },
    )
    while True:
        time.sleep(max(0.2, args.interval_seconds))
        current = fingerprint(args.codex_home, args.cockpit_home)
        changes = changed_paths(previous, current)
        if not changes:
            previous = current
            continue
        first_seen = dt.datetime.now().isoformat(timespec="seconds")
        time.sleep(max(0.2, args.debounce_seconds))
        settled = fingerprint(args.codex_home, args.cockpit_home)
        changes = changed_paths(previous, settled)
        previous = settled
        if not changes:
            continue
        now = time.monotonic()
        if now - last_repair_at < args.min_repair_interval_seconds:
            append_log(
                args.log_path,
                {
                    "event": "change_skipped_min_interval",
                    "timestamp": first_seen,
                    "changed_paths": changes,
                },
            )
            continue
        repair = run_interop_repair(
            repair_script=args.repair_script,
            codex_home=args.codex_home,
            cockpit_home=args.cockpit_home,
            cc_switch_db=args.cc_switch_db,
            timeout_seconds=args.timeout_seconds,
        )
        last_repair_at = time.monotonic()
        append_log(
            args.log_path,
            {
                "event": "change_repaired",
                "timestamp": first_seen,
                "changed_paths": changes,
                "repair": repair,
            },
        )


if __name__ == "__main__":
    raise SystemExit(main())
