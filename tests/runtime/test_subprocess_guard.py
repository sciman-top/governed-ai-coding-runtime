import os
import sys
import tempfile
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
        self.assertEqual(normalized.get("ProgramFiles"), r"C:\Program Files")
        self.assertIn(r"C:\Windows\System32", normalized.get("PATH", ""))

    @unittest.skipUnless(os.name == "nt", "Windows Codex environment policy")
    def test_imports_safe_codex_shell_policy_proxy_vars(self) -> None:
        import governed_ai_coding_runtime_contracts.subprocess_guard as guard

        original_env = os.environ.copy()
        with tempfile.TemporaryDirectory() as tmp_dir:
            codex_home = Path(tmp_dir)
            (codex_home / "config.toml").write_text(
                "\n".join(
                    [
                        "[shell_environment_policy.set]",
                        'HTTP_PROXY = "http://127.0.0.1:10808"',
                        'HTTPS_PROXY = "http://127.0.0.1:10808"',
                        'NO_PROXY = "localhost,127.0.0.1,::1"',
                        'ANTHROPIC_AUTH_TOKEN = "must-not-propagate"',
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            try:
                os.environ.clear()
                os.environ["CODEX_HOME"] = str(codex_home)
                os.environ["USERPROFILE"] = original_env.get("USERPROFILE", r"C:\Users\sciman")
                normalized = guard._subprocess_environment()
            finally:
                os.environ.clear()
                os.environ.update(original_env)

        self.assertEqual(normalized.get("HTTP_PROXY"), "http://127.0.0.1:10808")
        self.assertEqual(normalized.get("HTTPS_PROXY"), "http://127.0.0.1:10808")
        self.assertEqual(normalized.get("NO_PROXY"), "localhost,127.0.0.1,::1")
        self.assertNotIn("ANTHROPIC_AUTH_TOKEN", normalized)

    @unittest.skipUnless(os.name == "nt", "Windows shell normalization")
    def test_codex_shell_policy_cannot_override_comspec(self) -> None:
        import governed_ai_coding_runtime_contracts.subprocess_guard as guard

        original_env = os.environ.copy()
        with tempfile.TemporaryDirectory() as tmp_dir:
            codex_home = Path(tmp_dir) / "codex-home"
            codex_home.mkdir()
            fake_shell = Path(tmp_dir) / "fake-cmd.exe"
            fake_shell.write_text("", encoding="utf-8")
            (codex_home / "config.toml").write_text(
                "\n".join(
                    [
                        "[shell_environment_policy.set]",
                        f'ComSpec = "{fake_shell.as_posix()}"',
                        'HTTP_PROXY = "http://127.0.0.1:10808"',
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            try:
                os.environ.clear()
                os.environ["CODEX_HOME"] = str(codex_home)
                os.environ["USERPROFILE"] = original_env.get("USERPROFILE", r"C:\Users\sciman")
                normalized = guard._subprocess_environment()
            finally:
                os.environ.clear()
                os.environ.update(original_env)

        comspec = Path(normalized["ComSpec"])
        self.assertEqual(comspec.name.lower(), "cmd.exe")
        self.assertEqual(comspec.parent.name.lower(), "system32")
        self.assertNotEqual(str(comspec).lower(), str(fake_shell).lower())
        self.assertEqual(normalized.get("HTTP_PROXY"), "http://127.0.0.1:10808")

    @unittest.skipUnless(os.name == "nt", "Windows shell normalization")
    def test_existing_environment_cannot_override_comspec_or_systemroot(self) -> None:
        import governed_ai_coding_runtime_contracts.subprocess_guard as guard

        original_env = os.environ.copy()
        with tempfile.TemporaryDirectory() as tmp_dir:
            fake_root = Path(tmp_dir) / "Windows"
            fake_root.mkdir()
            fake_shell = fake_root / "cmd.exe"
            fake_shell.write_text("", encoding="utf-8")
            try:
                os.environ.clear()
                os.environ["SystemRoot"] = str(fake_root)
                os.environ["WINDIR"] = str(fake_root)
                os.environ["ComSpec"] = str(fake_shell)
                os.environ["USERPROFILE"] = original_env.get("USERPROFILE", r"C:\Users\sciman")
                normalized = guard._subprocess_environment()
            finally:
                os.environ.clear()
                os.environ.update(original_env)

        self.assertNotEqual(normalized["SystemRoot"].lower(), str(fake_root).lower())
        self.assertNotEqual(normalized["WINDIR"].lower(), str(fake_root).lower())
        comspec = Path(normalized["ComSpec"])
        self.assertEqual(comspec.name.lower(), "cmd.exe")
        self.assertEqual(comspec.parent.name.lower(), "system32")
        self.assertNotEqual(str(comspec).lower(), str(fake_shell).lower())


if __name__ == "__main__":
    unittest.main()
