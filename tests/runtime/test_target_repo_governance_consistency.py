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
        learning = baseline["required_profile_overrides"]["learning_assistance_policy"]
        coordination = baseline["required_profile_overrides"]["rule_file_coordination_policy"]
        policy = baseline["required_profile_overrides"]["windows_process_environment_policy"]
        managed_files = baseline["required_managed_files"]
        ownership = baseline["repo_profile_field_ownership"]
        speed_policy = baseline["target_repo_speed_profile_policy"]
        provenance_policy = baseline["managed_file_provenance_policy"]

        self.assertEqual(interaction["communication_language"], "zh-CN")
        self.assertEqual(interaction["user_facing_output_language"], "zh-CN")
        self.assertEqual(interaction["preserve_technical_tokens_language"], "original")
        self.assertEqual(interaction["commit_message_language"], "zh-CN")
        recommendation_policy = interaction["multi_option_recommendation_policy"]
        self.assertTrue(recommendation_policy["enabled"])
        self.assertEqual(recommendation_policy["minimum_option_count"], 2)
        self.assertEqual(recommendation_policy["required_label"], "AI 推荐")
        self.assertEqual(recommendation_policy["fallback_label"], "无推荐")
        self.assertEqual(recommendation_policy["required_reason"], "one_sentence")
        self.assertIn("implementation_paths", recommendation_policy["applies_to"])
        self.assertIn("Communicate", " ".join(interaction["language_guidance"]))
        self.assertTrue(learning["enabled"])
        self.assertTrue(learning["observable_signals_only"])
        self.assertTrue(learning["require_evidence_refs"])
        self.assertTrue(learning["trigger_on_user_correction"])
        self.assertEqual(learning["max_terms_per_response"], 1)
        self.assertEqual(learning["max_clarification_questions"], 3)
        self.assertIn("term_confusion", learning["trigger_signals"])
        self.assertIn("symptom_root_cause_confusion", learning["trigger_signals"])
        self.assertIn("after_user_correction", learning["restatement_triggers"])
        self.assertIn("logs_or_screenshot", learning["bug_observation_checklist"])
        self.assertIn("stage_summary", learning["token_budget_policy"]["compression_mode"])
        self.assertIn("observable interaction signals", " ".join(learning["guidance"]))
        self.assertIn("expected/actual/repro/logs", " ".join(learning["guidance"]))
        self.assertTrue(coordination["enabled"])
        self.assertIn("WHAT", coordination["global_rule_scope"])
        self.assertIn("WHERE/HOW", coordination["project_rule_scope"])
        self.assertIn("non-overlapping", coordination["synergy_requirement"])
        self.assertIn("Claude Code memory and settings guidance", " ".join(coordination["source_review_basis"]))
        self.assertIn("settings/permissions", " ".join(coordination["source_review_basis"]))
        self.assertIn("paths frontmatter", " ".join(coordination["source_review_basis"]))
        self.assertIn("Trusted Folders", " ".join(coordination["source_review_basis"]))
        self.assertIn("file-scoped validation", " ".join(coordination["source_review_basis"]))
        self.assertIn("constraint-oriented", " ".join(coordination["source_review_basis"]))
        self.assertIn("minimal", " ".join(coordination["source_review_basis"]))
        self.assertIn("verifiable acceptance criteria", " ".join(coordination["root_file_quality_rules"]))
        self.assertIn("supply chain", " ".join(coordination["root_file_quality_rules"]))
        self.assertIn("instruction-like text", " ".join(coordination["root_file_quality_rules"]))
        self.assertIn("rule sources conflict", " ".join(coordination["root_file_quality_rules"]))
        self.assertIn("deployed copies", " ".join(coordination["root_file_quality_rules"]))
        self.assertIn("gate/profile/CI/script/README", " ".join(coordination["root_file_quality_rules"]))
        self.assertIn("quick or file-scoped validation", " ".join(coordination["root_file_quality_rules"]))
        pre_change_gate = coordination["pre_change_review_gate"]
        self.assertTrue(pre_change_gate["enabled"])
        self.assertIn("rule_file_changes", pre_change_gate["applies_to"])
        self.assertIn("gate_command_changes", pre_change_gate["applies_to"])
        self.assertIn("governance_baseline_changes", pre_change_gate["applies_to"])
        self.assertIn("sync_script_changes", pre_change_gate["applies_to"])
        self.assertIn("target_repo_gate_scripts_and_ci", pre_change_gate["required_inputs"])
        self.assertIn("target_repo_repo_profile", pre_change_gate["required_inputs"])
        self.assertIn("target_repo_readme_and_operator_docs", pre_change_gate["required_inputs"])
        self.assertIn("current_official_tool_loading_docs", pre_change_gate["required_inputs"])
        self.assertIn("drift-integration decision", pre_change_gate["blocking_behavior"])
        self.assertTrue(pre_change_gate["evidence_required"])
        self.assertIn("root-to-cwd", coordination["tool_specific_loading_policy"]["codex"])
        self.assertIn(".codex/rules", coordination["tool_specific_loading_policy"]["codex"])
        self.assertIn("do not assume CLAUDE.override.md", coordination["tool_specific_loading_policy"]["claude"])
        self.assertIn("permissions.deny", coordination["tool_specific_loading_policy"]["claude"])
        self.assertIn("/memory show", coordination["tool_specific_loading_policy"]["gemini"])
        self.assertIn("/memory reload", coordination["tool_specific_loading_policy"]["gemini"])
        self.assertIn("current schema/help", coordination["tool_specific_loading_policy"]["gemini"])
        self.assertIn(".geminiignore", coordination["tool_specific_loading_policy"]["gemini"])
        self.assertTrue(coordination["progressive_disclosure"]["allowed"])
        self.assertTrue(coordination["progressive_disclosure"]["root_file_must_remain_self_contained"])
        self.assertIn("gate_commands", coordination["required_project_rule_fields"])
        self.assertIn("quick_feedback_boundary", coordination["required_project_rule_fields"])
        self.assertIn("source_target_drift_review", coordination["required_project_rule_fields"])
        self.assertIn("security_supply_chain_performance_data_guardrails", coordination["required_project_rule_fields"])
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
        self.assertIn(".claude/settings.json", [item["path"] for item in managed_files])
        self.assertIn(".claude/hooks/governed-pre-tool-use.py", [item["path"] for item in managed_files])
        managed_file_modes = {item["path"]: item.get("management_mode", "replace") for item in managed_files}
        self.assertEqual(managed_file_modes[".governed-ai/verify-powershell-policy.py"], "block_on_drift")
        self.assertEqual(managed_file_modes[".claude/settings.json"], "json_merge")
        self.assertEqual(managed_file_modes[".claude/hooks/governed-pre-tool-use.py"], "block_on_drift")
        self.assertEqual(set(ownership["baseline_override_fields"]), set(baseline["required_profile_overrides"].keys()))
        self.assertEqual(
            set(ownership["derived_runtime_fields"]),
            {"quick_gate_commands", "full_gate_commands", "gate_timeout_seconds"},
        )
        self.assertEqual(
            set(ownership["catalog_input_fields"]),
            {"repo_id", "display_name", "primary_language", "build_commands", "test_commands", "contract_commands"},
        )
        self.assertTrue(speed_policy["enabled"])
        self.assertTrue(speed_policy["materialize_quick_gate_commands"])
        self.assertTrue(speed_policy["materialize_full_gate_commands"])
        self.assertTrue(speed_policy["preserve_existing_gate_commands"])
        self.assertTrue(speed_policy["refresh_existing_derived_gate_commands"])
        self.assertGreaterEqual(speed_policy["quick_gate_timeout_seconds"], 1)
        self.assertGreaterEqual(speed_policy["full_gate_timeout_seconds"], speed_policy["quick_gate_timeout_seconds"])
        self.assertEqual(provenance_policy["status"], "observe")
        self.assertEqual(provenance_policy["strategy"], "sidecar")
        self.assertEqual(provenance_policy["sidecar_root"], ".governed-ai/managed-files")
        self.assertTrue(provenance_policy["write_on_apply"])
        self.assertFalse(provenance_policy["require_in_consistency"])
        generated_managed_files = baseline["generated_managed_files"]
        generated_modes = {item["path"]: item["management_mode"] for item in generated_managed_files}
        self.assertEqual(
            generated_modes[".governed-ai/quick-test-slice.prompt.md"],
            "block_on_drift",
        )

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
            provenance_path = (
                target_repo
                / ".governed-ai"
                / "managed-files"
                / ".governed-ai"
                / "verify-powershell-policy.py.provenance.json"
            )
            self.assertTrue(provenance_path.exists())
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            self.assertEqual(provenance["record_kind"], "target_repo_managed_file_provenance")
            self.assertEqual(provenance["path"], ".governed-ai/verify-powershell-policy.py")
            self.assertEqual(provenance["management_mode"], "block_on_drift")
            self.assertEqual(provenance["ownership_scope"], "whole_file")
            self.assertEqual(provenance["marker_strategy"], "sidecar")
            self.assertEqual(provenance["sync_revision"], "2026-04-23.1")
            self.assertEqual(
                payload["changed_managed_file_provenance"][0]["provenance_path"],
                ".governed-ai/managed-files/.governed-ai/verify-powershell-policy.py.provenance.json",
            )

    def test_apply_target_repo_governance_rejects_overlapping_repo_profile_ownership(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "repo-a"
            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            _write_json(profile_path, {"repo_id": "repo-a"})
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-05-02.5",
                    "repo_profile_field_ownership": {
                        "baseline_override_fields": ["auto_commit_policy"],
                        "derived_runtime_fields": ["quick_gate_commands", "gate_timeout_seconds"],
                        "catalog_input_fields": ["repo_id", "auto_commit_policy"],
                    },
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
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("repo_profile_field_ownership", completed.stderr)

    def test_apply_target_repo_governance_materializes_speed_profile_from_existing_gates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "repo-a"
            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            _write_json(
                profile_path,
                {
                    "repo_id": "repo-a",
                    "build_commands": [{"id": "build", "command": "python -m compileall src", "required": True}],
                    "test_commands": [{"id": "test", "command": "python -m unittest discover", "required": True}],
                    "contract_commands": [
                        {"id": "contract", "command": "python -m unittest tests.test_contracts", "required": True}
                    ],
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
                    "sync_revision": "2026-04-26.6",
                    "target_repo_speed_profile_policy": {
                        "enabled": True,
                        "materialize_quick_gate_commands": True,
                        "materialize_full_gate_commands": True,
                        "preserve_existing_gate_commands": True,
                        "default_gate_timeout_seconds": 90,
                        "quick_gate_timeout_seconds": 30,
                        "full_gate_timeout_seconds": 60,
                    },
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
            self.assertEqual(
                payload["changed_speed_profile_fields"],
                ["quick_gate_commands", "full_gate_commands", "gate_timeout_seconds"],
            )
            updated_profile = json.loads(profile_path.read_text(encoding="utf-8"))
            self.assertEqual([gate["id"] for gate in updated_profile["quick_gate_commands"]], ["test", "contract"])
            self.assertEqual([gate["id"] for gate in updated_profile["full_gate_commands"]], ["build", "test", "contract"])
            self.assertEqual(updated_profile["quick_gate_commands"][0]["timeout_seconds"], 30)
            self.assertEqual(updated_profile["full_gate_commands"][0]["timeout_seconds"], 60)
            self.assertEqual(updated_profile["gate_timeout_seconds"], 90)

    def test_apply_target_repo_governance_json_merge_managed_file_preserves_local_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "repo-a"
            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            _write_json(profile_path, {"repo_id": "repo-a"})
            target_settings_path = target_repo / ".claude" / "settings.json"
            _write_json(
                target_settings_path,
                {
                    "permissions": {"allow": ["Read(**/notes.md)"]},
                    "local_only": {"keep": True},
                },
            )
            template_path = workspace / "settings-template.json"
            _write_json(
                template_path,
                {
                    "permissions": {"deny": ["Read(**/.env)"]},
                    "hooks": {"PreToolUse": [{"matcher": "Read"}]},
                },
            )
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-05-02.1",
                    "required_managed_files": [
                        {
                            "path": ".claude/settings.json",
                            "source": str(template_path),
                            "management_mode": "json_merge",
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
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "applied")
            self.assertEqual(payload["changed_managed_files"][0]["management_mode"], "json_merge")
            backup_path = Path(payload["changed_managed_files"][0]["backup_path"])
            self.assertTrue(backup_path.exists())
            merged_settings = json.loads(target_settings_path.read_text(encoding="utf-8"))
            self.assertEqual(merged_settings["permissions"]["deny"], ["Read(**/.env)"])
            self.assertEqual(merged_settings["permissions"]["allow"], ["Read(**/notes.md)"])
            self.assertEqual(merged_settings["local_only"]["keep"], True)
            self.assertIn("PreToolUse", merged_settings["hooks"])
            provenance_path = (
                target_repo / ".governed-ai" / "managed-files" / ".claude" / "settings.json.provenance.json"
            )
            self.assertTrue(provenance_path.exists())
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
            self.assertEqual(provenance["path"], ".claude/settings.json")
            self.assertEqual(provenance["management_mode"], "json_merge")
            self.assertEqual(provenance["ownership_scope"], "field_or_block")
            self.assertEqual(provenance["marker_strategy"], "sidecar")
            self.assertEqual(provenance["mode_status"], "active")
            self.assertEqual(provenance["overwrite_policy"], "json_merge_overlay_preserve_target_local_keys")

    def test_apply_target_repo_governance_respects_disabled_managed_file_provenance_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "repo-a"
            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            _write_json(profile_path, {"repo_id": "repo-a"})
            template_path = workspace / "verify-powershell-policy.py"
            template_path.write_text("print('runtime-owned')\n", encoding="utf-8")
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-05-03.1",
                    "managed_file_provenance_policy": {
                        "status": "disabled",
                        "strategy": "sidecar",
                        "sidecar_root": ".governed-ai/managed-files",
                        "write_on_apply": True,
                        "require_in_consistency": False,
                    },
                    "required_managed_files": [
                        {
                            "path": ".governed-ai/verify-powershell-policy.py",
                            "source": str(template_path),
                            "management_mode": "block_on_drift",
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
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "applied")
            self.assertEqual(payload["changed_managed_file_provenance"], [])
            provenance_path = (
                target_repo
                / ".governed-ai"
                / "managed-files"
                / ".governed-ai"
                / "verify-powershell-policy.py.provenance.json"
            )
            self.assertFalse(provenance_path.exists())

    def test_apply_target_repo_governance_block_on_drift_managed_file_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "repo-a"
            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            _write_json(profile_path, {"repo_id": "repo-a"})
            target_hook_path = target_repo / ".claude" / "hooks" / "custom-hook.py"
            target_hook_path.parent.mkdir(parents=True, exist_ok=True)
            target_hook_path.write_text("print('target-local')\n", encoding="utf-8")
            template_path = workspace / "hook-template.py"
            template_path.write_text("print('runtime-owned')\n", encoding="utf-8")
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-05-02.2",
                    "required_managed_files": [
                        {
                            "path": ".claude/hooks/custom-hook.py",
                            "source": str(template_path),
                            "management_mode": "block_on_drift",
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
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 2, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "blocked")
            blocked = payload["blocked_managed_files"][0]
            self.assertEqual(blocked["management_mode"], "block_on_drift")
            self.assertEqual(blocked["reason"], "content_drift")
            self.assertEqual(blocked["conflict_policy"], "block_on_drift")
            self.assertIn("integrate target-local fixes", blocked["recommended_action"])
            self.assertTrue(blocked["source_sha256"])
            self.assertTrue(blocked["target_sha256"])
            self.assertTrue(blocked["expected_sha256"])
            self.assertEqual(target_hook_path.read_text(encoding="utf-8"), "print('target-local')\n")

    def test_apply_target_repo_governance_replace_managed_file_refuses_existing_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "repo-a"
            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            _write_json(profile_path, {"repo_id": "repo-a"})
            target_guard_path = target_repo / ".governed-ai" / "verify-powershell-policy.py"
            target_guard_path.parent.mkdir(parents=True, exist_ok=True)
            target_guard_path.write_text("print('target-local')\n", encoding="utf-8")
            template_path = workspace / "verify-powershell-policy.py"
            template_path.write_text("print('runtime-owned')\n", encoding="utf-8")
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-05-02.6",
                    "required_managed_files": [
                        {
                            "path": ".governed-ai/verify-powershell-policy.py",
                            "source": str(template_path),
                            "management_mode": "replace",
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
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 2, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "blocked")
            blocked = payload["blocked_managed_files"][0]
            self.assertEqual(blocked["management_mode"], "replace")
            self.assertEqual(blocked["mode_status"], "legacy_fail_closed")
            self.assertEqual(blocked["overwrite_policy"], "create_missing_block_existing_drift")
            self.assertEqual(blocked["reason"], "content_drift")
            self.assertIn("blocking_reason", blocked)
            self.assertEqual(blocked["conflict_policy"], "block_on_drift")
            self.assertIn("legacy fail-closed alias", blocked["recommended_action"])
            self.assertIn("rerun apply", blocked["recommended_action"])
            self.assertEqual(target_guard_path.read_text(encoding="utf-8"), "print('target-local')\n")

    def test_apply_target_repo_governance_block_on_drift_managed_file_creates_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "repo-a"
            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            _write_json(profile_path, {"repo_id": "repo-a"})
            template_path = workspace / "hook-template.py"
            template_path.write_text("print('runtime-owned')\n", encoding="utf-8")
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-05-02.3",
                    "required_managed_files": [
                        {
                            "path": ".claude/hooks/custom-hook.py",
                            "source": str(template_path),
                            "management_mode": "block_on_drift",
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
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "applied")
            self.assertEqual(payload["changed_managed_files"][0]["management_mode"], "block_on_drift")
            self.assertFalse(payload["blocked_managed_files"])
            self.assertEqual(
                (target_repo / ".claude" / "hooks" / "custom-hook.py").read_text(encoding="utf-8"),
                "print('runtime-owned')\n",
            )

    def test_apply_target_repo_governance_accepts_catalog_contract_command_array(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "repo-a"
            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            _write_json(
                profile_path,
                {
                    "repo_id": "repo-a",
                    "build_commands": [{"id": "build", "command": "python --version", "required": True}],
                    "test_commands": [{"id": "test", "command": "python --version", "required": True}],
                    "contract_commands": [],
                    "auto_commit_policy": {"enabled": False},
                },
            )
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-05-01.1",
                    "target_repo_speed_profile_policy": {
                        "enabled": True,
                        "materialize_quick_gate_commands": True,
                        "materialize_full_gate_commands": True,
                        "preserve_existing_gate_commands": True,
                        "refresh_existing_derived_gate_commands": True,
                        "default_gate_timeout_seconds": 90,
                        "quick_gate_timeout_seconds": 30,
                        "full_gate_timeout_seconds": 60,
                    },
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
                    "--contract-commands-json",
                    json.dumps(
                        [
                            {
                                "id": "contract:powershell-policy",
                                "command": "python .governed-ai/verify-powershell-policy.py",
                                "required": True,
                            },
                            {"id": "contract", "command": "python -m unittest -q", "required": True},
                        ]
                    ),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertIn("contract_commands", payload["changed_catalog_fields"])
            updated_profile = json.loads(profile_path.read_text(encoding="utf-8"))
            self.assertEqual(
                [gate["id"] for gate in updated_profile["contract_commands"]],
                ["contract:powershell-policy", "contract"],
            )
            self.assertIn(
                "contract:powershell-policy",
                {gate["id"] for gate in updated_profile["quick_gate_commands"]},
            )
            self.assertIn(
                "contract",
                {gate["id"] for gate in updated_profile["quick_gate_commands"]},
            )
            self.assertIn(
                "contract:powershell-policy",
                {gate["id"] for gate in updated_profile["full_gate_commands"]},
            )
            self.assertIn(
                "contract",
                {gate["id"] for gate in updated_profile["full_gate_commands"]},
            )

    def test_apply_target_repo_governance_blocks_catalog_gate_drift_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "repo-a"
            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            target_profile = {
                "repo_id": "repo-a",
                "build_commands": [{"id": "build", "command": "python -m compileall src", "required": True}],
                "test_commands": [{"id": "test", "command": "python -m unittest tests.fast", "required": True}],
                "contract_commands": [
                    {"id": "contract", "command": "python -m unittest tests.contracts", "required": True}
                ],
                "auto_commit_policy": {"enabled": False},
            }
            _write_json(profile_path, target_profile)
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-05-02.6",
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
                    "--test-command",
                    "python -m unittest discover",
                    "--quick-test-skip-reason",
                    "No safe smaller slice.",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 2, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "blocked")
            self.assertEqual(payload["blocked_catalog_fields"][0]["field"], "test_commands")
            self.assertEqual(payload["blocked_catalog_fields"][0]["reason"], "content_drift")
            self.assertEqual(json.loads(profile_path.read_text(encoding="utf-8")), target_profile)

    def test_apply_target_repo_governance_blocks_existing_quick_test_prompt_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "repo-a"
            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            _write_json(
                profile_path,
                {
                    "repo_id": "repo-a",
                    "test_commands": [{"id": "test", "command": "python -m unittest discover", "required": True}],
                    "contract_commands": [
                        {"id": "contract", "command": "python -m unittest tests.contracts", "required": True}
                    ],
                    "auto_commit_policy": {"enabled": False},
                },
            )
            prompt_path = target_repo / ".governed-ai" / "quick-test-slice.prompt.md"
            prompt_path.write_text("# Target-local prompt\n\nKeep this target-specific review note.\n", encoding="utf-8")
            original_prompt = prompt_path.read_text(encoding="utf-8")
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-05-02.6",
                    "generated_managed_files": [
                        {
                            "path": ".governed-ai/quick-test-slice.prompt.md",
                            "generator": "outer_ai_quick_test_prompt",
                            "management_mode": "block_on_drift",
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
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 2, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "blocked")
            self.assertEqual(payload["blocked_generated_files"][0]["path"], ".governed-ai/quick-test-slice.prompt.md")
            self.assertEqual(payload["blocked_generated_files"][0]["reason"], "content_drift")
            self.assertEqual(prompt_path.read_text(encoding="utf-8"), original_prompt)

    def test_apply_target_repo_governance_dedupes_identical_test_and_contract_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "repo-a"
            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            _write_json(
                profile_path,
                {
                    "repo_id": "repo-a",
                    "build_commands": [{"id": "build", "command": "python -m compileall src", "required": True}],
                    "test_commands": [{"id": "test", "command": "python -m unittest discover", "required": True}],
                    "contract_commands": [{"id": "contract", "command": "python -m unittest discover", "required": True}],
                    "auto_commit_policy": {"enabled": False},
                },
            )
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-26.7",
                    "target_repo_speed_profile_policy": {
                        "enabled": True,
                        "materialize_quick_gate_commands": True,
                        "materialize_full_gate_commands": True,
                        "preserve_existing_gate_commands": True,
                        "refresh_existing_derived_gate_commands": True,
                        "default_gate_timeout_seconds": 90,
                        "quick_gate_timeout_seconds": 30,
                        "full_gate_timeout_seconds": 60,
                    },
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
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            updated_profile = json.loads(profile_path.read_text(encoding="utf-8"))
            self.assertEqual(len(updated_profile["quick_gate_commands"]), 1)
            self.assertEqual(updated_profile["quick_gate_commands"][0]["satisfies_gate_ids"], ["test", "contract"])
            self.assertEqual([gate["id"] for gate in updated_profile["full_gate_commands"]], ["build", "test"])
            self.assertEqual(updated_profile["full_gate_commands"][1]["satisfies_gate_ids"], ["test", "contract"])

    def test_apply_target_repo_governance_uses_target_quick_test_slice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "repo-a"
            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            _write_json(
                profile_path,
                {
                    "repo_id": "repo-a",
                    "build_commands": [{"id": "build", "command": "python -m compileall src", "required": True}],
                    "test_commands": [{"id": "test", "command": "python -m unittest discover", "required": True}],
                    "contract_commands": [
                        {"id": "contract", "command": "python -m unittest tests.test_contracts", "required": True}
                    ],
                    "auto_commit_policy": {"enabled": False},
                },
            )
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-26.8",
                    "target_repo_speed_profile_policy": {
                        "enabled": True,
                        "materialize_quick_gate_commands": True,
                        "materialize_full_gate_commands": True,
                        "preserve_existing_gate_commands": True,
                        "default_gate_timeout_seconds": 90,
                        "quick_gate_timeout_seconds": 30,
                        "full_gate_timeout_seconds": 60,
                    },
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
                    "--quick-test-command",
                    "python -m unittest tests.test_fast",
                    "--quick-test-reason",
                    "Focused fast regression slice.",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            updated_profile = json.loads(profile_path.read_text(encoding="utf-8"))
            self.assertEqual(updated_profile["quick_gate_commands"][0]["command"], "python -m unittest tests.test_fast")
            self.assertEqual(updated_profile["quick_gate_commands"][0]["description"], "Focused fast regression slice.")
            self.assertEqual(updated_profile["quick_gate_commands"][1]["id"], "contract")
            self.assertEqual(updated_profile["full_gate_commands"][1]["command"], "python -m unittest discover")

    def test_apply_target_repo_governance_refreshes_derived_quick_group_to_target_slice(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "repo-a"
            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            _write_json(
                profile_path,
                {
                    "repo_id": "repo-a",
                    "build_commands": [{"id": "build", "command": "python -m compileall src", "required": True}],
                    "test_commands": [{"id": "test", "command": "python -m unittest discover", "required": True}],
                    "contract_commands": [{"id": "contract", "command": "python -m unittest discover", "required": True}],
                    "quick_gate_commands": [
                        {
                            "id": "test",
                            "command": "python -m unittest discover",
                            "required": True,
                            "timeout_seconds": 30,
                            "satisfies_gate_ids": ["test", "contract"],
                        }
                    ],
                    "auto_commit_policy": {"enabled": False},
                },
            )
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-26.8",
                    "target_repo_speed_profile_policy": {
                        "enabled": True,
                        "materialize_quick_gate_commands": True,
                        "materialize_full_gate_commands": True,
                        "preserve_existing_gate_commands": True,
                        "refresh_existing_derived_gate_commands": True,
                        "default_gate_timeout_seconds": 90,
                        "quick_gate_timeout_seconds": 30,
                        "full_gate_timeout_seconds": 60,
                    },
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
                    "--quick-test-command",
                    "python -m unittest tests.test_fast",
                    "--quick-test-reason",
                    "Focused fast regression slice.",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            updated_profile = json.loads(profile_path.read_text(encoding="utf-8"))
            self.assertEqual(len(updated_profile["quick_gate_commands"]), 2)
            self.assertEqual(updated_profile["quick_gate_commands"][0]["command"], "python -m unittest tests.test_fast")
            self.assertEqual(updated_profile["quick_gate_commands"][1]["command"], "python -m unittest discover")

    def test_apply_target_repo_governance_uses_outer_ai_recommendation_when_catalog_slice_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "repo-a"
            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            _write_json(
                profile_path,
                {
                    "repo_id": "repo-a",
                    "build_commands": [{"id": "build", "command": "python -m compileall src", "required": True}],
                    "test_commands": [{"id": "test", "command": "python -m unittest discover", "required": True}],
                    "contract_commands": [
                        {"id": "contract", "command": "python -m unittest tests.test_contracts", "required": True}
                    ],
                    "auto_commit_policy": {"enabled": False},
                },
            )
            _write_json(
                target_repo / ".governed-ai" / "quick-test-slice.recommendation.json",
                {
                    "schema_version": "1.0",
                    "status": "ready",
                    "quick_test_command": "python -m unittest tests.test_outer_fast",
                    "quick_test_reason": "Outer AI selected a focused fast slice.",
                    "quick_test_timeout_seconds": 45,
                },
            )
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-26.8",
                    "target_repo_speed_profile_policy": {
                        "enabled": True,
                        "materialize_quick_gate_commands": True,
                        "materialize_full_gate_commands": True,
                        "preserve_existing_gate_commands": True,
                        "default_gate_timeout_seconds": 90,
                        "quick_gate_timeout_seconds": 30,
                        "full_gate_timeout_seconds": 60,
                    },
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
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["quick_test_slice_source"], "recommendation_file")
            updated_profile = json.loads(profile_path.read_text(encoding="utf-8"))
            self.assertEqual(
                updated_profile["quick_gate_commands"][0]["command"],
                "python -m unittest tests.test_outer_fast",
            )
            self.assertEqual(updated_profile["quick_gate_commands"][0]["timeout_seconds"], 45)
            self.assertEqual(updated_profile["full_gate_commands"][1]["command"], "python -m unittest discover")

    def test_apply_target_repo_governance_treats_skip_recommendation_as_complete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "repo-a"
            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            _write_json(
                profile_path,
                {
                    "repo_id": "repo-a",
                    "test_commands": [{"id": "test", "command": "python -m unittest discover", "required": True}],
                    "contract_commands": [
                        {"id": "contract", "command": "python -m unittest tests.test_contracts", "required": True}
                    ],
                },
            )
            _write_json(
                target_repo / ".governed-ai" / "quick-test-slice.recommendation.json",
                {
                    "schema_version": "1.0",
                    "status": "skip",
                    "quick_test_reason": "No safe target-specific quick test slice found.",
                },
            )
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-26.8",
                    "target_repo_speed_profile_policy": {
                        "enabled": True,
                        "materialize_quick_gate_commands": True,
                        "materialize_full_gate_commands": True,
                        "preserve_existing_gate_commands": True,
                    },
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
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["quick_test_slice_source"], "recommendation_file_skip")
            self.assertEqual(payload["outer_ai_action"], "none")
            self.assertIsNone(payload["quick_test_prompt_path"])
            self.assertEqual(payload["outer_ai_instruction"], "")

    def test_apply_target_repo_governance_catalog_skip_suppresses_outer_ai_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "repo-a"
            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            _write_json(
                profile_path,
                {
                    "repo_id": "repo-a",
                    "test_commands": [{"id": "test", "command": "python -m unittest discover", "required": True}],
                    "contract_commands": [
                        {"id": "contract", "command": "python -m unittest tests.test_contracts", "required": True}
                    ],
                },
            )
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-26.8",
                    "target_repo_speed_profile_policy": {
                        "enabled": True,
                        "materialize_quick_gate_commands": True,
                        "materialize_full_gate_commands": True,
                        "preserve_existing_gate_commands": True,
                    },
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
                    "--quick-test-skip-reason",
                    "Full test command is already minimal.",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["quick_test_slice_source"], "argument_skip")
            self.assertEqual(payload["quick_test_skip_reason"], "Full test command is already minimal.")
            self.assertEqual(payload["outer_ai_action"], "none")
            self.assertIsNone(payload["quick_test_prompt_path"])

    def test_apply_target_repo_governance_catalog_gate_changes_refresh_speed_groups(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "repo-a"
            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            _write_json(
                profile_path,
                {
                    "repo_id": "repo-a",
                    "build_commands": [{"id": "build", "command": "python -m compileall src", "required": True}],
                    "test_commands": [{"id": "test", "command": "python -m unittest discover", "required": True}],
                    "contract_commands": [
                        {"id": "contract", "command": "python -m unittest tests.test_contracts", "required": True}
                    ],
                    "quick_gate_commands": [
                        {
                            "id": "test",
                            "command": "python --version",
                            "required": True,
                            "timeout_seconds": 180,
                            "satisfies_gate_ids": ["test", "contract"],
                        }
                    ],
                },
            )
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-26.8",
                    "target_repo_speed_profile_policy": {
                        "enabled": True,
                        "materialize_quick_gate_commands": True,
                        "materialize_full_gate_commands": True,
                        "preserve_existing_gate_commands": True,
                        "quick_gate_timeout_seconds": 30,
                        "full_gate_timeout_seconds": 60,
                    },
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
                    "--build-command",
                    "python -m compileall src",
                    "--test-command",
                    "python -m unittest discover",
                    "--contract-command",
                    "python -m unittest tests.test_contracts",
                    "--quick-test-skip-reason",
                    "No safe smaller slice.",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertNotIn("test_commands", payload["changed_catalog_fields"])
            self.assertIn("quick_gate_commands", payload["changed_speed_profile_fields"])
            updated_profile = json.loads(profile_path.read_text(encoding="utf-8"))
            self.assertEqual(updated_profile["quick_gate_commands"][0]["command"], "python -m unittest discover")
            self.assertEqual(updated_profile["quick_gate_commands"][1]["command"], "python -m unittest tests.test_contracts")

    def test_apply_target_repo_governance_preserves_existing_speed_profile(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target_repo = workspace / "repo-a"
            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            _write_json(
                profile_path,
                {
                    "repo_id": "repo-a",
                    "build_commands": [{"id": "build", "command": "python -m compileall src", "required": True}],
                    "test_commands": [{"id": "test", "command": "python -m unittest discover", "required": True}],
                    "contract_commands": [
                        {"id": "contract", "command": "python -m unittest tests.test_contracts", "required": True}
                    ],
                    "quick_gate_commands": [
                        {"id": "custom-quick", "command": "python -m unittest tests.test_fast", "required": True}
                    ],
                    "full_gate_commands": [
                        {"id": "custom-full", "command": "python -m unittest tests.test_all", "required": True}
                    ],
                    "gate_timeout_seconds": 42,
                    "auto_commit_policy": {"enabled": False},
                },
            )
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-26.6",
                    "target_repo_speed_profile_policy": {
                        "enabled": True,
                        "preserve_existing_gate_commands": True,
                        "default_gate_timeout_seconds": 90,
                    },
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
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            updated_profile = json.loads(profile_path.read_text(encoding="utf-8"))
            self.assertEqual(updated_profile["quick_gate_commands"][0]["id"], "custom-quick")
            self.assertEqual(updated_profile["full_gate_commands"][0]["id"], "custom-full")
            self.assertEqual(updated_profile["gate_timeout_seconds"], 42)

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

    def test_verify_target_repo_governance_consistency_fails_on_catalog_gate_fact_drift(self) -> None:
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
                    "sync_revision": "2026-04-26.9",
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
                            "repo_id": "repo-a",
                            "display_name": "repo-a",
                            "primary_language": "python",
                            "build_command": "python -m compileall src",
                            "test_command": "python -m unittest discover",
                            "contract_command": "python -m unittest tests.test_contracts",
                        }
                    },
                },
            )
            _write_json(
                code_root / "repo-a" / ".governed-ai" / "repo-profile.json",
                {
                    "repo_id": "repo-a",
                    "display_name": "repo-a",
                    "primary_language": "python",
                    "build_commands": [{"id": "build", "command": "python --version", "required": True}],
                    "test_commands": [{"id": "test", "command": "python --version", "required": True}],
                    "contract_commands": [{"id": "contract", "command": "python --version", "required": True}],
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
            self.assertEqual(payload["drift"][0]["reason"], "catalog_gate_fact_drift")
            self.assertIn("build_commands", payload["drift"][0]["mismatched_catalog_fields"])
            self.assertIn("test_commands", payload["drift"][0]["mismatched_catalog_fields"])

    def test_verify_target_repo_governance_consistency_accepts_catalog_contract_command_array(self) -> None:
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
                    "sync_revision": "2026-05-01.2",
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
                            "contract_commands": [
                                {
                                    "id": "contract:powershell-policy",
                                    "command": "python .governed-ai/verify-powershell-policy.py",
                                    "required": True,
                                },
                                {"id": "contract", "command": "python -m unittest -q", "required": True},
                            ],
                        }
                    },
                },
            )
            _write_json(
                code_root / "repo-a" / ".governed-ai" / "repo-profile.json",
                {
                    "repo_id": "repo-a",
                    "contract_commands": [
                        {
                            "id": "contract:powershell-policy",
                            "command": "python .governed-ai/verify-powershell-policy.py",
                            "required": True,
                        },
                        {"id": "contract", "command": "python -m unittest -q", "required": True},
                    ],
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

    def test_verify_target_repo_governance_consistency_fails_on_speed_profile_drift(self) -> None:
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
                    "sync_revision": "2026-04-26.6",
                    "target_repo_speed_profile_policy": {
                        "enabled": True,
                        "default_gate_timeout_seconds": 90,
                        "quick_gate_timeout_seconds": 30,
                        "full_gate_timeout_seconds": 60,
                    },
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
                    "build_commands": [{"id": "build", "command": "python -m compileall src", "required": True}],
                    "test_commands": [{"id": "test", "command": "python -m unittest discover", "required": True}],
                    "contract_commands": [
                        {"id": "contract", "command": "python -m unittest tests.test_contracts", "required": True}
                    ],
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
            self.assertEqual(payload["drift"][0]["reason"], "speed_profile_drift")
            self.assertIn("quick_gate_commands", payload["drift"][0]["mismatched_speed_profile_fields"])
            self.assertIn("full_gate_commands", payload["drift"][0]["mismatched_speed_profile_fields"])
            self.assertIn("gate_timeout_seconds", payload["drift"][0]["mismatched_speed_profile_fields"])

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
            mismatch = payload["drift"][0]["mismatched_managed_files"][0]
            self.assertEqual(mismatch["reason"], "missing")
            self.assertEqual(mismatch["conflict_policy"], "create_missing")
            self.assertIn("create the missing managed file", mismatch["recommended_action"])
            self.assertTrue(mismatch["source_sha256"])
            self.assertEqual(mismatch["target_sha256"], "")
            self.assertTrue(mismatch["expected_sha256"])

    def test_verify_target_repo_governance_consistency_allows_json_merge_managed_file_local_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_root = workspace / "runtime"
            code_root = workspace / "code"
            runtime_state_base = repo_root / ".runtime" / "attachments"
            repo_root.mkdir(parents=True)
            code_root.mkdir(parents=True)

            template_path = workspace / "settings-template.json"
            _write_json(
                template_path,
                {
                    "permissions": {"deny": ["Read(**/.env)"]},
                    "hooks": {"PreToolUse": [{"matcher": "Read"}]},
                },
            )
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-05-02.1",
                    "required_managed_files": [
                        {
                            "path": ".claude/settings.json",
                            "source": str(template_path),
                            "management_mode": "json_merge",
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
            _write_json(
                code_root / "repo-a" / ".claude" / "settings.json",
                {
                    "permissions": {
                        "deny": ["Read(**/.env)"],
                        "allow": ["Read(**/notes.md)"],
                    },
                    "hooks": {"PreToolUse": [{"matcher": "Read"}]},
                    "local_only": {"keep": True},
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

    def test_verify_target_repo_governance_consistency_fails_on_block_on_drift_managed_file_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_root = workspace / "runtime"
            code_root = workspace / "code"
            runtime_state_base = repo_root / ".runtime" / "attachments"
            repo_root.mkdir(parents=True)
            code_root.mkdir(parents=True)

            template_path = workspace / "hook-template.py"
            template_path.write_text("print('runtime-owned')\n", encoding="utf-8")
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-05-02.4",
                    "required_managed_files": [
                        {
                            "path": ".claude/hooks/custom-hook.py",
                            "source": str(template_path),
                            "management_mode": "block_on_drift",
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
            target_hook_path = code_root / "repo-a" / ".claude" / "hooks" / "custom-hook.py"
            target_hook_path.parent.mkdir(parents=True, exist_ok=True)
            target_hook_path.write_text("print('target-local')\n", encoding="utf-8")

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
            mismatch = payload["drift"][0]["mismatched_managed_files"][0]
            self.assertEqual(mismatch["management_mode"], "block_on_drift")
            self.assertEqual(mismatch["reason"], "content_drift")
            self.assertEqual(mismatch["conflict_policy"], "block_on_drift")
            self.assertIn("integrate target-local fixes", mismatch["recommended_action"])
            self.assertTrue(mismatch["source_sha256"])
            self.assertTrue(mismatch["target_sha256"])
            self.assertTrue(mismatch["expected_sha256"])

    def test_verify_target_repo_governance_consistency_marks_replace_as_legacy_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_root = workspace / "runtime"
            code_root = workspace / "code"
            runtime_state_base = repo_root / ".runtime" / "attachments"
            repo_root.mkdir(parents=True)
            code_root.mkdir(parents=True)

            template_path = workspace / "guard-template.py"
            template_path.write_text("print('runtime-owned')\n", encoding="utf-8")
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-05-04.1",
                    "required_managed_files": [
                        {
                            "path": ".governed-ai/legacy-guard.py",
                            "source": str(template_path),
                            "management_mode": "replace",
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
            target_guard_path = code_root / "repo-a" / ".governed-ai" / "legacy-guard.py"
            target_guard_path.parent.mkdir(parents=True, exist_ok=True)
            target_guard_path.write_text("print('target-local')\n", encoding="utf-8")

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
            mismatch = payload["drift"][0]["mismatched_managed_files"][0]
            self.assertEqual(mismatch["management_mode"], "replace")
            self.assertEqual(mismatch["mode_status"], "legacy_fail_closed")
            self.assertEqual(mismatch["overwrite_policy"], "create_missing_block_existing_drift")
            self.assertEqual(mismatch["conflict_policy"], "block_on_drift")
            self.assertIn("legacy fail-closed alias", mismatch["recommended_action"])


if __name__ == "__main__":
    unittest.main()
