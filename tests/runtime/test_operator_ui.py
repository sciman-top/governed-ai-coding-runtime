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

        self.assertIn("Governed Runtime 操作者面板", html)
        self.assertIn("暂无 governed task 记录", html)
        self.assertIn("维护策略", html)
        self.assertIn("Runtime 摘要", html)

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
        self.assertIn("接入仓", html)

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
            self.assertIn("Governed Runtime 操作者面板", output.read_text(encoding="utf-8"))

    def test_operator_ui_renders_english_html_when_requested(self) -> None:
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
            ),
            language="en",
        )

        self.assertIn('lang="en"', html)
        self.assertIn("Governed Runtime Operator Surface", html)
        self.assertIn("No governed tasks recorded", html)
        self.assertIn("Maintenance Policy Surface", html)

    def test_operator_ui_renders_attachment_table(self) -> None:
        maintenance_policy = importlib.import_module("governed_ai_coding_runtime_contracts.maintenance_policy")
        runtime_status = importlib.import_module("governed_ai_coding_runtime_contracts.runtime_status")
        operator_ui = importlib.import_module("governed_ai_coding_runtime_contracts.operator_ui")

        snapshot = runtime_status.RuntimeSnapshot(
            total_tasks=0,
            maintenance=maintenance_policy.MaintenancePolicyStatus(
                stage="completed",
                compatibility_policy_ref="docs/product/runtime-compatibility-and-upgrade-policy.md",
                upgrade_policy_ref="docs/product/runtime-compatibility-and-upgrade-policy.md",
                triage_policy_ref="docs/product/maintenance-deprecation-and-retirement-policy.md",
                deprecation_policy_ref="docs/product/maintenance-deprecation-and-retirement-policy.md",
                retirement_policy_ref="docs/product/maintenance-deprecation-and-retirement-policy.md",
            ),
            tasks=[],
            attachments=[
                runtime_status.RuntimeAttachmentStatus(
                    repo_id="demo-repo",
                    binding_id="binding-demo",
                    binding_state="attached",
                    light_pack_path=".governed-ai/light-pack.json",
                    adapter_preference="native_attach",
                    gate_profile="quick",
                    reason=None,
                    remediation=None,
                    fail_closed=False,
                )
            ],
            runtime_root=".runtime",
            persistence_backend="filesystem",
        )

        html = operator_ui.render_runtime_snapshot_html(snapshot)

        self.assertIn("demo-repo", html)
        self.assertIn(".governed-ai/light-pack.json", html)
        self.assertIn("native_attach", html)

    def test_operator_ui_interactive_mode_renders_actions_and_ref_buttons(self) -> None:
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
                    task_id="task-ui-action",
                    current_state="delivered",
                    goal="show interactive action",
                    rollback_ref="docs/runbooks/control-rollback.md",
                    active_run_id="run-ui-action",
                    workspace_root=".governed-workspaces/demo",
                    approval_ids=["approval-123"],
                    artifact_refs=["docs/README.md"],
                    evidence_refs=[],
                    verification_refs=[],
                )
            ],
        )

        html = operator_ui.render_runtime_snapshot_html(
            snapshot,
            interactive=True,
            target_options=["classroomtoolkit", "skills-manager"],
        )

        self.assertIn("data-action='readiness'", html)
        self.assertIn("id='ui-output'", html)
        self.assertIn("fetch('/api/run'", html)
        self.assertIn("id='ui-target'", html)
        self.assertIn("<option value='classroomtoolkit'>classroomtoolkit</option>", html)
        self.assertIn("id='ui-dry-run'", html)
        self.assertIn("id='ui-history'", html)
        self.assertIn("localStorage", html)
        self.assertIn("class='ref-button' data-ref='docs/README.md'", html)
        self.assertNotIn("data-ref='approval-123'", html)
        self.assertLess(html.index("id='ui-output'"), html.index("id='ui-language'"))


if __name__ == "__main__":
    unittest.main()
