import json
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
    def test_default_manifest_covers_global_and_project_rule_sources(self) -> None:
        manifest_path = ROOT / "rules" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries = manifest["entries"]
        ids = [entry["id"] for entry in entries]
        global_entries = [entry for entry in entries if entry["scope"] == "global"]
        project_entries = [entry for entry in entries if entry["scope"] == "project"]

        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(global_entries), 3)
        self.assertEqual(len(project_entries), 15)
        self.assertEqual({entry["tool"] for entry in global_entries}, {"codex", "claude", "gemini"})
        self.assertIn("self-runtime", {entry["target_repo_id"] for entry in project_entries})
        self.assertIn("vps-ssh-launcher", {entry["target_repo_id"] for entry in project_entries})
        for entry in entries:
            self.assertEqual(entry["version"], "9.44")
            self.assertTrue((ROOT / entry["source"]).exists(), entry["source"])

    def test_global_sync_skips_when_hashes_match(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            user_profile = Path(tmp_dir) / "user"
            copies = {
                user_profile / ".codex" / "AGENTS.md": ROOT / "rules" / "global" / "codex" / "AGENTS.md",
                user_profile / ".claude" / "CLAUDE.md": ROOT / "rules" / "global" / "claude" / "CLAUDE.md",
                user_profile / ".gemini" / "GEMINI.md": ROOT / "rules" / "global" / "gemini" / "GEMINI.md",
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
            self.assertEqual({item["status"] for item in payload["results"]}, {"skipped_same_hash"})

    def test_global_sync_blocks_same_version_content_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            user_profile = Path(tmp_dir) / "user"
            copies = {
                user_profile / ".codex" / "AGENTS.md": ROOT / "rules" / "global" / "codex" / "AGENTS.md",
                user_profile / ".claude" / "CLAUDE.md": ROOT / "rules" / "global" / "claude" / "CLAUDE.md",
                user_profile / ".gemini" / "GEMINI.md": ROOT / "rules" / "global" / "gemini" / "GEMINI.md",
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

    def test_project_apply_updates_older_version_and_writes_backup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            code_root = workspace / "code"
            target_repo = code_root / "ClassroomToolkit"
            target_repo.mkdir(parents=True)
            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "catalog_id": "test",
                    "targets": {
                        "classroomtoolkit": {
                            "attachment_root": "${code_root}/ClassroomToolkit",
                            "attachment_runtime_state_root": "${runtime_state_base}/classroomtoolkit",
                        }
                    },
                },
            )
            manifest = json.loads((ROOT / "rules" / "manifest.json").read_text(encoding="utf-8"))
            manifest["backup_policy"] = {"enabled": True, "root": str(workspace / "backups")}
            manifest_path = workspace / "manifest.json"
            _write_json(manifest_path, manifest)
            existing = target_repo / "AGENTS.md"
            old_text = "# AGENTS.md\n**承接来源**: `GlobalUser/AGENTS.md v9.43`\nold\n"
            existing.write_text(old_text, encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/sync-agent-rules.py",
                    "--scope",
                    "Targets",
                    "--target",
                    "classroomtoolkit",
                    "--manifest-path",
                    str(manifest_path),
                    "--catalog-path",
                    str(catalog_path),
                    "--code-root",
                    str(code_root),
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
            self.assertTrue((target_repo / "CLAUDE.md").exists())
            self.assertTrue((target_repo / "GEMINI.md").exists())
            self.assertIn("GlobalUser/AGENTS.md v9.44", existing.read_text(encoding="utf-8"))
            updated = [item for item in payload["results"] if item["id"] == "classroomtoolkit-codex-agents"][0]
            self.assertEqual(updated["status"], "updated")
            backup_path = Path(updated["backup_path"])
            self.assertTrue(backup_path.exists())
            self.assertNotEqual(backup_path.resolve(strict=False), existing.resolve(strict=False))
            self.assertEqual(backup_path.read_text(encoding="utf-8"), old_text)


if __name__ == "__main__":
    unittest.main()

