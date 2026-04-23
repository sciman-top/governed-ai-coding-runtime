import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_fake_runtime_flow_script(path: Path) -> None:
    script = """param(
  [string]$EntrypointId = "",
  [ValidateSet("onboard", "daily")]
  [string]$FlowMode = "daily",
  [string]$AttachmentRoot = "",
  [string]$AttachmentRuntimeStateRoot = "",
  [string]$Mode = "quick",
  [string]$PolicyStatus = "allow",
  [string]$TaskId = "",
  [string]$RunId = "",
  [string]$CommandId = "",
  [string]$AdapterId = "",
  [string]$RepoBindingId = "",
  [string]$RepoId = "",
  [string]$DisplayName = "",
  [string]$PrimaryLanguage = "",
  [string]$BuildCommand = "",
  [string]$TestCommand = "",
  [string]$ContractCommand = "",
  [string]$AdapterPreference = "",
  [string]$GovernanceBaselinePath = "",
  [string]$WriteTargetPath = "",
  [string]$WriteTier = "",
  [string]$WriteToolName = "",
  [string]$WriteToolCommand = "",
  [string]$RollbackReference = "",
  [string]$WriteContent = "",
  [switch]$ExecuteWriteFlow,
  [switch]$SkipVerifyAttachment,
  [switch]$Overwrite,
  [switch]$Json
)

if ($Json) {
  @{
    exit_code = 0
    overall_status = "pass"
    flow_mode = $FlowMode
    attachment_root = $AttachmentRoot
    task_id = $TaskId
  } | ConvertTo-Json -Depth 8
}
else {
  Write-Host ("flow-pass target={0} mode={1}" -f $AttachmentRoot, $FlowMode)
}
exit 0
"""
    path.write_text(script, encoding="utf-8")


def _write_fake_full_check_script(path: Path) -> None:
    script = """param(
  [string]$RepoProfilePath = "",
  [string]$WorkingDirectory = "",
  [string]$MilestoneTag = "",
  [int]$GateTimeoutSeconds = 0,
  [switch]$ContinueOnError,
  [switch]$Json
)

if ($Json) {
  @(
    [ordered]@{
      exit_code = 0
      summary = [ordered]@{
        mode = "full"
        repo_profile_path = $RepoProfilePath
        working_directory = $WorkingDirectory
        gate_timeout_seconds = $GateTimeoutSeconds
        auto_commit = [ordered]@{
          status = "committed"
          reason = "ok"
          commit_hash = "fake-commit-hash"
          commit_message = ("自动提交：fake-repo 里程碑 {0} 门禁通过 2026-04-23 00:00:00 +08:00" -f $MilestoneTag)
          trigger = "milestone"
          milestone_tag = $MilestoneTag
        }
      }
    }
  ) | ConvertTo-Json -Depth 20
}
else {
  Write-Host ("full-check-pass profile={0} milestone={1} gate_timeout={2}" -f $RepoProfilePath, $MilestoneTag, $GateTimeoutSeconds)
}
exit 0
"""
    path.write_text(script, encoding="utf-8")


def _write_fake_fast_check_script(path: Path) -> None:
    script = """param(
  [string]$RepoProfilePath = "",
  [string]$WorkingDirectory = "",
  [string]$MilestoneTag = "",
  [int]$GateTimeoutSeconds = 0,
  [switch]$ContinueOnError,
  [switch]$Json
)

if ($Json) {
  @(
    [ordered]@{
      exit_code = 0
      summary = [ordered]@{
        mode = "fast"
        repo_profile_path = $RepoProfilePath
        working_directory = $WorkingDirectory
        gate_timeout_seconds = $GateTimeoutSeconds
        auto_commit = [ordered]@{
          status = "committed"
          reason = "ok"
          commit_hash = "fake-fast-commit-hash"
          commit_message = ("自动提交：fake-repo 快速里程碑 {0} 门禁通过 2026-04-24 00:00:00 +08:00" -f $MilestoneTag)
          trigger = "milestone"
          milestone_tag = $MilestoneTag
        }
      }
    }
  ) | ConvertTo-Json -Depth 20
}
else {
  Write-Host ("fast-check-pass profile={0} milestone={1} gate_timeout={2}" -f $RepoProfilePath, $MilestoneTag, $GateTimeoutSeconds)
}
exit 0
"""
    path.write_text(script, encoding="utf-8")


