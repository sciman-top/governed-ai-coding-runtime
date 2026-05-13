#!/usr/bin/env python3
"""Deprecated Cockpit Tools -> Codex CLI preflight repair shim.

This file intentionally performs no writes. The previous implementation
rewrote Codex auth/provider/history state before every CLI launch, which made
Codex App and Cockpit Tools race on the same live configuration files.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


DEPRECATED_REASON = (
    "codex-cockpit-cli-preflight-repair is deprecated and performs no repair. "
    "Cockpit Tools owns Codex auth/API switching; this control repo may only "
    "diagnose state with scripts/codex-interop-check.py or clean old shims with "
    "scripts/Disable-CodexProjectInterop.ps1."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deprecated Codex/Cockpit preflight repair shim.")
    parser.add_argument("--codex-home", type=Path, default=Path.home() / ".codex")
    parser.add_argument("--cockpit-home", type=Path, default=Path.home() / ".antigravity_cockpit")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--print-env",
        action="store_true",
        help="Deprecated compatibility option. Prints no environment values.",
    )
    parser.add_argument(
        "--repair-sessions",
        action="store_true",
        help="Deprecated compatibility option. Session repair is disabled.",
    )
    return parser


def repair(
    codex_home: Path,
    cockpit_home: Path,
    *,
    dry_run: bool,
    repair_sessions: bool = False,
) -> list[str]:
    """Compatibility API retained for old callers; it never mutates state."""

    _ = (codex_home, cockpit_home, dry_run, repair_sessions)
    return []


def wrapper_environment(codex_home: Path) -> dict[str, str]:
    """Deprecated wrapper env injection is disabled for Codex App parity."""

    _ = codex_home
    return {}


def deprecated_payload() -> dict[str, object]:
    return {
        "status": "deprecated",
        "actions": [
            {
                "id": "codex_cockpit_cli_preflight_repair_deprecated",
                "tool": "codex",
                "status": "blocked",
                "reason": DEPRECATED_REASON,
            }
        ],
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.print_env:
        return 2
    if not args.quiet:
        print(json.dumps(deprecated_payload(), ensure_ascii=False, indent=2))
        print(DEPRECATED_REASON, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
