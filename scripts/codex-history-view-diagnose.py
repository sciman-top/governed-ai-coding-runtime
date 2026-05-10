from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


APP_SERVER_DEFAULT_PAGE_LIMIT = 25
NATIVE_RECENT_PAGE_LIMIT = 50
OBSERVED_MAX_PAGE_LIMIT = 100


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Diagnose why Codex App history sidebar pages do or do not show target repo threads."
    )
    parser.add_argument("--codex-home", required=True)
    parser.add_argument(
        "--target-cwd",
        action="append",
        default=[],
        help="Target cwd to diagnose. Repeat for multiple repositories.",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=None,
        help="threads.source value to include. Repeat for multiple values. Defaults to Codex App source 'vscode'.",
    )
    parser.add_argument("--default-limit", type=int, default=NATIVE_RECENT_PAGE_LIMIT)
    parser.add_argument("--max-first-page-limit", type=int, default=OBSERVED_MAX_PAGE_LIMIT)
    args = parser.parse_args()
    sources = args.source or ["vscode"]

    codex_home = Path(args.codex_home).expanduser().resolve()
    state_path = codex_home / "state_5.sqlite"
    payload: dict[str, Any] = {
        "status": "pass",
        "codex_home": str(codex_home),
        "state_path": str(state_path),
        "source_filter": list(sources),
        "app_server_observed_contract": {
            "protocol_default_thread_list_limit": APP_SERVER_DEFAULT_PAGE_LIMIT,
            "native_recent_page_limit": args.default_limit,
            "max_first_page_limit": args.max_first_page_limit,
            "pagination_required_after_first_page": True,
            "cwd_filter_supported": True,
            "native_show_more_fetches_next_cursor": False,
            "notes": [
                "Codex app-server thread/list returns nextCursor for additional history pages.",
                "The native sidebar can look sparse when older target repos fall outside the loaded global recent page.",
                "The native Show more control expands already-loaded thread keys; it does not fetch the next cursor page.",
            ],
        },
        "checks": [],
        "page_summaries": [],
        "targets": [],
    }

    if args.default_limit < 1 or args.max_first_page_limit < 1:
        payload["status"] = "fail"
        payload["checks"].append(
            {
                "id": "codex_history_view_limits",
                "status": "fail",
                "reason": "Page limits must be positive integers.",
            }
        )
        emit_json(payload)
        return 2

    if not state_path.exists():
        payload["status"] = "fail"
        payload["checks"].append(
            {
                "id": "codex_state_sqlite_exists",
                "status": "fail",
                "reason": "state_5.sqlite was not found.",
                "path": str(state_path),
            }
        )
        emit_json(payload)
        return 2

    connection = sqlite3.connect(state_path)
    connection.row_factory = sqlite3.Row
    try:
        columns = table_columns(connection, "threads")
        required = {"id", "cwd", "source", "title", "first_user_message", "updated_at", "archived"}
        missing = sorted(required - columns)
        if missing:
            payload["status"] = "fail"
            payload["checks"].append(
                {
                    "id": "codex_threads_history_columns",
                    "status": "fail",
                    "reason": "threads table is missing required history view columns.",
                    "missing_columns": missing,
                }
            )
            emit_json(payload)
            return 2

        rows = load_rows(connection, sources)
        payload["checks"].append(
            {
                "id": "codex_thread_rows_loaded",
                "status": "pass",
                "reason": "Loaded non-archived thread rows in updated_at descending order.",
                "row_count": len(rows),
            }
        )
        for limit in sorted({args.default_limit, args.max_first_page_limit, 50}):
            payload["page_summaries"].append(summarize_page(rows, limit))

        for target in args.target_cwd:
            payload["targets"].append(
                summarize_target(
                    rows,
                    target,
                    default_limit=args.default_limit,
                    max_first_page_limit=args.max_first_page_limit,
                )
            )
    finally:
        connection.close()

    emit_json(payload)
    return 0


def emit_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=True, indent=2))


def table_columns(connection: sqlite3.Connection, table: str) -> set[str]:
    return {str(row["name"]) for row in connection.execute(f"pragma table_info({table})")}


