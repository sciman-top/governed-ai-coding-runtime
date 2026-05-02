import json
import importlib.util
import os
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
        self.assertIn(".\\run.ps1 readiness -OpenUi", completed.stdout)
        self.assertIn("rules-check", completed.stdout)
        self.assertIn("operator-help", completed.stdout)
        self.assertIn("cleanup-targets", completed.stdout)
        self.assertIn("uninstall-governance", completed.stdout)

    def test_root_run_entrypoint_forwards_aliases(self) -> None:
        env = dict(os.environ)
        env["GOVERNED_RUNTIME_OPERATOR_PREFLIGHT_JSON"] = json.dumps(
            {
                "next_action": "default_defer",
                "why": "No blocking action.",
                "gate_state": "pass",
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
                str(ROOT / "run.ps1"),
                "readiness",
                "-DryRun",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
            env=env,
        )

        self.assertIn("operator-preflight: action=Readiness", completed.stdout)
        self.assertIn("DRY-RUN build", completed.stdout)

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
        self.assertIn("CleanupTargets", completed.stdout)
        self.assertIn("UninstallGovernance", completed.stdout)
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
        self.assertIn("下一步选择", html)
        self.assertIn("id='next-work-action'", html)
        self.assertIn("data-next-work-refresh='1'", html)
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
        self.assertIn("Next Work Selector", html)
        self.assertIn("id='next-work-state'", html)
        self.assertIn("Codex Account and Config", html)
        self.assertIn("Claude Provider and Config", html)

    def test_operator_ui_server_helpers_are_bounded_to_repo_actions_and_files(self) -> None:
        module = _load_serve_operator_ui_module()
        module.invalidate_status_cache()

        with (
            mock.patch.object(module, "codex_status", return_value={"sample": "codex"}),
            mock.patch.object(module, "claude_status", return_value={"sample": "claude"}),
            mock.patch.object(
                module,
                "_build_feedback_summary",
                return_value={
                    "overall_status": "pass",
                    "guide_path": "docs/product/host-feedback-loop.zh-CN.md",
                    "guide_path_en": "docs/product/host-feedback-loop.md",
                },
            ),
            mock.patch.object(
                module,
                "_build_next_work_summary",
                return_value={
                    "policy_status": "pass",
                    "ui_status": "healthy",
                    "next_action": "refresh_evidence_first",
                    "blocked_actions": [],
                    "cached_at": "test",
                },
            ),
        ):
            self.assertIn("readiness", module.ALLOWED_ACTIONS)
            self.assertIn("feedback_report", module.ALLOWED_ACTIONS)
            self.assertIn("cleanup_targets", module.ALLOWED_ACTIONS)
            self.assertIn("uninstall_governance", module.ALLOWED_ACTIONS)
            self.assertIn("evolution_review", module.ALLOWED_ACTIONS)
            self.assertIn("evolution_materialize", module.ALLOWED_ACTIONS)
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
            self.assertEqual("error", module.run_codex_sync_active({"name": "missing-profile"})["status"])
            self.assertIn(module.load_claude_status()["status"], {"ok", "error"})
            self.assertEqual("error", module.run_claude_switch({"name": ""})["status"])
            feedback = module.load_feedback_summary()
            self.assertIn(feedback["status"], {"pass", "attention", "fail"})
            self.assertEqual("docs/product/host-feedback-loop.zh-CN.md", feedback["guide_path"])
            self.assertEqual("docs/product/host-feedback-loop.md", feedback["guide_path_en"])
            next_work = module.load_next_work_summary()
            self.assertIn(next_work["status"], {"pass", "error"})
            if next_work["status"] != "error":
                self.assertIn(next_work["ui_status"], {"healthy", "attention", "action_required"})
                self.assertIn("next_action", next_work)
                self.assertIn("blocked_actions", next_work)
                self.assertIn("cached_at", next_work)
            process_status = module.operator_ui_process_status()

        self.assertEqual("ok", process_status["status"])
        self.assertIn("stale", process_status)
        self.assertIn("process_started_at", process_status)
        self.assertIn("source_last_write_utc", process_status)
        self.assertIn("restart_request", process_status)
        self.assertIn("scripts/serve-operator-ui.py", process_status["source_files"])

    def test_operator_ui_server_refuses_stale_content_and_disables_cache(self) -> None:
        script = (ROOT / "scripts" / "serve-operator-ui.py").read_text(encoding="utf-8")

        self.assertIn("SERVER_STARTED_AT", script)
        self.assertIn("UI_SOURCE_FILES", script)
        self.assertIn("is_operator_ui_process_stale", script)
        self.assertIn("operator_ui_process_status", script)
        self.assertIn("/api/ui-process", script)
        self.assertIn("render_stale_service_html", script)
        self.assertIn("maybe_request_operator_ui_restart", script)
        self.assertIn("meta http-equiv=\"refresh\"", script)
        self.assertIn("restart_requested_at", script)
        self.assertIn("cache-control", script)
        self.assertIn("no-store, max-age=0", script)
        self.assertIn("x-governed-runtime-ui-stale", script)
        self.assertIn("refresh_if_stale", script)

    def test_next_work_summary_keeps_daily_available_for_refresh_evidence_first(self) -> None:
        module = _load_serve_operator_ui_module()

        fake_selector = mock.Mock()
        fake_selector.inspect_next_work_selection.return_value = {
            "status": "pass",
            "next_action": "refresh_evidence_first",
            "why": "freshness",
        }

        with mock.patch.object(module, "_load_next_work_module", return_value=fake_selector):
            payload = module._build_next_work_summary()

        self.assertEqual("refresh_evidence_first", payload["safe_next_action"])
        self.assertEqual("action_required", payload["ui_status"])
        self.assertNotIn("daily_all", payload["blocked_actions"])
        self.assertIn("apply_all_features", payload["blocked_actions"])
        self.assertIn("evolution_materialize", payload["blocked_actions"])

    def test_operator_ui_next_work_panel_does_not_block_initial_html(self) -> None:
        module = _load_serve_operator_ui_module()

        with mock.patch.object(module, "load_next_work_summary", side_effect=AssertionError("selector should be async")):
            html = module.render_next_work_panel(language="zh-CN")

        self.assertIn("下一步选择", html)
        self.assertIn("加载中", html)
        self.assertIn("data-next-work-refresh='1'", html)

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

    def test_load_codex_status_can_refresh_if_stale(self) -> None:
        module = _load_serve_operator_ui_module()
        module.invalidate_status_cache("codex")

        with mock.patch.object(module, "codex_status", return_value={"sample": "codex"}) as codex_mock:
            payload = module.load_codex_status(refresh_if_stale=True)

        self.assertEqual("ok", payload["status"])
        codex_mock.assert_called_once_with(refresh_online=False, refresh_if_stale=True)

    def test_operator_ui_restart_request_is_throttled(self) -> None:
        module = _load_serve_operator_ui_module()

        with (
            mock.patch.object(module, "load_operator_ui_restart_state", return_value={"requested_epoch": 100.0, "requested": True}),
            mock.patch.object(module.time, "time", return_value=110.0),
            mock.patch.object(module.subprocess, "Popen") as popen_mock,
        ):
            payload = module.maybe_request_operator_ui_restart(language="zh-CN", host="127.0.0.1", port=8770)

        self.assertTrue(payload["requested"])
        popen_mock.assert_not_called()

    def test_operator_ui_server_dry_run_supports_single_target(self) -> None:
        module = _load_serve_operator_ui_module()

        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="DRY-RUN daily-all-targets",
            stderr="",
        )
        with mock.patch.object(module.subprocess, "run", return_value=completed) as run_mock:
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
        self.assertIn("run.ps1", " ".join(result["command"]))
        self.assertIn("-Target", result["command"])
        self.assertIn("classroomtoolkit", result["command"])
        self.assertIn("-DryRun", result["command"])
        self.assertIn("DRY-RUN daily-all-targets", result["output"])
        run_mock.assert_called_once()

    def test_operator_ui_server_batches_selected_targets_for_uninstall(self) -> None:
        module = _load_serve_operator_ui_module()

        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout='{"status":"pass"}',
            stderr="",
        )
        with mock.patch.object(module.subprocess, "run", return_value=completed) as run_mock:
            result = module.run_operator_action(
                {
                    "action": "uninstall_governance",
                    "targets": ["classroomtoolkit", "skills-manager"],
                    "apply_managed_asset_removal": True,
                    "dry_run": False,
                    "language": "zh-CN",
                    "mode": "quick",
                }
            )

        self.assertEqual(0, result["exit_code"])
        self.assertEqual(["classroomtoolkit", "skills-manager"], result["targets"])
        self.assertTrue(result["apply_managed_asset_removal"])
        self.assertEqual(2, run_mock.call_count)
        first_command = run_mock.call_args_list[0].args[0]
        second_command = run_mock.call_args_list[1].args[0]
        self.assertIn("uninstall-governance", first_command)
        self.assertIn("classroomtoolkit", first_command)
        self.assertIn("-ApplyManagedAssetRemoval", first_command)
        self.assertNotIn("-DryRun", first_command)
        self.assertIn("skills-manager", second_command)
        self.assertIn("===== target: classroomtoolkit =====", result["output"])
        self.assertIn("===== target: skills-manager =====", result["output"])

    def test_operator_preflight_blocks_high_impact_actions(self) -> None:
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
                "ApplyAllFeatures",
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
        self.assertIn("operator-preflight blocked: ApplyAllFeatures", completed.stderr)

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
        self.assertIn("stale", payload)
        self.assertIn("source_last_write_utc", payload)

    def test_operator_ui_service_detects_stale_source_processes(self) -> None:
        script = (ROOT / "scripts" / "operator-ui-service.ps1").read_text(encoding="utf-8")

        self.assertIn("function Test-ServiceProcessStale", script)
        self.assertIn("Get-ServiceSourceLastWriteUtc", script)
        self.assertIn("operator_ui.py", script)
        self.assertIn("serve-operator-ui.py", script)
        self.assertIn("Stop-ServiceProcess", script)
        self.assertIn("source_last_write_utc", script)

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
