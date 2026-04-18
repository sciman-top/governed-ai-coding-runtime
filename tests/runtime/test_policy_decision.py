import sys
import unittest
from pathlib import Path
import importlib
import json
import subprocess
from dataclasses import fields

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class PolicyDecisionTests(unittest.TestCase):
    def test_policy_decision_api_exists(self) -> None:
        try:
            module = importlib.import_module("governed_ai_coding_runtime_contracts.policy_decision")
        except ModuleNotFoundError as exc:
            self.fail(f"policy_decision module is not implemented: {exc}")
        if not hasattr(module, "PolicyDecision"):
            self.fail("PolicyDecision is not implemented")
        if not hasattr(module, "build_policy_decision"):
            self.fail("build_policy_decision is not implemented")
        if not hasattr(module, "is_executable_action"):
            self.fail("is_executable_action is not implemented")

    def test_allow_decision_is_executable(self) -> None:
        policy_decision = importlib.import_module("governed_ai_coding_runtime_contracts.policy_decision")

        decision = policy_decision.build_policy_decision(
            task_id="task-123",
            action_id="action-allow",
            risk_tier="low",
            subject="session_command:quick_gate",
            status="allow",
            decision_basis=["command stays within allowed posture"],
            evidence_ref="artifacts/task-123/policy/allow.json",
        )

        self.assertEqual(decision.schema_version, "1.0")
        self.assertEqual(decision.status, "allow")
        self.assertIsNone(decision.required_approval_ref)
        self.assertTrue(policy_decision.is_executable_action(decision))

    def test_escalate_decision_carries_approval_without_execution(self) -> None:
        policy_decision = importlib.import_module("governed_ai_coding_runtime_contracts.policy_decision")

        decision = policy_decision.build_policy_decision(
            task_id="task-123",
            action_id="action-escalate",
            risk_tier="high",
            subject="write_request:src/service.py",
            status="escalate",
            decision_basis=["high-tier write requires approval"],
            evidence_ref="artifacts/task-123/policy/escalate.json",
            required_approval_ref="approval-123",
        )

        self.assertEqual(decision.status, "escalate")
        self.assertEqual(decision.required_approval_ref, "approval-123")
        self.assertFalse(policy_decision.is_executable_action(decision))

    def test_deny_fails_closed_and_requires_remediation(self) -> None:
        policy_decision = importlib.import_module("governed_ai_coding_runtime_contracts.policy_decision")

        decision = policy_decision.build_policy_decision(
            task_id="task-123",
            action_id="action-deny",
            risk_tier="high",
            subject="write_request:secrets/prod.env",
            status="deny",
            decision_basis=["path is blocked by repository policy"],
            evidence_ref="artifacts/task-123/policy/deny.json",
            remediation_hint="write only under src/** or request a different workflow",
        )

        self.assertEqual(decision.status, "deny")
        self.assertFalse(policy_decision.is_executable_action(decision))

        with self.assertRaises(ValueError):
            policy_decision.build_policy_decision(
                task_id="task-123",
                action_id="action-deny-no-hint",
                risk_tier="high",
                subject="write_request:secrets/prod.env",
                status="deny",
                decision_basis=["path is blocked by repository policy"],
                evidence_ref="artifacts/task-123/policy/deny.json",
            )

    def test_invalid_status_is_rejected(self) -> None:
        policy_decision = importlib.import_module("governed_ai_coding_runtime_contracts.policy_decision")

        with self.assertRaises(ValueError):
            policy_decision.build_policy_decision(
                task_id="task-123",
                action_id="action-invalid",
                risk_tier="medium",
                subject="session_command:run_full_gate",
                status="pause",
                decision_basis=["unsupported decision status"],
                evidence_ref="artifacts/task-123/policy/invalid.json",
            )

    def test_python_contract_covers_schema_required_fields(self) -> None:
        policy_decision = importlib.import_module("governed_ai_coding_runtime_contracts.policy_decision")
        schema = json.loads((ROOT / "schemas" / "jsonschema" / "policy-decision.schema.json").read_text(encoding="utf-8"))

        dataclass_fields = {field.name for field in fields(policy_decision.PolicyDecision)}
        for required_field in schema["required"]:
            self.assertIn(required_field, dataclass_fields)

    def test_policy_decision_schema_rejects_non_escalation_approval_refs(self) -> None:
        base_payload = {
            "schema_version": "1.0",
            "task_id": "task-123",
            "action_id": "action-schema",
            "risk_tier": "low",
            "subject": "session_command:quick_gate",
            "decision_basis": ["schema should reject approval refs outside escalation"],
            "evidence_ref": "artifacts/task-123/policy/schema.json",
        }

        allow_payload = dict(base_payload, status="allow", required_approval_ref="approval-not-allowed")
        deny_payload = dict(
            base_payload,
            status="deny",
            risk_tier="high",
            required_approval_ref="approval-not-allowed",
            remediation_hint="choose an allowed path",
        )

        self.assertFalse(self._schema_accepts(allow_payload))
        self.assertFalse(self._schema_accepts(deny_payload))

    def test_policy_decision_exports_from_package_root(self) -> None:
        package = importlib.import_module("governed_ai_coding_runtime_contracts")
        if not hasattr(package, "PolicyDecision"):
            self.fail("PolicyDecision is not exported from package root")
        if not hasattr(package, "build_policy_decision"):
            self.fail("build_policy_decision is not exported from package root")

    def _schema_accepts(self, payload: dict) -> bool:
        schema_path = ROOT / "schemas" / "jsonschema" / "policy-decision.schema.json"
        command = (
            "$json = [Console]::In.ReadToEnd(); "
            f"if (Test-Json -Json $json -SchemaFile '{schema_path}') "
            "{ Write-Output 'true' } else { Write-Output 'false' }"
        )
        completed = subprocess.run(
            ["pwsh", "-NoProfile", "-Command", command],
            input=json.dumps(payload),
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        return completed.stdout.strip().lower() == "true"


if __name__ == "__main__":
    unittest.main()
