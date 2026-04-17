import sys
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class ApprovalTests(unittest.TestCase):
    def test_approval_api_exists(self) -> None:
        try:
            module = importlib.import_module("governed_ai_coding_runtime_contracts.approval")
        except ModuleNotFoundError as exc:
            self.fail(f"approval module is not implemented: {exc}")
        if not hasattr(module, "ApprovalLedger"):
            self.fail("ApprovalLedger is not implemented")

    def test_create_approval_interrupts_task_until_decision(self) -> None:
        approval = importlib.import_module("governed_ai_coding_runtime_contracts.approval")
        ledger = approval.ApprovalLedger()

        request = ledger.create(
            task_id="task-123",
            requested_by="agent",
            tier="medium",
            reason="write requires approval",
        )
        interruption = ledger.interruption_for(request.approval_id)

        self.assertEqual(request.status, "pending")
        self.assertEqual(interruption.task_id, "task-123")
        self.assertEqual(interruption.task_state, "approval_pending")

    def test_approval_supports_terminal_decisions(self) -> None:
        approval = importlib.import_module("governed_ai_coding_runtime_contracts.approval")

        for action, expected_status in (
            ("approve", "approved"),
            ("reject", "rejected"),
            ("revoke", "revoked"),
            ("timeout", "timed_out"),
        ):
            ledger = approval.ApprovalLedger()
            request = ledger.create("task-123", "agent", "medium", f"{action} path")
            decided = getattr(ledger, action)(request.approval_id, decided_by="operator")
            self.assertEqual(decided.status, expected_status)

    def test_approval_results_are_persisted_by_id(self) -> None:
        approval = importlib.import_module("governed_ai_coding_runtime_contracts.approval")
        ledger = approval.ApprovalLedger()
        request = ledger.create("task-123", "agent", "high", "dangerous write")

        ledger.approve(request.approval_id, decided_by="operator")
        persisted = ledger.get(request.approval_id)

        self.assertEqual(persisted.status, "approved")
        self.assertEqual(persisted.decided_by, "operator")

    def test_audit_trail_includes_decisions(self) -> None:
        approval = importlib.import_module("governed_ai_coding_runtime_contracts.approval")
        ledger = approval.ApprovalLedger()
        request = ledger.create("task-123", "agent", "high", "dangerous write")

        ledger.reject(request.approval_id, decided_by="operator")
        event_types = [event.event_type for event in ledger.audit_trail(request.approval_id)]

        self.assertEqual(event_types, ["approval_created", "approval_rejected"])


if __name__ == "__main__":
    unittest.main()
