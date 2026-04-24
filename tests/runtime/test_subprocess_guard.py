import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class SubprocessGuardTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "Windows shell lookup behavior")
    def test_shell_execution_uses_normalized_windows_environment(self) -> None:
        from governed_ai_coding_runtime_contracts.subprocess_guard import run_subprocess

        original_env = os.environ.copy()
        try:
            os.environ.clear()
            completed = run_subprocess(command="echo guard-ok", shell=True)
        finally:
            os.environ.clear()
            os.environ.update(original_env)

        self.assertEqual(completed.returncode, 0)
        self.assertIn("guard-ok", completed.stdout)
        self.assertFalse(completed.timed_out)

    @unittest.skipUnless(os.name == "nt", "Windows environment normalization")
    def test_normalizes_programdata_for_windows_subprocesses(self) -> None:
        import governed_ai_coding_runtime_contracts.subprocess_guard as guard

        original_env = os.environ.copy()
        try:
            os.environ.clear()
            os.environ["USERPROFILE"] = original_env.get("USERPROFILE", r"C:\Users\sciman")
            normalized = guard._subprocess_environment()
        finally:
            os.environ.clear()
            os.environ.update(original_env)

        self.assertEqual(normalized.get("PROGRAMDATA"), r"C:\ProgramData")


if __name__ == "__main__":
    unittest.main()
