import json
import importlib.util
import os
import shutil
import subprocess
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
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
        self.assertIn(".\\run.ps1 self-evolution", completed.stdout)
        self.assertNotIn("codex-optimize", completed.stdout)
        self.assertNotIn("codex-interop", completed.stdout)
        self.assertNotIn("codex-mode-new", completed.stdout)
        self.assertNotIn("codex-mode-old-api", completed.stdout)
        self.assertNotIn("codex-mode-old-oauth", completed.stdout)
        self.assertNotIn("codex-mode-rollback", completed.stdout)
        self.assertNotIn("codex-api-repair", completed.stdout)
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
        self.assertIn("scripts/verify-repo.ps1", completed.stdout)
        self.assertIn("-Check RuntimeQuick", completed.stdout)

    def test_root_run_entrypoint_codex_api_repair_alias_is_retired(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "run.ps1"),
                "codex-api-repair",
                "-DryRun",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )

        self.assertNotEqual(0, completed.returncode)
        self.assertIn("does not belong to the set", completed.stderr)

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
        self.assertIn("FastFeedback", completed.stdout)
        self.assertIn("Readiness", completed.stdout)
        self.assertNotIn("CodexLocalOptimize", completed.stdout)
        self.assertNotIn("CodexInteropCheck", completed.stdout)
        self.assertNotIn("CodexGatewayEnable", completed.stdout)
        self.assertNotIn("CodexGatewayRollback", completed.stdout)
        self.assertIn("FeedbackReport", completed.stdout)
        self.assertIn("SelfEvolutionRecommend", completed.stdout)
        self.assertIn("CleanupTargets", completed.stdout)
        self.assertIn("UninstallGovernance", completed.stdout)
        self.assertIn("CorePrincipleMaterialize", completed.stdout)
        self.assertIn("ConfirmCorePrincipleProposalWrite", completed.stdout)
        self.assertIn("OperatorUi", completed.stdout)
        self.assertIn("-UiLanguage <zh-CN|en>", completed.stdout)
        self.assertIn("EnableAutoStart", completed.stdout)
        self.assertIn("默认删除已证明安全的退役托管文件", completed.stdout)
        self.assertIn("-DisableManagedAssetRemoval", completed.stdout)

    def test_operator_apply_all_features_applies_safe_retired_cleanup_by_default(self) -> None:
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
                str(ROOT / "scripts" / "operator.ps1"),
                "-Action",
                "ApplyAllFeatures",
                "-Target",
                "self-runtime",
                "-Mode",
                "quick",
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

        self.assertIn("DRY-RUN rules-apply", completed.stdout)
        self.assertIn("DRY-RUN rules-drift-check", completed.stdout)
        self.assertIn("DRY-RUN apply-all-features", completed.stdout)
        self.assertLess(
            completed.stdout.index("DRY-RUN rules-apply"),
            completed.stdout.index("DRY-RUN apply-all-features"),
        )
        self.assertIn("-ApplyAllFeatures", completed.stdout)
        self.assertIn("-ExportTargetRepoRuns", completed.stdout)
        self.assertIn("-PruneRetiredManagedFiles", completed.stdout)
        self.assertIn("-ApplyManagedAssetRemoval", completed.stdout)

    def test_operator_apply_all_features_can_disable_managed_cleanup_apply(self) -> None:
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
                str(ROOT / "scripts" / "operator.ps1"),
                "-Action",
                "ApplyAllFeatures",
                "-Target",
                "self-runtime",
                "-Mode",
                "quick",
                "-DisableManagedAssetRemoval",
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

        self.assertIn("-PruneRetiredManagedFiles", completed.stdout)
        self.assertIn("-ExportTargetRepoRuns", completed.stdout)
        self.assertIn("-DisableManagedAssetRemoval", completed.stdout)

    def test_operator_codex_local_optimize_action_is_removed(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "scripts" / "operator.ps1"),
                "-Action",
                "CodexLocalOptimize",
                "-DryRun",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )

        self.assertNotEqual(0, completed.returncode)
        self.assertIn("CodexLocalOptimize", completed.stderr)

    def test_operator_codex_interop_check_is_removed(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "scripts" / "operator.ps1"),
                "-Action",
                "CodexInteropCheck",
                "-DryRun",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )

        self.assertNotEqual(0, completed.returncode)
        self.assertIn("CodexInteropCheck", completed.stderr)

    def test_operator_codex_write_repairs_and_gateway_switches_are_retired(self) -> None:
        retired_actions = [
            "CodexApiProjectionRepair",
            "CodexOauthProjectionRepair",
            "CodexLaunchBindingRepair",
            "CodexGatewayEnable",
            "CodexGatewayRollback",
        ]
        for action in retired_actions:
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
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    cwd=ROOT,
                )

                self.assertNotEqual(0, completed.returncode)
                self.assertIn(action, completed.stderr)

    def test_operator_codex_projection_smoke_is_removed(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "scripts" / "operator.ps1"),
                "-Action",
                "CodexProjectionSmoke",
                "-DryRun",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )

        self.assertNotEqual(0, completed.returncode)
        self.assertIn("CodexProjectionSmoke", completed.stderr)

    def test_operator_codex_switch_record_is_removed_but_absence_check_remains(self) -> None:
        removed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(ROOT / "scripts" / "operator.ps1"),
                "-Action",
                "CodexSwitchRecord",
                "-DryRun",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
        )
        self.assertNotEqual(0, removed.returncode)
        self.assertIn("CodexSwitchRecord", removed.stderr)

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

    def test_operator_apply_all_features_is_available_while_waiting_for_host_recovery(self) -> None:
        env = dict(os.environ)
        env["GOVERNED_RUNTIME_OPERATOR_PREFLIGHT_JSON"] = json.dumps(
            {
                "next_action": "wait_for_host_capability_recovery",
                "why": "Host native attach is still degraded.",
                "gate_state": "pass",
                "source_state": "fresh",
                "evidence_state": "stale",
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
                "-Target",
                "self-runtime",
                "-Mode",
                "quick",
                "-DisableManagedAssetRemoval",
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

        self.assertIn(
            "operator-preflight: action=ApplyAllFeatures next_action=wait_for_host_capability_recovery",
            completed.stdout,
        )
        self.assertIn("DRY-RUN apply-all-features", completed.stdout)
        self.assertIn("-ApplyAllFeatures", completed.stdout)
        self.assertIn("-ExportTargetRepoRuns", completed.stdout)
        self.assertIn("-DisableManagedAssetRemoval", completed.stdout)

    def test_operator_daily_all_dry_run_includes_self_evolution_recommendation(self) -> None:
        env = dict(os.environ)
        env["GOVERNED_RUNTIME_OPERATOR_PREFLIGHT_JSON"] = json.dumps(
            {
                "next_action": "wait_for_host_capability_recovery",
                "why": "Host native attach is still degraded.",
                "gate_state": "pass",
                "source_state": "fresh",
                "evidence_state": "stale",
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
                "DailyAll",
                "-Mode",
                "quick",
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

        self.assertIn("operator-preflight: action=DailyAll next_action=wait_for_host_capability_recovery", completed.stdout)
        self.assertIn("DRY-RUN daily-all-targets", completed.stdout)
        self.assertIn("DRY-RUN self-evolution-recommend", completed.stdout)

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
        self.assertNotIn("Codex 账号与配置", html)
        self.assertNotIn("Claude Provider 与配置", html)

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
        self.assertNotIn("Codex Account and Config", html)
        self.assertNotIn("Claude Provider and Config", html)

    def test_operator_ui_server_helpers_are_bounded_to_repo_actions_and_files(self) -> None:
        module = _load_serve_operator_ui_module()
        module.invalidate_status_cache()

        with (
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
            self.assertIn("fast_feedback", module.ALLOWED_ACTIONS)
            self.assertIn("feedback_report", module.ALLOWED_ACTIONS)
            self.assertIn("cleanup_targets", module.ALLOWED_ACTIONS)
            self.assertIn("uninstall_governance", module.ALLOWED_ACTIONS)
            self.assertNotIn("codex_local_optimize", module.ALLOWED_ACTIONS)
            self.assertNotIn("codex_interop_check", module.ALLOWED_ACTIONS)
            self.assertNotIn("codex_api_projection_repair", module.ALLOWED_ACTIONS)
            self.assertNotIn("codex_projection_smoke", module.ALLOWED_ACTIONS)
            self.assertNotIn("codex_oauth_projection_repair", module.ALLOWED_ACTIONS)
            self.assertNotIn("codex_launch_binding_repair", module.ALLOWED_ACTIONS)
            self.assertNotIn("codex_switch_record", module.ALLOWED_ACTIONS)
            self.assertNotIn("codex_guard_absence_check", module.ALLOWED_ACTIONS)
            self.assertNotIn("codex_guard_status", module.ALLOWED_ACTIONS)
            self.assertNotIn("codex_interop_repair", module.ALLOWED_ACTIONS)
            self.assertNotIn("codex_guard_start", module.ALLOWED_ACTIONS)
            self.assertIn("evolution_review", module.ALLOWED_ACTIONS)
            self.assertIn("evolution_materialize", module.ALLOWED_ACTIONS)
            self.assertIn("core_principle_materialize", module.ALLOWED_ACTIONS)
            self.assertIn("classroomtoolkit", module.load_target_ids())
            self.assertEqual(2, module.run_operator_action({"action": "unsupported"})["exit_code"])
            self.assertEqual(
                2,
                module.run_operator_action({"action": "daily_all", "target": "not-a-target", "dry_run": True})["exit_code"],
            )
            self.assertIn("Governed AI Coding Runtime", module.read_repo_file("README.md")["content"])
            self.assertIn("escapes repository root", module.read_repo_file("../outside.txt")["error"])
            self.assertFalse(hasattr(module, "load_codex_status"))
            self.assertFalse(hasattr(module, "run_codex_switch"))
            self.assertFalse(hasattr(module, "run_codex_sync_active"))
            self.assertFalse(hasattr(module, "run_codex_save_active"))
            self.assertFalse(hasattr(module, "run_codex_save_api"))
            self.assertFalse(hasattr(module, "run_codex_import_payload"))
            self.assertFalse(hasattr(module, "run_codex_delete"))
            self.assertFalse(hasattr(module, "load_claude_status"))
            self.assertFalse(hasattr(module, "run_claude_switch"))
            self.assertFalse(hasattr(module, "run_claude_delete"))
            feedback = module.load_feedback_summary()
            self.assertIn(feedback["status"], {"pass", "attention", "fail"})
            self.assertEqual("docs/product/host-feedback-loop.zh-CN.md", feedback["guide_path"])
            self.assertEqual("docs/product/host-feedback-loop.md", feedback["guide_path_en"])
            self.assertIn("self_evolution_recommend", module.ALLOWED_ACTIONS)
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
        self.assertIn(
            "packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui_script.py",
            process_status["source_files"],
        )
        self.assertIn(
            "packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui_style.py",
            process_status["source_files"],
        )
        self.assertIn(
            "packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui_text.py",
            process_status["source_files"],
        )

    def test_operator_ui_codex_panel_and_probe_are_retired(self) -> None:
        module = _load_serve_operator_ui_module()
        module.invalidate_status_cache()

        self.assertFalse(hasattr(module, "probe_auth_profiles"))
        self.assertFalse(hasattr(module, "run_codex_probe"))
        self.assertFalse(hasattr(module, "run_codex_save_api"))
        self.assertFalse(hasattr(module, "run_codex_import_cockpit"))
        self.assertFalse(hasattr(module, "run_codex_import_payload"))

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
        self.assertNotIn("refresh_if_stale", script)

    def test_operator_ui_stale_handler_returns_conflict_without_dropping_connection(self) -> None:
        module = _load_serve_operator_ui_module()
        handler = module._build_handler(default_language="zh-CN", host="127.0.0.1", port=0)
        server = module.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        port = server.server_address[1]
        thread = threading.Thread(target=server.handle_request, daemon=True)

        try:
            with (
                mock.patch.object(module, "is_operator_ui_process_stale", return_value=True),
                mock.patch.object(
                    module,
                    "maybe_request_operator_ui_restart",
                    return_value={"requested": False, "requested_at": "2026-05-04T00:00:00Z"},
                ) as restart_mock,
            ):
                thread.start()
                with self.assertRaises(urllib.error.HTTPError) as raised:
                    urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=10)

            self.assertEqual(409, raised.exception.code)
            body = raised.exception.read().decode("utf-8")
            self.assertIn("Operator UI 服务已过期", body)
            restart_mock.assert_called_once_with(language="zh-CN", host="127.0.0.1", port=0)
        finally:
            server.server_close()
            thread.join(timeout=5)

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

    def test_next_work_summary_keeps_feature_apply_available_while_waiting_for_host_recovery(self) -> None:
        module = _load_serve_operator_ui_module()

        fake_selector = mock.Mock()
        fake_selector.inspect_next_work_selection.return_value = {
            "status": "pass",
            "next_action": "wait_for_host_capability_recovery",
            "why": "bounded host defer",
        }

        with mock.patch.object(module, "_load_next_work_module", return_value=fake_selector):
            payload = module._build_next_work_summary()

        self.assertEqual("wait_for_host_capability_recovery", payload["safe_next_action"])
        self.assertEqual("attention", payload["ui_status"])
        self.assertNotIn("daily_all", payload["blocked_actions"])
        self.assertNotIn("apply_all_features", payload["blocked_actions"])
        self.assertIn("evolution_materialize", payload["blocked_actions"])

    def test_operator_ui_next_work_panel_does_not_block_initial_html(self) -> None:
        module = _load_serve_operator_ui_module()

        with mock.patch.object(module, "load_next_work_summary", side_effect=AssertionError("selector should be async")):
            html = module.render_next_work_panel(language="zh-CN")

        self.assertIn("下一步选择", html)
        self.assertIn("未自动刷新", html)
        self.assertIn("等待手动刷新", html)
        self.assertIn("data-next-work-refresh='1'", html)

    def test_operator_ui_status_helpers_cache_short_ttl_results(self) -> None:
        module = _load_serve_operator_ui_module()
        module.invalidate_status_cache()

        with mock.patch.object(module, "_build_feedback_summary", return_value={"overall_status": "pass"}) as feedback_mock:
            first_feedback = module.load_feedback_summary()
            second_feedback = module.load_feedback_summary()

        self.assertEqual("pass", first_feedback["status"])
        self.assertEqual("feedback", first_feedback["cache_kind"])
        self.assertEqual(1, feedback_mock.call_count)
        self.assertEqual(first_feedback["cached_at"], second_feedback["cached_at"])

    def test_operator_ui_self_evolution_recommendations_read_latest_artifact(self) -> None:
        module = _load_serve_operator_ui_module()

        with tempfile.TemporaryDirectory(dir=ROOT) as temp_dir:
            artifact = Path(temp_dir) / "20260530-self-evolution-recommendations.json"
            artifact.write_text(
                json.dumps(
                    {
                        "artifact_type": "self_evolution_recommendation_report",
                        "status": "pass",
                        "as_of": "2026-05-30",
                        "recommended_next_action": "report_only_until_wait_for_host_capability_recovery",
                        "materialization_blocked": True,
                        "selector_next_action": "wait_for_host_capability_recovery",
                        "selector_why": "bounded host defer",
                        "readiness_overall_state": "complete",
                        "ready_for_unattended_self_update": False,
                        "variant_review_candidate_count": 5,
                        "retire_proposal_count": 0,
                        "trigger_model": {
                            "proactive_operator_triggers": ["FeedbackReport", "DailyAll"],
                            "automatic_effective_change": False,
                        },
                        "guards": {"requires_human_review_before_effective_change": True},
                        "recommendations": [
                            {
                                "lane": "optimize",
                                "decision": "review_candidate_variants",
                                "priority": "P1",
                                "risk_level": "medium",
                                "title": "Review variants",
                                "reason": "5 candidate variants",
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with mock.patch.object(module, "_latest_self_evolution_recommendation_path", return_value=artifact):
                payload = module._build_self_evolution_recommendations()

        self.assertEqual("pass", payload["report_status"])
        self.assertEqual("2026-05-30", payload["as_of"])
        self.assertEqual("report_only_until_wait_for_host_capability_recovery", payload["recommended_next_action"])
        self.assertTrue(payload["materialization_blocked"])
        self.assertEqual("wait_for_host_capability_recovery", payload["selector_next_action"])
        self.assertEqual(5, payload["variant_review_candidate_count"])
        self.assertEqual(["FeedbackReport", "DailyAll"], payload["trigger_model"]["proactive_operator_triggers"])
        self.assertEqual("optimize", payload["recommendations"][0]["lane"])
        self.assertTrue(payload["report_path"].endswith("20260530-self-evolution-recommendations.json"))

    def test_operator_ui_self_evolution_recommendations_surface_missing_state(self) -> None:
        module = _load_serve_operator_ui_module()

        with mock.patch.object(module, "_latest_self_evolution_recommendation_path", return_value=None):
            payload = module._build_self_evolution_recommendations()

        self.assertEqual("missing", payload["report_status"])
        self.assertEqual("run_self_evolution_recommend", payload["recommended_next_action"])
        self.assertIn("SelfEvolutionRecommend", payload["trigger_model"]["recommended_operator_action"])
        self.assertIn("FeedbackReport", payload["trigger_model"]["proactive_operator_triggers"])

    def test_codex_status_refresh_helper_is_retired(self) -> None:
        module = _load_serve_operator_ui_module()

        self.assertFalse(hasattr(module, "codex_status"))
        self.assertFalse(hasattr(module, "load_codex_status"))

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

    def test_operator_ui_server_apply_all_defaults_to_managed_cleanup_apply(self) -> None:
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
                    "action": "apply_all_features",
                    "target": "self-runtime",
                    "dry_run": False,
                    "language": "zh-CN",
                    "mode": "quick",
                }
            )

        self.assertEqual(0, result["exit_code"])
        command = run_mock.call_args_list[0].args[0]
        self.assertIn("apply-all", command)
        self.assertIn("self-runtime", command)
        self.assertIn("-ApplyManagedAssetRemoval", command)
        self.assertNotIn("-DryRun", command)

    def test_operator_ui_server_apply_all_dry_run_disables_managed_cleanup_apply(self) -> None:
        module = _load_serve_operator_ui_module()

        completed = subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="DRY-RUN apply-all",
            stderr="",
        )
        with mock.patch.object(module.subprocess, "run", return_value=completed) as run_mock:
            result = module.run_operator_action(
                {
                    "action": "apply_all_features",
                    "target": "self-runtime",
                    "dry_run": True,
                    "language": "zh-CN",
                    "mode": "quick",
                }
            )

        self.assertEqual(0, result["exit_code"])
        command = run_mock.call_args_list[0].args[0]
        self.assertIn("apply-all", command)
        self.assertIn("-DryRun", command)
        self.assertNotIn("-ApplyManagedAssetRemoval", command)

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

    def test_next_work_summary_blocks_cleanup_and_uninstall_for_repair_gate_first(self) -> None:
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
        self.assertIn("daily_all", payload["blocked_actions"])
        self.assertIn("apply_all_features", payload["blocked_actions"])
        self.assertIn("cleanup_targets", payload["blocked_actions"])
        self.assertIn("uninstall_governance", payload["blocked_actions"])
        self.assertIn("evolution_materialize", payload["blocked_actions"])

    def test_operator_preflight_blocks_cleanup_and_uninstall_actions(self) -> None:
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

        for action in ("CleanupTargets", "UninstallGovernance"):
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
                    env=env,
                )

                self.assertNotEqual(0, completed.returncode)
                self.assertIn(f"operator-preflight blocked: {action}", completed.stderr)

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
        self.assertIn("self-evolution-recommend", completed.stdout)
        self.assertIn("self-evolution-recommendations", completed.stdout)

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
        self.assertIn("function Resolve-PythonWindowlessCommand", script)
        self.assertIn("Get-Command pythonw", script)
        self.assertIn("scripts/serve-operator-ui.py", script)
        self.assertIn("Get-ServiceSourceLastWriteUtc", script)
        self.assertIn("function New-OperatorUiTaskSettings", script)
        self.assertIn("-ExecutionTimeLimit ([timespan]::Zero)", script)
        self.assertIn("-RestartInterval (New-TimeSpan -Minutes 1)", script)
        self.assertIn("operator_ui.py", script)
        self.assertIn("operator_ui_script.py", script)
        self.assertIn("operator_ui_style.py", script)
        self.assertIn("operator_ui_text.py", script)
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
