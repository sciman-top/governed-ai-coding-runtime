import sys
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class ControlConsoleTests(unittest.TestCase):
    def test_control_console_api_exists(self) -> None:
        try:
            module = importlib.import_module("governed_ai_coding_runtime_contracts.control_console")
        except ModuleNotFoundError as exc:
            self.fail(f"control_console module is not implemented: {exc}")
        if not hasattr(module, "ControlPlaneConsole"):
            self.fail("ControlPlaneConsole is not implemented")

    def test_user_can_approve_or_reject_pending_steps(self) -> None:
        approval = importlib.import_module("governed_ai_coding_runtime_contracts.approval")
        evidence = importlib.import_module("governed_ai_coding_runtime_contracts.evidence")
        control_console = importlib.import_module("governed_ai_coding_runtime_contracts.control_console")
        ledger = approval.ApprovalLedger()
        timeline = evidence.EvidenceTimeline()
        console = control_console.ControlPlaneConsole(ledger, timeline)
        first = ledger.create("task-123", "apply_patch", "medium", "write src/service.py")
        second = ledger.create("task-456", "apply_patch", "medium", "write src/other.py")

        approved = console.approve(first.approval_id, operator="user")
        rejected = console.reject(second.approval_id, operator="user")

        self.assertEqual(approved.status, "approved")
        self.assertEqual(rejected.status, "rejected")

    def test_user_can_inspect_evidence_by_task(self) -> None:
        approval = importlib.import_module("governed_ai_coding_runtime_contracts.approval")
        evidence = importlib.import_module("governed_ai_coding_runtime_contracts.evidence")
        control_console = importlib.import_module("governed_ai_coding_runtime_contracts.control_console")
        timeline = evidence.EvidenceTimeline()
        timeline.append("task-123", "decision", {"summary": "approved write"})
        console = control_console.ControlPlaneConsole(approval.ApprovalLedger(), timeline)

        events = console.evidence_for_task("task-123")

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].payload["summary"], "approved write")

    def test_console_scope_stays_control_plane_focused(self) -> None:
        approval = importlib.import_module("governed_ai_coding_runtime_contracts.approval")
        evidence = importlib.import_module("governed_ai_coding_runtime_contracts.evidence")
        control_console = importlib.import_module("governed_ai_coding_runtime_contracts.control_console")
        console = control_console.ControlPlaneConsole(approval.ApprovalLedger(), evidence.EvidenceTimeline())

        self.assertEqual(console.scope, "control_plane")
        self.assertFalse(hasattr(console, "execute_tool"))


if __name__ == "__main__":
    unittest.main()
