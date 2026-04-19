import importlib
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class ContractReaderParityTests(unittest.TestCase):
    def test_adapter_selection_reader_requires_contract_shape(self) -> None:
        adapter_registry = importlib.import_module("governed_ai_coding_runtime_contracts.adapter_registry")
        selection = adapter_registry.adapter_selection_from_dict(
            {
                "adapter_id": "codex-cli",
                "tier": "process_bridge",
                "flow_kind": "process_bridge",
                "reason": "native attach unavailable",
                "unsupported_capability_behavior": "degrade_to_process_bridge",
                "probe_source": "live_probe",
                "requested_tier": "native_attach",
                "degraded": True,
                "degrade_reason": "requested native_attach degraded to process_bridge",
            }
        )
        self.assertEqual(selection.adapter_id, "codex-cli")
        with self.assertRaises(ValueError):
            adapter_registry.adapter_selection_from_dict(
                {
                    "adapter_id": "codex-cli",
                    "tier": "process_bridge",
                }
            )

    def test_reader_contracts_fail_loudly_on_missing_fields(self) -> None:
        session_bridge = importlib.import_module("governed_ai_coding_runtime_contracts.session_bridge")
        runtime_status = importlib.import_module("governed_ai_coding_runtime_contracts.runtime_status")
        verification_runner = importlib.import_module("governed_ai_coding_runtime_contracts.verification_runner")

        with self.assertRaises(ValueError):
            session_bridge.session_bridge_result_from_dict({"command_id": "cmd"})
        with self.assertRaises(ValueError):
            runtime_status.runtime_snapshot_from_dict({"total_tasks": 0})
        with self.assertRaises(ValueError):
            verification_runner.verification_artifact_from_dict({"mode": "quick"})


if __name__ == "__main__":
    unittest.main()
