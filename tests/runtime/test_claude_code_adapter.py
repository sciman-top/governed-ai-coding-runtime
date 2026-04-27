import importlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class ClaudeCodeAdapterTests(unittest.TestCase):
    def test_claude_code_adapter_api_exists(self) -> None:
        module = self._module()

        self.assertTrue(hasattr(module, "ClaudeCodeAdapterProfile"))
        self.assertTrue(hasattr(module, "build_claude_code_adapter_profile"))
        self.assertTrue(hasattr(module, "probe_claude_code_surface"))

    def test_claude_code_profile_keeps_native_attach_degraded(self) -> None:
        module = self._module()

        profile = module.build_claude_code_adapter_profile(
            process_bridge_available=True,
            settings_available=True,
            hooks_available=True,
            structured_events_available=False,
            evidence_export_available=False,
            resume_available=False,
        )

        self.assertEqual(profile.adapter_id, "claude-code")
        self.assertEqual(profile.adapter_tier, "process_bridge")
        self.assertIn("native_attach", profile.unsupported_capabilities)
        self.assertEqual(profile.unsupported_capability_behavior, "degrade_to_process_bridge")

    def test_claude_code_probe_blocks_to_manual_when_cli_missing(self) -> None:
        module = self._module()

        def missing_runner(argv, _cwd):
            if argv == ["claude", "--version"]:
                return 127, "", "claude: command not found"
            return 127, "", "unsupported"

        probe = module.probe_claude_code_surface(command_runner=missing_runner)
        profile = module.build_claude_code_adapter_profile_from_probe(probe)

        self.assertFalse(probe.claude_cli_available)
        self.assertEqual(module.classify_claude_code_adapter(profile).tier, "manual_handoff")
        self.assertEqual(probe.failure_stage, "claude_command_unavailable")
        self.assertIn("command not found", probe.reason)

    def test_claude_code_probe_detects_managed_settings_and_hooks(self) -> None:
        module = self._module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / ".claude" / "hooks").mkdir(parents=True)
            (root / ".claude" / "settings.json").write_text("{}\n", encoding="utf-8")
            (root / ".claude" / "hooks" / "governed-pre-tool-use.py").write_text("print('ok')\n", encoding="utf-8")

            def ready_runner(argv, _cwd):
                if argv == ["claude", "--version"]:
                    return 0, "2.1.114 (Claude Code)\n", ""
                if argv == ["claude", "--help"]:
                    return 0, "Options:\n  --output-format json\nCommands:\n  resume\n", ""
                return 1, "", "unsupported"

            probe = module.probe_claude_code_surface(cwd=root, command_runner=ready_runner)
            readiness = module.summarize_claude_code_capability_readiness(probe)

        self.assertTrue(probe.claude_cli_available)
        self.assertTrue(probe.settings_available)
        self.assertTrue(probe.hooks_available)
        self.assertEqual(readiness.status, "degraded")
        self.assertEqual(readiness.adapter_tier, "process_bridge")
        self.assertIn("native_attach", readiness.unsupported_capabilities)

    def test_claude_code_trial_conforms_with_hook_and_replay_refs(self) -> None:
        module = self._module()
        conformance = importlib.import_module("governed_ai_coding_runtime_contracts.adapter_conformance")

        result = module.build_claude_code_adapter_trial_result(
            repo_id="python-service",
            task_id="task-claude-trial",
            binding_id="binding-python-service",
            process_bridge_available=True,
            settings_available=True,
            hooks_available=True,
            structured_events_available=False,
            evidence_export_available=False,
            resume_available=False,
        )
        payload = module.claude_code_adapter_trial_to_dict(result)
        conformance_result = conformance.evaluate_claude_trial_conformance(payload)

        self.assertEqual(conformance_result.status, "pass")
        self.assertEqual(conformance_result.parity_status, "degraded")
        self.assertIn("native_attach", payload["unsupported_capabilities"])
        self.assertTrue(payload["hook_evidence_refs"])
        self.assertTrue(payload["replay_ref"])

    def test_claude_code_trial_script_emits_json_summary(self) -> None:
        script = ROOT / "scripts" / "run-claude-code-adapter-trial.py"

        completed = subprocess.run(
            [
                sys.executable,
                str(script),
                "--repo-id",
                "python-service",
                "--task-id",
                "task-claude-trial",
                "--binding-id",
                "binding-python-service",
                "--settings",
                "--hooks",
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["adapter_id"], "claude-code")
        self.assertEqual(payload["adapter_tier"], "process_bridge")
        self.assertIn("hook_evidence_refs", payload)
        self.assertIn("replay_ref", payload)

    def test_claude_code_adapter_exports_from_package_root(self) -> None:
        package = importlib.import_module("governed_ai_coding_runtime_contracts")

        self.assertTrue(hasattr(package, "ClaudeCodeAdapterProfile"))
        self.assertTrue(hasattr(package, "probe_claude_code_surface"))

    def _module(self):
        try:
            return importlib.import_module("governed_ai_coding_runtime_contracts.claude_code_adapter")
        except ModuleNotFoundError as exc:
            self.fail(f"claude_code_adapter module is not implemented: {exc}")


if __name__ == "__main__":
    unittest.main()
