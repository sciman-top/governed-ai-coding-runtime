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


if __name__ == "__main__":
    unittest.main()
