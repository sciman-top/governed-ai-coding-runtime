from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class CodexHistoryViewDiagnoseTests(unittest.TestCase):
    def test_reports_target_hidden_by_global_recent_page(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            codex_home = Path(tmp_dir) / "codex-home"
            codex_home.mkdir()
            _create_state(codex_home / "state_5.sqlite")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "codex-history-view-diagnose.py"),
                    "--codex-home",
                    str(codex_home),
                    "--default-limit",
                    "3",
                    "--max-first-page-limit",
                    "5",
                    "--target-cwd",
                    r"\\?\D:\CODE\old-target",
                    "--target-cwd",
                    r"D:\CODE\missing-target",
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=30,
            )

            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual("pass", payload["status"])
            self.assertEqual(5, payload["checks"][0]["row_count"])
            self.assertEqual(3, payload["page_summaries"][0]["limit"])
            self.assertEqual(3, payload["page_summaries"][0]["returned_rows"])

            old_target = payload["targets"][0]
            self.assertEqual("old-target", old_target["repo"])
            self.assertEqual(2, old_target["total_rows"])
            self.assertEqual(4, old_target["latest_rank"])
            self.assertFalse(old_target["visible_in_default_page"])
            self.assertTrue(old_target["visible_in_max_first_page"])
            self.assertEqual(2, old_target["default_page_number_needed"])
            self.assertEqual("hidden_until_native_recent_list_loads_a_larger_page", old_target["diagnosis"])

            missing = payload["targets"][1]
            self.assertEqual(0, missing["total_rows"])
            self.assertIsNone(missing["latest_rank"])
            self.assertEqual("missing_from_state_db_or_source_filter", missing["diagnosis"])

    def test_source_filter_excludes_non_app_threads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            codex_home = Path(tmp_dir) / "codex-home"
            codex_home.mkdir()
            _create_state(codex_home / "state_5.sqlite")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "codex-history-view-diagnose.py"),
                    "--codex-home",
                    str(codex_home),
                    "--target-cwd",
                    r"D:\CODE\cli-only",
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=30,
            )

            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual("vscode", payload["source_filter"][0])
            self.assertEqual(0, payload["targets"][0]["total_rows"])
            self.assertEqual("missing_from_state_db_or_source_filter", payload["targets"][0]["diagnosis"])

    def test_explicit_source_replaces_default_app_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            codex_home = Path(tmp_dir) / "codex-home"
            codex_home.mkdir()
            _create_state(codex_home / "state_5.sqlite")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "codex-history-view-diagnose.py"),
                    "--codex-home",
                    str(codex_home),
                    "--source",
                    "cli",
                    "--target-cwd",
                    r"D:\CODE\cli-only",
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=30,
            )

            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(["cli"], payload["source_filter"])
            self.assertEqual(1, payload["checks"][0]["row_count"])
            self.assertEqual(1, payload["targets"][0]["total_rows"])


def _create_state(path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.execute(
            """
            create table threads(
                id text primary key,
                cwd text not null,
                source text not null,
                title text,
                first_user_message text,
                updated_at integer not null,
                archived integer not null default 0
            )
            """
        )
        connection.executemany(
            """
            insert into threads(id, cwd, source, title, first_user_message, updated_at, archived)
            values(?, ?, ?, ?, ?, ?, ?)
            """,
            [
                ("new-1", r"D:\CODE\busy", "vscode", "new 1", None, 106, 0),
                ("new-2", r"D:\CODE\busy", "vscode", "new 2", None, 105, 0),
                ("new-3", r"D:\CODE\other", "vscode", "new 3", None, 104, 0),
                ("archived", r"D:\CODE\old-target", "vscode", "archived", None, 103, 1),
                ("old-1", r"D:\CODE\old-target", "vscode", "old 1", None, 102, 0),
                ("old-2", r"\\?\D:\CODE\old-target", "vscode", "old 2", None, 101, 0),
                ("cli-1", r"D:\CODE\cli-only", "cli", "cli only", None, 100, 0),
            ],
        )
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    unittest.main()
