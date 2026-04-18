import sys
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class EvidenceTimelineTests(unittest.TestCase):
    def test_evidence_timeline_api_exists(self) -> None:
        try:
            module = importlib.import_module("governed_ai_coding_runtime_contracts.evidence")
        except ModuleNotFoundError as exc:
            self.fail(f"evidence module is not implemented: {exc}")
        if not hasattr(module, "EvidenceTimeline"):
            self.fail("EvidenceTimeline is not implemented")

    def test_timeline_captures_structured_events_by_task_id(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.evidence")
        timeline = module.EvidenceTimeline()
        timeline.append("task-1", "task_created", {"goal": "inspect repo"})
        timeline.append("task-1", "decision", {"state": "scoped"})
        timeline.append("task-1", "command", {"command": "rg TODO", "exit_code": 0})
        timeline.append("task-1", "output", {"summary": "no TODO markers"})

        events = timeline.for_task("task-1")

        self.assertEqual([event.event_type for event in events], ["task_created", "decision", "command", "output"])
        self.assertEqual(events[2].payload["command"], "rg TODO")

    def test_task_output_summary_is_reviewable_by_task_id(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.evidence")
        timeline = module.EvidenceTimeline()
        timeline.append("task-1", "task_created", {"goal": "inspect repo"})
        timeline.append("task-1", "output", {"summary": "read-only session accepted"})

        output = module.build_task_output("task-1", timeline)

        self.assertEqual(output.task_id, "task-1")
        self.assertEqual(output.event_count, 2)
        self.assertEqual(output.latest_summary, "read-only session accepted")

    def test_evidence_quality_flags_missing_required_evidence_separately(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.evidence")

        assessment = module.assess_evidence_bundle(
            {
                "task_id": "task-1",
                "repo_id": "repo-1",
                "goal": "land clarification policy",
                "verification_results": [],
                "final_outcome": {"status": "blocked"},
                "open_questions": [],
            }
        )

        self.assertFalse(assessment.ready_for_completion)
        self.assertIn("commands_run", assessment.missing_required_fields)
        self.assertEqual(assessment.advisory_findings, [])

    def test_evidence_quality_keeps_advisory_weaknesses_distinct_from_missing_fields(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.evidence")

        assessment = module.assess_evidence_bundle(
            {
                "task_id": "task-1",
                "repo_id": "repo-1",
                "goal": "land clarification policy",
                "commands_run": [{"command": "python -m unittest", "exit_code": 0}],
                "tool_calls": [],
                "files_changed": [],
                "approvals": [],
                "required_evidence": [{"kind": "verification_log", "status": "advisory_only"}],
                "verification_results": [{"gate_level": "test", "status": "advisory"}],
                "rollback_ref": "git:HEAD~1",
                "final_outcome": {"status": "completed"},
                "open_questions": [],
            }
        )

        self.assertTrue(assessment.ready_for_completion)
        self.assertEqual(assessment.missing_required_fields, [])
        self.assertIn("verification:test:advisory", assessment.advisory_findings)

    def test_evidence_completeness_flags_missing_rollback_reference(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.evidence")

        assessment = module.assess_evidence_bundle(
            {
                "task_id": "task-1",
                "repo_id": "repo-1",
                "goal": "land control completeness",
                "commands_run": [{"command": "python -m unittest", "exit_code": 0}],
                "tool_calls": [],
                "files_changed": [],
                "approvals": [],
                "required_evidence": [{"kind": "verification_log", "status": "present"}],
                "verification_results": [{"gate_level": "test", "status": "passed"}],
                "final_outcome": {"status": "completed"},
                "open_questions": [],
            }
        )

        self.assertFalse(assessment.ready_for_completion)
        self.assertIn("rollback_ref", assessment.missing_required_fields)

    def test_adapter_evidence_summary_counts_codex_events(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.evidence")
        timeline = module.EvidenceTimeline()
        timeline.append("task-1", "adapter_file_change", {"path": "src/service.py"})
        timeline.append("task-1", "adapter_tool_call", {"tool": "apply_patch"})
        timeline.append("task-1", "adapter_gate_run", {"artifact_ref": "artifacts/task-1/test.txt"})
        timeline.append("task-1", "adapter_approval_event", {"approval_id": "approval-123"})
        timeline.append("task-1", "adapter_handoff", {"handoff_ref": "artifacts/task-1/handoff.json"})

        summary = module.summarize_adapter_evidence("task-1", timeline)

        self.assertEqual(summary.file_change_count, 1)
        self.assertEqual(summary.tool_call_count, 1)
        self.assertEqual(summary.gate_run_count, 1)
        self.assertEqual(summary.approval_event_count, 1)
        self.assertEqual(summary.handoff_ref_count, 1)

    def test_evidence_bundle_can_embed_multi_repo_trial_feedback(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.evidence")
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")
        plan = verification_runner.build_verification_plan("quick")
        artifact = verification_runner.build_verification_artifact(
            plan,
            "docs/change-evidence/trial.md",
            {"test": "pass", "contract": "pass"},
        )

        bundle = module.build_evidence_bundle(
            task_id="task-trial",
            repo_id="python-service",
            goal="exercise trial evidence",
            acceptance_criteria=["trial record is linked"],
            verification_artifact=artifact,
            rollback_ref="git:HEAD~1",
            final_status="completed",
            final_summary="trial completed",
            artifact_refs=["artifacts/task-trial/evidence/bundle.json"],
            trial_feedback={
                "trial_id": "trial-001",
                "repo_id": "python-service",
                "adapter_tier": "process_bridge",
                "follow_up_categories": ["repo_specific", "adapter_generic"],
            },
        )

        self.assertEqual(bundle["trial_feedback"]["trial_id"], "trial-001")
        self.assertEqual(bundle["trial_feedback"]["adapter_tier"], "process_bridge")


if __name__ == "__main__":
    unittest.main()
