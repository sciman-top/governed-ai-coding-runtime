import json
import importlib.util
import shutil
import subprocess
import unittest
from unittest import mock
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_serve_operator_ui_module():
    path = ROOT / "scripts" / "serve-operator-ui.py"
    spec = importlib.util.spec_from_file_location("serve_operator_ui", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load serve-operator-ui.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(shutil.which("pwsh"), "pwsh is not available")
class OperatorEntrypointTests(unittest.TestCase):
    def test_operator_entrypoint_help_succeeds(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "scripts" / "operator.ps1"),
                "-Action",
                "Help",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )

        self.assertIn("AI 推荐", completed.stdout)
        self.assertIn("Readiness", completed.stdout)
        self.assertIn("FeedbackReport", completed.stdout)
        self.assertIn("CorePrincipleMaterialize", completed.stdout)
        self.assertIn("ConfirmCorePrincipleProposalWrite", completed.stdout)
        self.assertIn("OperatorUi", completed.stdout)
        self.assertIn("-UiLanguage <zh-CN|en>", completed.stdout)
        self.assertIn("EnableAutoStart", completed.stdout)

    def test_operator_ui_action_generates_html(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "scripts" / "operator.ps1"),
                "-Action",
                "OperatorUi",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )

        payload_start = completed.stdout.find("{")
        self.assertGreaterEqual(payload_start, 0)
        payload = json.loads(completed.stdout[payload_start:])
        output = ROOT / payload["output_path"]

        self.assertEqual(".runtime/artifacts/operator-ui/index.html", payload["output_path"])
        self.assertEqual("zh-CN", payload["language"])
        self.assertTrue(output.exists())
        html = output.read_text(encoding="utf-8")
        self.assertIn("Runtime 摘要", html)
        self.assertIn("Codex 账号与配置", html)
        self.assertIn("Claude Provider 与配置", html)

    def test_operator_ui_action_generates_english_html(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "scripts" / "operator.ps1"),
                "-Action",
                "OperatorUi",
                "-UiLanguage",
                "en",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )

        payload_start = completed.stdout.find("{")
        self.assertGreaterEqual(payload_start, 0)
        payload = json.loads(completed.stdout[payload_start:])
        output = ROOT / payload["output_path"]

        self.assertEqual("en", payload["language"])
        self.assertTrue(output.exists())
        html = output.read_text(encoding="utf-8")
        self.assertIn("Runtime Summary", html)
        self.assertIn("Codex Account and Config", html)
        self.assertIn("Claude Provider and Config", html)

    def test_operator_ui_server_helpers_are_bounded_to_repo_actions_and_files(self) -> None:
        module = _load_serve_operator_ui_module()

        self.assertIn("readiness", module.ALLOWED_ACTIONS)
        self.assertIn("feedback_report", module.ALLOWED_ACTIONS)
        self.assertIn("classroomtoolkit", module.load_target_ids())
        self.assertEqual(2, module.run_operator_action({"action": "unsupported"})["exit_code"])
        self.assertEqual(
            2,
            module.run_operator_action({"action": "daily_all", "target": "not-a-target", "dry_run": True})["exit_code"],
        )
        self.assertIn("Governed AI Coding Runtime", module.read_repo_file("README.md")["content"])
        self.assertIn("escapes repository root", module.read_repo_file("../outside.txt")["error"])
        self.assertIn(module.load_codex_status()["status"], {"ok", "error"})
        self.assertEqual("error", module.run_codex_switch({"name": ""})["status"])
        self.assertIn(module.load_claude_status()["status"], {"ok", "error"})
        self.assertEqual("error", module.run_claude_switch({"name": ""})["status"])
        feedback = module.load_feedback_summary()
        self.assertIn(feedback["status"], {"pass", "attention", "fail"})
        self.assertEqual("docs/product/host-feedback-loop.zh-CN.md", feedback["guide_path"])
        self.assertEqual("docs/product/host-feedback-loop.md", feedback["guide_path_en"])

    def test_operator_ui_status_helpers_cache_short_ttl_results(self) -> None:
        module = _load_serve_operator_ui_module()
        module.invalidate_status_cache()

        with (
            mock.patch.object(module, "codex_status", return_value={"sample": "codex"}) as codex_mock,
            mock.patch.object(module, "claude_status", return_value={"sample": "claude"}) as claude_mock,
        ):
            first_codex = module.load_codex_status()
            second_codex = module.load_codex_status()
            first_claude = module.load_claude_status()
            second_claude = module.load_claude_status()

        self.assertEqual("ok", first_codex["status"])
        self.assertEqual("ok", first_claude["status"])
        self.assertEqual("codex", first_codex["cache_kind"])
        self.assertEqual("claude", first_claude["cache_kind"])
        self.assertEqual(1, codex_mock.call_count)
        self.assertEqual(1, claude_mock.call_count)
        self.assertEqual(first_codex["cached_at"], second_codex["cached_at"])
        self.assertEqual(first_claude["cached_at"], second_claude["cached_at"])

    def test_operator_ui_server_dry_run_supports_single_target(self) -> None:
        module = _load_serve_operator_ui_module()

        result = module.run_operator_action(
            {
                "action": "daily_all",
                "target": "classroomtoolkit",
                "dry_run": True,
                "language": "zh-CN",
                "mode": "quick",
            }
        )

        self.assertEqual(0, result["exit_code"])
        self.assertIn("-Target", result["command"])
        self.assertIn("classroomtoolkit", result["command"])
        self.assertIn("-DryRun", result["command"])
        self.assertIn("DRY-RUN daily-all-targets", result["output"])

    def test_operator_feedback_report_action_writes_summary(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "scripts" / "operator.ps1"),
                "-Action",
                "FeedbackReport",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("host-feedback-summary", completed.stdout)
        self.assertIn(".runtime/artifacts/host-feedback-summary/latest.md", completed.stdout)

    def test_operator_ui_service_status_succeeds(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "scripts" / "operator-ui-service.ps1"),
                "-Action",
                "Status",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )

        payload = json.loads(completed.stdout)
        self.assertIn(payload["status"], {"running", "stopped"})
        self.assertIn("operator-ui.pid", payload["pid_path"])
        self.assertIn("operator-ui.log", payload["log_path"])

    def test_operator_ui_service_autostart_status_succeeds(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "scripts" / "operator-ui-service.ps1"),
                "-Action",
                "AutoStartStatus",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )

        payload = json.loads(completed.stdout)
        self.assertEqual("AutoStartStatus", payload["action"])
        self.assertIn("GovernedRuntimeOperatorUi-", payload["task_name"])
        self.assertIn("enabled", payload["autostart"])


if __name__ == "__main__":
    unittest.main()
