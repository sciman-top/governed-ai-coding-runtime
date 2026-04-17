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


if __name__ == "__main__":
    unittest.main()
