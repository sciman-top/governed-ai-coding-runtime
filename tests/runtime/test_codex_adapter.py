import importlib
import sys
import unittest
import subprocess
from dataclasses import fields
from pathlib import Path

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
