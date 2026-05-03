import importlib.util
import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "run-runtime-tests.py"


def _load_runner_module():
    spec = importlib.util.spec_from_file_location("run_runtime_tests", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load run-runtime-tests.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RunRuntimeTestsRunnerTests(unittest.TestCase):
    def test_default_worker_count_stays_conservative(self) -> None:
        runner = _load_runner_module()

        self.assertEqual(runner._resolve_worker_count(0, 20), min(8, runner.os.cpu_count() or 2))

    def test_auto_worker_cap_can_reduce_default_parallelism(self) -> None:
        runner = _load_runner_module()

        with mock.patch.dict(runner.os.environ, {"GOVERNED_RUNTIME_TEST_AUTO_WORKER_CAP": "3"}, clear=False):
            self.assertEqual(runner._resolve_worker_count(0, 20), 3)

    def test_explicit_worker_env_overrides_auto_worker_cap(self) -> None:
        runner = _load_runner_module()

        with mock.patch.dict(
            runner.os.environ,
            {
                "GOVERNED_RUNTIME_TEST_WORKERS": "5",
                "GOVERNED_RUNTIME_TEST_AUTO_WORKER_CAP": "3",
            },
            clear=False,
        ):
            self.assertEqual(runner._resolve_worker_count(0, 20), 5)

    def test_prioritize_targets_starts_known_slow_files_first(self) -> None:
        runner = _load_runner_module()
        fast = runner.TestTarget(
            suite="runtime",
            module="tests.runtime.test_fast",
            path=ROOT / "tests" / "runtime" / "test_fast.py",
        )
        slow = runner.TestTarget(
            suite="runtime",
            module="tests.runtime.test_slow",
            path=ROOT / "tests" / "runtime" / "test_slow.py",
        )

        ordered = runner._prioritize_targets(
            [fast, slow],
            {"tests.runtime.test_slow": 30.0},
        )

        self.assertEqual([target.module for target in ordered], ["tests.runtime.test_slow", "tests.runtime.test_fast"])

    def test_load_timing_history_accepts_windows_paths(self) -> None:
        runner = _load_runner_module()
        with tempfile.TemporaryDirectory(prefix="tmp_runtime_runner_", dir=ROOT) as tmp_dir:
            history_path = Path(tmp_dir) / "history.json"
            history_path.write_text(
                json.dumps(
                    {
                        "slowest": [
                            {
                                "duration_seconds": 12.5,
                                "target": {
                                    "module": "tests.runtime.test_slow",
                                    "path": "tests\\runtime\\test_slow.py",
                                },
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            history = runner._load_timing_history(history_path)

        self.assertEqual(history["tests.runtime.test_slow"], 12.5)
        self.assertEqual(history["tests/runtime/test_slow.py"], 12.5)

    def test_per_file_timeout_returns_timeout_exit(self) -> None:
        runner = _load_runner_module()
        with tempfile.TemporaryDirectory(prefix="tmp_runtime_runner_", dir=ROOT) as tmp_dir:
            package_dir = Path(tmp_dir)
            (package_dir / "__init__.py").write_text("", encoding="utf-8")
            test_path = package_dir / "test_sleep.py"
            test_path.write_text(
                textwrap.dedent(
                    """
                    import time
                    import unittest

                    class SleepTests(unittest.TestCase):
                        def test_slow(self):
                            time.sleep(2)
                    """
                ),
                encoding="utf-8",
            )
            target = runner.TestTarget(
                suite="tmp",
                module=f"{package_dir.name}.test_sleep",
                path=test_path,
            )

            result = runner._run_target(target, timeout_seconds=1)

            self.assertEqual(result.exit_code, 124)
            self.assertIn("Timed out after 1s", result.stderr)

    def test_summary_json_records_timing_metadata(self) -> None:
        with tempfile.TemporaryDirectory(prefix="tmp_runtime_runner_", dir=ROOT) as tmp_dir:
            package_dir = Path(tmp_dir)
            (package_dir / "__init__.py").write_text("", encoding="utf-8")
            (package_dir / "test_ok.py").write_text(
                textwrap.dedent(
                    """
                    import unittest

                    class OkTests(unittest.TestCase):
                        def test_ok(self):
                            self.assertTrue(True)
                    """
                ),
                encoding="utf-8",
            )
            summary_path = package_dir / "summary.json"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--suite",
                    f"tmp={package_dir.relative_to(ROOT)}",
                    "--workers",
                    "1",
                    "--timeout-seconds",
                    "30",
                    "--summary-json",
                    str(summary_path.relative_to(ROOT)),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["target_count"], 1)
            self.assertEqual(payload["worker_count"], 1)
            self.assertEqual(payload["timeout_seconds"], 30)
            self.assertIn("prioritized_target_count", payload)
            self.assertIn("timing_history_path", payload)
            self.assertEqual(payload["failure_count"], 0)
            self.assertEqual(payload["slowest"][0]["target"]["path"], str((package_dir / "test_ok.py").relative_to(ROOT)))


if __name__ == "__main__":
    unittest.main()
