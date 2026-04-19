import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class MultiRepoTrialTests(unittest.TestCase):
    def test_multi_repo_trial_api_exists(self) -> None:
        module = self._module()
        if not hasattr(module, "MultiRepoTrialRecord"):
            self.fail("MultiRepoTrialRecord is not implemented")
        if not hasattr(module, "build_multi_repo_trial_record"):
            self.fail("build_multi_repo_trial_record is not implemented")

    def test_multi_repo_trial_record_captures_onboarding_feedback_shape(self) -> None:
        module = self._module()

        record = module.build_multi_repo_trial_record(
            trial_id="trial-001",
            repo_id="python-service",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            adapter_tier="process_bridge",
            unsupported_capabilities=["native_attach"],
            approval_friction="medium_write_needs_human",
            gate_failures=["contract"],
            replay_quality="replay_ready",
            evidence_refs=["artifacts/trial-001/evidence/bundle.json"],
            verification_refs=["artifacts/trial-001/verification-output/runtime.txt"],
            handoff_refs=["artifacts/trial-001/handoff/package.json"],
            follow_ups=[
                {
                    "category": "repo_specific",
                    "summary": "tighten repo build command",
                },
                {
                    "category": "adapter_generic",
                    "summary": "capture structured events when available",
                },
            ],
        )

        self.assertEqual(record.repo_id, "python-service")
        self.assertEqual(record.adapter_tier, "process_bridge")
        self.assertEqual(record.replay_quality, "replay_ready")
        self.assertEqual(record.follow_ups[0].category, "repo_specific")
        self.assertEqual(record.follow_ups[1].category, "adapter_generic")
        self.assertEqual(record.evidence_refs, ["artifacts/trial-001/evidence/bundle.json"])
        self.assertEqual(record.verification_refs, ["artifacts/trial-001/verification-output/runtime.txt"])
        self.assertEqual(record.handoff_refs, ["artifacts/trial-001/handoff/package.json"])

    def test_multi_repo_trial_rejects_unknown_follow_up_category(self) -> None:
        module = self._module()

        with self.assertRaises(ValueError):
            module.build_multi_repo_trial_record(
                trial_id="trial-002",
                repo_id="python-service",
                repo_binding_id="binding-python-service",
                adapter_id="codex-cli",
                adapter_tier="manual_handoff",
                unsupported_capabilities=["native_attach", "process_bridge"],
                approval_friction="manual_only",
                gate_failures=[],
                replay_quality="needs_follow_up",
                evidence_refs=["artifacts/trial-002/evidence/bundle.json"],
                verification_refs=["artifacts/trial-002/verification-output/runtime.txt"],
                handoff_refs=["artifacts/trial-002/handoff/package.json"],
                follow_ups=[{"category": "unknown_bucket", "summary": "bad category"}],
            )

    def test_run_multi_repo_trial_summarizes_two_repo_profiles(self) -> None:
        module = self._module()

        summary = module.run_multi_repo_trial(
            repo_profile_paths=[
                str(ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"),
                str(ROOT / "schemas" / "examples" / "repo-profile" / "typescript-webapp.example.json"),
            ],
            adapter_id="codex-cli",
            adapter_tier="process_bridge",
            unsupported_capabilities=["native_attach"],
        )

        self.assertEqual(summary.total_repos, 2)
        self.assertEqual(summary.records[0].adapter_tier, "process_bridge")
        self.assertTrue(all(record.verification_refs for record in summary.records))
        self.assertTrue(all(record.evidence_refs for record in summary.records))
        self.assertTrue(all(record.attachment_posture == "profile_validated" for record in summary.records))

    def test_run_multi_repo_trial_supports_two_attached_repos(self) -> None:
        module = self._module()
        repo_attachment = importlib.import_module("governed_ai_coding_runtime_contracts.repo_attachment")

        with self._temp_dir() as workspace:
            target_a = workspace / "target-a"
            target_b = workspace / "target-b"
            target_a.mkdir()
            target_b.mkdir()
            runtime_a = workspace / "runtime-state" / "target-a"
            runtime_b = workspace / "runtime-state" / "target-b"
            repo_attachment.attach_target_repo(
                target_repo_root=str(target_a),
                runtime_state_root=str(runtime_a),
                repo_id="target-a",
                display_name="Target A",
                primary_language="python",
                build_command="cmd /c exit 0",
                test_command="cmd /c exit 0",
                contract_command="cmd /c exit 0",
                adapter_preference="process_bridge",
            )
            repo_attachment.attach_target_repo(
                target_repo_root=str(target_b),
                runtime_state_root=str(runtime_b),
                repo_id="target-b",
                display_name="Target B",
                primary_language="python",
                build_command="cmd /c exit 0",
                test_command="cmd /c exit 0",
                contract_command="cmd /c exit 0",
                adapter_preference="process_bridge",
            )

            summary = module.run_multi_repo_trial(
                trial_id="trial-attached",
                adapter_id="codex-cli",
                adapter_tier="process_bridge",
                unsupported_capabilities=["native_attach"],
                attachment_roots=[str(target_a), str(target_b)],
                attachment_runtime_state_roots=[str(runtime_a), str(runtime_b)],
            )

            self.assertEqual(summary.total_repos, 2)
            self.assertTrue(all(record.attachment_posture == "healthy" for record in summary.records))
            self.assertTrue(all(record.verification_refs for record in summary.records))
            self.assertTrue(all(record.evidence_refs for record in summary.records))
            self.assertTrue(all(record.handoff_refs for record in summary.records))

    def test_run_multi_repo_trial_reports_attachment_doctor_failures(self) -> None:
        module = self._module()

        with self._temp_dir() as workspace:
            missing_pack_repo = workspace / "target-missing"
            missing_pack_repo.mkdir()
            runtime_root = workspace / "runtime-state" / "target-missing"

            summary = module.run_multi_repo_trial(
                trial_id="trial-missing-pack",
                adapter_id="codex-cli",
                adapter_tier="process_bridge",
                unsupported_capabilities=["native_attach"],
                attachment_roots=[str(missing_pack_repo)],
                attachment_runtime_state_roots=[str(runtime_root)],
            )

            self.assertEqual(summary.total_repos, 1)
            record = summary.records[0]
            self.assertEqual(record.attachment_posture, "missing_light_pack")
            self.assertEqual(record.replay_quality, "insufficient")
            self.assertIn("attachment_doctor", record.gate_failures)

    def _module(self):
        try:
            return importlib.import_module("governed_ai_coding_runtime_contracts.multi_repo_trial")
        except ModuleNotFoundError as exc:
            self.fail(f"multi_repo_trial module is not implemented: {exc}")

    def _temp_dir(self):
        from contextlib import contextmanager
        import tempfile

        @contextmanager
        def _wrapper():
            with tempfile.TemporaryDirectory() as tmp_dir:
                yield Path(tmp_dir)

        return _wrapper()


if __name__ == "__main__":
    unittest.main()