def _write_fake_slow_runtime_flow_script(path: Path) -> None:
    script = """param(
  [switch]$Json
)

Start-Sleep -Seconds 3
if ($Json) {
  @{ exit_code = 0; overall_status = "pass" } | ConvertTo-Json -Depth 8
}
else {
  Write-Host "slow-flow-pass"
}
exit 0
"""
    path.write_text(script, encoding="utf-8")


class RuntimeFlowPresetScriptTests(unittest.TestCase):
    def test_runtime_flow_preset_all_targets_onboard_applies_governance_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_a = workspace / "repo-a"
            repo_b = workspace / "repo-b"
            for repo in (repo_a, repo_b):
                _write_json(
                    repo / ".governed-ai" / "repo-profile.json",
                    {
                        "repo_id": repo.name,
                        "required_entrypoint_policy": {"current_mode": "advisory"},
                        "auto_commit_policy": {"enabled": False},
                    },
                )

            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "catalog_id": "test",
                    "targets": {
                        "repo-a": {
                            "attachment_root": str(repo_a),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-a"),
                            "repo_id": "repo-a",
                            "display_name": "repo-a",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                            "contract_command": "python --version",
                        },
                        "repo-b": {
                            "attachment_root": str(repo_b),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-b"),
                            "repo_id": "repo-b",
                            "display_name": "repo-b",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                            "contract_command": "python --version",
                        },
                    },
                },
            )

            baseline_path = workspace / "target-repo-governance-baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-23.1",
                    "required_profile_overrides": {
                        "required_entrypoint_policy": {"current_mode": "targeted_enforced"},
                        "auto_commit_policy": {"enabled": True, "on": ["milestone"]},
                    },
                },
            )

            fake_runtime_flow_path = workspace / "fake-runtime-flow.ps1"
            _write_fake_runtime_flow_script(fake_runtime_flow_path)

            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "runtime-flow-preset.ps1"),
                    "-AllTargets",
                    "-FlowMode",
                    "onboard",
                    "-Mode",
                    "quick",
                    "-Json",
                    "-Overwrite",
                    "-TaskId",
                    "task-test",
                    "-RunId",
                    "run-test",
                    "-CommandId",
                    "cmd-test",
                    "-CatalogPath",
                    str(catalog_path),
                    "-GovernanceBaselinePath",
                    str(baseline_path),
                    "-RuntimeFlowPath",
                    str(fake_runtime_flow_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["all_targets"], True)
            self.assertEqual(payload["failure_count"], 0)
            self.assertEqual(payload["target_count"], 2)
            for result in payload["results"]:
                self.assertEqual(result["governance_sync_status"], "pass")

            for repo in (repo_a, repo_b):
                profile = json.loads((repo / ".governed-ai" / "repo-profile.json").read_text(encoding="utf-8"))
                self.assertEqual(profile["required_entrypoint_policy"]["current_mode"], "targeted_enforced")
                self.assertEqual(profile["auto_commit_policy"]["enabled"], True)

    def test_runtime_flow_preset_single_target_json_keeps_runtime_payload_when_sync_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_a = workspace / "repo-a"
            _write_json(
                repo_a / ".governed-ai" / "repo-profile.json",
                {
                    "repo_id": "repo-a",
                    "required_entrypoint_policy": {"current_mode": "advisory"},
                    "auto_commit_policy": {"enabled": False},
                },
            )

            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "catalog_id": "test",
                    "targets": {
                        "repo-a": {
                            "attachment_root": str(repo_a),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-a"),
                            "repo_id": "repo-a",
                            "display_name": "repo-a",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                            "contract_command": "python --version",
                        }
                    },
                },
            )
            fake_runtime_flow_path = workspace / "fake-runtime-flow.ps1"
            _write_fake_runtime_flow_script(fake_runtime_flow_path)

            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "runtime-flow-preset.ps1"),
                    "-Target",
                    "repo-a",
                    "-FlowMode",
                    "daily",
                    "-Mode",
                    "quick",
                    "-Json",
                    "-CatalogPath",
                    str(catalog_path),
                    "-RuntimeFlowPath",
                    str(fake_runtime_flow_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["overall_status"], "pass")
            self.assertEqual(payload["flow_mode"], "daily")

    def test_runtime_flow_preset_apply_governance_baseline_only_skips_runtime_flow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_a = workspace / "repo-a"
            _write_json(
                repo_a / ".governed-ai" / "repo-profile.json",
                {
                    "repo_id": "repo-a",
                    "required_entrypoint_policy": {"current_mode": "advisory"},
                    "auto_commit_policy": {"enabled": False},
                },
            )
            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "catalog_id": "test",
                    "targets": {
                        "repo-a": {
                            "attachment_root": str(repo_a),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-a"),
                            "repo_id": "repo-a",
                            "display_name": "repo-a",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                            "contract_command": "python --version",
                        }
                    },
                },
            )
            baseline_path = workspace / "target-repo-governance-baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-23.1",
                    "required_profile_overrides": {
                        "required_entrypoint_policy": {"current_mode": "targeted_enforced"},
                        "auto_commit_policy": {"enabled": True, "on": ["milestone"]},
                    },
                },
            )

            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "runtime-flow-preset.ps1"),
                    "-Target",
                    "repo-a",
                    "-ApplyGovernanceBaselineOnly",
                    "-Json",
                    "-CatalogPath",
                    str(catalog_path),
                    "-GovernanceBaselinePath",
                    str(baseline_path),
                    "-RuntimeFlowPath",
                    str(workspace / "missing-runtime-flow.ps1"),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["governance_baseline_sync"]["status"], "pass")
            profile = json.loads((repo_a / ".governed-ai" / "repo-profile.json").read_text(encoding="utf-8"))
            self.assertEqual(profile["required_entrypoint_policy"]["current_mode"], "targeted_enforced")
            self.assertEqual(profile["auto_commit_policy"]["enabled"], True)

    def test_runtime_flow_preset_all_targets_apply_feature_baseline_and_milestone_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_a = workspace / "repo-a"
            repo_b = workspace / "repo-b"
            for repo in (repo_a, repo_b):
                _write_json(
                    repo / ".governed-ai" / "repo-profile.json",
                    {
                        "repo_id": repo.name,
                        "required_entrypoint_policy": {"current_mode": "advisory"},
                        "auto_commit_policy": {"enabled": False},
                    },
                )

            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "catalog_id": "test",
                    "targets": {
                        "repo-a": {
                            "attachment_root": str(repo_a),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-a"),
                            "repo_id": "repo-a",
                            "display_name": "repo-a",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                            "contract_command": "python --version",
                        },
                        "repo-b": {
                            "attachment_root": str(repo_b),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-b"),
                            "repo_id": "repo-b",
                            "display_name": "repo-b",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                            "contract_command": "python --version",
                        },
                    },
                },
            )

            baseline_path = workspace / "target-repo-governance-baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-23.1",
                    "required_profile_overrides": {
                        "required_entrypoint_policy": {"current_mode": "targeted_enforced"},
                        "auto_commit_policy": {"enabled": True, "on": ["milestone"]},
                    },
                },
            )

            fake_full_check_path = workspace / "fake-full-check.ps1"
            _write_fake_full_check_script(fake_full_check_path)

            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "runtime-flow-preset.ps1"),
                    "-AllTargets",
                    "-ApplyFeatureBaselineAndMilestoneCommit",
                    "-MilestoneTag",
                    "milestone",
                    "-Json",
                    "-CatalogPath",
                    str(catalog_path),
                    "-GovernanceBaselinePath",
                    str(baseline_path),
                    "-GovernanceFullCheckPath",
                    str(fake_full_check_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["all_targets"], True)
            self.assertEqual(payload["failure_count"], 0)
            self.assertEqual(payload["apply_feature_baseline_and_milestone_commit"], True)
            self.assertEqual(payload["milestone_tag"], "milestone")
            self.assertEqual(payload["milestone_gate_mode"], "full")
            self.assertEqual(payload["milestone_gate_mode_source"], "manual")
            self.assertEqual(payload["milestone_gate_mode_reason"], "manual_override")
            self.assertEqual(payload["milestone_gate_timeout_seconds"], 900)
            self.assertEqual(payload["milestone_command_timeout_seconds"], 0)
            for result in payload["results"]:
                self.assertEqual(result["governance_sync_status"], "pass")
                self.assertEqual(result["milestone_commit_status"], "pass")
                self.assertEqual(result["milestone_gate_mode"], "full")
                self.assertEqual(result["milestone_gate_mode_source"], "manual")
                self.assertEqual(result["milestone_gate_mode_reason"], "manual_override")
                self.assertEqual(result["auto_commit_status"], "committed")
                self.assertEqual(result["auto_commit_trigger"], "milestone")

            for repo in (repo_a, repo_b):
                profile = json.loads((repo / ".governed-ai" / "repo-profile.json").read_text(encoding="utf-8"))
                self.assertEqual(profile["required_entrypoint_policy"]["current_mode"], "targeted_enforced")
                self.assertEqual(profile["auto_commit_policy"]["enabled"], True)

    def test_runtime_flow_preset_all_targets_apply_all_features(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_a = workspace / "repo-a"
            repo_b = workspace / "repo-b"
            for repo in (repo_a, repo_b):
                _write_json(
                    repo / ".governed-ai" / "repo-profile.json",
                    {
                        "repo_id": repo.name,
                        "required_entrypoint_policy": {"current_mode": "advisory"},
                        "auto_commit_policy": {"enabled": False},
                    },
                )

            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "catalog_id": "test",
                    "targets": {
                        "repo-a": {
                            "attachment_root": str(repo_a),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-a"),
                            "repo_id": "repo-a",
                            "display_name": "repo-a",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                            "contract_command": "python --version",
                        },
                        "repo-b": {
                            "attachment_root": str(repo_b),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-b"),
                            "repo_id": "repo-b",
                            "display_name": "repo-b",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                            "contract_command": "python --version",
                        },
                    },
                },
            )

            baseline_path = workspace / "target-repo-governance-baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-23.1",
                    "required_profile_overrides": {
                        "required_entrypoint_policy": {"current_mode": "targeted_enforced"},
                        "auto_commit_policy": {"enabled": True, "on": ["milestone"]},
                    },
                },
            )

            fake_runtime_flow_path = workspace / "fake-runtime-flow.ps1"
            _write_fake_runtime_flow_script(fake_runtime_flow_path)
            fake_full_check_path = workspace / "fake-full-check.ps1"
            _write_fake_full_check_script(fake_full_check_path)

            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "runtime-flow-preset.ps1"),
                    "-AllTargets",
                    "-ApplyAllFeatures",
                    "-FlowMode",
                    "daily",
                    "-MilestoneTag",
                    "milestone",
                    "-Json",
                    "-CatalogPath",
                    str(catalog_path),
                    "-GovernanceBaselinePath",
                    str(baseline_path),
                    "-RuntimeFlowPath",
                    str(fake_runtime_flow_path),
                    "-GovernanceFullCheckPath",
                    str(fake_full_check_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["all_targets"], True)
            self.assertEqual(payload["failure_count"], 0)
            self.assertEqual(payload["apply_all_features"], True)
            self.assertEqual(payload["milestone_tag"], "milestone")
            self.assertEqual(payload["milestone_gate_mode"], "full")
            self.assertEqual(payload["milestone_gate_mode_source"], "manual")
            self.assertEqual(payload["milestone_gate_mode_reason"], "manual_override")
            self.assertEqual(payload["milestone_gate_timeout_seconds"], 900)
            self.assertEqual(payload["milestone_command_timeout_seconds"], 0)
            self.assertEqual(payload["batch_timed_out"], False)
            for result in payload["results"]:
                self.assertEqual(result["flow_exit_code"], 0)
                self.assertEqual(result["governance_sync_status"], "pass")
                self.assertEqual(result["milestone_commit_status"], "pass")
                self.assertEqual(result["milestone_gate_mode"], "full")
                self.assertEqual(result["milestone_gate_mode_source"], "manual")
                self.assertEqual(result["milestone_gate_mode_reason"], "manual_override")
                self.assertEqual(result["auto_commit_status"], "committed")
                self.assertEqual(result["auto_commit_trigger"], "milestone")

            for repo in (repo_a, repo_b):
                profile = json.loads((repo / ".governed-ai" / "repo-profile.json").read_text(encoding="utf-8"))
                self.assertEqual(profile["required_entrypoint_policy"]["current_mode"], "targeted_enforced")
                self.assertEqual(profile["auto_commit_policy"]["enabled"], True)

    def test_runtime_flow_preset_all_targets_apply_all_features_supports_fast_milestone_gate_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_a = workspace / "repo-a"
            repo_b = workspace / "repo-b"
            for repo in (repo_a, repo_b):
                _write_json(
                    repo / ".governed-ai" / "repo-profile.json",
                    {
                        "repo_id": repo.name,
                        "required_entrypoint_policy": {"current_mode": "advisory"},
                        "auto_commit_policy": {"enabled": False},
                    },
                )

            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "catalog_id": "test",
                    "targets": {
                        "repo-a": {
                            "attachment_root": str(repo_a),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-a"),
                            "repo_id": "repo-a",
                            "display_name": "repo-a",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                            "contract_command": "python --version",
                        },
                        "repo-b": {
                            "attachment_root": str(repo_b),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-b"),
                            "repo_id": "repo-b",
                            "display_name": "repo-b",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                            "contract_command": "python --version",
                        },
                    },
                },
            )

            baseline_path = workspace / "target-repo-governance-baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-23.1",
                    "required_profile_overrides": {
                        "required_entrypoint_policy": {"current_mode": "targeted_enforced"},
                        "auto_commit_policy": {"enabled": True, "on": ["milestone"]},
                    },
                },
            )

            fake_runtime_flow_path = workspace / "fake-runtime-flow.ps1"
            _write_fake_runtime_flow_script(fake_runtime_flow_path)
            fake_fast_check_path = workspace / "fake-fast-check.ps1"
            _write_fake_fast_check_script(fake_fast_check_path)

            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "runtime-flow-preset.ps1"),
                    "-AllTargets",
                    "-ApplyAllFeatures",
                    "-FlowMode",
                    "daily",
                    "-MilestoneGateMode",
                    "fast",
                    "-MilestoneTag",
                    "milestone",
                    "-Json",
                    "-CatalogPath",
                    str(catalog_path),
                    "-GovernanceBaselinePath",
                    str(baseline_path),
                    "-RuntimeFlowPath",
                    str(fake_runtime_flow_path),
                    "-GovernanceFastCheckPath",
                    str(fake_fast_check_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["milestone_gate_mode"], "fast")
            self.assertEqual(payload["milestone_gate_mode_source"], "manual")
            self.assertEqual(payload["milestone_gate_mode_reason"], "manual_override")
            self.assertEqual(payload["failure_count"], 0)
            for result in payload["results"]:
                self.assertEqual(result["milestone_gate_mode"], "fast")
                self.assertEqual(result["milestone_gate_mode_source"], "manual")
                self.assertEqual(result["milestone_gate_mode_reason"], "manual_override")
                self.assertEqual(result["auto_commit_status"], "committed")
                self.assertEqual(result["auto_commit_commit_hash"], "fake-fast-commit-hash")

    def test_runtime_flow_preset_auto_milestone_gate_mode_selects_fast_for_daily_low_risk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_a = workspace / "repo-a"
            repo_b = workspace / "repo-b"
            for repo in (repo_a, repo_b):
                _write_json(
                    repo / ".governed-ai" / "repo-profile.json",
                    {
                        "repo_id": repo.name,
                        "required_entrypoint_policy": {"current_mode": "advisory"},
                        "auto_commit_policy": {"enabled": False},
                    },
                )

            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "catalog_id": "test",
                    "targets": {
                        "repo-a": {
                            "attachment_root": str(repo_a),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-a"),
                            "repo_id": "repo-a",
                            "display_name": "repo-a",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                            "contract_command": "python --version",
                        },
                        "repo-b": {
                            "attachment_root": str(repo_b),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-b"),
                            "repo_id": "repo-b",
                            "display_name": "repo-b",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                            "contract_command": "python --version",
                        },
                    },
                },
            )

            baseline_path = workspace / "target-repo-governance-baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-23.1",
                    "required_profile_overrides": {
                        "required_entrypoint_policy": {"current_mode": "targeted_enforced"},
                        "auto_commit_policy": {"enabled": True, "on": ["milestone"]},
                    },
                },
            )

            fake_runtime_flow_path = workspace / "fake-runtime-flow.ps1"
            _write_fake_runtime_flow_script(fake_runtime_flow_path)
            fake_fast_check_path = workspace / "fake-fast-check.ps1"
            _write_fake_fast_check_script(fake_fast_check_path)
            fake_full_check_path = workspace / "fake-full-check.ps1"
            _write_fake_full_check_script(fake_full_check_path)

            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "runtime-flow-preset.ps1"),
                    "-AllTargets",
                    "-ApplyAllFeatures",
                    "-FlowMode",
                    "daily",
                    "-MilestoneGateMode",
                    "full",
                    "-AutoMilestoneGateMode",
                    "-MilestoneTag",
                    "milestone",
                    "-Json",
                    "-CatalogPath",
                    str(catalog_path),
                    "-GovernanceBaselinePath",
                    str(baseline_path),
                    "-RuntimeFlowPath",
                    str(fake_runtime_flow_path),
                    "-GovernanceFastCheckPath",
                    str(fake_fast_check_path),
                    "-GovernanceFullCheckPath",
                    str(fake_full_check_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["milestone_gate_mode"], "fast")
            self.assertEqual(payload["milestone_gate_mode_source"], "auto")
            self.assertEqual(payload["milestone_gate_mode_reason"], "daily_low_to_medium_risk")
            self.assertEqual(payload["auto_milestone_gate_mode"], True)
            self.assertEqual(payload["failure_count"], 0)
            for result in payload["results"]:
                self.assertEqual(result["milestone_gate_mode"], "fast")
                self.assertEqual(result["milestone_gate_mode_source"], "auto")
                self.assertEqual(result["milestone_gate_mode_reason"], "daily_low_to_medium_risk")
                self.assertEqual(result["auto_commit_commit_hash"], "fake-fast-commit-hash")

    def test_runtime_flow_preset_auto_milestone_gate_mode_selects_full_for_release_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_a = workspace / "repo-a"
            repo_b = workspace / "repo-b"
            for repo in (repo_a, repo_b):
                _write_json(
                    repo / ".governed-ai" / "repo-profile.json",
                    {
                        "repo_id": repo.name,
                        "required_entrypoint_policy": {"current_mode": "advisory"},
                        "auto_commit_policy": {"enabled": False},
                    },
                )

            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "catalog_id": "test",
                    "targets": {
                        "repo-a": {
                            "attachment_root": str(repo_a),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-a"),
                            "repo_id": "repo-a",
                            "display_name": "repo-a",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                            "contract_command": "python --version",
                        },
                        "repo-b": {
                            "attachment_root": str(repo_b),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-b"),
                            "repo_id": "repo-b",
                            "display_name": "repo-b",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                            "contract_command": "python --version",
                        },
                    },
                },
            )

            baseline_path = workspace / "target-repo-governance-baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-23.1",
                    "required_profile_overrides": {
                        "required_entrypoint_policy": {"current_mode": "targeted_enforced"},
                        "auto_commit_policy": {"enabled": True, "on": ["milestone"]},
                    },
                },
            )

            fake_runtime_flow_path = workspace / "fake-runtime-flow.ps1"
            _write_fake_runtime_flow_script(fake_runtime_flow_path)
            fake_fast_check_path = workspace / "fake-fast-check.ps1"
            _write_fake_fast_check_script(fake_fast_check_path)
            fake_full_check_path = workspace / "fake-full-check.ps1"
            _write_fake_full_check_script(fake_full_check_path)

            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "runtime-flow-preset.ps1"),
                    "-AllTargets",
                    "-ApplyAllFeatures",
                    "-FlowMode",
                    "daily",
                    "-MilestoneGateMode",
                    "fast",
                    "-AutoMilestoneGateMode",
                    "-ReleaseCandidate",
                    "-MilestoneTag",
                    "milestone",
                    "-Json",
                    "-CatalogPath",
                    str(catalog_path),
                    "-GovernanceBaselinePath",
                    str(baseline_path),
                    "-RuntimeFlowPath",
                    str(fake_runtime_flow_path),
                    "-GovernanceFastCheckPath",
                    str(fake_fast_check_path),
                    "-GovernanceFullCheckPath",
                    str(fake_full_check_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["milestone_gate_mode"], "full")
            self.assertEqual(payload["milestone_gate_mode_source"], "auto")
            self.assertEqual(payload["milestone_gate_mode_reason"], "release_candidate_full")
            self.assertEqual(payload["release_candidate"], True)
            self.assertEqual(payload["failure_count"], 0)
            for result in payload["results"]:
                self.assertEqual(result["milestone_gate_mode"], "full")
                self.assertEqual(result["milestone_gate_mode_source"], "auto")
                self.assertEqual(result["milestone_gate_mode_reason"], "release_candidate_full")
                self.assertEqual(result["auto_commit_commit_hash"], "fake-commit-hash")

    def test_runtime_flow_preset_all_targets_runtime_flow_timeout_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_a = workspace / "repo-a"
            _write_json(
                repo_a / ".governed-ai" / "repo-profile.json",
                {
                    "repo_id": "repo-a",
                    "required_entrypoint_policy": {"current_mode": "advisory"},
                    "auto_commit_policy": {"enabled": False},
                },
            )

            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "catalog_id": "test",
                    "targets": {
                        "repo-a": {
                            "attachment_root": str(repo_a),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-a"),
                            "repo_id": "repo-a",
                            "display_name": "repo-a",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                            "contract_command": "python --version",
                        }
                    },
                },
            )

            slow_runtime_flow_path = workspace / "slow-runtime-flow.ps1"
            _write_fake_slow_runtime_flow_script(slow_runtime_flow_path)

            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "runtime-flow-preset.ps1"),
                    "-AllTargets",
                    "-FlowMode",
                    "daily",
                    "-Json",
                    "-CatalogPath",
                    str(catalog_path),
                    "-RuntimeFlowPath",
                    str(slow_runtime_flow_path),
                    "-RuntimeFlowTimeoutSeconds",
                    "1",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["failure_count"], 1)
            self.assertEqual(payload["results"][0]["flow_exit_code"], 124)
            self.assertEqual(payload["results"][0]["flow_timed_out"], True)

    def test_runtime_flow_preset_all_targets_batch_timeout_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_a = workspace / "repo-a"
            repo_b = workspace / "repo-b"
            for repo in (repo_a, repo_b):
                _write_json(
                    repo / ".governed-ai" / "repo-profile.json",
                    {
                        "repo_id": repo.name,
                        "required_entrypoint_policy": {"current_mode": "advisory"},
                        "auto_commit_policy": {"enabled": False},
                    },
                )

            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "catalog_id": "test",
                    "targets": {
                        "repo-a": {
                            "attachment_root": str(repo_a),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-a"),
                            "repo_id": "repo-a",
                            "display_name": "repo-a",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                            "contract_command": "python --version",
                        },
                        "repo-b": {
                            "attachment_root": str(repo_b),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-b"),
                            "repo_id": "repo-b",
                            "display_name": "repo-b",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                            "contract_command": "python --version",
                        },
                    },
                },
            )

            slow_runtime_flow_path = workspace / "slow-runtime-flow.ps1"
            _write_fake_slow_runtime_flow_script(slow_runtime_flow_path)

            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "runtime-flow-preset.ps1"),
                    "-AllTargets",
                    "-FlowMode",
                    "daily",
                    "-Json",
                    "-CatalogPath",
                    str(catalog_path),
                    "-RuntimeFlowPath",
                    str(slow_runtime_flow_path),
                    "-BatchTimeoutSeconds",
                    "1",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertNotEqual(completed.returncode, 0)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["batch_timed_out"], True)
            self.assertEqual(payload["target_count"], 1)

    def test_runtime_flow_preset_all_targets_apply_all_features_logs_stage_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_a = workspace / "repo-a"
            repo_b = workspace / "repo-b"
            for repo in (repo_a, repo_b):
                _write_json(
                    repo / ".governed-ai" / "repo-profile.json",
                    {
                        "repo_id": repo.name,
                        "required_entrypoint_policy": {"current_mode": "advisory"},
                        "auto_commit_policy": {"enabled": False},
                    },
                )

            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "catalog_id": "test",
                    "targets": {
                        "repo-a": {
                            "attachment_root": str(repo_a),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-a"),
                            "repo_id": "repo-a",
                            "display_name": "repo-a",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                            "contract_command": "python --version",
                        },
                        "repo-b": {
                            "attachment_root": str(repo_b),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-b"),
                            "repo_id": "repo-b",
                            "display_name": "repo-b",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                            "contract_command": "python --version",
                        },
                    },
                },
            )

            baseline_path = workspace / "target-repo-governance-baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-04-23.1",
                    "required_profile_overrides": {
                        "required_entrypoint_policy": {"current_mode": "targeted_enforced"},
                        "auto_commit_policy": {"enabled": True, "on": ["milestone"]},
                    },
                },
            )

            fake_runtime_flow_path = workspace / "fake-runtime-flow.ps1"
            _write_fake_runtime_flow_script(fake_runtime_flow_path)
            fake_full_check_path = workspace / "fake-full-check.ps1"
            _write_fake_full_check_script(fake_full_check_path)

            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "runtime-flow-preset.ps1"),
                    "-AllTargets",
                    "-ApplyAllFeatures",
                    "-FlowMode",
                    "daily",
                    "-MilestoneTag",
                    "milestone",
                    "-CatalogPath",
                    str(catalog_path),
                    "-GovernanceBaselinePath",
                    str(baseline_path),
                    "-RuntimeFlowPath",
                    str(fake_runtime_flow_path),
                    "-GovernanceFullCheckPath",
                    str(fake_full_check_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("batch-progress: target=repo-a stage=target status=start", completed.stdout)
            self.assertIn("batch-progress: target=repo-a stage=runtime_flow status=start", completed.stdout)
            self.assertIn("batch-progress: target=repo-a stage=milestone_commit status=pass", completed.stdout)
            self.assertIn("batch-progress: target=repo-b stage=target status=pass", completed.stdout)

    def test_runtime_flow_preset_single_target_prunes_target_repo_runs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_a = workspace / "repo-a"
            _write_json(
                repo_a / ".governed-ai" / "repo-profile.json",
                {
                    "repo_id": "repo-a",
                    "required_entrypoint_policy": {"current_mode": "advisory"},
                    "auto_commit_policy": {"enabled": False},
                },
            )

            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "catalog_id": "test",
                    "targets": {
                        "repo-a": {
                            "attachment_root": str(repo_a),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-a"),
                            "repo_id": "repo-a",
                            "display_name": "repo-a",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                            "contract_command": "python --version",
                        }
                    },
                },
            )

            fake_runtime_flow_path = workspace / "fake-runtime-flow.ps1"
            _write_fake_runtime_flow_script(fake_runtime_flow_path)

            runs_root = workspace / "target-repo-runs"
            _write_json(runs_root / "repo-a-onboard-20260101010101.json", {"id": "onboard"})
            _write_json(runs_root / "repo-a-daily-20260102020202.json", {"id": "daily-old"})
            _write_json(runs_root / "repo-a-daily-20260103030303.json", {"id": "daily-new"})
            _write_json(runs_root / "summary-active-targets-latest.json", {"summary": "keep"})

            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "runtime-flow-preset.ps1"),
                    "-Target",
                    "repo-a",
                    "-FlowMode",
                    "daily",
                    "-Mode",
                    "quick",
                    "-Json",
                    "-CatalogPath",
                    str(catalog_path),
                    "-RuntimeFlowPath",
                    str(fake_runtime_flow_path),
                    "-PruneTargetRepoRuns",
                    "-PruneRunsRoot",
                    str(runs_root),
                    "-PruneKeepDays",
                    "0",
                    "-PruneKeepLatestPerTarget",
                    "1",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["overall_status"], "pass")
            self.assertEqual(payload["flow_mode"], "daily")
            self.assertIn("prune_target_repo_runs", payload)
            self.assertEqual(payload["prune_target_repo_runs"]["status"], "pass")
            self.assertEqual(payload["prune_target_repo_runs"]["delete_candidates"], 2)
            self.assertEqual(payload["prune_target_repo_runs"]["deleted"], 2)
            self.assertFalse((runs_root / "repo-a-onboard-20260101010101.json").exists())
            self.assertFalse((runs_root / "repo-a-daily-20260102020202.json").exists())
            self.assertTrue((runs_root / "repo-a-daily-20260103030303.json").exists())
            self.assertTrue((runs_root / "summary-active-targets-latest.json").exists())


if __name__ == "__main__":
    unittest.main()
