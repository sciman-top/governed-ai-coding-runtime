import datetime as dt
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_current_source_script():
    script_path = ROOT / "scripts" / "verify-current-source-compatibility.py"
    spec = importlib.util.spec_from_file_location("verify_current_source_compatibility_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["verify_current_source_compatibility_script"] = module
    spec.loader.exec_module(module)
    return module


class CurrentSourceCompatibilityTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("verify_current_source_compatibility_script", None)

    def test_current_source_policy_succeeds_for_repo(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/verify-current-source-compatibility.py", "--as-of", "2026-04-27"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["policy_id"], "default-current-source-compatibility")
        self.assertIn("a2a_1_0_0", payload["protocol_ids"])
        self.assertIn("github-copilot-repository-instructions", payload["source_ids"])
        self.assertIn("vscode-copilot-custom-instructions", payload["source_ids"])
        self.assertIn("anthropic-claude-code-best-practices", payload["source_ids"])
        self.assertIn("openhands-sandbox-overview", payload["source_ids"])
        self.assertFalse(payload["expired"])

    def test_current_source_policy_fails_when_review_expired(self) -> None:
        module = _load_current_source_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            policy_path = self._write_policy(
                repo_root,
                reviewed_on="2025-12-01",
                review_expires_at="2026-01-01",
            )

            with self.assertRaisesRegex(ValueError, "current-source review expired"):
                module.assert_current_source_compatibility(
                    repo_root=repo_root,
                    policy_path=policy_path,
                    as_of=dt.date(2026, 4, 27),
                )

    def test_current_source_policy_fails_when_required_doc_token_missing(self) -> None:
        module = _load_current_source_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            policy_path = self._write_policy(repo_root, required_token="not present")

            with self.assertRaisesRegex(ValueError, "missing doc refs"):
                module.assert_current_source_compatibility(
                    repo_root=repo_root,
                    policy_path=policy_path,
                    as_of=dt.date(2026, 4, 27),
                )

    def test_verify_repo_docs_runs_current_source_policy(self) -> None:
        verifier = (ROOT / "scripts" / "verify-repo.ps1").read_text(encoding="utf-8")

        self.assertIn("function Invoke-DocsChecks", verifier)
        self.assertIn("Invoke-CurrentSourceCompatibilityChecks", verifier)
        self.assertIn('Write-CheckOk "current-source-compatibility"', verifier)

    def _write_policy(
        self,
        repo_root: Path,
        *,
        reviewed_on: str = "2026-04-27",
        review_expires_at: str = "2026-07-26",
        required_token: str = "boundary token",
    ) -> Path:
        docs_dir = repo_root / "docs"
        evidence_path = docs_dir / "evidence.md"
        required_doc = docs_dir / "required.md"
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text("evidence", encoding="utf-8")
        required_doc.write_text("boundary token", encoding="utf-8")
        policy = {
            "schema_version": "1.0",
            "policy_id": "test-current-source",
            "status": "enforced",
            "reviewed_on": reviewed_on,
            "review_expires_at": review_expires_at,
            "compatibility_claim": "protocols cannot replace runtime-owned semantics",
            "kernel_owned_semantics": ["approval", "evidence"],
            "sources": [
                {
                    "source_id": "a2a-latest",
                    "url": "https://a2a-protocol.org/latest/specification/",
                    "source_kind": "protocol",
                    "reviewed_version": "1.0.0",
                    "boundary_assertions": ["adapter conformance only"],
                }
            ],
            "protocol_boundaries": [
                {
                    "protocol_id": "a2a_1_0_0",
                    "integration_owner": "adapter",
                    "required_mapping": "map authorization into approval",
                    "kernel_owned_semantics": ["approval", "evidence"],
                    "forbidden_claims": ["A2A replaces approval"],
                }
            ],
            "required_doc_refs": [{"path": "docs/required.md", "contains": required_token}],
            "forbidden_active_patterns": [
                {
                    "pattern": "A2A replaces approval",
                    "scan_roots": ["docs/required.md"],
                }
            ],
            "evidence_refs": ["docs/evidence.md"],
            "rollback_ref": "git revert test current-source policy",
        }
        policy_path = repo_root / "policy.json"
        policy_path.write_text(json.dumps(policy), encoding="utf-8")
        return policy_path


if __name__ == "__main__":
    unittest.main()
