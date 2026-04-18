import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ISSUE_SEEDS_PATH = ROOT / "docs" / "backlog" / "issue-seeds.yaml"
BACKLOG_PATH = ROOT / "docs" / "backlog" / "issue-ready-backlog.md"


class IssueSeedingScriptTests(unittest.TestCase):
    @staticmethod
    def _seed_version() -> str:
        content = ISSUE_SEEDS_PATH.read_text(encoding="utf-8")
        match = re.search(r'^issue_seed_version:\s+"([^"]+)"\s*$', content, re.MULTILINE)
        if match is None:
            raise AssertionError("issue_seed_version missing from issue-seeds.yaml")
        return match.group(1)

    @staticmethod
    def _seed_count() -> int:
        content = ISSUE_SEEDS_PATH.read_text(encoding="utf-8")
        return len(re.findall(r"^\s*-\s+id:\s+GAP-\d+\s*$", content, re.MULTILINE))

    @staticmethod
    def _completed_backlog_issue_count() -> int:
        content = BACKLOG_PATH.read_text(encoding="utf-8")
        return len(re.findall(r"^- Status: complete\b", content, re.MULTILINE))

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
        self.assertEqual(summary["issue_seed_version"], self._seed_version())
        self.assertEqual(summary["issue_count"], self._seed_count())
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
        self.assertIn("land the complete local runtime path", rendered["body"])
        self.assertIn("complete through `GAP-024` to `GAP-028`", rendered["body"])
        self.assertIn("## Acceptance Criteria", rendered["body"])
        self.assertIn("complete through `GAP-024` to `GAP-028`", rendered["body"])

    def test_validate_only_can_render_strategy_alignment_epic(self) -> None:
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
                "Strategy Alignment Gates",
            ],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        rendered = json.loads(completed.stdout)
        self.assertEqual(rendered["epic_id"], "Strategy Alignment Gates")
        self.assertEqual(rendered["title"], "[Epic] Strategy Alignment Gates")
        self.assertIn("fuse the governance-runtime positioning work", rendered["body"])
        self.assertIn("borrowing matrix", rendered["body"])

    def test_strategy_alignment_gates_are_rendered_as_productization_dependencies(self) -> None:
        script = ROOT / "scripts" / "github" / "create-roadmap-issues.ps1"

        expectations = {
            "GAP-035": "GAP-042",
            "GAP-036": "GAP-043",
            "GAP-037": "GAP-043",
            "GAP-038": "GAP-044",
            "GAP-039": "GAP-044",
        }

        for issue_id, expected_dependency in expectations.items():
            with self.subTest(issue_id=issue_id):
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
                        issue_id,
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                    cwd=ROOT,
                )

                rendered = json.loads(completed.stdout)
                self.assertIn(expected_dependency, rendered["body"])

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
        self.assertIn("generic, attach-first, interactive governed AI coding runtime", rendered["body"])
        self.assertIn("## Success Criteria", rendered["body"])
        self.assertIn("a new target repo can be attached through a repo-local light pack", rendered["body"])

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
        self.assertEqual(summary["issue_seed_version"], self._seed_version())
        self.assertEqual(summary["rendered_tasks"], self._seed_count())
        self.assertEqual(summary["rendered_epics"], 13)
        self.assertTrue(summary["rendered_initiative"])
        self.assertEqual(
            summary["rendered_issue_creation_tasks"],
            self._seed_count() - self._completed_backlog_issue_count(),
        )


if __name__ == "__main__":
    unittest.main()
