import json
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


if __name__ == "__main__":
    unittest.main()
