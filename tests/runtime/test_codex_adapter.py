import importlib
import sys
import unittest
import subprocess
from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class CodexAdapterTests(unittest.TestCase):
    def test_codex_adapter_api_exists(self) -> None:
        module = self._module()
        if not hasattr(module, "CodexAdapterProfile"):
            self.fail("CodexAdapterProfile is not implemented")
        if not hasattr(module, "build_codex_adapter_profile"):
            self.fail("build_codex_adapter_profile is not implemented")
        if not hasattr(module, "classify_codex_adapter"):
            self.fail("classify_codex_adapter is not implemented")

    def test_codex_adapter_declares_core_capabilities(self) -> None:
        module = self._module()

        profile = module.build_codex_adapter_profile(
            native_attach_available=False,
            process_bridge_available=True,
            structured_events_available=False,
            evidence_export_available=False,
            resume_available=False,
        )

        self.assertEqual(profile.adapter_id, "codex-cli")
        self.assertEqual(profile.auth_ownership, "user_owned_upstream_auth")
        self.assertEqual(profile.workspace_control, "external_workspace")
        self.assertEqual(profile.tool_visibility, "logs_or_transcript_only")
        self.assertEqual(profile.mutation_model, "direct_workspace_write")
        self.assertEqual(profile.resume_behavior, "manual")
        self.assertEqual(profile.evidence_export_capability, "manual_summary")
        self.assertEqual(profile.unsupported_capability_behavior, "degrade_to_process_bridge")

    def test_codex_adapter_classifies_native_process_and_manual_tiers(self) -> None:
        module = self._module()

        native = module.build_codex_adapter_profile(
            native_attach_available=True,
            process_bridge_available=True,
            structured_events_available=True,
            evidence_export_available=True,
            resume_available=True,
        )
        process = module.build_codex_adapter_profile(
            native_attach_available=False,
            process_bridge_available=True,
            structured_events_available=False,
            evidence_export_available=False,
            resume_available=False,
        )
        manual = module.build_codex_adapter_profile(
            native_attach_available=False,
            process_bridge_available=False,
            structured_events_available=False,
            evidence_export_available=False,
            resume_available=False,
        )

        self.assertEqual(module.classify_codex_adapter(native).tier, "native_attach")
        self.assertEqual(module.classify_codex_adapter(process).tier, "process_bridge")
        self.assertEqual(module.classify_codex_adapter(manual).tier, "manual_handoff")

    def test_codex_live_probe_marks_manual_handoff_when_codex_cli_is_missing(self) -> None:
        module = self._module()

        def missing_runner(argv, _cwd):
            if argv == ["codex", "--version"]:
                return 127, "", "codex: command not found"
            return 127, "", "unsupported"

        probe = module.probe_codex_surface(command_runner=missing_runner)
        profile = module.build_codex_adapter_profile_from_probe(probe)

        self.assertFalse(probe.codex_cli_available)
        self.assertFalse(probe.process_bridge_available)
        self.assertEqual(module.classify_codex_adapter(profile).tier, "manual_handoff")
        self.assertIn("command not found", probe.reason)
        self.assertEqual(probe.failure_stage, "codex_command_unavailable")
        self.assertIsNotNone(probe.remediation_hint)
        self.assertIn("--version", probe.remediation_hint)

    def test_codex_live_probe_degrades_to_process_bridge_when_status_is_non_interactive(self) -> None:
        module = self._module()

        def non_interactive_runner(argv, _cwd):
            if argv == ["codex", "--version"]:
                return 0, "codex 1.2.3\n", ""
            if argv == ["codex", "--help"]:
                return 0, "Commands:\n  exec  Run Codex non-interactively\n  resume  Resume a previous session\n  status  Show runtime status\n", ""
            if argv == ["codex", "exec", "--help"]:
                return 0, "Options:\n  --json  Print events to stdout as JSONL\n  -o, --output-last-message <FILE>\n", ""
            if argv == ["codex", "status"]:
                return 1, "", "stdin is not a terminal"
            return 1, "", "unsupported"

        probe = module.probe_codex_surface(command_runner=non_interactive_runner)
        profile = module.build_codex_adapter_profile_from_probe(probe)
        capability = module.classify_codex_adapter(profile)

        self.assertTrue(probe.codex_cli_available)
        self.assertFalse(probe.native_attach_available)
        self.assertTrue(probe.process_bridge_available)
        self.assertTrue(probe.structured_events_available)
        self.assertTrue(probe.evidence_export_available)
        self.assertTrue(probe.resume_available)
        self.assertEqual(capability.tier, "process_bridge")
        self.assertIn("live attach unavailable", probe.reason)
        self.assertEqual(probe.failure_stage, "live_attach_unavailable_non_interactive")
        self.assertIsNotNone(probe.remediation_hint)
        self.assertIn("interactive terminal", probe.remediation_hint)

    def test_codex_live_probe_supports_custom_executable_override(self) -> None:
        module = self._module()
        executable = "D:/tools/codex.exe"

        def custom_runner(argv, _cwd):
            if argv == [executable, "--version"]:
                return 0, "codex 9.9.9\n", ""
            if argv == [executable, "--help"]:
                return 0, "Commands:\n  exec  Run Codex non-interactively\n  resume  Resume session\n  status  Show status\n", ""
            if argv == [executable, "exec", "--help"]:
                return 0, "Options:\n  --json  Print events to stdout as JSONL\n  -o, --output-last-message <FILE>\n", ""
            if argv == [executable, "status"]:
                return 0, "session_id=s-001 resume_id=r-001\n", ""
            return 1, "", "unsupported"

        probe = module.probe_codex_surface(
            command_runner=custom_runner,
            codex_executable=executable,
        )

        self.assertTrue(probe.codex_cli_available)
        self.assertTrue(probe.native_attach_available)
        self.assertIsNone(probe.failure_stage)
        self.assertIsNone(probe.remediation_hint)
        self.assertEqual(probe.probe_commands[0].cmd, f"{executable} --version")
        self.assertEqual(probe.probe_commands[1].cmd, f"{executable} --help")
        self.assertEqual(probe.probe_commands[2].cmd, f"{executable} exec --help")
        self.assertEqual(probe.probe_commands[3].cmd, f"{executable} status")

    def test_codex_live_probe_falls_back_to_codex_cmd_when_default_name_is_missing(self) -> None:
        module = self._module()

        def fallback_runner(argv, _cwd):
            if argv == ["codex", "--version"]:
                return 127, "", "[WinError 2] The system cannot find the file specified."
            if argv == ["codex.cmd", "--version"]:
                return 0, "codex-cli 0.121.0\n", ""
            if argv == ["codex.cmd", "--help"]:
                return 0, "Commands:\n  exec  Run Codex non-interactively\n  resume  Resume session\n  status  Show status\n", ""
            if argv == ["codex.cmd", "exec", "--help"]:
                return 0, "Options:\n  --json  Print events to stdout as JSONL\n", ""
            if argv == ["codex.cmd", "status"]:
                return 1, "", "stdin is not a terminal"
            return 1, "", "unsupported"

        probe = module.probe_codex_surface(command_runner=fallback_runner)
        profile = module.build_codex_adapter_profile_from_probe(probe)
        capability = module.classify_codex_adapter(profile)

        self.assertTrue(probe.codex_cli_available)
        self.assertEqual(capability.tier, "process_bridge")
        self.assertEqual(probe.failure_stage, "live_attach_unavailable_non_interactive")
        self.assertEqual(probe.probe_commands[0].cmd, "codex --version")
        self.assertEqual(probe.probe_commands[1].cmd, "codex.cmd --version")
        self.assertEqual(probe.probe_commands[2].cmd, "codex.cmd --help")
        self.assertEqual(probe.probe_commands[3].cmd, "codex.cmd exec --help")
        self.assertEqual(probe.probe_commands[4].cmd, "codex.cmd status")

    @unittest.skipUnless(sys.platform.startswith("win"), "Windows command shim behavior")
    def test_default_probe_runner_uses_shell_for_windows_command_shims(self) -> None:
        module = self._module()
        calls = []

        def fake_run_subprocess(**kwargs):
            calls.append(kwargs)
            return SimpleNamespace(returncode=0, stdout="codex-cli 0.124.0\n", stderr="")

        original_run_subprocess = module.run_subprocess
        module.run_subprocess = fake_run_subprocess
        try:
            exit_code, stdout, stderr = module._default_probe_runner(["codex", "--version"], ROOT)
        finally:
            module.run_subprocess = original_run_subprocess

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "codex-cli 0.124.0\n")
        self.assertEqual(stderr, "")
        self.assertTrue(calls[0]["shell"])
        self.assertIsInstance(calls[0]["command"], str)
        self.assertIn("codex --version", calls[0]["command"])

    def test_codex_live_probe_retries_and_stabilizes_transient_failure(self) -> None:
        module = self._module()
        calls = {"count": 0}

        def transient_runner(argv, _cwd):
            if argv == ["codex", "--version"]:
                calls["count"] += 1
                if calls["count"] == 1:
                    return 127, "", "codex: command not found"
                return 0, "codex-cli 0.121.0\n", ""
            if argv == ["codex", "--help"]:
                return 0, "Commands:\n  exec\n  resume\n", ""
            if argv == ["codex", "exec", "--help"]:
                return 0, "Options:\n  --json\n  --output-last-message\n", ""
            return 1, "", "unsupported"

        probe = module.probe_codex_surface(
            command_runner=transient_runner,
            max_probe_attempts=2,
        )
        profile = module.build_codex_adapter_profile_from_probe(probe)

        self.assertTrue(probe.codex_cli_available)
        self.assertEqual(probe.probe_attempts, 2)
        self.assertEqual(probe.stability_state, "stabilized")
        self.assertIn("recovered after probe retry", probe.reason)
        self.assertEqual(profile.adapter_tier, "native_attach")
        self.assertEqual(profile.unsupported_capabilities, [])
        self.assertGreaterEqual(len(probe.probe_commands), 4)

    def test_codex_live_probe_uses_exec_surface_when_status_command_is_missing(self) -> None:
        module = self._module()

        def no_status_runner(argv, _cwd):
            if argv == ["codex", "--version"]:
                return 0, "codex-cli 0.122.0\n", ""
            if argv == ["codex", "--help"]:
                return 0, "Commands:\n  exec  Run Codex non-interactively\n  resume  Resume a previous session\n", ""
            if argv == ["codex", "exec", "--help"]:
                return 0, "Options:\n  --json  Print events to stdout as JSONL\n  -o, --output-last-message <FILE>\n", ""
            return 1, "", "unsupported"

        probe = module.probe_codex_surface(command_runner=no_status_runner)
        profile = module.build_codex_adapter_profile_from_probe(probe)
        capability = module.classify_codex_adapter(profile)

        self.assertTrue(probe.codex_cli_available)
        self.assertTrue(probe.native_attach_available)
        self.assertTrue(probe.process_bridge_available)
        self.assertTrue(probe.structured_events_available)
        self.assertTrue(probe.evidence_export_available)
        self.assertTrue(probe.resume_available)
        self.assertEqual(capability.tier, "native_attach")
        self.assertIsNone(probe.failure_stage)
        self.assertIn("inferred from resume command surface", probe.reason)
        self.assertIsNotNone(probe.remediation_hint)

    def test_codex_live_probe_keeps_process_bridge_when_status_and_resume_are_missing(self) -> None:
        module = self._module()

        def no_status_no_resume_runner(argv, _cwd):
            if argv == ["codex", "--version"]:
                return 0, "codex-cli 0.122.0\n", ""
            if argv == ["codex", "--help"]:
                return 0, "Commands:\n  exec  Run Codex non-interactively\n", ""
            if argv == ["codex", "exec", "--help"]:
                return 0, "Options:\n  --json  Print events to stdout as JSONL\n", ""
            return 1, "", "unsupported"

        probe = module.probe_codex_surface(command_runner=no_status_no_resume_runner)
        profile = module.build_codex_adapter_profile_from_probe(probe)
        capability = module.classify_codex_adapter(profile)

        self.assertTrue(probe.codex_cli_available)
        self.assertFalse(probe.native_attach_available)
        self.assertTrue(probe.process_bridge_available)
        self.assertFalse(probe.resume_available)
        self.assertEqual(capability.tier, "process_bridge")
        self.assertEqual(probe.failure_stage, "live_attach_probe_unsupported_status_command_missing")
        self.assertEqual(probe.stability_state, "degraded_after_retry")
        self.assertEqual(probe.probe_attempts, 2)

    def test_codex_capability_readiness_marks_ready_and_blocked_states(self) -> None:
        module = self._module()
        ready_probe = module.CodexSurfaceProbe(
            codex_cli_available=True,
            version="codex-cli 0.121.0",
            native_attach_available=True,
            process_bridge_available=True,
            structured_events_available=True,
            evidence_export_available=True,
            resume_available=True,
            live_session_id=None,
            live_resume_id=None,
            reason="ready",
            probe_commands=[],
        )
        blocked_probe = module.CodexSurfaceProbe(
            codex_cli_available=False,
            version=None,
            native_attach_available=False,
            process_bridge_available=False,
            structured_events_available=False,
            evidence_export_available=False,
            resume_available=False,
            live_session_id=None,
            live_resume_id=None,
            reason="missing codex",
            probe_commands=[],
            failure_stage="codex_command_unavailable",
            remediation_hint="install codex",
        )

        ready = module.summarize_codex_capability_readiness(ready_probe)
        blocked = module.summarize_codex_capability_readiness(blocked_probe)

        self.assertEqual(ready.status, "ready")
        self.assertEqual(ready.adapter_tier, "native_attach")
        self.assertEqual(ready.flow_kind, "live_attach")
        self.assertEqual(ready.unsupported_capabilities, [])
        self.assertEqual(blocked.status, "blocked")
        self.assertEqual(blocked.adapter_tier, "manual_handoff")
        self.assertIn("native_attach", blocked.unsupported_capabilities)

    def test_codex_live_handshake_preserves_session_resume_and_continuation_identity(self) -> None:
        module = self._module()

        probe = module.CodexSurfaceProbe(
            codex_cli_available=True,
            version="codex 1.2.3",
            native_attach_available=True,
            process_bridge_available=True,
            structured_events_available=False,
            evidence_export_available=False,
            resume_available=True,
            live_session_id="session-live-001",
            live_resume_id="resume-live-001",
            reason="codex status handshake succeeded",
            probe_commands=[],
        )
        handshake = module.handshake_codex_session(
            task_id="task-codex",
            command_id="cmd-codex",
            payload={
                "session_id": "session-explicit-001",
                "resume_id": "resume-explicit-001",
                "continuation_id": "cont-explicit-001",
            },
            probe=probe,
        )

        self.assertEqual(handshake.adapter_tier, "native_attach")
        self.assertEqual(handshake.flow_kind, "live_attach")
        self.assertEqual(handshake.session_id, "session-explicit-001")
        self.assertEqual(handshake.resume_id, "resume-explicit-001")
        self.assertEqual(handshake.continuation_id, "cont-explicit-001")

    def test_codex_adapter_lists_unsupported_capabilities_explicitly(self) -> None:
        module = self._module()

        profile = module.build_codex_adapter_profile(
            native_attach_available=False,
            process_bridge_available=True,
            structured_events_available=False,
            evidence_export_available=False,
            resume_available=False,
        )

        self.assertIn("native_attach", profile.unsupported_capabilities)
        self.assertIn("structured_events", profile.unsupported_capabilities)
        self.assertIn("structured_evidence_export", profile.unsupported_capabilities)
        self.assertIn("resume_id", profile.unsupported_capabilities)

    def test_codex_adapter_profile_fields_are_stable(self) -> None:
        module = self._module()

        dataclass_fields = {field.name for field in fields(module.CodexAdapterProfile)}

        for expected in {
            "adapter_id",
            "auth_ownership",
            "workspace_control",
            "tool_visibility",
            "mutation_model",
            "resume_behavior",
            "evidence_export_capability",
            "adapter_tier",
            "unsupported_capabilities",
            "unsupported_capability_behavior",
        }:
            self.assertIn(expected, dataclass_fields)

    def test_codex_adapter_exports_from_package_root(self) -> None:
        package = importlib.import_module("governed_ai_coding_runtime_contracts")
        if not hasattr(package, "CodexAdapterProfile"):
            self.fail("CodexAdapterProfile is not exported from package root")
        if not hasattr(package, "build_codex_adapter_profile"):
            self.fail("build_codex_adapter_profile is not exported from package root")

    def test_codex_session_evidence_maps_runtime_events_to_one_task(self) -> None:
        module = self._module()
        evidence = importlib.import_module("governed_ai_coding_runtime_contracts.evidence")
        timeline = evidence.EvidenceTimeline()

        session = module.CodexSessionEvidence(
            task_id="task-codex",
            adapter_id="codex-cli",
            adapter_tier="native_attach",
            flow_kind="direct_adapter",
            file_changes=["src/service.py"],
            tool_calls=[{"tool": "apply_patch", "summary": "updated service"}],
            gate_runs=["artifacts/task-codex/run-1/verification-output/test.txt"],
            approvals=["approval-123"],
            handoff_refs=["artifacts/task-codex/run-1/handoff/package.json"],
            unsupported_capabilities=[],
        )

        events = module.record_codex_session_evidence(timeline, session)
        summary = evidence.summarize_adapter_evidence("task-codex", timeline)

        self.assertTrue(all(event.task_id == "task-codex" for event in events))
        self.assertEqual(summary.file_change_count, 1)
        self.assertEqual(summary.tool_call_count, 1)
        self.assertEqual(summary.gate_run_count, 1)
        self.assertEqual(summary.approval_event_count, 1)
        self.assertEqual(summary.handoff_ref_count, 1)

    def test_codex_session_evidence_distinguishes_manual_handoff_from_direct_adapter(self) -> None:
        module = self._module()
        evidence = importlib.import_module("governed_ai_coding_runtime_contracts.evidence")
        timeline = evidence.EvidenceTimeline()

        direct = module.CodexSessionEvidence(
            task_id="task-direct",
            adapter_id="codex-cli",
            adapter_tier="native_attach",
            flow_kind="direct_adapter",
            file_changes=[],
            tool_calls=[],
            gate_runs=[],
            approvals=[],
            handoff_refs=[],
            unsupported_capabilities=[],
        )
        manual = module.CodexSessionEvidence(
            task_id="task-manual",
            adapter_id="codex-cli",
            adapter_tier="manual_handoff",
            flow_kind="manual_handoff",
            file_changes=[],
            tool_calls=[],
            gate_runs=[],
            approvals=[],
            handoff_refs=[],
            unsupported_capabilities=["native_attach", "process_bridge"],
        )

        module.record_codex_session_evidence(timeline, direct)
        module.record_codex_session_evidence(timeline, manual)

        self.assertEqual(timeline.for_task("task-direct")[0].payload["flow_kind"], "direct_adapter")
        self.assertEqual(timeline.for_task("task-manual")[0].payload["flow_kind"], "manual_handoff")
        self.assertIn("native_attach", timeline.for_task("task-manual")[0].payload["unsupported_capabilities"])

    def test_codex_session_evidence_records_unsupported_events_instead_of_dropping_them(self) -> None:
        module = self._module()
        evidence = importlib.import_module("governed_ai_coding_runtime_contracts.evidence")
        timeline = evidence.EvidenceTimeline()

        session = module.CodexSessionEvidence(
            task_id="task-unsupported",
            adapter_id="codex-cli",
            adapter_tier="process_bridge",
            flow_kind="process_bridge",
            file_changes=[],
            tool_calls=[],
            gate_runs=[],
            approvals=[],
            handoff_refs=[],
            unsupported_capabilities=["structured_events"],
            execution_id="task-unsupported:run-1",
            continuation_id="task-unsupported:run-1",
            event_source="process_bridge",
            unsupported_events=[
                {
                    "event_type": "tool_diff_chunk",
                    "reason": "adapter did not provide diff chunk payload",
                }
            ],
        )
        module.record_codex_session_evidence(timeline, session)
        unsupported = [event for event in timeline.for_task("task-unsupported") if event.event_type == "adapter_unsupported_event"]

        self.assertGreaterEqual(len(unsupported), 2)
        self.assertTrue(any(event.payload.get("capability") == "structured_events" for event in unsupported))
        self.assertTrue(any(event.payload.get("event_type") == "tool_diff_chunk" for event in unsupported))

    def test_codex_adapter_trial_defaults_to_safe_mode_with_stable_refs(self) -> None:
        module = self._module()

        result = module.build_codex_adapter_trial_result(
            repo_id="python-service",
            task_id="task-codex-trial",
            binding_id="binding-python-service",
            native_attach_available=False,
            process_bridge_available=True,
            structured_events_available=False,
            evidence_export_available=False,
            resume_available=False,
        )

        self.assertEqual(result.mode, "safe")
        self.assertEqual(result.task_id, "task-codex-trial")
        self.assertEqual(result.binding_id, "binding-python-service")
        self.assertEqual(result.adapter_tier, "process_bridge")
        self.assertEqual(result.unsupported_capability_behavior, "degrade_to_process_bridge")
        self.assertTrue(result.evidence_refs)
        self.assertTrue(result.verification_refs)
        self.assertIn("artifacts/task-codex-trial/codex-trial-safe/evidence/codex-session.json", result.evidence_refs)
        self.assertIn(
            "artifacts/task-codex-trial/codex-trial-safe/verification-output/runtime.txt",
            result.verification_refs,
        )
        self.assertIn(result.flow_kind, {"live_attach", "process_bridge", "manual_handoff"})
        self.assertTrue(result.continuation_id.startswith("task-codex-trial:"))

    def test_codex_adapter_trial_script_emits_json_summary(self) -> None:
        script = ROOT / "scripts" / "run-codex-adapter-trial.py"

        completed = subprocess.run(
            [
                sys.executable,
                str(script),
                "--repo-id",
                "python-service",
                "--task-id",
                "task-codex-trial",
                "--binding-id",
                "binding-python-service",
            ],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = __import__("json").loads(completed.stdout)
        self.assertEqual(payload["mode"], "safe")
        self.assertEqual(payload["task_id"], "task-codex-trial")
        self.assertEqual(payload["binding_id"], "binding-python-service")
        self.assertIn("adapter_tier", payload)
        self.assertIn("evidence_refs", payload)
        self.assertIn("verification_refs", payload)

    def _module(self):
        try:
            return importlib.import_module("governed_ai_coding_runtime_contracts.codex_adapter")
        except ModuleNotFoundError as exc:
            self.fail(f"codex_adapter module is not implemented: {exc}")


if __name__ == "__main__":
    unittest.main()
