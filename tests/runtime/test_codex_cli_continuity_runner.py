import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "codex-cli-continuity-runner.py"


def load_runner_module():
    spec = importlib.util.spec_from_file_location("codex_cli_continuity_runner", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CodexCliContinuityRunnerTests(unittest.TestCase):
    def test_classify_retryable_failures(self):
        runner = load_runner_module()
        cases = [
            (1, "", "429 insufficient_quota", "quota"),
            (1, "", "401 Unauthorized token_invalidated", "auth_401"),
            (1, "account limit reached", "", "account_limit"),
            (2, "syntax exploded", "", "unknown_error"),
            (0, "ok", "", "success"),
        ]
        for exit_code, stdout, stderr, expected in cases:
            with self.subTest(expected=expected):
                result = runner.SegmentResult(exit_code, stdout, stderr)
                self.assertEqual(runner.classify_failure(result), expected)

    def test_dry_run_builds_command_without_starting_codex(self):
        runner = load_runner_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cockpit_home = root / ".antigravity_cockpit"
            cockpit_home.mkdir()
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps({"currentAccountId": "acct_before"}),
                encoding="utf-8",
            )
            args = runner.parse_args(
                [
                    "--task-id",
                    "task-dry",
                    "--repo",
                    str(root),
                    "--prompt",
                    "continue safely",
                    "--cockpit-home",
                    str(cockpit_home),
                ]
            )

            report = runner.execute_once(args)

        self.assertEqual(report["mode"], "dry_run")
        self.assertEqual(report["status"], "success")
        self.assertEqual(report["segments"][0]["failure_reason"], "success")
        self.assertEqual(report["segments"][0]["command"][0:4], ["codex", "exec", "--cd", str(root)])
        self.assertEqual(report["write_actions"], [])

    def test_retryable_failure_generates_handoff_after_account_change(self):
        runner = load_runner_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cockpit_home = root / ".antigravity_cockpit"
            evidence_dir = root / "evidence"
            cockpit_home.mkdir()
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps({"currentAccountId": "acct_before_1234"}),
                encoding="utf-8",
            )
            args = runner.parse_args(
                [
                    "--task-id",
                    "task-quota",
                    "--repo",
                    str(root),
                    "--prompt",
                    "resume this task",
                    "--cockpit-home",
                    str(cockpit_home),
                    "--evidence-dir",
                    str(evidence_dir),
                    "--simulate-exit-code",
                    "1",
                    "--simulate-stderr",
                    "429 insufficient_quota",
                ]
            )
            observed_accounts = iter(["acct_before_1234", "acct_after_5678", "acct_after_5678"])
            runner.current_account_id = lambda _home: next(observed_accounts)
            report = runner.execute_once(args)

            self.assertEqual(report["status"], "retry_limit_reached")
            self.assertEqual(report["segments"][0]["failure_reason"], "quota")
            self.assertTrue(report["segments"][0]["retryable"])
            self.assertTrue(report["handoff_refs"])
            handoff = Path(report["handoff_refs"][0])
            self.assertTrue(handoff.exists())
            text = handoff.read_text(encoding="utf-8")
            self.assertIn("Failure reason: quota", text)
            self.assertIn("resume this task", text)
            self.assertIn("...5678", text)

    def test_retryable_failure_auto_starts_next_segment_after_account_change(self):
        runner = load_runner_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cockpit_home = root / ".antigravity_cockpit"
            evidence_dir = root / "evidence"
            cockpit_home.mkdir()
            args = runner.parse_args(
                [
                    "--task-id",
                    "task-loop",
                    "--repo",
                    str(root),
                    "--prompt",
                    "finish this task",
                    "--cockpit-home",
                    str(cockpit_home),
                    "--evidence-dir",
                    str(evidence_dir),
                    "--max-segments",
                    "2",
                    "--wait-seconds",
                    "1",
                    "--simulate-results",
                    json.dumps(
                        [
                            {"exit_code": 1, "stderr": "401 Unauthorized token_invalidated"},
                            {"exit_code": 0, "stdout": "done"},
                        ]
                    ),
                ]
            )
            account_calls = {"count": 0}

            def fake_current_account(_home):
                account_calls["count"] += 1
                return "acct_before_1234" if account_calls["count"] == 1 else "acct_after_5678"

            runner.current_account_id = fake_current_account

            report = runner.execute_continuity(args)

        self.assertEqual(report["status"], "success")
        self.assertEqual(len(report["segments"]), 2)
        self.assertEqual(report["segments"][0]["failure_reason"], "auth_401")
        self.assertEqual(report["segments"][1]["failure_reason"], "success")
        self.assertIn("Continue the same task", report["segments"][1]["command"][-1])
        self.assertEqual(len(report["handoff_refs"]), 1)

    def test_retryable_failure_does_not_restart_without_account_change(self):
        runner = load_runner_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cockpit_home = root / ".antigravity_cockpit"
            evidence_dir = root / "evidence"
            cockpit_home.mkdir()
            args = runner.parse_args(
                [
                    "--task-id",
                    "task-no-change",
                    "--repo",
                    str(root),
                    "--prompt",
                    "finish this task",
                    "--cockpit-home",
                    str(cockpit_home),
                    "--evidence-dir",
                    str(evidence_dir),
                    "--max-segments",
                    "2",
                    "--simulate-results",
                    json.dumps(
                        [
                            {"exit_code": 1, "stderr": "429 insufficient_quota"},
                            {"exit_code": 0, "stdout": "would be skipped"},
                        ]
                    ),
                ]
            )
            runner.current_account_id = lambda _home: "acct_same_1234"

            report = runner.execute_continuity(args)

        self.assertEqual(report["status"], "waiting_for_account_change")
        self.assertEqual(len(report["segments"]), 1)


if __name__ == "__main__":
    unittest.main()
