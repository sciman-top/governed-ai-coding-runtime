import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "check-source-string-contract-guard.py"


class SourceStringContractGuardTests(unittest.TestCase):
    def test_guard_skips_when_no_source_string_contract_tests_are_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            target_repo = Path(tmp_dir) / "target"
            target_repo.mkdir(parents=True)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--target-repo-root",
                    str(target_repo),
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "skip")
            self.assertEqual(payload["reason"], "no_source_string_contract_tests_detected")

    def test_guard_executes_detected_source_string_contract_tests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            target_repo = Path(tmp_dir) / "target"
            contract_file = self._create_dotnet_contract_fixture(target_repo)
            log_path = Path(tmp_dir) / "dotnet.log"
            dotnet_cmd = self._create_fake_dotnet_command(Path(tmp_dir), log_path)

            env = os.environ.copy()
            env["SOURCE_STRING_GUARD_DOTNET_LOG"] = str(log_path)
            env["SOURCE_STRING_GUARD_FAIL_CONTAINS"] = ""

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--target-repo-root",
                    str(target_repo),
                    "--dotnet-command",
                    str(dotnet_cmd),
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
                env=env,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(len(payload["detected_classes"]), 1)
            self.assertEqual(payload["failed_classes"], [])
            self.assertEqual(payload["detected_files"], [str(contract_file.resolve())])
            log_text = log_path.read_text(encoding="utf-8")
            self.assertIn("--filter", log_text)
            self.assertIn("FullyQualifiedName~Sample.RuntimeContractTests", log_text)

    def test_guard_fails_when_source_string_contract_tests_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            target_repo = Path(tmp_dir) / "target"
            self._create_dotnet_contract_fixture(target_repo)
            log_path = Path(tmp_dir) / "dotnet.log"
            dotnet_cmd = self._create_fake_dotnet_command(Path(tmp_dir), log_path)

            env = os.environ.copy()
            env["SOURCE_STRING_GUARD_DOTNET_LOG"] = str(log_path)
            env["SOURCE_STRING_GUARD_FAIL_CONTAINS"] = "Sample.RuntimeContractTests"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--target-repo-root",
                    str(target_repo),
                    "--dotnet-command",
                    str(dotnet_cmd),
                    "--json",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
                env=env,
            )

            self.assertEqual(completed.returncode, 1)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "fail")
            self.assertIn("Sample.RuntimeContractTests", payload["failed_classes"])

    @staticmethod
    def _create_dotnet_contract_fixture(target_repo: Path) -> Path:
        test_project_dir = target_repo / "tests" / "Sample.Tests"
        test_project_dir.mkdir(parents=True)
        (test_project_dir / "Sample.Tests.csproj").write_text(
            "<Project Sdk=\"Microsoft.NET.Sdk\"></Project>",
            encoding="utf-8",
        )
        contract_file = test_project_dir / "SampleRuntimeContractTests.cs"
        contract_file.write_text(
            "\n".join(
                [
                    "using FluentAssertions;",
                    "namespace Sample;",
                    "public sealed class RuntimeContractTests",
                    "{",
                    "    [Fact]",
                    "    public void EnsureContractString()",
                    "    {",
                    "        var source = \"sample\";",
                    "        source.Should().Contain(\"sample\");",
                    "    }",
                    "}",
                ]
            ),
            encoding="utf-8",
        )
        return contract_file

    @staticmethod
    def _create_fake_dotnet_command(workspace: Path, log_path: Path) -> Path:
        fake_dotnet_script = workspace / "fake_dotnet.py"
        fake_dotnet_script.write_text(
            "\n".join(
                [
                    "import os",
                    "import sys",
                    "from pathlib import Path",
                    "",
                    "log_path = Path(os.environ['SOURCE_STRING_GUARD_DOTNET_LOG'])",
                    "args_text = ' '.join(sys.argv[1:])",
                    "existing = ''",
                    "if log_path.exists():",
                    "    existing = log_path.read_text(encoding='utf-8')",
                    "log_path.write_text(existing + args_text + '\\n', encoding='utf-8')",
                    "fail_contains = os.environ.get('SOURCE_STRING_GUARD_FAIL_CONTAINS', '').strip()",
                    "if fail_contains and fail_contains in args_text:",
                    "    raise SystemExit(1)",
                    "raise SystemExit(0)",
                ]
            ),
            encoding="utf-8",
        )

        command_path = workspace / "fake-dotnet.cmd"
        command_path.write_text(
            "\n".join(
                [
                    "@echo off",
                    f"python \"{fake_dotnet_script}\" %*",
                ]
            ),
            encoding="utf-8",
        )
        return command_path


if __name__ == "__main__":
    unittest.main()
