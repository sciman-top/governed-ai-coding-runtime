import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "verify-target-repo-rollout-contract.py"
DEFAULT_BASELINE_PATH = ROOT / "docs" / "targets" / "target-repo-governance-baseline.json"
DEFAULT_CONTRACT_PATH = ROOT / "docs" / "targets" / "target-repo-rollout-contract.json"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _run_rollout_contract_check(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=ROOT,
    )


class TargetRepoRolloutContractTests(unittest.TestCase):
    def test_default_rollout_contract_passes(self) -> None:
        completed = _run_rollout_contract_check()

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertGreaterEqual(payload["capability_count"], 10)
        self.assertGreaterEqual(payload["feature_count"], 4)
        self.assertEqual(payload["errors"], [])
        contract = json.loads(DEFAULT_CONTRACT_PATH.read_text(encoding="utf-8"))
        managed_modes = {item["path"]: item["management_mode"] for item in contract["managed_file_rollout"]["required_managed_files"]}
        self.assertEqual(managed_modes[".claude/hooks/governed-pre-tool-use.py"], "block_on_drift")
        ownership = contract["repo_profile_ownership_contract"]
        self.assertEqual(
            set(ownership["catalog_input_fields"]),
            {"repo_id", "display_name", "primary_language", "build_commands", "test_commands", "contract_commands"},
        )
        runtime_contract_ids = {item["capability_id"] for item in contract["runtime_orchestrated_capability_contracts"]}
        self.assertIn("target-repo-problem-trace-and-kpi", runtime_contract_ids)
        self.assertIn("native-attach-runtime-flow", runtime_contract_ids)

    def test_fails_when_baseline_field_is_not_registered_for_one_click_rollout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            baseline = json.loads(DEFAULT_BASELINE_PATH.read_text(encoding="utf-8"))
            baseline["required_profile_overrides"]["new_unregistered_target_feature"] = {
                "enabled": True
            }
            baseline_path = workspace / "baseline.json"
            _write_json(baseline_path, baseline)

            completed = _run_rollout_contract_check(
                "--contract-path",
                str(DEFAULT_CONTRACT_PATH),
                "--baseline-path",
                str(baseline_path),
            )

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            codes = {error["code"] for error in payload["errors"]}
            self.assertIn("baseline_field_not_in_rollout_contract", codes)

    def test_fails_when_managed_file_is_not_registered_for_one_click_rollout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            baseline = json.loads(DEFAULT_BASELINE_PATH.read_text(encoding="utf-8"))
            baseline["required_managed_files"].append(
                {
                    "path": ".governed-ai/new-managed-check.py",
                    "source": "docs/targets/templates/verify-powershell-policy.py",
                }
            )
            baseline_path = workspace / "baseline.json"
            _write_json(baseline_path, baseline)

            completed = _run_rollout_contract_check(
                "--contract-path",
                str(DEFAULT_CONTRACT_PATH),
                "--baseline-path",
                str(baseline_path),
            )

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            codes = {error["code"] for error in payload["errors"]}
            self.assertIn("managed_file_not_in_rollout_contract", codes)

    def test_fails_when_speed_policy_field_is_not_registered_for_one_click_rollout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            baseline = json.loads(DEFAULT_BASELINE_PATH.read_text(encoding="utf-8"))
            baseline["target_repo_speed_profile_policy"]["new_required_speed_behavior"] = True
            baseline_path = workspace / "baseline.json"
            _write_json(baseline_path, baseline)

            completed = _run_rollout_contract_check(
                "--contract-path",
                str(DEFAULT_CONTRACT_PATH),
                "--baseline-path",
                str(baseline_path),
            )

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            codes = {error["code"] for error in payload["errors"]}
            self.assertIn("target_repo_speed_profile_policy_field_not_in_rollout_contract", codes)

    def test_fails_when_managed_file_mode_is_not_supported_by_rollout_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            contract = json.loads(DEFAULT_CONTRACT_PATH.read_text(encoding="utf-8"))
            contract["managed_file_rollout"]["required_managed_files"][0]["management_mode"] = "yaml_patch"
            contract_path = workspace / "contract.json"
            _write_json(contract_path, contract)

            completed = _run_rollout_contract_check("--contract-path", str(contract_path))

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            codes = {error["code"] for error in payload["errors"]}
            self.assertIn("managed_file_not_in_rollout_contract", codes)

    def test_fails_when_repo_profile_ownership_contract_mismatches_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            contract = json.loads(DEFAULT_CONTRACT_PATH.read_text(encoding="utf-8"))
            contract["repo_profile_ownership_contract"]["catalog_input_fields"] = ["repo_id", "display_name"]
            contract_path = workspace / "contract.json"
            _write_json(contract_path, contract)

            completed = _run_rollout_contract_check("--contract-path", str(contract_path))

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            codes = {error["code"] for error in payload["errors"]}
            self.assertIn("repo_profile_ownership_contract_catalog_mismatch", codes)

    def test_fails_when_runtime_orchestrated_capability_contract_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            contract = json.loads(DEFAULT_CONTRACT_PATH.read_text(encoding="utf-8"))
            contract["runtime_orchestrated_capability_contracts"] = [
                item for item in contract["runtime_orchestrated_capability_contracts"]
                if item["capability_id"] != "native-attach-runtime-flow"
            ]
            contract_path = workspace / "contract.json"
            _write_json(contract_path, contract)

            completed = _run_rollout_contract_check("--contract-path", str(contract_path))

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            codes = {error["code"] for error in payload["errors"]}
            self.assertIn("runtime_orchestrated_capability_missing_contract", codes)

    def test_fails_when_coding_speed_profile_args_are_missing_from_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            contract = json.loads(DEFAULT_CONTRACT_PATH.read_text(encoding="utf-8"))
            contract["canonical_one_click_entrypoint"]["coding_speed_profile_args"] = ["-AllTargets"]
            contract["target_repo_speed_profile_rollout"]["coding_speed_profile_args"] = ["-AllTargets"]
            contract_path = workspace / "contract.json"
            _write_json(contract_path, contract)

            completed = _run_rollout_contract_check("--contract-path", str(contract_path))

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            codes = {error["code"] for error in payload["errors"]}
            self.assertIn("missing_coding_speed_profile_arg", codes)
            self.assertIn("missing_target_repo_speed_profile_rollout_arg", codes)

    def test_fails_when_milestone_commit_template_is_not_chinese(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            baseline = json.loads(DEFAULT_BASELINE_PATH.read_text(encoding="utf-8"))
            baseline["required_profile_overrides"]["auto_commit_policy"][
                "commit_message_template"
            ] = "auto commit {repo_id} {milestone} {timestamp}"
            baseline_path = workspace / "baseline.json"
            _write_json(baseline_path, baseline)

            completed = _run_rollout_contract_check(
                "--contract-path",
                str(DEFAULT_CONTRACT_PATH),
                "--baseline-path",
                str(baseline_path),
            )

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            codes = {error["code"] for error in payload["errors"]}
            self.assertIn("auto_commit_policy_template_not_chinese", codes)
            self.assertIn("auto_commit_policy_template_missing_token", codes)

    def test_fails_when_profile_baseline_capability_is_missing_rollout_feature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            contract = json.loads(DEFAULT_CONTRACT_PATH.read_text(encoding="utf-8"))
            contract["target_repo_capabilities"].append(
                {
                    "capability_id": "new-profile-capability",
                    "distribution_scope": "profile_baseline",
                    "reason": "must be distributed to target repos",
                    "baseline_fields": ["new_profile_policy"],
                }
            )
            contract_path = workspace / "contract.json"
            _write_json(contract_path, contract)

            baseline = json.loads(DEFAULT_BASELINE_PATH.read_text(encoding="utf-8"))
            baseline["required_profile_overrides"]["new_profile_policy"] = {"enabled": True}
            baseline_path = workspace / "baseline.json"
            _write_json(baseline_path, baseline)

            completed = _run_rollout_contract_check(
                "--contract-path",
                str(contract_path),
                "--baseline-path",
                str(baseline_path),
            )

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            codes = {error["code"] for error in payload["errors"]}
            self.assertIn("profile_capability_missing_rollout_feature", codes)

    def test_fails_when_runtime_only_capability_declares_baseline_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            contract = json.loads(DEFAULT_CONTRACT_PATH.read_text(encoding="utf-8"))
            contract["target_repo_capabilities"].append(
                {
                    "capability_id": "bad-runtime-only-capability",
                    "distribution_scope": "runtime_orchestrated",
                    "reason": "runtime-owned feature",
                    "baseline_fields": ["bad_policy"],
                }
            )
            contract_path = workspace / "contract.json"
            _write_json(contract_path, contract)

            completed = _run_rollout_contract_check("--contract-path", str(contract_path))

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            codes = {error["code"] for error in payload["errors"]}
            self.assertIn("non_profile_capability_declares_baseline_fields", codes)


if __name__ == "__main__":
    unittest.main()
