import sys
import unittest
from pathlib import Path
import importlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class TrialEntrypointTests(unittest.TestCase):
    def test_codex_adapter_declaration_keeps_user_owned_auth(self) -> None:
        try:
            module = importlib.import_module("governed_ai_coding_runtime_contracts.trial_entrypoint")
        except ModuleNotFoundError as exc:
            self.fail(f"trial_entrypoint module is not implemented: {exc}")
        if not hasattr(module, "codex_cli_adapter_declaration"):
            self.fail("codex_cli_adapter_declaration is not implemented")

        declaration = module.codex_cli_adapter_declaration()

        self.assertEqual(declaration["adapter_id"], "codex.cli.compatible")
        self.assertEqual(declaration["auth_ownership"], "user_owned_upstream_auth")
        self.assertEqual(declaration["unsupported_capability_behavior"], "degrade_to_manual_handoff")

    def test_run_scripted_readonly_trial_attaches_profile_and_budgets(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.trial_entrypoint")
        if not hasattr(module, "run_scripted_readonly_trial"):
            self.fail("run_scripted_readonly_trial is not implemented")

        result = module.run_scripted_readonly_trial(
            goal="inspect repository",
            scope="readonly trial",
            acceptance=["readonly request accepted"],
            repo_profile_path=ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json",
            target_path="src/service.py",
            budgets={"max_steps": 1, "max_minutes": 5},
        )

        self.assertEqual(result.task.repo, "python-service-sample")
        self.assertEqual(result.task.budgets, {"max_steps": 1, "max_minutes": 5})
        self.assertEqual(result.session.accepted_count, 1)
        self.assertEqual(result.output.latest_summary, "read-only trial accepted 1 tool request")
        self.assertEqual(result.adapter["auth_ownership"], "user_owned_upstream_auth")

    def test_repo_scripted_entrypoint_outputs_trial_summary(self) -> None:
        script = ROOT / "scripts" / "run-readonly-trial.py"
        if not script.exists():
            self.fail("scripts/run-readonly-trial.py is not implemented")

        completed = subprocess.run(
            [
                sys.executable,
                str(script),
                "--goal",
                "inspect repository",
                "--scope",
                "readonly trial",
                "--acceptance",
                "readonly request accepted",
                "--repo-profile",
                str(ROOT / "schemas" / "examples" / "repo-profile" / "python-service.example.json"),
                "--target-path",
                "src/service.py",
                "--max-steps",
                "1",
                "--max-minutes",
                "5",
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        summary = json.loads(completed.stdout)
        self.assertEqual(summary["repo_id"], "python-service-sample")
        self.assertEqual(summary["accepted_count"], 1)
        self.assertEqual(summary["auth_ownership"], "user_owned_upstream_auth")


if __name__ == "__main__":
    unittest.main()
