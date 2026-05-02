import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class TargetRepoManagedAssetInventoryTests(unittest.TestCase):
    def test_inventory_classifies_active_drifted_retired_and_target_owned_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            source = workspace / "templates" / "managed.py"
            retired_source = workspace / "templates" / "old.py"
            managed_text = "print('managed')\n"
            retired_text = "print('old managed')\n"
            _write_text(source, managed_text)
            _write_text(retired_source, retired_text)
            _write_text(target / ".governed-ai" / "managed.py", managed_text)
            _write_text(target / ".governed-ai" / "drifted.py", "target improvement\n")
            _write_text(target / ".governed-ai" / "old.py", retired_text)
            _write_text(target / "tests" / "target_owned_test.py", "def test_target(): pass\n")
            baseline = {
                "required_managed_files": [
                    {
                        "path": ".governed-ai/managed.py",
                        "source": str(source),
                        "management_mode": "block_on_drift",
                    },
                    {
                        "path": ".governed-ai/drifted.py",
                        "source": str(source),
                        "management_mode": "block_on_drift",
                    },
                ],
                "generated_managed_files": [],
                "retired_managed_files": [
                    {
                        "path": ".governed-ai/old.py",
                        "previous_source": str(retired_source),
                        "previous_sha256": f"sha256:{_sha256(retired_text)}",
                        "retire_reason": "replaced by active guard",
                        "replacement": ".governed-ai/managed.py",
                        "safe_delete_when": ["target_sha256_matches_previous_sha256", "no_active_references"],
                        "backup_required": True,
                    }
                ],
            }
            baseline_path = workspace / "baseline.json"
            _write_json(baseline_path, baseline)

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/inspect-target-repo-managed-assets.py",
                    "--target-repo",
                    str(target),
                    "--baseline-path",
                    str(baseline_path),
                    "--candidate-path",
                    ".governed-ai/managed.py",
                    "--candidate-path",
                    ".governed-ai/drifted.py",
                    "--candidate-path",
                    ".governed-ai/old.py",
                    "--candidate-path",
                    "tests/target_owned_test.py",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            by_path = {item["path"]: item for item in payload["assets"]}
            self.assertEqual(by_path[".governed-ai/managed.py"]["classification"], "active_managed")
            self.assertEqual(by_path[".governed-ai/drifted.py"]["classification"], "managed_drifted")
            self.assertEqual(by_path[".governed-ai/old.py"]["classification"], "retired_managed_candidate")
            self.assertEqual(by_path["tests/target_owned_test.py"]["classification"], "target_owned")
            self.assertFalse(payload["modified"])

    def test_inventory_candidate_path_limits_scope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            target = workspace / "target"
            source = workspace / "templates" / "managed.py"
            _write_text(source, "print('managed')\n")
            _write_text(target / ".governed-ai" / "managed.py", "print('managed')\n")
            _write_text(target / "tests" / "target_owned_test.py", "def test_target(): pass\n")
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "required_managed_files": [
                        {
                            "path": ".governed-ai/managed.py",
                            "source": str(source),
                            "management_mode": "block_on_drift",
                        }
                    ],
                    "generated_managed_files": [],
                    "retired_managed_files": [],
                },
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/inspect-target-repo-managed-assets.py",
                    "--target-repo",
                    str(target),
                    "--baseline-path",
                    str(baseline_path),
                    "--candidate-path",
                    "tests/target_owned_test.py",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual([asset["path"] for asset in payload["assets"]], ["tests/target_owned_test.py"])
            self.assertEqual(payload["assets"][0]["classification"], "target_owned")


if __name__ == "__main__":
    unittest.main()
