from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_SRC = ROOT / "scripts"
if str(SCRIPTS_SRC) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_SRC))

from lib.codex_local import codex_status, install_account_switcher, list_auth_profiles, switch_auth_profile


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manage local Codex ChatGPT auth profiles without printing tokens.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List local auth profiles.")
    subparsers.add_parser("status", help="Show active Codex auth and config status.")
    install_parser = subparsers.add_parser("install", help="Install the codex-account PowerShell shim into the user profile.")
    install_parser.add_argument("--codex-home", default=None)
    switch_parser = subparsers.add_parser("switch", help="Switch active auth.json to another auth profile.")
    switch_parser.add_argument("name")
    switch_parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "list":
        payload = [profile.to_dict() for profile in list_auth_profiles()]
    elif args.command == "status":
        payload = codex_status()
    elif args.command == "install":
        payload = install_account_switcher(Path(args.codex_home) if args.codex_home else None)
    elif args.command == "switch":
        payload = switch_auth_profile(args.name, dry_run=args.dry_run)
    else:
        parser.error("unsupported command")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not isinstance(payload, dict) or payload.get("status") != "error" else 2


if __name__ == "__main__":
    raise SystemExit(main())
