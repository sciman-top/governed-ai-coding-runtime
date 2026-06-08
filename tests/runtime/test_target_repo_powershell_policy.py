import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "verify-target-repo-powershell-policy.py"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _load_policy_module():
    spec = importlib.util.spec_from_file_location("verify_target_repo_powershell_policy", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TargetRepoPowerShellPolicyTests(unittest.TestCase):
    def test_default_target_repos_do_not_directly_invoke_windows_powershell(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT_PATH)],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["violation_count"], 0)

    def test_fails_on_direct_windows_powershell_invocation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            code_root = workspace / "code"
            target_root = code_root / "bad-repo"
            (target_root / "scripts").mkdir(parents=True)
            (target_root / "scripts" / "bad.ps1").write_text(
                "& powershell -File scripts/check.ps1\n",
                encoding="utf-8",
            )
            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "catalog_id": "test",
                    "targets": {
                        "bad-repo": {
                            "attachment_root": "${code_root}/bad-repo",
                            "attachment_runtime_state_root": "${runtime_state_base}/bad-repo",
                        }
                    },
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--catalog-path",
                    str(catalog_path),
                    "--repo-root",
                    str(workspace / "runtime"),
                    "--code-root",
                    str(code_root),
                    "--runtime-state-base",
                    str(workspace / "state"),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "fail")
            self.assertEqual(payload["violation_count"], 1)
            self.assertEqual(payload["violations"][0]["target"], "bad-repo")

    def test_skips_playwright_mcp_runtime_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            code_root = workspace / "code"
            target_root = code_root / "target-repo"
            (target_root / ".playwright-mcp").mkdir(parents=True)
            (target_root / ".playwright-mcp" / "page.yml").write_text(
                "command: powershell -File scripts/check.ps1\n",
                encoding="utf-8",
            )
            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "catalog_id": "test",
                    "targets": {
                        "target-repo": {
                            "attachment_root": "${code_root}/target-repo",
                            "attachment_runtime_state_root": "${runtime_state_base}/target-repo",
                        }
                    },
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--catalog-path",
                    str(catalog_path),
                    "--repo-root",
                    str(workspace / "runtime"),
                    "--code-root",
                    str(code_root),
                    "--runtime-state-base",
                    str(workspace / "state"),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["violation_count"], 0)

    def test_iter_policy_files_prunes_skipped_directories_during_walk(self) -> None:
        module = _load_policy_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "scripts").mkdir(parents=True)
            (repo_root / "scripts" / "ok.ps1").write_text("Write-Host ok\n", encoding="utf-8")
            (repo_root / "node_modules" / "deep").mkdir(parents=True)
            (repo_root / "node_modules" / "deep" / "bad.ps1").write_text("& powershell -File bad.ps1\n", encoding="utf-8")
            (repo_root / "packages" / "nested").mkdir(parents=True)
            (repo_root / "packages" / "nested" / "bad.yml").write_text("shell: powershell\n", encoding="utf-8")

            visited_dirs: list[Path] = []
            original_walk = module.Path.walk

            def tracking_walk(self, *args, **kwargs):
                for current_root, dirnames, filenames in original_walk(self, *args, **kwargs):
                    visited_dirs.append(Path(current_root))
                    yield current_root, dirnames, filenames

            original_path_walk = module.Path.walk
            module.Path.walk = tracking_walk
            try:
                files = module._iter_policy_files(repo_root)
            finally:
                module.Path.walk = original_path_walk

            relative_files = {path.relative_to(repo_root).as_posix() for path in files}
            self.assertEqual(relative_files, {"scripts/ok.ps1"})
            self.assertNotIn(repo_root / "node_modules", visited_dirs)
            self.assertNotIn(repo_root / "packages", visited_dirs)

    def test_iter_policy_files_does_not_depend_on_rglob(self) -> None:
        module = _load_policy_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            (repo_root / "scripts").mkdir(parents=True)
            (repo_root / "scripts" / "ok.ps1").write_text("Write-Host ok\n", encoding="utf-8")

            original_rglob = module.Path.rglob

            def fail_rglob(self, pattern):
                raise AssertionError("rglob should not be used for prunable policy scans")

            module.Path.rglob = fail_rglob
            try:
                files = module._iter_policy_files(repo_root)
            finally:
                module.Path.rglob = original_rglob

            relative_files = {path.relative_to(repo_root).as_posix() for path in files}
            self.assertEqual(relative_files, {"scripts/ok.ps1"})


if __name__ == "__main__":
    unittest.main()
