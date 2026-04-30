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
        self.assertIn("暂无运行记录", html)
        self.assertIn("维护与升级", html)
        self.assertIn("Runtime 摘要", html)
        self.assertIn("Claude Provider 与配置", html)
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
        self.assertIn("已接入仓库", html)
        self.assertIn("已完成", html)

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
        self.assertIn("No runtime activity has been recorded", html)
        self.assertIn("Maintenance and Upgrade", html)
        self.assertIn("Claude Provider and Config", html)
        self.assertIn("Host Feedback Loop", html)

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
        self.assertIn("原生接入", html)

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
        self.assertIn("data-action='feedback_report'", html)
        self.assertIn("id='ui-output'", html)
        self.assertIn("fetch('/api/run'", html)
        self.assertIn("id='ui-target'", html)
        self.assertIn("<option value='classroomtoolkit'>classroomtoolkit</option>", html)
        self.assertIn("id='ui-dry-run'", html)
        self.assertIn("id='ui-history'", html)
        self.assertIn("class='feedback-grid'", html)
        self.assertIn("class=\"details-grid\"", html)
        self.assertIn("data-view-tab='feedback'", html)
        self.assertIn("data-view-panel=\"feedback\"", html)
        self.assertIn("id='feedback-summary'", html)
        self.assertIn("id='feedback-cache-state'", html)
        self.assertIn("id='feedback-dimensions'", html)
        self.assertIn("id='feedback-latest-runs'", html)
        self.assertIn("id='feedback-preview'", html)
        self.assertIn("fetch('/api/feedback/summary'", html)
        self.assertIn("governed-runtime-operator-feedback-summary", html)
        self.assertIn("data-feedback-refresh='1'", html)
        self.assertIn("看这 3 项就够了", html)
        self.assertIn("function summarizeFeedbackAdapter(value)", html)
        self.assertIn("function summarizeFeedbackFlow(value)", html)
        self.assertIn("function summarizeFeedbackClosure(value)", html)
        self.assertIn("function summarizeFeedbackWrite(value)", html)
        self.assertIn("原生直连", html)
        self.assertIn("已具备闭环", html)
        self.assertIn("未记录写入执行", html)
        self.assertIn("function renderFeedbackSummary(payload)", html)
        self.assertIn("function refreshFeedbackSummary()", html)
        self.assertIn("function formatFeedbackStatusLabel(value)", html)
        self.assertIn("function createRefButton(path, label, previewTarget = 'runtime')", html)
        self.assertIn("function setFeedbackPreview(text)", html)
        self.assertIn("data-view-tab='claude'", html)
        self.assertIn("fetch('/api/claude/status'", html)
        self.assertIn("fetch('/api/claude/optimize'", html)
        self.assertIn("fetch('/api/claude/file?kind='", html)
        self.assertIn("function codexAccountLabel(account)", html)
        self.assertIn("function configCheckLabel(key)", html)
        self.assertIn("function formatConfigHealth(config)", html)
        self.assertIn("function summarizeClaudeContext(provider)", html)
        self.assertIn("function currentUiLanguage()", html)
        self.assertIn("data-codex-refresh-online='1'", html)
        self.assertIn("fetch('/api/codex/refresh'", html)
        self.assertIn("governed-runtime-operator-codex-status", html)
        self.assertIn("governed-runtime-operator-claude-status", html)
        self.assertIn("function readPanelCache(key)", html)
        self.assertIn("function writePanelCache(key, payload)", html)
        self.assertIn("function formatCachedAtLabel(value)", html)
        self.assertIn("function setPanelCacheState(kind, state, cachedAt)", html)
        self.assertIn("function hydratePanelCache(kind, key)", html)
        self.assertIn("window.setTimeout(() => {", html)
        self.assertIn("account.account_label", html)
        self.assertIn("function formatUsageWindow(item)", html)
        self.assertIn("function formatTokenExpirySummary(account)", html)
        self.assertIn("function formatSubscriptionExpirySummary(account)", html)
        self.assertIn("white-space: pre-line", html)
        self.assertIn("return windows.map(formatUsageWindow).join('\\n');", html)
        self.assertIn("return parts.join('\\n');", html)
        self.assertIn("subscription_active_until", html)
        self.assertIn("remaining_percent", html)
        self.assertIn("data-codex-switch-name", html)
        self.assertIn("data-claude-switch-name", html)
        self.assertIn("data-claude-optimize-preview='1'", html)
        self.assertIn("data-claude-optimize-apply='1'", html)
        self.assertIn("data-claude-file='settings'", html)
        self.assertIn("data-claude-file='profiles'", html)
        self.assertIn("className = account.active ? 'codex-account-switch is-current' : 'codex-account-switch'", html)
        self.assertIn("只开放本机 Claude 配置相关文件预览", html)
        self.assertIn("class='claude-console-grid'", html)
        self.assertIn("className = provider.credential_present ? 'provider-status-pill ready' : 'provider-status-pill missing'", html)
        self.assertNotIn("id='codex-summary'", html)
        self.assertNotIn("id='claude-summary'", html)
        self.assertNotIn("id='codex-recommended-note'", html)
        self.assertNotIn("id='codex-login'", html)
        self.assertNotIn("id='codex-cache-state'", html)
        self.assertNotIn("id='codex-token-note'", html)
        self.assertNotIn("id='claude-command'", html)
        self.assertNotIn("id='claude-cache-state'", html)
        self.assertNotIn("function renderCodexSummary(payload)", html)
        self.assertNotIn("function renderClaudeSummary(payload)", html)
        self.assertNotIn("function formatCodexAuthPointer(auth)", html)
        self.assertIn("hydratePanelCache('codex', codexCacheKey);", html)
        self.assertIn("hydratePanelCache('claude', claudeCacheKey);", html)
        self.assertIn("hydratePanelCache('feedback', feedbackCacheKey);", html)
        self.assertNotIn("当前使用 ChatGPT 账号", html)
        self.assertIn("localStorage", html)
        self.assertIn("class='ref-button' data-ref='docs/README.md'", html)
        self.assertNotIn("data-ref='approval-123'", html)
        self.assertNotIn("id='codex-account-select'", html)
        self.assertNotIn("id='claude-provider-select'", html)
        self.assertNotIn("data-claude-switch='1'", html)
        self.assertLess(html.index("id='ui-language'"), html.index("id='ui-output'"))
        self.assertLess(html.index("id='ui-output'"), html.index("<section class='section'>\n<h2>维护与升级</h2>"))


if __name__ == "__main__":
    unittest.main()
