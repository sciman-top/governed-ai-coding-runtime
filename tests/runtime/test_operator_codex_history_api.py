from __future__ import annotations

import importlib.util
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class OperatorCodexHistoryApiTests(unittest.TestCase):
    def test_load_codex_history_reads_state_sqlite_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            codex_home = Path(tmp_dir) / "codex-home"
            codex_home.mkdir()
            state = codex_home / "state_5.sqlite"
            _create_state(state)

            previous_home = os.environ.get("CODEX_HOME")
            os.environ["CODEX_HOME"] = str(codex_home)
            try:
                module = _load_operator_server()
                payload = module.load_codex_history(
                    {
                        "source": ["vscode,cli"],
                        "search": ["history"],
                        "limit": ["2"],
                    }
                )
            finally:
                if previous_home is None:
                    os.environ.pop("CODEX_HOME", None)
                else:
                    os.environ["CODEX_HOME"] = previous_home

            self.assertEqual("ok", payload["status"])
            self.assertTrue(payload["read_only"])
            self.assertEqual(str(state), payload["state_path"])
            self.assertEqual(2, payload["total"])
            self.assertEqual(2, payload["returned"])
            self.assertEqual(["vscode", "cli"], payload["sources"])
            self.assertEqual(["newer", "older"], [row["id"] for row in payload["rows"]])
            self.assertEqual(1_020_000, payload["rows"][0]["updated_at_ms"])
            self.assertIn("repo-a", {item["repo"] for item in payload["repo_counts"]})

    def test_load_codex_history_filters_cwd_with_extended_windows_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            codex_home = Path(tmp_dir) / "codex-home"
            codex_home.mkdir()
            _create_state(codex_home / "state_5.sqlite")

            previous_home = os.environ.get("CODEX_HOME")
            os.environ["CODEX_HOME"] = str(codex_home)
            try:
                module = _load_operator_server()
                payload = module.load_codex_history(
                    {
                        "source": ["vscode,cli"],
                        "cwd": [r"D:\CODE\repo-a"],
                    }
                )
            finally:
                if previous_home is None:
                    os.environ.pop("CODEX_HOME", None)
                else:
                    os.environ["CODEX_HOME"] = previous_home

            self.assertEqual("ok", payload["status"])
            self.assertEqual(2, payload["total"])
            self.assertEqual(["newer", "older"], [row["id"] for row in payload["rows"]])


def _load_operator_server():
    module_name = "serve_operator_ui_test_module"
    spec = importlib.util.spec_from_file_location(module_name, ROOT / "scripts" / "serve-operator-ui.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load serve-operator-ui.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _create_state(path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            """
            create table threads(
                id text primary key,
                rollout_path text not null,
                created_at integer not null,
                updated_at integer not null,
                source text not null,
                model_provider text not null,
                cwd text not null,
                title text not null,
                archived integer not null default 0,
                first_user_message text not null default ''
            )
            """
        )
        connection.executemany(
            """
            insert into threads(id, rollout_path, created_at, updated_at, source, model_provider, cwd, title, archived, first_user_message)
            values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("newer", "rollout-newer.jsonl", 900, 1020, "vscode", "openai", r"\\?\D:\CODE\repo-a", "history newer", 0, "first"),
                ("older", "rollout-older.jsonl", 800, 1010, "cli", "openai", r"D:\CODE\repo-a", "history older", 0, "first"),
                ("archived", "rollout-archived.jsonl", 700, 1030, "vscode", "openai", r"D:\CODE\repo-a", "history archived", 1, "first"),
                ("exec", "rollout-exec.jsonl", 700, 1040, "exec", "openai", r"D:\CODE\repo-b", "history exec", 0, "first"),
            ],
        )
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    unittest.main()
