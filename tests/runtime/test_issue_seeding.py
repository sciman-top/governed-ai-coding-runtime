import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class IssueSeedingScriptTests(unittest.TestCase):
    def test_validate_only_reports_seed_summary_from_yaml(self) -> None:
        script = ROOT / "scripts" / "github" / "create-roadmap-issues.ps1"

        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
                "-ValidateOnly",
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        summary = json.loads(completed.stdout)
        self.assertEqual(summary["issue_seed_version"], "3.1")
        self.assertEqual(summary["issue_count"], 17)
        self.assertEqual(summary["first_issue_id"], "GAP-018")
        self.assertEqual(summary["gap_027_title"], "Minimal Operator Surface For Task, Approval, Evidence, And Replay")

    def test_validate_only_can_render_task_body_from_backlog(self) -> None:
        script = ROOT / "scripts" / "github" / "create-roadmap-issues.ps1"

        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
                "-ValidateOnly",
                "-IssueId",
                "GAP-027",
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        rendered = json.loads(completed.stdout)
        self.assertEqual(rendered["issue_id"], "GAP-027")
        self.assertEqual(rendered["title"], "[Task] Minimal Operator Surface For Task, Approval, Evidence, And Replay")
        self.assertIn("## Goal", rendered["body"])
        self.assertIn("CLI-first operator path backed by stable runtime read models", rendered["body"])
        self.assertIn("## Acceptance Criteria", rendered["body"])
        self.assertIn("the first delivery can be CLI-first", rendered["body"])

    def test_validate_only_can_render_epic_body_from_lifecycle_plan(self) -> None:
        script = ROOT / "scripts" / "github" / "create-roadmap-issues.ps1"

        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
                "-ValidateOnly",
                "-EpicId",
                "Full Runtime",
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        rendered = json.loads(completed.stdout)
        self.assertEqual(rendered["epic_id"], "Full Runtime")
        self.assertEqual(rendered["title"], "[Epic] Full Runtime")
        self.assertIn("## Goal", rendered["body"])
        self.assertIn("## Scope", rendered["body"])
        self.assertIn("execution worker", rendered["body"])
        self.assertIn("runtime health and status query surface", rendered["body"])
        self.assertIn("## Acceptance Criteria", rendered["body"])
        self.assertIn("one real governed task can run end-to-end", rendered["body"])

    def test_validate_only_can_render_initiative_body_from_lifecycle_plan(self) -> None:
        script = ROOT / "scripts" / "github" / "create-roadmap-issues.ps1"

        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
                "-ValidateOnly",
                "-Initiative",
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        rendered = json.loads(completed.stdout)
        self.assertEqual(rendered["title"], "[Initiative] Governed AI Coding Runtime Full Functional Lifecycle")
        self.assertIn("## Goal", rendered["body"])
        self.assertIn("single-machine self-hosted governed AI coding runtime", rendered["body"])
        self.assertIn("## Success Criteria", rendered["body"])
        self.assertIn("a real governed task can be created, executed, approved, verified, handed off, replayed, and recovered", rendered["body"])

    def test_verify_repo_scripts_runs_issue_seeding_render_check(self) -> None:
        script = ROOT / "scripts" / "verify-repo.ps1"

        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
                "-Check",
                "Scripts",
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertIn("OK powershell-parse", completed.stdout)
        self.assertIn("OK issue-seeding-render", completed.stdout)

    def test_validate_only_render_all_checks_all_issue_body_sources(self) -> None:
        script = ROOT / "scripts" / "github" / "create-roadmap-issues.ps1"

        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
                "-ValidateOnly",
                "-RenderAll",
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        summary = json.loads(completed.stdout)
        self.assertEqual(summary["issue_seed_version"], "3.1")
        self.assertEqual(summary["rendered_tasks"], 17)
        self.assertEqual(summary["rendered_epics"], 5)
        self.assertTrue(summary["rendered_initiative"])


if __name__ == "__main__":
    unittest.main()
