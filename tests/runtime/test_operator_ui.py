import json
import sys
import tempfile
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class OperatorUiTests(unittest.TestCase):
    def test_operator_ui_renders_empty_state_html(self) -> None:
        runtime_status = importlib.import_module("governed_ai_coding_runtime_contracts.runtime_status")
        operator_ui = importlib.import_module("governed_ai_coding_runtime_contracts.operator_ui")

        html = operator_ui.render_runtime_snapshot_html(
            runtime_status.RuntimeSnapshot(
                total_tasks=0,
                maintenance=importlib.import_module(
                    "governed_ai_coding_runtime_contracts.maintenance_policy"
                ).MaintenancePolicyStatus(
                    stage="missing",
                    compatibility_policy_ref=None,
                    upgrade_policy_ref=None,
                    triage_policy_ref=None,
                    deprecation_policy_ref=None,
                    retirement_policy_ref=None,
                ),
                tasks=[],
            )
        )

        self.assertIn("Governed Runtime Operator Surface", html)
        self.assertIn("No governed tasks recorded", html)
        self.assertIn("Maintenance Policy Surface", html)

    def test_operator_ui_renders_non_empty_snapshot(self) -> None:
        maintenance_policy = importlib.import_module("governed_ai_coding_runtime_contracts.maintenance_policy")
        runtime_status = importlib.import_module("governed_ai_coding_runtime_contracts.runtime_status")
        operator_ui = importlib.import_module("governed_ai_coding_runtime_contracts.operator_ui")

        snapshot = runtime_status.RuntimeSnapshot(
            total_tasks=1,
            maintenance=maintenance_policy.MaintenancePolicyStatus(
                stage="completed",
                compatibility_policy_ref="docs/product/runtime-compatibility-and-upgrade-policy.md",
                upgrade_policy_ref="docs/product/runtime-compatibility-and-upgrade-policy.md",
                triage_policy_ref="docs/product/maintenance-deprecation-and-retirement-policy.md",
                deprecation_policy_ref="docs/product/maintenance-deprecation-and-retirement-policy.md",
                retirement_policy_ref="docs/product/maintenance-deprecation-and-retirement-policy.md",
            ),
            tasks=[
                runtime_status.RuntimeTaskStatus(
                    task_id="task-ui-001",
                    current_state="delivered",
                    goal="show operator task",
                    rollback_ref="docs/runbooks/control-rollback.md",
                    active_run_id="run-ui-001",
                    workspace_root=".governed-workspaces/demo",
                    approval_ids=[],
                    artifact_refs=["artifacts/task-ui-001/run-ui-001/execution-output/worker.txt"],
                    evidence_refs=["artifacts/task-ui-001/run-ui-001/evidence/bundle.json"],
                    verification_refs=["artifacts/task-ui-001/run-ui-001/verification-output/test.txt"],
                )
            ],
        )

        html = operator_ui.render_runtime_snapshot_html(snapshot)

        self.assertIn("task-ui-001", html)
        self.assertIn("show operator task", html)
        self.assertIn("verification-output/test.txt", html)
        self.assertIn("runtime-compatibility-and-upgrade-policy.md", html)

    def test_operator_ui_writes_html_file(self) -> None:
        maintenance_policy = importlib.import_module("governed_ai_coding_runtime_contracts.maintenance_policy")
        runtime_status = importlib.import_module("governed_ai_coding_runtime_contracts.runtime_status")
        operator_ui = importlib.import_module("governed_ai_coding_runtime_contracts.operator_ui")

        with tempfile.TemporaryDirectory() as tmp_dir:
            snapshot = runtime_status.RuntimeSnapshot(
                total_tasks=0,
                maintenance=maintenance_policy.MaintenancePolicyStatus(
                    stage="missing",
                    compatibility_policy_ref=None,
                    upgrade_policy_ref=None,
                    triage_policy_ref=None,
                    deprecation_policy_ref=None,
                    retirement_policy_ref=None,
                ),
                tasks=[],
            )
            output = operator_ui.write_runtime_snapshot_html(snapshot, Path(tmp_dir) / "operator.html")

            self.assertTrue(output.exists())
            self.assertIn("Governed Runtime Operator Surface", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
