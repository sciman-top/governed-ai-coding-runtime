import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path
from unittest import mock
import importlib.util


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
    def test_operator_ui_backend_subprocesses_are_windowless_on_windows(self) -> None:
        module = _load_serve_operator_ui_module()

        with (
            mock.patch.object(module.sys, "platform", "win32"),
            mock.patch.object(module.subprocess, "CREATE_NO_WINDOW", 0x08000000, create=True),
        ):
            self.assertEqual({"creationflags": 0x08000000}, module._windows_no_window_kwargs())

    def test_root_run_entrypoint_help_succeeds(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "run.ps1"),
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )

        self.assertIn("AI 推荐", completed.stdout)
        self.assertIn(".\\run.ps1 fast", completed.stdout)
        self.assertIn(".\\run.ps1 readiness -OpenUi", completed.stdout)
        self.assertIn(".\\run.ps1 rules-check", completed.stdout)
        self.assertIn(".\\run.ps1 feedback", completed.stdout)
        self.assertIn(".\\run.ps1 self-evolution", completed.stdout)
        self.assertIn(".\\run.ps1 self-evolution-promotion", completed.stdout)
        self.assertNotIn("ApplyAllFeatures", completed.stdout)
        self.assertNotIn("DailyAll", completed.stdout)

    def test_root_run_entrypoint_fast_feedback_alias(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "run.ps1"),
                "fast",
                "-DryRun",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )

        self.assertIn("DRY-RUN build", completed.stdout)
        self.assertIn("DRY-RUN quick-feedback", completed.stdout)
        self.assertIn("-Check RuntimeQuick", completed.stdout)

    def test_root_run_entrypoint_retired_aliases_fail_closed(self) -> None:
        for action in ("daily", "apply-all", "cleanup-targets", "uninstall-governance", "targets"):
            with self.subTest(action=action):
                completed = subprocess.run(
                    [
                        "pwsh",
                        "-NoProfile",
                        "-ExecutionPolicy",
                        "Bypass",
                        "-File",
                        str(ROOT / "run.ps1"),
                        action,
                        "-DryRun",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    cwd=ROOT,
                )

                self.assertNotEqual(0, completed.returncode)
                self.assertIn("Retired run action", completed.stderr)

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

        self.assertIn("FastFeedback", completed.stdout)
        self.assertIn("Readiness", completed.stdout)
        self.assertIn("RulesDryRun", completed.stdout)
        self.assertIn("RulesApply", completed.stdout)
        self.assertIn("FeedbackReport", completed.stdout)
        self.assertIn("SelfEvolutionRecommend", completed.stdout)
        self.assertIn("SelfEvolutionPromotionPlan", completed.stdout)
        self.assertIn("CodexGuardAbsenceCheck", completed.stdout)
        self.assertNotIn("ApplyAllFeatures", completed.stdout)
        self.assertNotIn("DailyAll", completed.stdout)
        self.assertNotIn("CleanupTargets", completed.stdout)
        self.assertNotIn("UninstallGovernance", completed.stdout)

    def test_operator_retired_actions_fail_closed(self) -> None:
        for action in ("GovernanceBaselineAll", "DailyAll", "ApplyAllFeatures", "CleanupTargets", "UninstallGovernance"):
            with self.subTest(action=action):
                completed = subprocess.run(
                    [
                        "pwsh",
                        "-NoProfile",
                        "-ExecutionPolicy",
                        "Bypass",
                        "-File",
                        str(ROOT / "scripts" / "operator.ps1"),
                        "-Action",
                        action,
                        "-DryRun",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    cwd=ROOT,
                )

                self.assertNotEqual(0, completed.returncode)
                self.assertIn("Retired operator action", completed.stderr)

    def test_operator_guard_absence_check_dry_run_succeeds(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "scripts" / "operator.ps1"),
                "-Action",
                "CodexGuardAbsenceCheck",
                "-DryRun",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )

        self.assertIn("DRY-RUN codex-guard-absence-check", completed.stdout)
        self.assertIn("scripts/Test-CodexGuardAbsence.ps1", completed.stdout)

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
        self.assertTrue(output.exists())
        html = output.read_text(encoding="utf-8")
        self.assertIn("Runtime 摘要", html)
        self.assertIn("下一步选择", html)
        self.assertIn("id='next-work-action'", html)
        self.assertNotIn("id='ui-target'", html)
        self.assertNotIn("id='ui-target-all'", html)
        self.assertNotIn("id='ui-apply-removal'", html)

    def test_operator_ui_server_run_action_is_repo_local(self) -> None:
        module = _load_serve_operator_ui_module()

        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="DRY-RUN quick-feedback",
            stderr="",
        )
        with mock.patch.object(module.subprocess, "run", return_value=completed) as run_mock:
            result = module.run_operator_action(
                {
                    "action": "fast_feedback",
                    "dry_run": True,
                    "language": "zh-CN",
                    "mode": "quick",
                }
            )

        self.assertEqual(0, result["exit_code"])
        self.assertIn("run.ps1", " ".join(result["command"]))
        self.assertIn("-DryRun", result["command"])
        self.assertNotIn("-Target", result["command"])
        self.assertNotIn("apply_managed_asset_removal", result)
        run_mock.assert_called_once()

    def test_next_work_summary_blocks_only_materialization_actions(self) -> None:
        module = _load_serve_operator_ui_module()

        fake_selector = mock.Mock()
        fake_selector.inspect_next_work_selection.return_value = {
            "status": "pass",
            "next_action": "repair_gate_first",
            "why": "gate failure",
        }

        with mock.patch.object(module, "_load_next_work_module", return_value=fake_selector):
            payload = module._build_next_work_summary()

        self.assertEqual("repair_gate_first", payload["safe_next_action"])
        self.assertEqual("action_required", payload["ui_status"])
        self.assertEqual(["evolution_materialize"], payload["blocked_actions"])

    def test_operator_preflight_blocks_materialization_only(self) -> None:
        env = dict(os.environ)
        env["GOVERNED_RUNTIME_OPERATOR_PREFLIGHT_JSON"] = json.dumps(
            {
                "next_action": "repair_gate_first",
                "why": "Repo gates are not healthy.",
                "gate_state": "fail",
                "source_state": "fresh",
                "evidence_state": "fresh",
            }
        )

        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "scripts" / "operator.ps1"),
                "-Action",
                "EvolutionMaterialize",
                "-DryRun",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
            env=env,
        )

        self.assertNotEqual(0, completed.returncode)
        self.assertIn("operator-preflight blocked: EvolutionMaterialize", completed.stderr)

    def test_operator_preflight_does_not_block_readiness(self) -> None:
        env = dict(os.environ)
        env["GOVERNED_RUNTIME_OPERATOR_PREFLIGHT_JSON"] = json.dumps(
            {
                "next_action": "repair_gate_first",
                "why": "Repo gates are not healthy.",
                "gate_state": "fail",
                "source_state": "fresh",
                "evidence_state": "fresh",
            }
        )

        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "scripts" / "operator.ps1"),
                "-Action",
                "Readiness",
                "-DryRun",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
            env=env,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn("operator-preflight: action=Readiness next_action=repair_gate_first", completed.stdout)

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


if __name__ == "__main__":
    unittest.main()
