import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]


def _load_host_feedback_summary_script():
    script_path = ROOT / "scripts" / "host-feedback-summary.py"
    spec = importlib.util.spec_from_file_location("host_feedback_summary_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["host_feedback_summary_script"] = module
    spec.loader.exec_module(module)
    return module


class HostFeedbackSummaryTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("host_feedback_summary_script", None)

    def test_repo_summary_cli_succeeds(self) -> None:
        completed = __import__("subprocess").run(
            [sys.executable, "scripts/host-feedback-summary.py"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertIn(payload["status"], {"pass", "attention", "fail"})
        self.assertEqual(6, len(payload["dimensions"]))

    def test_assert_minimum_passes_for_complete_temp_repo(self) -> None:
        module = _load_host_feedback_summary_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            self._write_minimal_repo(repo_root)

            with (
                mock.patch.object(module, "codex_status", return_value={"login_status": {"exit_code": 0}, "config": {"status": "ok"}}),
                mock.patch.object(module, "claude_status", return_value={"active_provider": {"name": "glm"}, "config": {"status": "ok"}, "command": {"exit_code": 0}, "mcp": {"exit_code": 0}}),
                mock.patch.object(module, "probe_claude_code_surface", return_value=self._claude_probe(module)),
            ):
                payload = module.build_host_feedback_summary(repo_root=repo_root)
                failures = module.validate_minimum_feedback_surface(payload)

        self.assertEqual([], failures)
        self.assertEqual("ok", payload["dimensions"][0]["status"])

    def test_assert_minimum_rejects_missing_target_run_evidence(self) -> None:
        module = _load_host_feedback_summary_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            self._write_minimal_repo(repo_root, include_target_run=False)

            with (
                mock.patch.object(module, "codex_status", return_value={"login_status": {"exit_code": 0}, "config": {"status": "ok"}}),
                mock.patch.object(module, "claude_status", return_value={"active_provider": {"name": "glm"}, "config": {"status": "ok"}, "command": {"exit_code": 0}, "mcp": {"exit_code": 0}}),
                mock.patch.object(module, "probe_claude_code_surface", return_value=self._claude_probe(module)),
            ):
                payload = module.build_host_feedback_summary(repo_root=repo_root)
                failures = module.validate_minimum_feedback_surface(payload)

        self.assertTrue(any("target repo run evidence" in item for item in failures))

    def test_host_dimension_surfaces_config_attention(self) -> None:
        module = _load_host_feedback_summary_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            self._write_minimal_repo(repo_root)

            with (
                mock.patch.object(module, "codex_status", return_value={"login_status": {"exit_code": 0}, "config": {"status": "attention"}}),
                mock.patch.object(module, "claude_status", return_value={"active_provider": {"name": "glm"}, "config": {"status": "ok"}, "command": {"exit_code": 0}, "mcp": {"exit_code": 0}}),
                mock.patch.object(module, "probe_claude_code_surface", return_value=self._claude_probe(module)),
            ):
                payload = module.build_host_feedback_summary(repo_root=repo_root)

        hosts = next(item for item in payload["dimensions"] if item["dimension_id"] == "hosts")
        self.assertEqual("attention", hosts["status"])
        self.assertEqual("attention", hosts["details"]["codex"]["health"])
        self.assertEqual("attention", payload["status"])

    def test_latest_target_run_prefers_newer_daily_evidence_over_onboard_snapshot(self) -> None:
        module = _load_host_feedback_summary_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            self._write_minimal_repo(repo_root, include_target_run=False)
            runs_root = repo_root / "docs" / "change-evidence" / "target-repo-runs"
            runs_root.mkdir(parents=True, exist_ok=True)
            (runs_root / "demo-onboard-20260430090000.json").write_text(
                json.dumps(self._target_run_payload("onboard")),
                encoding="utf-8",
            )
            (runs_root / "demo-daily-20260430110000.json").write_text(
                json.dumps(self._target_run_payload("daily")),
                encoding="utf-8",
            )

            with (
                mock.patch.object(module, "codex_status", return_value={"login_status": {"exit_code": 0}, "config": {"status": "ok"}}),
                mock.patch.object(module, "claude_status", return_value={"active_provider": {"name": "glm"}, "config": {"status": "ok"}, "command": {"exit_code": 0}, "mcp": {"exit_code": 0}}),
                mock.patch.object(module, "probe_claude_code_surface", return_value=self._claude_probe(module)),
            ):
                payload = module.build_host_feedback_summary(repo_root=repo_root)

        target_runs = next(item for item in payload["dimensions"] if item["dimension_id"] == "target_runs")
        demo_run = next(item for item in target_runs["details"]["latest_runs"] if item["repo_id"] == "demo")
        self.assertEqual("demo-daily-20260430110000.json", demo_run["file_name"])
        self.assertEqual("daily", demo_run["run_kind"])

    def test_claude_workload_dimension_surfaces_degraded_probe(self) -> None:
        module = _load_host_feedback_summary_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            self._write_minimal_repo(repo_root)

            with (
                mock.patch.object(module, "codex_status", return_value={"login_status": {"exit_code": 0}, "config": {"status": "ok"}}),
                mock.patch.object(module, "claude_status", return_value={"active_provider": {"name": "glm"}, "config": {"status": "ok"}, "command": {"exit_code": 0}, "mcp": {"exit_code": 0}}),
                mock.patch.object(module, "probe_claude_code_surface", return_value=self._claude_probe(module, native_attach_available=False, structured_events_available=False)),
            ):
                payload = module.build_host_feedback_summary(repo_root=repo_root)
                failures = module.validate_minimum_feedback_surface(payload)

        claude_workload = next(item for item in payload["dimensions"] if item["dimension_id"] == "claude_workload")
        self.assertEqual([], failures)
        self.assertEqual("attention", claude_workload["status"])
        self.assertEqual("degraded", claude_workload["details"]["readiness"]["status"])
        self.assertEqual("process_bridge", payload["summary"]["claude_adapter_tier"])

    def _write_minimal_repo(self, repo_root: Path, *, include_target_run: bool = True) -> None:
        for relative in (
            "docs/product/host-feedback-loop.md",
            "docs/product/host-feedback-loop.zh-CN.md",
            "docs/product/adapter-conformance-parity-matrix.md",
            "docs/quickstart/ai-coding-usage-guide.md",
            "docs/quickstart/ai-coding-usage-guide.zh-CN.md",
        ):
            path = repo_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            content = "Codex\nClaude Code\n" if path.name == "adapter-conformance-parity-matrix.md" else "ok\n"
            path.write_text(content, encoding="utf-8")

        manifest = {
            "sync_revision": "2026-04-30.1",
            "default_version": "9.47",
            "entries": [
                {"scope": "global", "tool": "codex", "target_path": "${user_profile}/.codex/AGENTS.md"},
                {"scope": "global", "tool": "claude", "target_path": "${user_profile}/.claude/CLAUDE.md"},
            ],
        }
        manifest_path = repo_root / "rules" / "manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        if include_target_run:
            run_path = repo_root / "docs" / "change-evidence" / "target-repo-runs" / "demo-daily-20260430120000.json"
            run_path.parent.mkdir(parents=True, exist_ok=True)
            run_path.write_text(json.dumps(self._target_run_payload("daily")), encoding="utf-8")

    def _target_run_payload(self, flow_mode: str) -> dict:
        return {
            "overall_status": "pass",
            "flow_mode": flow_mode,
            "runtime_check": {
                "payload": {
                    "status": {"codex_capability": {"adapter_tier": "native_attach", "flow_kind": "live_attach", "status": "ready", "unsupported_capabilities": []}},
                    "summary": {"flow_kind": "live_attach", "attachment_health": "healthy"},
                    "live_loop": {"closure_state": "live_closure_ready"},
                    "write_execute": {"execution_status": "executed"},
                }
            },
        }

    def _claude_probe(
        self,
        module,
        *,
        native_attach_available: bool = True,
        structured_events_available: bool = True,
    ):
        return module.ClaudeCodeSurfaceProbe(
            claude_cli_available=True,
            version="2.1.114",
            native_attach_available=native_attach_available,
            process_bridge_available=True,
            settings_available=True,
            hooks_available=True,
            session_id_available=True,
            structured_events_available=structured_events_available,
            evidence_export_available=True,
            resume_available=True,
            live_session_id=None,
            live_resume_id=None,
            reason="test probe",
            probe_commands=[
                module.ClaudeCodeProbeCommand(
                    cmd="claude --version",
                    exit_code=0,
                    key_output="2.1.114",
                    timestamp="2026-05-01T00:00:00+00:00",
                )
            ],
        )


if __name__ == "__main__":
    unittest.main()