def load_rows(connection: sqlite3.Connection, sources: list[str]) -> list[dict[str, Any]]:
    placeholders = ",".join("?" for _ in sources)
    where_source = f"and source in ({placeholders})" if sources else ""
    params: list[Any] = list(sources)
    query = f"""
        select id, cwd, source, title, first_user_message, updated_at
        from threads
        where coalesce(archived, 0) = 0
        {where_source}
        order by updated_at desc, id desc
    """
    rows: list[dict[str, Any]] = []
    for row in connection.execute(query, params):
        rows.append(
            {
                "id": str(row["id"]),
                "cwd": normalize_cwd(str(row["cwd"] or "")),
                "source": str(row["source"] or ""),
                "title": str(row["title"] or row["first_user_message"] or ""),
                "updated_at": int(row["updated_at"] or 0),
            }
        )
    return rows


def summarize_page(rows: list[dict[str, Any]], limit: int) -> dict[str, Any]:
    page = rows[:limit]
    counts: dict[str, int] = {}
    for row in page:
        repo = repo_name(row["cwd"])
        counts[repo] = counts.get(repo, 0) + 1
    return {
        "limit": limit,
        "returned_rows": len(page),
        "repo_counts": dict(sorted(counts.items(), key=lambda item: (-item[1], item[0].lower()))),
    }


def summarize_target(
    rows: list[dict[str, Any]],
    target_cwd: str,
    *,
    default_limit: int,
    max_first_page_limit: int,
) -> dict[str, Any]:
    target = normalize_cwd(target_cwd)
    target_rows = [row for row in rows if cwd_in_project(row["cwd"], target)]
    latest_rank = None
    if target_rows:
        latest_id = target_rows[0]["id"]
        latest_rank = next(index for index, row in enumerate(rows, start=1) if row["id"] == latest_id)
    visible_default = latest_rank is not None and latest_rank <= default_limit
    visible_max = latest_rank is not None and latest_rank <= max_first_page_limit
    return {
        "cwd": target,
        "repo": repo_name(target),
        "total_rows": len(target_rows),
        "latest_rank": latest_rank,
        "latest_updated_at": target_rows[0]["updated_at"] if target_rows else None,
        "latest_title": target_rows[0]["title"] if target_rows else None,
        "visible_in_default_page": visible_default,
        "visible_in_max_first_page": visible_max,
        "default_page_number_needed": page_number(latest_rank, default_limit),
        "max_page_number_needed": page_number(latest_rank, max_first_page_limit),
        "diagnosis": diagnose_visibility(latest_rank, default_limit, max_first_page_limit),
    }


def diagnose_visibility(latest_rank: int | None, default_limit: int, max_first_page_limit: int) -> str:
    if latest_rank is None:
        return "missing_from_state_db_or_source_filter"
    if latest_rank <= default_limit:
        return "visible_in_initial_thread_list_page"
    if latest_rank <= max_first_page_limit:
        return "hidden_until_native_recent_list_loads_a_larger_page"
    return "hidden_until_next_cursor_page_or_cwd_filtered_history_query"


def page_number(rank: int | None, limit: int) -> int | None:
    if rank is None:
        return None
    return ((rank - 1) // limit) + 1


def normalize_cwd(cwd: str) -> str:
    if cwd.startswith("\\\\?\\"):
        cwd = cwd[4:]
    return cwd.rstrip("\\/")


def cwd_in_project(cwd: str, project_root: str) -> bool:
    normalized_cwd = normalize_cwd(cwd).replace("/", "\\").rstrip("\\")
    normalized_root = normalize_cwd(project_root).replace("/", "\\").rstrip("\\")
    if normalized_cwd.lower() == normalized_root.lower():
        return True
    return normalized_cwd.lower().startswith((normalized_root + "\\").lower())


def repo_name(cwd: str) -> str:
    return cwd.rstrip("\\/").replace("/", "\\").split("\\")[-1] or cwd


if __name__ == "__main__":
    sys.exit(main())
