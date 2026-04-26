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
        interaction = baseline["required_profile_overrides"]["interaction_profile"]
        coordination = baseline["required_profile_overrides"]["rule_file_coordination_policy"]
        policy = baseline["required_profile_overrides"]["windows_process_environment_policy"]
        managed_files = baseline["required_managed_files"]

        self.assertEqual(interaction["communication_language"], "zh-CN")
        self.assertEqual(interaction["user_facing_output_language"], "zh-CN")
        self.assertEqual(interaction["preserve_technical_tokens_language"], "original")
        self.assertEqual(interaction["commit_message_language"], "zh-CN")
        self.assertIn("Communicate", " ".join(interaction["language_guidance"]))
        self.assertTrue(coordination["enabled"])
        self.assertIn("WHAT", coordination["global_rule_scope"])
        self.assertIn("WHERE/HOW", coordination["project_rule_scope"])
        self.assertIn("non-overlapping", coordination["synergy_requirement"])
        self.assertIn("Claude Code memory guidance", " ".join(coordination["source_review_basis"]))
        self.assertIn("constraint-oriented", " ".join(coordination["source_review_basis"]))
        self.assertIn("verifiable acceptance criteria", " ".join(coordination["root_file_quality_rules"]))
        self.assertIn("root-to-cwd", coordination["tool_specific_loading_policy"]["codex"])
        self.assertIn("do not assume CLAUDE.override.md", coordination["tool_specific_loading_policy"]["claude"])
        self.assertIn("/memory list/show/refresh", coordination["tool_specific_loading_policy"]["gemini"])
        self.assertTrue(coordination["progressive_disclosure"]["allowed"])
        self.assertTrue(coordination["progressive_disclosure"]["root_file_must_remain_self_contained"])
        self.assertIn("gate_commands", coordination["required_project_rule_fields"])
        self.assertIn("medium/high-risk", coordination["missing_project_rule_behavior"])
        self.assertTrue(policy["enabled"])
        self.assertIn("ComSpec", policy["required_variables"])
        self.assertIn("SystemRoot", policy["required_variables"])
        self.assertIn("PROGRAMDATA", policy["required_variables"])
        self.assertIn("ProgramFiles", policy["required_variables"])
        self.assertIn("HTTP_PROXY", policy["inherited_network_variables"])
        self.assertIn("HTTPS_PROXY", policy["inherited_network_variables"])
        self.assertIn("NO_PROXY", policy["inherited_network_variables"])
        self.assertIn("shell_environment_policy.set", policy["safe_codex_policy_source"])
        self.assertEqual(policy["preferred_powershell_executable"], "pwsh")
        self.assertEqual(policy["fallback_powershell_executable"], "powershell")
        self.assertEqual(policy["windows_powershell_escape_hatch_env"], "CODEX_ALLOW_WINDOWS_POWERSHELL")
        self.assertIn("coding_guidance", policy)
        self.assertIn("process_environment_incomplete", " ".join(policy["coding_guidance"]))
        self.assertIn("os error 11003", " ".join(policy["coding_guidance"]))
        self.assertIn("codex.cmd", " ".join(policy["coding_guidance"]))
        self.assertIn("PowerShell 7", " ".join(policy["coding_guidance"]))
        self.assertIn("Resolve-PowerShellExecutable", " ".join(policy["coding_guidance"]))
        self.assertIn("git or gh", " ".join(policy["coding_guidance"]))
        self.assertIn("Initialize-WindowsProcessEnvironment", policy["powershell_entrypoint_pattern"])
        self.assertIn("python -c", policy["verification_commands"][0])
        self.assertIn("node -e", policy["verification_commands"][1])
        self.assertIn(".governed-ai/verify-powershell-policy.py", [item["path"] for item in managed_files])

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
                    "required_managed_files": [
                        {
                            "path": ".governed-ai/verify-powershell-policy.py",
                            "source": str(ROOT / "docs" / "targets" / "templates" / "verify-powershell-policy.py"),
                        }
                    ],
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
            self.assertEqual(payload["changed_managed_files"][0]["path"], ".governed-ai/verify-powershell-policy.py")
            updated_profile = json.loads(profile_path.read_text(encoding="utf-8"))
            self.assertEqual(updated_profile["required_entrypoint_policy"]["current_mode"], "targeted_enforced")
            self.assertEqual(updated_profile["auto_commit_policy"]["enabled"], True)
            self.assertTrue((target_repo / ".governed-ai" / "verify-powershell-policy.py").exists())

    def test_apply_target_repo_governance_check_only_fails_on_managed_file_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "repo-a"
            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            _write_json(profile_path, {"repo_id": "repo-a"})
            template_path = workspace / "template.py"
            template_path.write_text("print('guard')\n", encoding="utf-8")
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-26.1",
                    "required_managed_files": [
                        {
                            "path": ".governed-ai/verify-powershell-policy.py",
                            "source": str(template_path),
                        }
                    ],
                    "required_profile_overrides": {"auto_commit_policy": {"enabled": True}},
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
                    "--check-only",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "drift")
            self.assertEqual(payload["changed_managed_files"][0]["reason"], "missing")

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

    def test_verify_target_repo_governance_consistency_fails_on_managed_file_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_root = workspace / "runtime"
            code_root = workspace / "code"
            runtime_state_base = repo_root / ".runtime" / "attachments"
            repo_root.mkdir(parents=True)
            code_root.mkdir(parents=True)

            template_path = workspace / "verify-powershell-policy.py"
            template_path.write_text("print('guard')\n", encoding="utf-8")
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-26.1",
                    "required_managed_files": [
                        {
                            "path": ".governed-ai/verify-powershell-policy.py",
                            "source": str(template_path),
                        }
                    ],
                    "required_profile_overrides": {
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

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "fail")
            self.assertEqual(payload["drift"][0]["reason"], "managed_file_drift")
            self.assertEqual(payload["drift"][0]["mismatched_managed_files"][0]["reason"], "missing")


if __name__ == "__main__":
    unittest.main()
