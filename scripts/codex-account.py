from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_SRC = ROOT / "scripts"
if str(SCRIPTS_SRC) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_SRC))

from lib.codex_local import (
    codex_status,
    context_window_probe,
    delete_auth_profile,
    install_account_switcher,
    list_auth_profiles,
    switch_auth_profile,
    sync_active_auth_snapshot,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Manage local Codex ChatGPT auth profiles without printing tokens.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="List local auth profiles.")
    subparsers.add_parser("status", help="Show active Codex auth and config status.")
    context_parser = subparsers.add_parser("context-probe", help="Inspect Codex context window and auto-compact policy.")
    context_parser.add_argument("--codex-home", default=None)
    context_parser.add_argument("--run-codex", action="store_true", help="Run `codex debug models --bundled`.")
    context_parser.add_argument("--live", action="store_true", help="Refresh the Codex model catalog instead of using --bundled.")
    context_parser.add_argument("--codex-binary", default=None)
    install_parser = subparsers.add_parser("install", help="Install the codex-account PowerShell shim into the user profile.")
    install_parser.add_argument("--codex-home", default=None)
    switch_parser = subparsers.add_parser("switch", help="Switch active auth.json to another auth profile.")
    switch_parser.add_argument("name")
    switch_parser.add_argument("--dry-run", action="store_true")
    sync_parser = subparsers.add_parser("sync-active", help="Save the current auth.json back into its named auth snapshot.")
    sync_parser.add_argument("--name", default=None, help="Optional named auth profile to overwrite.")
    sync_parser.add_argument("--dry-run", action="store_true")
    delete_parser = subparsers.add_parser("delete", help="Back up and delete a non-active local auth profile.")
    delete_parser.add_argument("name")
    delete_parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "list":
        payload = [profile.to_dict() for profile in list_auth_profiles()]
    elif args.command == "status":
        payload = codex_status()
    elif args.command == "context-probe":
        payload = context_window_probe(
            Path(args.codex_home) if args.codex_home else None,
            run_codex=args.run_codex,
            bundled=not args.live,
            codex_binary=args.codex_binary,
        )
    elif args.command == "install":
        payload = install_account_switcher(Path(args.codex_home) if args.codex_home else None)
    elif args.command == "switch":
        payload = switch_auth_profile(args.name, dry_run=args.dry_run)
    elif args.command == "sync-active":
        payload = sync_active_auth_snapshot(target_name=args.name, dry_run=args.dry_run)
    elif args.command == "delete":
        payload = delete_auth_profile(args.name, dry_run=args.dry_run)
    else:
        parser.error("unsupported command")
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not isinstance(payload, dict) or payload.get("status") != "error" else 2


if __name__ == "__main__":
    raise SystemExit(main())
