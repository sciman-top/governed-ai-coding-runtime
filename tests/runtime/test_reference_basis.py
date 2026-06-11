import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, check=False, capture_output=True, text=True)


def _init_repo(path: Path) -> None:
    _run(["git", "init", "-b", "main"], path)
    _run(["git", "config", "user.email", "test@example.invalid"], path)
    _run(["git", "config", "user.name", "Test User"], path)
    (path / "README.md").write_text("baseline\n", encoding="utf-8")
    _run(["git", "add", "README.md"], path)
    _run(["git", "commit", "-m", "baseline"], path)


class ReferenceBasisTests(unittest.TestCase):
    def test_guarded_surface_requires_reference_basis_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = Path(tmp_dir)
            _init_repo(repo)
            (repo / "scripts").mkdir()
            (repo / "scripts" / "verify-current-source-compatibility.py").write_text("print('changed')\n", encoding="utf-8")
            policy_path = self._write_policy(repo)

            completed = _run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "verify-reference-basis.py"),
                    "--repo-root",
                    str(repo),
                    "--policy",
                    str(policy_path),
                ],
                repo,
            )

            self.assertEqual(completed.returncode, 1)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "fail")
            self.assertEqual(payload["reason"], "missing_reference_basis_evidence")
            self.assertEqual(payload["guarded_paths"][0]["path"], "scripts/verify-current-source-compatibility.py")

    def test_guarded_surface_passes_with_reference_basis_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = Path(tmp_dir)
            _init_repo(repo)
            (repo / "scripts").mkdir()
            (repo / "scripts" / "verify-current-source-compatibility.py").write_text("print('changed')\n", encoding="utf-8")
            evidence = repo / "docs" / "change-evidence" / "reference-basis.md"
            evidence.parent.mkdir(parents=True)
            evidence.write_text(
                "\n".join(
                    [
                        "reference_basis_review",
                        "changed_surface_paths",
                        "scripts/verify-current-source-compatibility.py",
                        "reference_basis_surface_ids",
                        "host-and-adapter-boundaries",
                        "required_local_reference_ids_reviewed",
                        "openai-codex",
                        "anthropic-claude-code",
                        "reference_adoption_decision",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            policy_path = self._write_policy(repo)

            completed = _run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "verify-reference-basis.py"),
                    "--repo-root",
                    str(repo),
                    "--policy",
                    str(policy_path),
                ],
                repo,
            )

            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertEqual(payload["matched_evidence"], "docs/change-evidence/reference-basis.md")

    def test_verify_repo_contract_runs_reference_basis_gate(self) -> None:
        verifier = (ROOT / "scripts" / "verify-repo.ps1").read_text(encoding="utf-8")

        self.assertIn("function Invoke-ReferenceBasisChecks", verifier)
        self.assertIn("Invoke-ReferenceBasisChecks", verifier)
        self.assertIn('Write-CheckOk "reference-basis"', verifier)

    def _write_policy(self, repo_root: Path) -> Path:
        catalog_path = repo_root / "docs" / "research" / "reference-basis-catalog.json"
        catalog_path.parent.mkdir(parents=True, exist_ok=True)
        catalog_path.write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "references": [
                        {"reference_id": "openai-codex", "upstream": "https://github.com/openai/codex"},
                        {"reference_id": "anthropic-claude-code", "upstream": "https://github.com/anthropics/claude-code"},
                    ],
                }
            ),
            encoding="utf-8",
        )

        policy = {
            "schema_version": "1.0",
            "policy_id": "test-reference-basis",
            "status": "enforced",
            "reviewed_on": "2026-06-09",
            "review_expires_at": "2026-07-09",
            "decision_claim": "Guarded surfaces require mapped local references.",
            "reference_catalog_path": "docs/research/reference-basis-catalog.json",
            "evidence_directory": "docs/change-evidence/",
            "evidence_excluded_prefixes": [
                "docs/change-evidence/rule-sync-backups/",
                "docs/change-evidence/snapshots/",
            ],
            "required_evidence_tokens": [
                "reference_basis_review",
                "changed_surface_paths",
                "reference_basis_surface_ids",
                "required_local_reference_ids_reviewed",
                "reference_adoption_decision",
            ],
            "reference_surfaces": [
                {
                    "surface_id": "host-and-adapter-boundaries",
                    "path_exact": ["scripts/verify-current-source-compatibility.py"],
                    "required_local_reference_ids": ["openai-codex", "anthropic-claude-code"],
                    "rationale": "test surface",
                }
            ],
            "rollback_ref": "git revert test-reference-basis",
        }
        policy_path = repo_root / "reference-basis-policy.json"
        policy_path.write_text(json.dumps(policy), encoding="utf-8")
        return policy_path


if __name__ == "__main__":
    unittest.main()
