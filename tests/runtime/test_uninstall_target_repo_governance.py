import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_ROOT = ROOT / "scripts"
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from lib.target_repo_quick_test_prompt import build_quick_test_slice_prompt


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _load_uninstall_module():
    path = ROOT / "scripts" / "uninstall-target-repo-governance.py"
    spec = importlib.util.spec_from_file_location("uninstall_target_repo_governance_script", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load script: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["uninstall_target_repo_governance_script"] = module
    spec.loader.exec_module(module)
    return module


class UninstallTargetRepoGovernanceTests(unittest.TestCase):
    def test_uninstall_governance_dry_run_keeps_files_and_reports_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            source = workspace / "templates" / "managed.py"
            settings_source = workspace / "templates" / "settings.json"
            _write_text(source, "print('managed')\n")
            _write_text(target / ".governed-ai" / "managed.py", "print('managed')\n")
            _write_json(settings_source, {"permissions": {"deny": ["Bash(powershell:*)"]}})
            _write_json(
                target / ".claude" / "settings.json",
                {
                    "permissions": {"deny": ["Bash(powershell:*)", "Read(**/.env)"]},
                    "local": {"keep": True},
                },
            )
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "required_managed_files": [
                        {"path": ".governed-ai/managed.py", "source": str(source), "management_mode": "block_on_drift"},
                        {"path": ".claude/settings.json", "source": str(settings_source), "management_mode": "json_merge"},
                    ],
                    "generated_managed_files": [],
                    "retired_managed_files": [],
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/uninstall-target-repo-governance.py",
                    "--target-repo",
                    str(target),
                    "--baseline-path",
                    str(baseline_path),
                    "--dry-run",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 2, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["summary"]["delete_candidates"], 1)
            self.assertEqual(payload["summary"]["shared_patch_candidates"], 0)
            self.assertEqual(payload["summary"]["blocked"], 1)
            self.assertEqual(payload["blocked_files"][0]["reason"], "shared_patch_requires_ownership_evidence")
            self.assertTrue((target / ".governed-ai" / "managed.py").exists())
            self.assertTrue((target / ".claude" / "settings.json").exists())

    def test_uninstall_governance_blocks_without_partial_delete_or_unverified_shared_patch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            source = workspace / "templates" / "managed.py"
            drift_source = workspace / "templates" / "drifted.py"
            settings_source = workspace / "templates" / "settings.json"
            backup_root = workspace / "backups"
            _write_text(source, "print('managed')\n")
            _write_text(drift_source, "print('managed')\n")
            _write_text(target / ".governed-ai" / "managed.py", "print('managed')\n")
            _write_text(target / ".governed-ai" / "drifted.py", "target edit\n")
            _write_json(settings_source, {"permissions": {"deny": ["Bash(powershell:*)"]}})
            _write_json(
                target / ".claude" / "settings.json",
                {
                    "permissions": {"deny": ["Bash(powershell:*)", "Read(**/.env)"]},
                    "local": {"keep": True},
                },
            )
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "required_managed_files": [
                        {"path": ".governed-ai/managed.py", "source": str(source), "management_mode": "block_on_drift"},
                        {"path": ".governed-ai/drifted.py", "source": str(drift_source), "management_mode": "block_on_drift"},
                        {"path": ".claude/settings.json", "source": str(settings_source), "management_mode": "json_merge"},
                    ],
                    "generated_managed_files": [],
                    "retired_managed_files": [],
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/uninstall-target-repo-governance.py",
                    "--target-repo",
                    str(target),
                    "--baseline-path",
                    str(baseline_path),
                    "--backup-root",
                    str(backup_root),
                    "--apply",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 2, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "blocked")
            self.assertEqual(payload["summary"]["deleted"], 0)
            self.assertEqual(payload["summary"]["shared_patched"], 0)
            self.assertEqual(payload["summary"]["blocked"], 2)
            self.assertTrue((target / ".governed-ai" / "managed.py").exists())
            self.assertTrue((target / ".governed-ai" / "drifted.py").exists())
            settings = json.loads((target / ".claude" / "settings.json").read_text(encoding="utf-8"))
            self.assertEqual(settings["permissions"]["deny"], ["Bash(powershell:*)", "Read(**/.env)"])
            self.assertEqual(settings["local"], {"keep": True})
            reasons = {item["reason"] for item in payload["blocked_files"]}
            self.assertIn("expected_content_differs", reasons)
            self.assertIn("shared_patch_requires_ownership_evidence", reasons)
            self.assertEqual(payload["deleted_files"], [])
            self.assertEqual(payload["patched_shared_files"], [])

    def test_uninstall_governance_blocks_malformed_shared_json_with_structured_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            settings_source = workspace / "templates" / "settings.json"
            _write_json(settings_source, {"permissions": {"deny": ["Bash(powershell:*)"]}})
            _write_text(target / ".claude" / "settings.json", "{ invalid json")
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "required_managed_files": [
                        {
                            "path": ".claude/settings.json",
                            "source": str(settings_source),
                            "management_mode": "json_merge",
                            "shared_ownership_evidence": ["permissions.deny entries from template"],
                        },
                    ],
                    "generated_managed_files": [],
                    "retired_managed_files": [],
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/uninstall-target-repo-governance.py",
                    "--target-repo",
                    str(target),
                    "--baseline-path",
                    str(baseline_path),
                    "--dry-run",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 2, completed.stderr)
            self.assertNotIn("Traceback", completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "blocked")
            self.assertEqual(payload["summary"]["blocked"], 1)
            self.assertEqual(payload["blocked_files"][0]["path"], ".claude/settings.json")
            self.assertEqual(payload["blocked_files"][0]["reason"], "invalid_json")
            self.assertIn("line 1 column", payload["blocked_files"][0]["error"])

    def test_uninstall_governance_blocks_generated_files_without_hash_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            prompt_text = "target-local quick test prompt improvement\n"
            _write_text(target / ".governed-ai" / "quick-test-slice.prompt.md", prompt_text)
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "required_managed_files": [],
                    "generated_managed_files": [
                        {
                            "path": ".governed-ai/quick-test-slice.prompt.md",
                            "generator": "outer_ai_quick_test_prompt",
                            "management_mode": "block_on_drift",
                        }
                    ],
                    "retired_managed_files": [],
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/uninstall-target-repo-governance.py",
                    "--target-repo",
                    str(target),
                    "--baseline-path",
                    str(baseline_path),
                    "--apply",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 2, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["summary"]["deleted"], 0)
            self.assertEqual(payload["blocked_files"][0]["reason"], "generated_managed_hash_missing")
            self.assertTrue((target / ".governed-ai" / "quick-test-slice.prompt.md").exists())

    def test_uninstall_governance_deletes_generated_file_when_hash_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            backup_root = workspace / "backups"
            prompt_text = "generated quick test prompt\n"
            _write_text(target / ".governed-ai" / "quick-test-slice.prompt.md", prompt_text)
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "required_managed_files": [],
                    "generated_managed_files": [
                        {
                            "path": ".governed-ai/quick-test-slice.prompt.md",
                            "generator": "outer_ai_quick_test_prompt",
                            "management_mode": "block_on_drift",
                            "expected_sha256": f"sha256:{_sha256(prompt_text)}",
                        }
                    ],
                    "retired_managed_files": [],
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/uninstall-target-repo-governance.py",
                    "--target-repo",
                    str(target),
                    "--baseline-path",
                    str(baseline_path),
                    "--backup-root",
                    str(backup_root),
                    "--apply",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["summary"]["deleted"], 1)
            self.assertFalse((target / ".governed-ai" / "quick-test-slice.prompt.md").exists())
            self.assertTrue(Path(payload["deleted_files"][0]["backup_path"]).exists())

    def test_uninstall_governance_deletes_generated_prompt_when_computed_hash_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            backup_root = workspace / "backups"
            profile = {
                "repo_id": "target",
                "display_name": "Target",
                "primary_language": "python",
                "quick_gate_commands": [{"id": "unit", "command": "python -m unittest"}],
                "quick_test_command": "python -m unittest",
                "quick_test_reason": "Focused regression slice.",
            }
            _write_json(target / ".governed-ai" / "repo-profile.json", profile)
            prompt_text = build_quick_test_slice_prompt(target_repo=target, profile=profile)
            _write_text(target / ".governed-ai" / "quick-test-slice.prompt.md", prompt_text)
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "required_managed_files": [],
                    "generated_managed_files": [
                        {
                            "path": ".governed-ai/quick-test-slice.prompt.md",
                            "generator": "outer_ai_quick_test_prompt",
                            "management_mode": "block_on_drift",
                        }
                    ],
                    "retired_managed_files": [],
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/uninstall-target-repo-governance.py",
                    "--target-repo",
                    str(target),
                    "--baseline-path",
                    str(baseline_path),
                    "--backup-root",
                    str(backup_root),
                    "--apply",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["summary"]["deleted"], 1)
            self.assertFalse((target / ".governed-ai" / "quick-test-slice.prompt.md").exists())
            self.assertTrue(Path(payload["deleted_files"][0]["backup_path"]).exists())

    def test_uninstall_governance_blocks_referenced_managed_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            source = workspace / "templates" / "managed.py"
            _write_text(source, "print('managed')\n")
            _write_text(target / ".governed-ai" / "managed.py", "print('managed')\n")
            _write_text(target / ".github" / "workflows" / "ci.yml", "python .governed-ai/managed.py\n")
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "required_managed_files": [
                        {"path": ".governed-ai/managed.py", "source": str(source), "management_mode": "block_on_drift"},
                    ],
                    "generated_managed_files": [],
                    "retired_managed_files": [],
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/uninstall-target-repo-governance.py",
                    "--target-repo",
                    str(target),
                    "--baseline-path",
                    str(baseline_path),
                    "--apply",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 2, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["blocked_files"][0]["reason"], "active_references")
            self.assertEqual(payload["blocked_files"][0]["referenced_by"], [".github/workflows/ci.yml"])
            self.assertTrue((target / ".governed-ai" / "managed.py").exists())

    def test_uninstall_governance_removes_runtime_owned_profile_fields_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            _write_json(
                target / ".governed-ai" / "repo-profile.json",
                {
                    "repo_id": "target",
                    "display_name": "Target",
                    "required_entrypoint_policy": {"current_mode": "targeted_enforced"},
                    "auto_commit_policy": {"enabled": True},
                    "quick_gate_commands": [{"id": "test", "command": "pytest"}],
                    "full_gate_commands": [{"id": "test", "command": "pytest"}],
                    "gate_timeout_seconds": 300,
                    "target_owned": {"keep": True},
                },
            )
            baseline_path = workspace / "baseline.json"
            backup_root = workspace / "backups"
            _write_json(
                baseline_path,
                {
                    "required_managed_files": [],
                    "generated_managed_files": [],
                    "retired_managed_files": [],
                    "repo_profile_field_ownership": {
                        "baseline_override_fields": ["required_entrypoint_policy", "auto_commit_policy"],
                        "derived_runtime_fields": ["quick_gate_commands", "full_gate_commands", "gate_timeout_seconds"],
                        "catalog_input_fields": ["repo_id", "display_name"],
                    },
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/uninstall-target-repo-governance.py",
                    "--target-repo",
                    str(target),
                    "--baseline-path",
                    str(baseline_path),
                    "--backup-root",
                    str(backup_root),
                    "--apply",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["summary"]["profile_patch_candidates"], 1)
            self.assertEqual(payload["summary"]["profile_patched"], 1)
            profile = json.loads((target / ".governed-ai" / "repo-profile.json").read_text(encoding="utf-8"))
            self.assertEqual(profile["repo_id"], "target")
            self.assertEqual(profile["display_name"], "Target")
            self.assertEqual(profile["target_owned"], {"keep": True})
            self.assertNotIn("required_entrypoint_policy", profile)
            self.assertNotIn("auto_commit_policy", profile)
            self.assertNotIn("quick_gate_commands", profile)
            self.assertNotIn("full_gate_commands", profile)
            self.assertNotIn("gate_timeout_seconds", profile)
            self.assertTrue(Path(payload["patched_profile_files"][0]["backup_path"]).exists())

    def test_uninstall_governance_blocks_malformed_repo_profile_with_structured_reason(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            _write_text(target / ".governed-ai" / "repo-profile.json", "{ invalid json")
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "required_managed_files": [],
                    "generated_managed_files": [],
                    "retired_managed_files": [],
                    "repo_profile_field_ownership": {
                        "baseline_override_fields": ["required_entrypoint_policy"],
                    },
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/uninstall-target-repo-governance.py",
                    "--target-repo",
                    str(target),
                    "--baseline-path",
                    str(baseline_path),
                    "--apply",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 2, completed.stderr)
            self.assertNotIn("Traceback", completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "blocked")
            self.assertEqual(payload["summary"]["profile_patch_candidates"], 0)
            self.assertEqual(payload["blocked_files"][0]["reason"], "repo_profile_invalid_json")

    def test_uninstall_governance_removes_runtime_sidecars_without_self_reference_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            verify_source = workspace / "templates" / "verify-powershell-policy.py"
            hook_source = workspace / "templates" / "governed-pre-tool-use.py"
            settings_source = workspace / "templates" / "settings.json"
            verify_text = "print('verify')\n"
            hook_text = "print('hook')\n"
            settings_overlay = {
                "hooks": {
                    "PreToolUse": [
                        {
                            "matcher": "Write",
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": ".claude/hooks/governed-pre-tool-use.py",
                                }
                            ],
                        }
                    ]
                },
                "permissions": {"deny": ["Bash(powershell:*)"]},
            }
            _write_text(verify_source, verify_text)
            _write_text(hook_source, hook_text)
            _write_json(settings_source, settings_overlay)
            _write_text(target / ".governed-ai" / "verify-powershell-policy.py", verify_text)
            _write_text(target / ".claude" / "hooks" / "governed-pre-tool-use.py", hook_text)
            _write_json(
                target / ".claude" / "settings.json",
                {
                    **settings_overlay,
                    "local": {"keep": True},
                },
            )
            _write_json(
                target
                / ".governed-ai"
                / "managed-files"
                / ".governed-ai"
                / "verify-powershell-policy.py.provenance.json",
                {"path": ".governed-ai/verify-powershell-policy.py"},
            )
            _write_json(
                target
                / ".governed-ai"
                / "managed-files"
                / ".claude"
                / "hooks"
                / "governed-pre-tool-use.py.provenance.json",
                {"path": ".claude/hooks/governed-pre-tool-use.py"},
            )
            _write_json(
                target
                / ".governed-ai"
                / "managed-files"
                / ".claude"
                / "settings.json.provenance.json",
                {"path": ".claude/settings.json"},
            )
            baseline_path = workspace / "baseline.json"
            backup_root = workspace / "backups"
            _write_json(
                baseline_path,
                {
                    "required_managed_files": [
                        {
                            "path": ".governed-ai/verify-powershell-policy.py",
                            "source": str(verify_source),
                            "management_mode": "block_on_drift",
                        },
                        {
                            "path": ".claude/settings.json",
                            "source": str(settings_source),
                            "management_mode": "json_merge",
                            "shared_ownership_evidence": ["hooks and permissions overlay"],
                        },
                        {
                            "path": ".claude/hooks/governed-pre-tool-use.py",
                            "source": str(hook_source),
                            "management_mode": "block_on_drift",
                        },
                    ],
                    "generated_managed_files": [],
                    "retired_managed_files": [],
                    "repo_profile_field_ownership": {},
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/uninstall-target-repo-governance.py",
                    "--target-repo",
                    str(target),
                    "--baseline-path",
                    str(baseline_path),
                    "--backup-root",
                    str(backup_root),
                    "--apply",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
            payload = json.loads(completed.stdout)
            deleted_paths = {item["path"] for item in payload["deleted_files"]}
            self.assertIn(".governed-ai/verify-powershell-policy.py", deleted_paths)
            self.assertIn(".claude/hooks/governed-pre-tool-use.py", deleted_paths)
            self.assertIn(
                ".governed-ai/managed-files/.governed-ai/verify-powershell-policy.py.provenance.json",
                deleted_paths,
            )
            self.assertIn(
                ".governed-ai/managed-files/.claude/hooks/governed-pre-tool-use.py.provenance.json",
                deleted_paths,
            )
            self.assertEqual(payload["summary"]["blocked"], 0)
            self.assertEqual(payload["summary"]["shared_patched"], 1)
            settings = json.loads((target / ".claude" / "settings.json").read_text(encoding="utf-8"))
            self.assertEqual(settings, {"local": {"keep": True}})
            manifest_path = backup_root / "manifest.json"
            self.assertTrue(manifest_path.exists())
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["summary"]["deleted"], payload["summary"]["deleted"])
            self.assertEqual(manifest["summary"]["shared_patched"], 1)

    def test_uninstall_governance_blocks_when_delete_target_changes_after_backup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            source = workspace / "templates" / "managed.py"
            target_path = target / ".governed-ai" / "managed.py"
            managed_text = "print('managed')\n"
            _write_text(source, managed_text)
            _write_text(target_path, managed_text)
            baseline = {
                "required_managed_files": [
                    {"path": ".governed-ai/managed.py", "source": str(source), "management_mode": "block_on_drift"},
                ],
                "generated_managed_files": [],
                "retired_managed_files": [],
                "repo_profile_field_ownership": {},
            }
            backup_root = workspace / "backups"
            module = _load_uninstall_module()
            original_copy2 = module.shutil.copy2

            def copy_then_mutate(src, dst):
                result = original_copy2(src, dst)
                target_path.write_text("changed after backup\n", encoding="utf-8")
                return result

            with mock.patch.object(module.shutil, "copy2", side_effect=copy_then_mutate):
                payload, exit_code = module.uninstall_target_repo_governance(
                    target_repo=target,
                    baseline=baseline,
                    backup_root=backup_root,
                    dry_run=False,
                    apply=True,
                )

            self.assertEqual(exit_code, 2)
            self.assertEqual(payload["status"], "blocked")
            self.assertEqual(payload["summary"]["deleted"], 0)
            self.assertEqual(payload["blocked_files"][0]["reason"], "target_changed_before_delete")
            self.assertEqual(target_path.read_text(encoding="utf-8"), "changed after backup\n")
            self.assertTrue((backup_root / "manifest.json").exists())

    def test_uninstall_governance_blocks_when_shared_patch_target_changes_after_backup(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            settings_source = workspace / "templates" / "settings.json"
            target_path = target / ".claude" / "settings.json"
            _write_json(settings_source, {"permissions": {"deny": ["Bash(powershell:*)"]}})
            _write_json(
                target_path,
                {
                    "permissions": {"deny": ["Bash(powershell:*)", "Read(**/.env)"]},
                    "local": {"keep": True},
                },
            )
            baseline = {
                "required_managed_files": [
                    {
                        "path": ".claude/settings.json",
                        "source": str(settings_source),
                        "management_mode": "json_merge",
                        "shared_ownership_evidence": ["permissions.deny entries"],
                    },
                ],
                "generated_managed_files": [],
                "retired_managed_files": [],
                "repo_profile_field_ownership": {},
            }
            backup_root = workspace / "backups"
            module = _load_uninstall_module()
            original_copy2 = module.shutil.copy2

            def copy_then_mutate(src, dst):
                result = original_copy2(src, dst)
                _write_json(target_path, {"permissions": {"deny": ["target changed"]}})
                return result

            with mock.patch.object(module.shutil, "copy2", side_effect=copy_then_mutate):
                payload, exit_code = module.uninstall_target_repo_governance(
                    target_repo=target,
                    baseline=baseline,
                    backup_root=backup_root,
                    dry_run=False,
                    apply=True,
                )

            self.assertEqual(exit_code, 2)
            self.assertEqual(payload["status"], "blocked")
            self.assertEqual(payload["summary"]["shared_patched"], 0)
            self.assertEqual(payload["blocked_files"][0]["reason"], "target_changed_before_patch")
            settings = json.loads(target_path.read_text(encoding="utf-8"))
            self.assertEqual(settings, {"permissions": {"deny": ["target changed"]}})
            self.assertTrue((backup_root / "manifest.json").exists())

    def test_uninstall_governance_blocks_reference_scan_errors_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            source = workspace / "templates" / "managed.py"
            managed_path = target / ".governed-ai" / "managed.py"
            managed_text = "print('managed')\n"
            _write_text(source, managed_text)
            _write_text(managed_path, managed_text)
            baseline = {
                "required_managed_files": [
                    {"path": ".governed-ai/managed.py", "source": str(source), "management_mode": "block_on_drift"},
                ],
                "generated_managed_files": [],
                "retired_managed_files": [],
                "repo_profile_field_ownership": {},
            }
            module = _load_uninstall_module()

            def build_index_with_error(root, *, scan_errors=None):
                if scan_errors is not None:
                    scan_errors.append(
                        {
                            "path": "scripts/locked.py",
                            "reason": "reference_scan_unreadable",
                            "error": "file is locked",
                        }
                    )
                return []

            with mock.patch.object(module, "build_reference_index", side_effect=build_index_with_error):
                payload, exit_code = module.uninstall_target_repo_governance(
                    target_repo=target,
                    baseline=baseline,
                    backup_root=workspace / "backups",
                    dry_run=False,
                    apply=True,
                )

            self.assertEqual(exit_code, 2)
            self.assertEqual(payload["status"], "blocked")
            self.assertEqual(payload["summary"]["deleted"], 0)
            self.assertEqual(payload["blocked_files"][0]["reason"], "reference_scan_unreadable")
            self.assertEqual(payload["blocked_files"][0]["classification"], "reference_scan_error")
            self.assertTrue(managed_path.exists())


if __name__ == "__main__":
    unittest.main()
