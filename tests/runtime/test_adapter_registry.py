import importlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class AdapterRegistryTests(unittest.TestCase):
    def test_resolve_launch_fallback_prefers_native_attach_when_available(self) -> None:
        adapter_registry = importlib.import_module("governed_ai_coding_runtime_contracts.adapter_registry")

        capability = adapter_registry.resolve_launch_fallback(
            adapter_id="codex-cli",
            native_attach_available=True,
            process_bridge_available=True,
        )

        self.assertEqual(capability.tier, "native_attach")
        self.assertTrue(capability.supported)

    def test_resolve_launch_fallback_uses_process_bridge_when_native_attach_unavailable(self) -> None:
        adapter_registry = importlib.import_module("governed_ai_coding_runtime_contracts.adapter_registry")

        capability = adapter_registry.resolve_launch_fallback(
            adapter_id="codex-cli",
            native_attach_available=False,
            process_bridge_available=True,
        )

        self.assertEqual(capability.tier, "process_bridge")
        self.assertEqual(capability.unsupported_capability_behavior, "degrade_to_process_bridge")

    def test_resolve_launch_fallback_uses_manual_handoff_when_process_bridge_unavailable(self) -> None:
        adapter_registry = importlib.import_module("governed_ai_coding_runtime_contracts.adapter_registry")

        capability = adapter_registry.resolve_launch_fallback(
            adapter_id="codex-cli",
            native_attach_available=False,
            process_bridge_available=False,
        )

        self.assertEqual(capability.tier, "manual_handoff")
        self.assertEqual(capability.unsupported_capability_behavior, "degrade_to_manual_handoff")

    def test_build_adapter_contract_includes_tier_and_governance_guarantees(self) -> None:
        adapter_registry = importlib.import_module("governed_ai_coding_runtime_contracts.adapter_registry")

        contract = adapter_registry.build_adapter_contract(
            adapter_id="codex-cli",
            display_name="Codex CLI",
            product_family="codex",
            adapter_tier="process_bridge",
            auth_ownership="user_owned_upstream_auth",
            workspace_control="external_workspace",
            event_visibility="logs_only",
            mutation_model="direct_workspace_write",
            continuation_model="manual",
            evidence_model="manual_summary",
            unsupported_capability_behavior="degrade_to_process_bridge",
        )

        self.assertEqual(contract.adapter_tier, "process_bridge")
        self.assertIn("captured process boundary", contract.governance_guarantees)
        self.assertEqual(contract.unsupported_capability_behavior, "degrade_to_process_bridge")

    def test_codex_profile_projects_into_generic_adapter_contract(self) -> None:
        codex_adapter = importlib.import_module("governed_ai_coding_runtime_contracts.codex_adapter")
        adapter_registry = importlib.import_module("governed_ai_coding_runtime_contracts.adapter_registry")

        profile = codex_adapter.build_codex_adapter_profile(
            native_attach_available=False,
            process_bridge_available=True,
            structured_events_available=False,
            evidence_export_available=False,
            resume_available=False,
        )
        contract = adapter_registry.project_codex_profile_to_adapter_contract(profile)

        self.assertEqual(contract.adapter_id, "codex-cli")
        self.assertEqual(contract.adapter_tier, "process_bridge")
        self.assertEqual(contract.auth_ownership, "user_owned_upstream_auth")
        self.assertEqual(contract.unsupported_capability_behavior, "degrade_to_process_bridge")

    def test_claude_code_contract_is_available_as_first_class_adapter(self) -> None:
        adapter_registry = importlib.import_module("governed_ai_coding_runtime_contracts.adapter_registry")

        contract = adapter_registry.build_claude_code_contract(adapter_tier="process_bridge")

        self.assertEqual(contract.adapter_id, "claude-code")
        self.assertEqual(contract.product_family, "claude_code")
        self.assertEqual(contract.adapter_tier, "process_bridge")
        self.assertIn("session_bridge", contract.minimum_required_runtime_controls)

    def test_agent_adapter_examples_cover_process_bridge_and_manual_handoff(self) -> None:
        manual_path = ROOT / "schemas" / "examples" / "agent-adapter-contract" / "manual-handoff.example.json"
        process_path = ROOT / "schemas" / "examples" / "agent-adapter-contract" / "process-bridge.example.json"

        self.assertTrue(manual_path.exists(), "manual handoff example is missing")
        self.assertTrue(process_path.exists(), "process bridge example is missing")

        manual_payload = json.loads(manual_path.read_text(encoding="utf-8"))
        process_payload = json.loads(process_path.read_text(encoding="utf-8"))

        self.assertEqual(manual_payload["adapters"][0]["adapter_tier"], "manual_handoff")
        self.assertEqual(process_payload["adapters"][0]["adapter_tier"], "process_bridge")

    def test_executable_registry_can_register_probe_select_and_delegate(self) -> None:
        adapter_registry = importlib.import_module("governed_ai_coding_runtime_contracts.adapter_registry")

        registry = adapter_registry.ExecutableAdapterRegistry()
        codex_contract = adapter_registry.build_adapter_contract(
            adapter_id="codex-cli",
            display_name="Codex CLI",
            product_family="codex",
            adapter_tier="process_bridge",
            auth_ownership="user_owned_upstream_auth",
            workspace_control="external_workspace",
            event_visibility="logs_only",
            mutation_model="direct_workspace_write",
            continuation_model="manual",
            evidence_model="manual_summary",
            unsupported_capability_behavior="degrade_to_manual_handoff",
        )

        def codex_probe(_context: dict) -> object:
            return adapter_registry.AdapterProbeResult(
                adapter_id="codex-cli",
                native_attach_available=False,
                process_bridge_available=True,
                reason="live attach unavailable in non-interactive session",
                probe_source="live_probe",
            )

        def codex_delegate(request: dict) -> dict:
            return {
                "status": "delegated",
                "request_id": request.get("request_id"),
            }

        registry.register(contract=codex_contract, probe=codex_probe, delegate=codex_delegate)
        selection = registry.select("codex-cli", context={"attachment_root": "D:/repos/target"})
        delegated = registry.delegate(
            adapter_id="codex-cli",
            context={"attachment_root": "D:/repos/target"},
            request={"request_id": "req-001"},
        )

        self.assertEqual(selection.tier, "process_bridge")
        self.assertEqual(selection.flow_kind, "process_bridge")
        self.assertEqual(selection.probe_source, "live_probe")
        self.assertEqual(delegated["status"], "delegated")
        self.assertEqual(delegated["request_id"], "req-001")
        self.assertEqual(delegated["adapter_id"], "codex-cli")

    def test_executable_registry_supports_non_codex_fixture_through_same_interface(self) -> None:
        adapter_registry = importlib.import_module("governed_ai_coding_runtime_contracts.adapter_registry")

        registry = adapter_registry.ExecutableAdapterRegistry()
        generic_contract = adapter_registry.build_adapter_contract(
            adapter_id="generic.process.cli",
            display_name="Generic Process CLI",
            product_family="generic_process",
            adapter_tier="manual_handoff",
            auth_ownership="unsupported",
            workspace_control="external_workspace",
            event_visibility="logs_only",
            mutation_model="git_diff",
            continuation_model="stateless",
            evidence_model="command_log",
            unsupported_capability_behavior="degrade_to_advisory",
        )
        registry.register(contract=generic_contract)

        discovered = registry.discover(product_family="generic_process")
        selection = registry.select("generic.process.cli")
        delegated = registry.delegate(adapter_id="generic.process.cli", request={"request_id": "req-002"})

        self.assertEqual(len(discovered), 1)
        self.assertEqual(discovered[0].adapter_id, "generic.process.cli")
        self.assertEqual(selection.tier, "manual_handoff")
        self.assertEqual(selection.flow_kind, "manual_handoff")
        self.assertEqual(delegated["status"], "manual_handoff")

    def test_attachment_scoped_selection_uses_requested_tier_and_detected_probe(self) -> None:
        adapter_registry = importlib.import_module("governed_ai_coding_runtime_contracts.adapter_registry")

        registry = adapter_registry.ExecutableAdapterRegistry()
        codex_contract = adapter_registry.build_adapter_contract(
            adapter_id="codex-cli",
            display_name="Codex CLI",
            product_family="codex",
            adapter_tier="native_attach",
            auth_ownership="user_owned_upstream_auth",
            workspace_control="external_workspace",
            event_visibility="logs_only",
            mutation_model="direct_workspace_write",
            continuation_model="manual",
            evidence_model="manual_summary",
            unsupported_capability_behavior="degrade_to_process_bridge",
        )
        generic_contract = adapter_registry.build_adapter_contract(
            adapter_id="generic.process.cli",
            display_name="Generic Process CLI",
            product_family="generic_process",
            adapter_tier="manual_handoff",
            auth_ownership="unsupported",
            workspace_control="external_workspace",
            event_visibility="logs_only",
            mutation_model="git_diff",
            continuation_model="stateless",
            evidence_model="command_log",
            unsupported_capability_behavior="degrade_to_advisory",
        )

        def codex_probe(_context: dict) -> object:
            return adapter_registry.AdapterProbeResult(
                adapter_id="codex-cli",
                native_attach_available=False,
                process_bridge_available=True,
                reason="host cannot attach natively",
                probe_source="live_probe",
            )

        registry.register(contract=codex_contract, probe=codex_probe)
        registry.register(contract=generic_contract)

        selection = registry.select_for_attachment(
            attachment={
                "adapter_preference": "native_attach",
                "allowed_adapters": ["codex-cli", "generic.process.cli"],
            }
        )

        self.assertEqual(selection.adapter_id, "codex-cli")
        self.assertEqual(selection.tier, "process_bridge")
        self.assertTrue(selection.degraded)
        self.assertEqual(selection.requested_tier, "native_attach")
        self.assertIn("degraded", selection.degrade_reason)


if __name__ == "__main__":
    unittest.main()
