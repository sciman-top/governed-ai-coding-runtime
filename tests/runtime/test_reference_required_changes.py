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


class ReferenceRequiredChangeTests(unittest.TestCase):
    def test_guarded_surface_requires_structured_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = Path(tmp_dir)
            _init_repo(repo)
            (repo / "scripts").mkdir()
            (repo / "scripts" / "evaluate-runtime-evolution.py").write_text("print('changed')\n", encoding="utf-8")
            policy_path = self._write_policy(repo)

            completed = _run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "verify-reference-required-changes.py"),
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
            self.assertEqual(payload["reason"], "missing_reference_required_evidence")
            self.assertEqual(payload["guarded_paths"][0]["path"], "scripts/evaluate-runtime-evolution.py")

    def test_guarded_surface_passes_with_structured_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = Path(tmp_dir)
            _init_repo(repo)
            (repo / "scripts").mkdir()
            (repo / "scripts" / "evaluate-runtime-evolution.py").write_text("print('changed')\n", encoding="utf-8")
            evidence = repo / "docs" / "change-evidence" / "reference-required.md"
            evidence.parent.mkdir(parents=True)
            evidence.write_text(
                "\n".join(
                    [
                        "reference_required_review",
                        "changed_surface_paths",
                        "scripts/evaluate-runtime-evolution.py",
                        "official_sources_reviewed",
                        "primary_references_reviewed",
                        "local_runtime_evidence_reviewed",
                        "source_decision",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            policy_path = self._write_policy(repo)

            completed = _run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "verify-reference-required-changes.py"),
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
            self.assertEqual(payload["matched_evidence"], "docs/change-evidence/reference-required.md")

    def test_guarded_surface_fails_when_evidence_omits_changed_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = Path(tmp_dir)
            _init_repo(repo)
            (repo / "scripts").mkdir()
            (repo / "scripts" / "evaluate-runtime-evolution.py").write_text("print('changed')\n", encoding="utf-8")
            evidence = repo / "docs" / "change-evidence" / "reference-required.md"
            evidence.parent.mkdir(parents=True)
            evidence.write_text(
                "\n".join(
                    [
                        "reference_required_review",
                        "changed_surface_paths",
                        "official_sources_reviewed",
                        "primary_references_reviewed",
                        "local_runtime_evidence_reviewed",
                        "source_decision",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
            policy_path = self._write_policy(repo)

            completed = _run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "verify-reference-required-changes.py"),
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
            self.assertEqual(payload["reason"], "reference_required_evidence_incomplete")
            self.assertIn(
                "scripts/evaluate-runtime-evolution.py",
                payload["evidence_diagnostics"][0]["missing_guarded_path_mentions"],
            )

    def test_unrelated_change_passes_without_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            repo = Path(tmp_dir)
            _init_repo(repo)
            (repo / "notes.txt").write_text("unrelated\n", encoding="utf-8")
            policy_path = self._write_policy(repo)

            completed = _run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "verify-reference-required-changes.py"),
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
            self.assertEqual(payload["reason"], "no_reference_required_surfaces_changed")

    def test_verify_repo_contract_runs_reference_required_gate(self) -> None:
        verifier = (ROOT / "scripts" / "verify-repo.ps1").read_text(encoding="utf-8")

        self.assertIn("function Invoke-ReferenceRequiredChangeChecks", verifier)
        self.assertIn("Invoke-ReferenceRequiredChangeChecks", verifier)
        self.assertIn('Write-CheckOk "reference-required-changes"', verifier)

    def _write_policy(self, repo_root: Path) -> Path:
        policy = {
            "schema_version": "1.0",
            "policy_id": "test-reference-required",
            "status": "enforced",
            "reviewed_on": "2026-06-09",
            "review_expires_at": "2026-07-09",
            "decision_claim": "Guarded source changes require structured evidence.",
            "evidence_directory": "docs/change-evidence/",
            "evidence_excluded_prefixes": [
                "docs/change-evidence/rule-sync-backups/",
                "docs/change-evidence/snapshots/",
            ],
            "required_source_categories": [
                "official_doc_or_changelog",
                "primary_project_or_reference_implementation",
                "local_runtime_evidence",
            ],
            "required_evidence_tokens": [
                "reference_required_review",
                "changed_surface_paths",
                "official_sources_reviewed",
                "primary_references_reviewed",
                "local_runtime_evidence_reviewed",
                "source_decision",
            ],
            "change_surfaces": [
                {
                    "surface_id": "runtime-evolution",
                    "path_exact": ["scripts/evaluate-runtime-evolution.py"],
                    "rationale": "test surface",
                }
            ],
            "rollback_ref": "git revert test-reference-required",
        }
        policy_path = repo_root / "policy.json"
        policy_path.write_text(json.dumps(policy), encoding="utf-8")
        return policy_path


if __name__ == "__main__":
    unittest.main()
