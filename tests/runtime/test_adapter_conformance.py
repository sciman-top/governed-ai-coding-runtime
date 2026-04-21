import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class AdapterConformanceTests(unittest.TestCase):
    def test_codex_and_non_codex_use_shared_conformance_gate_family(self) -> None:
        conformance = importlib.import_module("governed_ai_coding_runtime_contracts.adapter_conformance")

        codex_payload = {
            "adapter_id": "codex-cli",
            "flow_kind": "live_attach",
            "session_id": "session-codex",
            "resume_id": "resume-codex",
            "continuation_id": "task-codex:run-codex",
            "unsupported_capability_behavior": "none",
            "evidence_refs": ["artifacts/task-codex/evidence/codex-session.json"],
            "verification_refs": ["artifacts/task-codex/verification/runtime.txt"],
            "handoff_ref": "artifacts/task-codex/handoff/package.json",
        }
        generic_runtime_payload = {
            "summary": {
                "session_id": "session-generic",
                "resume_id": "resume-generic",
                "continuation_id": "task-generic:run-generic",
            },
            "request_gate": {
                "payload": {
                    "adapter_id": "generic.process.cli",
                }
            },
            "live_loop": {
                "flow_kind": "unknown",
                "fallback_explicit": True,
                "runtime_refs": [
                    "artifacts/task-generic/session-bridge-request/verification-output/contract.txt",
                    "artifacts/task-generic/session-bridge-request/verification-output/test.txt",
                ],
            },
        }

        codex_result = conformance.evaluate_codex_trial_conformance(codex_payload)
        generic_result = conformance.evaluate_runtime_check_conformance(
            generic_runtime_payload,
            host_family="generic_process",
        )

        self.assertEqual(codex_result.status, "pass")
        self.assertEqual(generic_result.status, "pass")
        self.assertEqual(codex_result.parity_status, "supported")
        self.assertEqual(generic_result.parity_status, "degraded")
        self.assertGreaterEqual(len(codex_result.linkage_refs), 3)
        self.assertGreaterEqual(len(generic_result.linkage_refs), 2)

    def test_parity_matrix_lists_supported_degraded_and_blocked(self) -> None:
        conformance = importlib.import_module("governed_ai_coding_runtime_contracts.adapter_conformance")

        supported = conformance.AdapterConformanceResult(
            adapter_id="codex-cli",
            host_family="codex",
            status="pass",
            failed_checks=[],
            parity_status="supported",
            linkage_refs=["a", "b", "c"],
        )
        degraded = conformance.AdapterConformanceResult(
            adapter_id="generic.process.cli",
            host_family="generic_process",
            status="pass",
            failed_checks=[],
            parity_status="degraded",
            linkage_refs=["a"],
        )
        blocked = conformance.AdapterConformanceResult(
            adapter_id="broken.adapter",
            host_family="fixture",
            status="fail",
            failed_checks=["missing_session_id"],
            parity_status="blocked",
            linkage_refs=[],
        )

        matrix = conformance.build_parity_matrix([supported, degraded, blocked])

        self.assertEqual(matrix[0]["parity_status"], "supported")
        self.assertEqual(matrix[1]["parity_status"], "degraded")
        self.assertEqual(matrix[2]["parity_status"], "blocked")
        self.assertEqual(matrix[2]["failed_checks"], ["missing_session_id"])

    def test_claude_trial_conformance_uses_same_gate_family(self) -> None:
        conformance = importlib.import_module("governed_ai_coding_runtime_contracts.adapter_conformance")

        payload = {
            "adapter_id": "claude-code",
            "flow_kind": "process_bridge",
            "session_id": "session-claude",
            "resume_id": "resume-claude",
            "continuation_id": "task-claude:run-claude",
            "unsupported_capability_behavior": "degrade_to_process_bridge",
            "evidence_refs": ["artifacts/task-claude/evidence/claude-session.json"],
            "verification_refs": ["artifacts/task-claude/verification/runtime.txt"],
            "handoff_ref": "artifacts/task-claude/handoff/package.json",
        }

        result = conformance.evaluate_claude_trial_conformance(payload)

        self.assertEqual(result.status, "pass")
        self.assertEqual(result.host_family, "claude_code")
        self.assertEqual(result.parity_status, "degraded")
        self.assertGreaterEqual(len(result.linkage_refs), 3)


if __name__ == "__main__":
    unittest.main()
