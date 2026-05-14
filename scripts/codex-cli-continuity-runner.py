#!/usr/bin/env python3
"""Mock-first Codex CLI continuity runner for Cockpit account switches."""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


QUOTA_RE = re.compile(r"(quota|insufficient_quota|usage limit|rate limit|429)", re.IGNORECASE)
AUTH_RE = re.compile(r"(401\s+Unauthorized|token_invalidated|invalid api key|authentication failed)", re.IGNORECASE)
ACCOUNT_LIMIT_RE = re.compile(r"(account limit|too many accounts|account exhausted|account.*disabled)", re.IGNORECASE)


class SegmentResult:
    def __init__(self, exit_code: int, stdout: str, stderr: str) -> None:
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr


def default_cockpit_home() -> Path:
    return Path.home() / ".antigravity_cockpit"


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except Exception:
        return None


def current_account_id(cockpit_home: Path) -> str | None:
    accounts = read_json(cockpit_home / "codex_accounts.json")
    config = read_json(cockpit_home / "config.json")
    for doc in (accounts, config):
        if isinstance(doc, dict):
            raw = (
                doc.get("currentAccountId")
                or doc.get("current_account_id")
                or doc.get("activeAccountId")
                or doc.get("current")
            )
            if raw:
                return str(raw)
    return None


def account_suffix(account_id: str | None, keep: int = 4) -> str | None:
    if account_id is None:
        return None
    return account_id if len(account_id) <= keep else f"...{account_id[-keep:]}"


def classify_failure(result: SegmentResult) -> str:
    text = f"{result.stdout}\n{result.stderr}"
    if result.exit_code == 0:
        return "success"
    if AUTH_RE.search(text):
        return "auth_401"
    if ACCOUNT_LIMIT_RE.search(text):
        return "account_limit"
    if QUOTA_RE.search(text):
        return "quota"
    return "unknown_error"


def retryable_failure(reason: str) -> bool:
    return reason in {"quota", "auth_401", "account_limit"}


def build_codex_exec_command(repo: Path, prompt: str, output_last_message: Path | None = None) -> list[str]:
    command = ["codex", "exec", "--cd", str(repo)]
    if output_last_message is not None:
        command.extend(["--output-last-message", str(output_last_message)])
    command.append(prompt)
    return command


def run_segment(command: list[str], execute: bool, simulated: SegmentResult | None = None) -> SegmentResult:
    if simulated is not None:
        return simulated
    if not execute:
        return SegmentResult(0, "dry_run: codex exec not started", "")
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    return SegmentResult(completed.returncode, completed.stdout, completed.stderr)


def wait_for_account_change(cockpit_home: Path, before: str | None, wait_seconds: int, poll_seconds: float = 1.0) -> dict[str, Any]:
    deadline = time.monotonic() + max(0, wait_seconds)
    after = current_account_id(cockpit_home)
    while wait_seconds > 0 and time.monotonic() < deadline:
        after = current_account_id(cockpit_home)
        if after and after != before:
            break
        time.sleep(poll_seconds)
    changed = bool(after and before and after != before)
    return {
        "before_account_suffix": account_suffix(before),
        "after_account_suffix": account_suffix(after),
        "changed": changed,
        "wait_seconds": wait_seconds,
    }


def write_handoff(
    evidence_dir: Path,
    task_id: str,
    repo: Path,
    segment_index: int,
    failure_reason: str,
    prompt: str,
    account_before: str | None,
    account_after: str | None,
) -> Path:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    path = evidence_dir / f"{task_id}-segment-{segment_index}-handoff.md"
    path.write_text(
        "\n".join(
            [
                f"# Codex CLI Continuity Handoff: {task_id}",
                "",
                f"- Segment: {segment_index}",
                f"- Repo: {repo}",
                f"- Failure reason: {failure_reason}",
                f"- Account before: {account_suffix(account_before)}",
                f"- Account after: {account_suffix(account_after)}",
                "",
                "## Resume Prompt",
                prompt,
                "",
                "## Operator Notes",
                "- Restart a fresh `codex exec` or `codex resume` segment only after Cockpit account state changes or quota health recovers.",
                "- Do not restart Codex App from this runner.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return path


def execute_once(args: argparse.Namespace) -> dict[str, Any]:
    repo = args.repo.resolve()
    prompt = args.prompt
    command = build_codex_exec_command(repo, prompt, args.output_last_message)
    before = current_account_id(args.cockpit_home)
    simulated = None
    if args.simulate_exit_code is not None:
        simulated = SegmentResult(args.simulate_exit_code, args.simulate_stdout or "", args.simulate_stderr or "")
    result = run_segment(command, args.execute, simulated)
    reason = classify_failure(result)
    account_wait = {"before_account_suffix": account_suffix(before), "after_account_suffix": account_suffix(before), "changed": False, "wait_seconds": 0}
    handoff_ref = None
    if retryable_failure(reason):
        account_wait = wait_for_account_change(args.cockpit_home, before, args.wait_seconds)
        after = current_account_id(args.cockpit_home)
        handoff_ref = str(
            write_handoff(args.evidence_dir, args.task_id, repo, 1, reason, prompt, before, after)
        )
    return {
        "schema_version": 1,
        "timestamp": _dt.datetime.now().isoformat(timespec="seconds"),
        "task_id": args.task_id,
        "mode": "execute" if args.execute else "dry_run",
        "segment": {
            "index": 1,
            "command": command,
            "exit_code": result.exit_code,
            "failure_reason": reason,
            "retryable": retryable_failure(reason),
        },
        "account_wait": account_wait,
        "handoff_ref": handoff_ref,
        "write_actions": [handoff_ref] if handoff_ref else [],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--evidence-dir", type=Path, default=Path("docs/change-evidence/codex-cli-continuity"))
    parser.add_argument("--cockpit-home", type=Path, default=default_cockpit_home())
    parser.add_argument("--wait-seconds", type=int, default=0)
    parser.add_argument("--output-last-message", type=Path)
    parser.add_argument("--execute", action="store_true", help="Actually start codex exec. Default is dry-run.")
    parser.add_argument("--simulate-exit-code", type=int)
    parser.add_argument("--simulate-stdout", default="")
    parser.add_argument("--simulate-stderr", default="")
    parser.add_argument("--json", action="store_true", help="Emit JSON. This is the default output format.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = execute_once(args)
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
