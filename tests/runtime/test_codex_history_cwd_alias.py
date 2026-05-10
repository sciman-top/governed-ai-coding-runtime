from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class CodexHistoryCwdAliasTests(unittest.TestCase):
    def test_dry_run_reports_alias_counts_without_mutating_threads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            codex_home = Path(tmp_dir) / "codex-home"
            codex_home.mkdir()
            _create_state(codex_home / "state_5.sqlite")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "codex-history-cwd-alias.py"),
                    "--codex-home",
                    str(codex_home),
                    "--alias",
                    r"E:\CODE\demo=>\\?\D:\CODE\demo",
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=30,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual("pass", payload["status"])
            self.assertFalse(payload["apply"])
            self.assertEqual(2, payload["checks"][0]["summary"][0]["from_count"])
            self.assertEqual(1, payload["checks"][0]["summary"][0]["to_count"])
            self.assertEqual(2, payload["checks"][0]["summary"][0]["would_update_rows"])
            self.assertEqual(2, _count_cwd(codex_home / "state_5.sqlite", r"E:\CODE\demo"))

    def test_apply_backs_up_and_rewrites_alias_cwd_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            codex_home = Path(tmp_dir) / "codex-home"
            codex_home.mkdir()
            state_path = codex_home / "state_5.sqlite"
            _create_state(state_path)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "codex-history-cwd-alias.py"),
                    "--codex-home",
                    str(codex_home),
                    "--alias",
                    r"E:\CODE\demo=>\\?\D:\CODE\demo",
                    "--apply",
                ],
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=30,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertTrue(payload["apply"])
            self.assertEqual(2, payload["actions"][1]["updated_rows"])
            self.assertTrue(Path(payload["actions"][0]["path"]).exists())
            self.assertEqual(0, _count_cwd(state_path, r"E:\CODE\demo"))
            self.assertEqual(3, _count_cwd(state_path, r"\\?\D:\CODE\demo"))
            self.assertEqual(1, _count_cwd(state_path, r"D:\CODE\other"))


def _create_state(path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        connection.execute("create table threads(id text primary key, cwd text not null, title text)")
        connection.executemany(
            "insert into threads(id, cwd, title) values(?, ?, ?)",
            [
                ("old-1", r"E:\CODE\demo", "old one"),
                ("old-2", r"E:\CODE\demo", "old two"),
                ("new-1", r"\\?\D:\CODE\demo", "new one"),
                ("other", r"D:\CODE\other", "other"),
            ],
        )
        connection.commit()
    finally:
        connection.close()


def _count_cwd(path: Path, cwd: str) -> int:
    connection = sqlite3.connect(path)
    try:
        row = connection.execute("select count(*) from threads where cwd = ?", (cwd,)).fetchone()
        return int(row[0])
    finally:
        connection.close()


if __name__ == "__main__":
    unittest.main()
