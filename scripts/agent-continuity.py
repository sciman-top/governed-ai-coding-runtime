from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))

from governed_ai_coding_runtime_contracts.agent_continuity import LocalAgentContinuityIndex, audit_agent_continuity


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only agent continuity auditor.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit_parser = subparsers.add_parser("audit", help="Audit host continuity posture without mutating host state.")
    audit_parser.add_argument("--repo-root", default=str(ROOT))
    audit_parser.add_argument("--codex-home")
    audit_parser.add_argument("--claude-home")
    audit_parser.add_argument("--json", action="store_true")

    write_parser = subparsers.add_parser("write-record", help="Write a classified continuity record into a local index.")
    write_parser.add_argument("--index-root", required=True)
    write_parser.add_argument("--record-json", required=True, help="Path to an agent-continuity-record JSON file.")
    write_parser.add_argument("--json", action="store_true")

    search_parser = subparsers.add_parser("search", help="Search the local continuity index.")
    search_parser.add_argument("--index-root", required=True)
    search_parser.add_argument("--repo-id")
    search_parser.add_argument("--tool-family")
    search_parser.add_argument("--account-alias")
    search_parser.add_argument("--provider-alias")
    search_parser.add_argument("--include-expired", action="store_true")
    search_parser.add_argument("--include-secret-blocked", action="store_true")
    search_parser.add_argument("--json", action="store_true")

    args = parser.parse_args()
    if args.command == "audit":
        payload = audit_agent_continuity(
            repo_root=Path(args.repo_root),
            codex_home=Path(args.codex_home) if args.codex_home else None,
            claude_home=Path(args.claude_home) if args.claude_home else None,
        )
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"status={payload['status']}")
            print(f"record_count={payload['record_count']}")
            for record in payload["records"]:
                print(
                    "record={record_id} tool={tool_family} surface={surface} class={continuity_class}".format(
                        **record
                    )
                )
        return 0

    if args.command == "write-record":
        record_path = Path(args.record_json)
        payload = json.loads(record_path.read_text(encoding="utf-8"))
        result = LocalAgentContinuityIndex(Path(args.index_root)).write_record(payload)
        if args.json:
            print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(f"status={result.status}")
            print(f"record_id={result.record_id}")
            print(f"record_ref={result.record_ref}")
        return 0

    if args.command == "search":
        payload = LocalAgentContinuityIndex(Path(args.index_root)).search(
            repo_id=args.repo_id,
            tool_family=args.tool_family,
            account_alias=args.account_alias,
            provider_alias=args.provider_alias,
            include_expired=args.include_expired,
            include_secret_blocked=args.include_secret_blocked,
        )
        if args.json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"status={payload['status']}")
            print(f"record_count={payload['record_count']}")
            for record in payload["records"]:
                print(
                    "record={record_id} repo={repo_id} tool={tool_family} provider={provider_alias}".format(
                        **record
                    )
                )
        return 0

    parser.error(f"unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
