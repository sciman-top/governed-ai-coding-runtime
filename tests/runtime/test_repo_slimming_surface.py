import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "audit-repo-slimming-surface.py"


def _load_script_module():
    spec = importlib.util.spec_from_file_location("audit_repo_slimming_surface_script", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load script module from {SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RepoSlimmingSurfaceAuditTests(unittest.TestCase):
    def test_audit_generates_surface_summary_and_safety_fence(self) -> None:
        module = _load_script_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "surface-audit.json"
            payload = module.audit_repo_slimming_surface(repo_root=ROOT, output_path=output_path)

            self.assertEqual(payload["report_kind"], "repo_slimming_surface_audit")
            self.assertEqual(payload["safety_fence"]["delete_mode"], "forbidden_by_default")
            self.assertEqual(payload["visible_surface"]["file_count"] > 0, True)
            self.assertEqual(payload["text_surface"]["line_count"] > 0, True)
            self.assertIn("docs", payload["active_surface_breakdown"])
            self.assertIn("docs_change_evidence", payload["active_surface_breakdown"])
            self.assertIn("scripts", payload["active_surface_breakdown"])
            self.assertIn(".runtime", payload["transient_surface_breakdown"])
            self.assertGreaterEqual(len(payload["large_binary_evidence"]), 1)
            self.assertTrue(output_path.exists())

            written = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(written["report_kind"], "repo_slimming_surface_audit")
            self.assertEqual(written["comparison_keys"]["visible_surface_path"], "visible_surface")

    def test_cli_writes_expected_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "surface-audit.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/audit-repo-slimming-surface.py",
                    "--output",
                    str(output_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["report_kind"], "repo_slimming_surface_audit")
            self.assertTrue(output_path.exists())
            written = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(written["repo_id"], "governed-ai-coding-runtime")


if __name__ == "__main__":
    unittest.main()
