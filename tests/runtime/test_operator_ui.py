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
    def test_operator_ui_translation_keys_stay_in_sync(self) -> None:
        operator_ui_text = importlib.import_module("governed_ai_coding_runtime_contracts.operator_ui_text")

        zh_keys = set(operator_ui_text.TRANSLATIONS["zh-CN"])
        en_keys = set(operator_ui_text.TRANSLATIONS["en"])

        self.assertEqual(zh_keys, en_keys)

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

        self.assertIn("治理运行时操作台", html)
        self.assertIn("暂无运行记录", html)
        self.assertIn("维护与升级", html)
        self.assertIn("Runtime 摘要", html)
        self.assertNotIn("已接入仓库", html)
        self.assertIn("共享上下文连续性", html)
        self.assertIn("功能反馈闭环", html)

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
        self.assertIn("已完成", html)
        self.assertNotIn("light-pack.json", html)

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
            self.assertIn("治理运行时操作台", output.read_text(encoding="utf-8"))

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
        self.assertIn("Governed Runtime Operator Console", html)
        self.assertIn("No runtime activity has been recorded", html)
        self.assertIn("Maintenance and Upgrade", html)
        self.assertIn("Shared Context Continuity", html)
        self.assertIn("Host Feedback Loop", html)

    def test_operator_ui_interactive_mode_renders_repo_local_actions(self) -> None:
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

        html = operator_ui.render_runtime_snapshot_html(snapshot, interactive=True)

        self.assertIn("data-action='readiness'", html)
        self.assertIn("data-action='fast_feedback'", html)
        self.assertIn("data-action='feedback_report'", html)
        self.assertIn("data-action='codex_guard_absence_check'", html)
        self.assertIn("data-action='rules_dry_run'", html)
        self.assertIn("data-action='rules_apply'", html)
        self.assertIn("data-action='self_evolution_recommend'", html)
        self.assertIn("data-action='self_evolution_promotion_plan'", html)
        self.assertIn("data-action='evolution_review'", html)
        self.assertIn("data-action='experience_review'", html)
        self.assertIn("data-action='evolution_materialize'", html)
        self.assertIn("data-action='core_principle_materialize'", html)
        self.assertNotIn("data-action='cleanup_targets'", html)
        self.assertNotIn("data-action='uninstall_governance'", html)
        self.assertNotIn("data-action='daily_all'", html)
        self.assertNotIn("data-action='apply_all_features'", html)
        self.assertNotIn("id='ui-target'", html)
        self.assertNotIn("id='ui-target-all'", html)
        self.assertNotIn("id='ui-apply-removal'", html)
        self.assertIn("id='ui-output'", html)
        self.assertIn("/api/run", html)
        self.assertIn("id='ui-dry-run'", html)
        self.assertIn("id='ui-history'", html)
        self.assertIn("class='feedback-grid'", html)
        self.assertIn("data-view-tab='feedback'", html)
        self.assertIn("data-view-panel=\"feedback\"", html)
        self.assertIn("操作台总览", html)
        self.assertIn("本仓验证", html)
        self.assertIn("规则与演进", html)
        self.assertIn("自演化晋升控制器", html)
        self.assertIn("id='self-evolution-promotion-status'", html)
        self.assertIn("data-self-evolution-promotion-refresh='1'", html)
        self.assertIn("/api/self-evolution/promotion", html)
        self.assertIn("<summary>规则与演进</summary>", html)
        self.assertIn("<summary>高级参数</summary>", html)
        self.assertIn(".\\run.ps1 fast", html)
        self.assertIn(".\\run.ps1 readiness -OpenUi", html)
        self.assertIn(".\\run.ps1 rules-check", html)
        self.assertIn(".\\run.ps1 feedback", html)
        self.assertIn("shortcut-item recommended", html)
        self.assertIn("function renderNextWorkSummary(payload)", html)
        self.assertIn("function refreshNextWorkSummary(forceRefresh)", html)
        self.assertIn("function syncNextWorkActionGuards()", html)
        self.assertIn("function activateView(selected)", html)
        self.assertIn("const nextWorkAction = document.getElementById('next-work-action');", html)
        self.assertIn("const nextWorkCacheKey = 'governed-runtime-operator-next-work';", html)
        self.assertIn("/api/feedback/summary", html)
        self.assertIn("/api/self-evolution/recommendations", html)
        self.assertIn("/api/continuity/search", html)
        self.assertIn("localStorage", html)
        self.assertIn("class='ref-button' data-ref='docs/README.md'", html)
        self.assertLess(html.index("id='ui-language'"), html.index("id='ui-output'"))


if __name__ == "__main__":
    unittest.main()
