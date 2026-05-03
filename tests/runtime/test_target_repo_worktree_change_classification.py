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


@unittest.skipIf(shutil.which("git") is None, "git is required for worktree classification tests")
class TargetRepoWorktreeChangeClassificationTests(unittest.TestCase):
    def test_classifies_managed_rule_profile_and_unrelated_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            code_root = workspace / "code"
            target_repo = code_root / "sample-repo"
            target_repo.mkdir(parents=True)
            subprocess.run(["git", "init"], cwd=target_repo, check=True, capture_output=True, text=True)

            (target_repo / "AGENTS.md").write_text("# managed rule\n", encoding="utf-8")
            (target_repo / ".governed-ai" / "repo-profile.json").parent.mkdir(parents=True)
            (target_repo / ".governed-ai" / "repo-profile.json").write_text("{}\n", encoding="utf-8")
            provenance = target_repo / ".governed-ai" / "managed-files" / ".claude" / "settings.json.provenance.json"
            provenance.parent.mkdir(parents=True)
            provenance.write_text("{}\n", encoding="utf-8")
            (target_repo / "README.md").write_text("# local change\n", encoding="utf-8")

            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "targets": {
                        "sample": {
                            "attachment_root": "${code_root}/sample-repo",
                            "attachment_runtime_state_root": "${runtime_state_base}/sample",
                        }
                    },
                },
            )
            manifest_path = workspace / "manifest.json"
            _write_json(
                manifest_path,
                {
                    "schema_version": "1.0",
                    "entries": [
                        {
                            "id": "sample-codex-agents",
                            "scope": "project",
                            "tool": "codex",
                            "target_repo_id": "sample",
                            "target_path": "AGENTS.md",
                            "source": "rules/projects/sample/codex/AGENTS.md",
                            "version": "1.0",
                        }
                    ],
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/classify-target-repo-worktree-changes.py",
                    "--catalog-path",
                    str(catalog_path),
                    "--manifest-path",
                    str(manifest_path),
                    "--code-root",
                    str(code_root),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "attention")
            self.assertEqual(payload["target_count"], 1)
            self.assertEqual(payload["unrelated_change_count"], 1)
            result = payload["results"][0]
            self.assertEqual(result["status"], "attention")
            self.assertEqual(result["managed_change_count"], 3)
            self.assertEqual(result["unrelated_change_count"], 1)
            categories = {item["path"]: item["category"] for item in result["changes"]}
            self.assertEqual(categories["AGENTS.md"], "managed_rule_file")
            self.assertEqual(categories[".governed-ai/repo-profile.json"], "managed_repo_profile")
            self.assertEqual(
                categories[".governed-ai/managed-files/.claude/settings.json.provenance.json"],
                "managed_file_provenance",
            )
            self.assertEqual(categories["README.md"], "target_local_unrelated")

    def test_fail_on_unrelated_returns_nonzero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            code_root = workspace / "code"
            target_repo = code_root / "sample-repo"
            target_repo.mkdir(parents=True)
            subprocess.run(["git", "init"], cwd=target_repo, check=True, capture_output=True, text=True)
            (target_repo / "README.md").write_text("# local change\n", encoding="utf-8")

            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "targets": {
                        "sample": {
                            "attachment_root": "${code_root}/sample-repo",
                            "attachment_runtime_state_root": "${runtime_state_base}/sample",
                        }
                    },
                },
            )
            manifest_path = workspace / "manifest.json"
            _write_json(manifest_path, {"schema_version": "1.0", "entries": []})

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/classify-target-repo-worktree-changes.py",
                    "--catalog-path",
                    str(catalog_path),
                    "--manifest-path",
                    str(manifest_path),
                    "--code-root",
                    str(code_root),
                    "--fail-on-unrelated",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 1)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "attention")
            self.assertEqual(payload["unrelated_change_count"], 1)

    def test_output_path_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            code_root = workspace / "code"
            target_repo = code_root / "sample-repo"
            target_repo.mkdir(parents=True)
            subprocess.run(["git", "init"], cwd=target_repo, check=True, capture_output=True, text=True)

            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "targets": {
                        "sample": {
                            "attachment_root": "${code_root}/sample-repo",
                            "attachment_runtime_state_root": "${runtime_state_base}/sample",
                        }
                    },
                },
            )
            manifest_path = workspace / "manifest.json"
            _write_json(manifest_path, {"schema_version": "1.0", "entries": []})
            output_path = workspace / "report.json"

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/classify-target-repo-worktree-changes.py",
                    "--catalog-path",
                    str(catalog_path),
                    "--manifest-path",
                    str(manifest_path),
                    "--code-root",
                    str(code_root),
                    "--output-path",
                    str(output_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue(output_path.exists())
            self.assertEqual(json.loads(completed.stdout), json.loads(output_path.read_text(encoding="utf-8")))

    def test_self_runtime_control_repo_changes_are_not_target_unrelated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_root = workspace / "runtime"
            repo_root.mkdir(parents=True)
            subprocess.run(["git", "init"], cwd=repo_root, check=True, capture_output=True, text=True)
            (repo_root / "rules").mkdir()
            (repo_root / "rules" / "manifest.json").write_text("{}\n", encoding="utf-8")
            (repo_root / "README.md").write_text("# current task change\n", encoding="utf-8")

            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "targets": {
                        "self-runtime": {
                            "attachment_root": "${repo_root}",
                            "attachment_runtime_state_root": "${runtime_state_base}/self-runtime",
                        }
                    },
                },
            )
            manifest_path = workspace / "manifest.json"
            _write_json(manifest_path, {"schema_version": "1.0", "entries": []})

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/classify-target-repo-worktree-changes.py",
                    "--catalog-path",
                    str(catalog_path),
                    "--manifest-path",
                    str(manifest_path),
                    "--repo-root",
                    str(repo_root),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["unrelated_change_count"], 0)
            result = payload["results"][0]
            self.assertEqual(result["status"], "managed_only")
            categories = {item["path"]: item["category"] for item in result["changes"]}
            self.assertEqual(categories["README.md"], "control_repo_current_change")
            self.assertEqual(categories["rules/manifest.json"], "control_repo_current_change")


if __name__ == "__main__":
    unittest.main()
