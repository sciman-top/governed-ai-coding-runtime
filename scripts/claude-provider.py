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
    delete_provider_profile,
    install_provider_switcher,
    load_provider_profiles,
    optimize_claude_local,
    session_continuity_status,
    switch_provider,
)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Read local Claude Code provider/session status without changing account or API state.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List observed provider profiles without writing defaults.")
    status_parser = subparsers.add_parser("status", help="Show active Claude Code provider and config status.")
    status_parser.add_argument("--cc-switch-db", default=None, help="Optional CC Switch sqlite DB for redacted interop status.")
    subparsers.add_parser("continuity", help="Show Claude Code session continuity anchors for provider switching.")
    install_parser = subparsers.add_parser("install", help="Deprecated: Claude switching is owned by CC Switch.")
    install_parser.add_argument("--claude-home", default=None)
    switch_parser = subparsers.add_parser("switch", help="Deprecated: use CC Switch to change Claude Code/Desktop account or API.")
    switch_parser.add_argument("name")
    switch_parser.add_argument("--dry-run", action="store_true")
    switch_parser.add_argument("--cc-switch-db", default=None, help="Optional CC Switch sqlite DB to import the matching local provider env.")
    delete_parser = subparsers.add_parser("delete", help="Deprecated: provider profile management is owned by CC Switch.")
    delete_parser.add_argument("name")
    delete_parser.add_argument("--dry-run", action="store_true")
    optimize_parser = subparsers.add_parser("optimize", help="Deprecated: Claude account/API setup is owned by CC Switch.")
    optimize_parser.add_argument("--provider", default="bigmodel-glm")
    optimize_parser.add_argument("--apply", action="store_true")
    optimize_parser.add_argument("--no-install-switcher", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "list":
        payload = [profile.to_dict() for profile in load_provider_profiles()]
    elif args.command == "status":
        payload = claude_status(cc_switch_db=Path(args.cc_switch_db) if args.cc_switch_db else None)
    elif args.command == "continuity":
        payload = session_continuity_status()
    elif args.command == "install":
        home = Path(args.claude_home) if args.claude_home else None
        payload = install_provider_switcher(home)
    elif args.command == "switch":
        payload = switch_provider(args.name, dry_run=args.dry_run, cc_switch_db=Path(args.cc_switch_db) if args.cc_switch_db else None)
    elif args.command == "delete":
        payload = delete_provider_profile(args.name, dry_run=args.dry_run)
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
