import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class TargetRepoGovernanceConsistencyTests(unittest.TestCase):
    def test_default_baseline_requires_windows_process_environment_policy(self) -> None:
        baseline_path = ROOT / "docs" / "targets" / "target-repo-governance-baseline.json"
        baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
        policy = baseline["required_profile_overrides"]["windows_process_environment_policy"]

        self.assertTrue(policy["enabled"])
        self.assertIn("ComSpec", policy["required_variables"])
        self.assertIn("SystemRoot", policy["required_variables"])
        self.assertIn("PROGRAMDATA", policy["required_variables"])
        self.assertIn("coding_guidance", policy)
        self.assertIn("process_environment_incomplete", " ".join(policy["coding_guidance"]))
        self.assertIn("Initialize-WindowsProcessEnvironment", policy["powershell_entrypoint_pattern"])
        self.assertIn("python -c", policy["verification_commands"][0])
        self.assertIn("node -e", policy["verification_commands"][1])

    def test_apply_target_repo_governance_updates_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "repo-a"
            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            _write_json(
                profile_path,
                {
                    "repo_id": "repo-a",
                    "required_entrypoint_policy": {"current_mode": "advisory"},
                    "auto_commit_policy": {"enabled": False},
                },
            )
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-23.1",
                    "required_profile_overrides": {
                        "required_entrypoint_policy": {"current_mode": "targeted_enforced"},
                        "auto_commit_policy": {"enabled": True, "on": ["milestone"]},
                    },
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/apply-target-repo-governance.py",
                    "--target-repo",
                    str(target_repo),
                    "--baseline-path",
                    str(baseline_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "applied")
            updated_profile = json.loads(profile_path.read_text(encoding="utf-8"))
            self.assertEqual(updated_profile["required_entrypoint_policy"]["current_mode"], "targeted_enforced")
            self.assertEqual(updated_profile["auto_commit_policy"]["enabled"], True)

    def test_verify_target_repo_governance_consistency_passes_on_matched_profiles(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_root = workspace / "runtime"
            code_root = workspace / "code"
            runtime_state_base = repo_root / ".runtime" / "attachments"
            repo_root.mkdir(parents=True)
            code_root.mkdir(parents=True)

            baseline_overrides = {
                "required_entrypoint_policy": {"current_mode": "targeted_enforced"},
                "auto_commit_policy": {"enabled": True, "on": ["milestone"]},
            }
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-23.1",
                    "required_profile_overrides": baseline_overrides,
                },
            )

            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "catalog_id": "test",
                    "targets": {
                        "repo-a": {
                            "attachment_root": "${code_root}/repo-a",
                            "attachment_runtime_state_root": "${runtime_state_base}/repo-a",
                        },
                        "repo-b": {
                            "attachment_root": "${code_root}/repo-b",
                            "attachment_runtime_state_root": "${runtime_state_base}/repo-b",
                        },
                    },
                },
            )

            for repo_name in ("repo-a", "repo-b"):
                _write_json(
                    code_root / repo_name / ".governed-ai" / "repo-profile.json",
                    {
                        "repo_id": repo_name,
                        "required_entrypoint_policy": {"current_mode": "targeted_enforced"},
                        "auto_commit_policy": {"enabled": True, "on": ["milestone"]},
                    },
                )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/verify-target-repo-governance-consistency.py",
                    "--catalog-path",
                    str(catalog_path),
                    "--baseline-path",
                    str(baseline_path),
                    "--repo-root",
                    str(repo_root),
                    "--code-root",
                    str(code_root),
                    "--runtime-state-base",
                    str(runtime_state_base),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["drift_count"], 0)

    def test_verify_target_repo_governance_consistency_fails_on_profile_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_root = workspace / "runtime"
            code_root = workspace / "code"
            runtime_state_base = repo_root / ".runtime" / "attachments"
            repo_root.mkdir(parents=True)
            code_root.mkdir(parents=True)

            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-23.1",
                    "required_profile_overrides": {
                        "required_entrypoint_policy": {"current_mode": "targeted_enforced"},
                        "auto_commit_policy": {"enabled": True, "on": ["milestone"]},
                    },
                },
            )
            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "catalog_id": "test",
                    "targets": {
                        "repo-a": {
                            "attachment_root": "${code_root}/repo-a",
                            "attachment_runtime_state_root": "${runtime_state_base}/repo-a",
                        }
                    },
                },
            )
            _write_json(
                code_root / "repo-a" / ".governed-ai" / "repo-profile.json",
                {
                    "repo_id": "repo-a",
                    "required_entrypoint_policy": {"current_mode": "advisory"},
                    "auto_commit_policy": {"enabled": False},
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/verify-target-repo-governance-consistency.py",
                    "--catalog-path",
                    str(catalog_path),
                    "--baseline-path",
                    str(baseline_path),
                    "--repo-root",
                    str(repo_root),
                    "--code-root",
                    str(code_root),
                    "--runtime-state-base",
                    str(runtime_state_base),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "fail")
            self.assertEqual(payload["drift_count"], 1)
            self.assertEqual(payload["drift"][0]["target"], "repo-a")
            self.assertIn("auto_commit_policy", payload["drift"][0]["mismatched_fields"])


if __name__ == "__main__":
    unittest.main()
