import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class AgentRuleSyncTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("pwsh"), "PowerShell is not available")
    def test_powershell_wrapper_resolves_repo_paths_from_another_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            user_profile = Path(tmp_dir) / "user"
            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "sync-agent-rules.ps1"),
                    "-FailOnChange",
                    "-ManifestPath",
                    "rules/manifest.json",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=tmp_dir,
                env={**os.environ, "USERPROFILE": str(user_profile)},
            )

        self.assertEqual(completed.returncode, 1, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "dry_run_changes")
        self.assertEqual(payload["changed_count"], 2)

    def test_default_manifest_covers_global_rule_sources_only(self) -> None:
        manifest_path = ROOT / "rules" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries = manifest["entries"]
        ids = [entry["id"] for entry in entries]

        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(entries), 2)
        self.assertEqual({entry["scope"] for entry in entries}, {"global"})
        self.assertEqual({entry["tool"] for entry in entries}, {"codex", "claude"})
        global_version = manifest["default_version"]
        for entry in entries:
            self.assertEqual(entry["version"], global_version)
            self.assertTrue((ROOT / entry["source"]).exists(), entry["source"])
            self.assertNotIn("target_repo_id", entry)

    def test_global_sync_skips_when_hashes_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            user_profile = Path(tmp_dir) / "user"
            copies = {
                user_profile / ".codex" / "AGENTS.md": ROOT / "rules" / "global" / "codex" / "AGENTS.md",
                user_profile / ".claude" / "CLAUDE.md": ROOT / "rules" / "global" / "claude" / "CLAUDE.md",
            }
            for target, source in copies.items():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/sync-agent-rules.py",
                    "--scope",
                    "Global",
                    "--user-profile",
                    str(user_profile),
                    "--fail-on-change",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["scope"], "global")
            self.assertEqual({item["status"] for item in payload["results"]}, {"skipped_same_hash"})

    def test_scope_all_behaves_as_global_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            user_profile = Path(tmp_dir) / "user"

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/sync-agent-rules.py",
                    "--scope",
                    "All",
                    "--user-profile",
                    str(user_profile),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["scope"], "all")
            self.assertEqual(payload["entry_count"], 2)
            self.assertEqual({item["scope"] for item in payload["results"]}, {"global"})

    def test_global_sync_blocks_same_version_content_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            user_profile = Path(tmp_dir) / "user"
            copies = {
                user_profile / ".codex" / "AGENTS.md": ROOT / "rules" / "global" / "codex" / "AGENTS.md",
                user_profile / ".claude" / "CLAUDE.md": ROOT / "rules" / "global" / "claude" / "CLAUDE.md",
            }
            for target, source in copies.items():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
            codex_target = user_profile / ".codex" / "AGENTS.md"
            codex_target.write_text(
                codex_target.read_text(encoding="utf-8") + "\n<!-- local drift with same version -->\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/sync-agent-rules.py",
                    "--scope",
                    "Global",
                    "--user-profile",
                    str(user_profile),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 2)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "blocked")
            blocked = [item for item in payload["results"] if item["status"].startswith("blocked_")]
            self.assertEqual(blocked[0]["status"], "blocked_same_version_drift")

    def test_global_apply_updates_older_version_and_writes_backup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            user_profile = workspace / "user"
            target = user_profile / ".codex" / "AGENTS.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            old_text = "# AGENTS.md\n**版本**: 9.43\nold\n"
            target.write_text(old_text, encoding="utf-8")
            manifest = json.loads((ROOT / "rules" / "manifest.json").read_text(encoding="utf-8"))
            manifest["backup_policy"] = {"enabled": True, "root": str(workspace / "backups")}
            manifest_path = workspace / "manifest.json"
            _write_json(manifest_path, manifest)

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/sync-agent-rules.py",
                    "--scope",
                    "Global",
                    "--manifest-path",
                    str(manifest_path),
                    "--user-profile",
                    str(user_profile),
                    "--apply",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "applied")
            updated = [item for item in payload["results"] if item["id"] == "global-codex-agents"][0]
            self.assertEqual(updated["status"], "updated")
            self.assertIn(f"GlobalUser/AGENTS.md v{manifest['default_version']}", target.read_text(encoding="utf-8"))
            backup_path = Path(updated["backup_path"])
            self.assertTrue(backup_path.exists())
            self.assertNotEqual(backup_path.resolve(strict=False), target.resolve(strict=False))
            self.assertEqual(backup_path.read_text(encoding="utf-8"), old_text)


if __name__ == "__main__":
    unittest.main()
