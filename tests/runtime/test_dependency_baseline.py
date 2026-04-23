import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[2]


def _load_dependency_script():
    script_path = ROOT / "scripts" / "verify-dependency-baseline.py"
    spec = importlib.util.spec_from_file_location("verify_dependency_baseline_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["verify_dependency_baseline_script"] = module
    spec.loader.exec_module(module)
    return module


class DependencyBaselineTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("verify_dependency_baseline_script", None)

    def test_dependency_baseline_script_succeeds_for_repo(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/verify-dependency-baseline.py"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn('"status": "pass"', completed.stdout)
        self.assertIn('"allowed_external_modules": []', completed.stdout)
        self.assertIn('"host_tooling"', completed.stdout)

    def test_dependency_baseline_detects_undeclared_external_module(self) -> None:
        module = _load_dependency_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "scripts").mkdir(parents=True)
            (repo_root / "scripts" / "sample.py").write_text("import requests\n", encoding="utf-8")
            baseline_path = repo_root / "dependency-baseline.json"
            baseline_path.write_text(
                (
                    '{\n'
                    '  "version": 1,\n'
                    '  "python": {\n'
                    '    "scan_roots": ["scripts"],\n'
                    '    "allowed_local_modules": [],\n'
                    '    "allowed_external_modules": []\n'
                    "  }\n"
                    "}\n"
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "requests"):
                module.assert_dependency_baseline(repo_root=repo_root, baseline_path=baseline_path)

    def test_verify_repo_contract_runs_dependency_baseline(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "scripts/verify-repo.ps1",
                "-Check",
                "Contract",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("OK dependency-baseline", completed.stdout)
        self.assertIn("OK target-repo-governance-consistency", completed.stdout)

    def test_dependency_baseline_detects_missing_required_host_tool(self) -> None:
        module = _load_dependency_script()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "scripts").mkdir(parents=True)
            (repo_root / "scripts" / "sample.py").write_text("import json\n", encoding="utf-8")
            baseline_path = repo_root / "dependency-baseline.json"
            baseline_path.write_text(
                (
                    '{\n'
                    '  "version": 1,\n'
                    '  "python": {\n'
                    '    "scan_roots": ["scripts"],\n'
                    '    "allowed_local_modules": [],\n'
                    '    "allowed_external_modules": []\n'
                    "  },\n"
                    '  "host_tooling": [{"name": "required-tool", "required": true}]\n'
                    "}\n"
                ),
                encoding="utf-8",
            )

            with patch.object(module.shutil, "which", return_value=None):
                with self.assertRaisesRegex(ValueError, "required-tool"):
                    module.assert_dependency_baseline(repo_root=repo_root, baseline_path=baseline_path)

    def test_dependency_baseline_can_require_target_repo_baseline(self) -> None:
        module = _load_dependency_script()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            target_repo_root = repo_root / "target"
            target_repo_root.mkdir(parents=True)
            (repo_root / "scripts").mkdir(parents=True)
            (repo_root / "scripts" / "sample.py").write_text("import json\n", encoding="utf-8")
            baseline_path = repo_root / "dependency-baseline.json"
            baseline_path.write_text(
                (
                    '{\n'
                    '  "version": 1,\n'
                    '  "python": {\n'
                    '    "scan_roots": ["scripts"],\n'
                    '    "allowed_local_modules": [],\n'
                    '    "allowed_external_modules": []\n'
                    "  },\n"
                    '  "target_repo": {\n'
                    '    "baseline_paths": ["docs/dependency-baseline.md"]\n'
                    "  }\n"
                    "}\n"
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "target_repo_dependency_baseline"):
                module.assert_dependency_baseline(
                    repo_root=repo_root,
                    baseline_path=baseline_path,
                    target_repo_root=target_repo_root,
                    require_target_repo_baseline=True,
                )

            baseline_doc = target_repo_root / "docs" / "dependency-baseline.md"
            baseline_doc.parent.mkdir(parents=True, exist_ok=True)
            baseline_doc.write_text("# baseline\n", encoding="utf-8")
            result = module.assert_dependency_baseline(
                repo_root=repo_root,
                baseline_path=baseline_path,
                target_repo_root=target_repo_root,
                require_target_repo_baseline=True,
            )
            self.assertEqual(result["target_repo_baseline"]["present"], True)

    def test_dependency_baseline_rejects_non_repo_relative_scan_roots(self) -> None:
        module = _load_dependency_script()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            baseline_path = repo_root / "dependency-baseline.json"
            baseline_path.write_text(
                (
                    '{\n'
                    '  "version": 1,\n'
                    '  "python": {\n'
                    '    "scan_roots": ["../outside"],\n'
                    '    "allowed_local_modules": [],\n'
                    '    "allowed_external_modules": []\n'
                    "  }\n"
                    "}\n"
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "scan_roots"):
                module.assert_dependency_baseline(repo_root=repo_root, baseline_path=baseline_path)

    def test_dependency_baseline_reports_python_syntax_errors_with_file_context(self) -> None:
        module = _load_dependency_script()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "scripts").mkdir(parents=True)
            (repo_root / "scripts" / "broken.py").write_text("def oops(:\n    pass\n", encoding="utf-8")
            baseline_path = repo_root / "dependency-baseline.json"
            baseline_path.write_text(
                (
                    '{\n'
                    '  "version": 1,\n'
                    '  "python": {\n'
                    '    "scan_roots": ["scripts"],\n'
                    '    "allowed_local_modules": [],\n'
                    '    "allowed_external_modules": []\n'
                    "  }\n"
                    "}\n"
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(ValueError, "scripts/broken.py"):
                module.assert_dependency_baseline(repo_root=repo_root, baseline_path=baseline_path)


if __name__ == "__main__":
    unittest.main()
