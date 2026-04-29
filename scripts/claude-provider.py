from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_SRC = ROOT / "scripts"
if str(SCRIPTS_SRC) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_SRC))

from lib.claude_local import (
    claude_status,
    install_provider_switcher,
    load_provider_profiles,
    optimize_claude_local,
    switch_provider,
    write_default_provider_profiles,
)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Manage local Claude Code third-party provider profiles without printing secrets.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List provider profiles.")
    subparsers.add_parser("status", help="Show active Claude Code provider and config status.")
    install_parser = subparsers.add_parser("install", help="Install provider profile metadata and the claude-provider shim.")
    install_parser.add_argument("--claude-home", default=None)
    switch_parser = subparsers.add_parser("switch", help="Switch active Claude Code provider profile.")
    switch_parser.add_argument("name")
    switch_parser.add_argument("--dry-run", action="store_true")
    optimize_parser = subparsers.add_parser("optimize", help="Apply the recommended local Claude Code third-party provider setup.")
    optimize_parser.add_argument("--provider", default="bigmodel-glm")
    optimize_parser.add_argument("--apply", action="store_true")
    optimize_parser.add_argument("--no-install-switcher", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "list":
        write_default_provider_profiles()
        payload = [profile.to_dict() for profile in load_provider_profiles()]
    elif args.command == "status":
        write_default_provider_profiles()
        payload = claude_status()
    elif args.command == "install":
        home = Path(args.claude_home) if args.claude_home else None
        payload = {
            "profiles": write_default_provider_profiles(home),
            "switcher": install_provider_switcher(home),
        }
    elif args.command == "switch":
        write_default_provider_profiles()
        payload = switch_provider(args.name, dry_run=args.dry_run)
    elif args.command == "optimize":
        payload = optimize_claude_local(
            provider_name=args.provider,
            apply=args.apply,
            install_switcher=not args.no_install_switcher,
        )
    else:
        parser.error("unsupported command")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not isinstance(payload, dict) or payload.get("status") != "error" else 2


if __name__ == "__main__":
    raise SystemExit(main())
