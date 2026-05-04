import json
import subprocess
import tempfile
import time
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


def _write_fake_runtime_flow_requires_synced_profile_script(path: Path) -> None:
    script = """param(
  [string]$AttachmentRoot = "",
  [string]$FlowMode = "daily",
  [switch]$Json
)

$profilePath = Join-Path $AttachmentRoot ".governed-ai\\repo-profile.json"
$profile = Get-Content -LiteralPath $profilePath -Raw | ConvertFrom-Json
$mode = [string]$profile.required_entrypoint_policy.current_mode
if ($mode -ne "targeted_enforced") {
  if ($Json) {
    @{
      exit_code = 9
      overall_status = "fail"
      reason = "profile_not_synced"
      current_mode = $mode
    } | ConvertTo-Json -Depth 8
  }
  exit 9
}

if ($Json) {
  @{
    exit_code = 0
    overall_status = "pass"
    flow_mode = $FlowMode
    current_mode = $mode
  } | ConvertTo-Json -Depth 8
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
  [switch]$DisableAutoCommit,
  [switch]$Json
)

if ($Json) {
  Write-Host "fake-full-check gate log before json"
  $autoCommit = if ($DisableAutoCommit) {
    [ordered]@{
      status = "skipped"
      reason = "disabled_by_caller"
      commit_hash = ""
      commit_message = ""
      trigger = $null
      milestone_tag = $MilestoneTag
    }
  }
  else {
    [ordered]@{
      status = "committed"
      reason = "ok"
      commit_hash = "fake-commit-hash"
      commit_message = ("自动提交：fake-repo 里程碑 {0} 门禁通过 2026-04-23 00:00:00 +08:00" -f $MilestoneTag)
      trigger = "milestone"
      milestone_tag = $MilestoneTag
    }
  }
  @(
    [ordered]@{
      exit_code = 0
      summary = [ordered]@{
        mode = "full"
        repo_profile_path = $RepoProfilePath
        working_directory = $WorkingDirectory
        gate_timeout_seconds = $GateTimeoutSeconds
        auto_commit = $autoCommit
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
  [switch]$DisableAutoCommit,
  [switch]$Json
)

if ($Json) {
  Write-Host "fake-fast-check gate log before json"
  $autoCommit = if ($DisableAutoCommit) {
    [ordered]@{
      status = "skipped"
      reason = "disabled_by_caller"
      commit_hash = ""
      commit_message = ""
      trigger = $null
      milestone_tag = $MilestoneTag
    }
  }
  else {
    [ordered]@{
      status = "committed"
      reason = "ok"
      commit_hash = "fake-fast-commit-hash"
      commit_message = ("自动提交：fake-repo 快速里程碑 {0} 门禁通过 2026-04-24 00:00:00 +08:00" -f $MilestoneTag)
      trigger = "milestone"
      milestone_tag = $MilestoneTag
    }
  }
  @(
    [ordered]@{
      exit_code = 0
      summary = [ordered]@{
        mode = "fast"
        repo_profile_path = $RepoProfilePath
        working_directory = $WorkingDirectory
        gate_timeout_seconds = $GateTimeoutSeconds
        auto_commit = $autoCommit
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


def _write_fake_fast_check_marker_script(path: Path, marker_path: Path, exit_code: int) -> None:
    marker = str(marker_path).replace("'", "''")
    script = f"""param(
  [string]$RepoProfilePath = "",
  [string]$WorkingDirectory = "",
  [string]$MilestoneTag = "",
  [int]$GateTimeoutSeconds = 0,
  [switch]$ContinueOnError,
  [switch]$DisableAutoCommit,
  [switch]$Json
)

Set-Content -LiteralPath '{marker}' -Value 'ran' -Encoding UTF8
if ($Json) {{
  Write-Host "fake-fast-check marker log before json"
  $autoCommit = if ($DisableAutoCommit) {{
    [ordered]@{{
      status = "skipped"
      reason = "disabled_by_caller"
      commit_hash = ""
      commit_message = ""
      trigger = $null
      milestone_tag = $MilestoneTag
    }}
  }}
  else {{
    [ordered]@{{
      status = "committed"
      reason = "ok"
      commit_hash = "fake-fast-commit-hash"
      commit_message = ("自动提交：fake-repo 快速里程碑 {{0}} 门禁通过 2026-04-24 00:00:00 +08:00" -f $MilestoneTag)
      trigger = "milestone"
      milestone_tag = $MilestoneTag
    }}
  }}
  [ordered]@{{
    exit_code = {exit_code}
    summary = [ordered]@{{
      mode = "fast"
      repo_profile_path = $RepoProfilePath
      working_directory = $WorkingDirectory
      gate_timeout_seconds = $GateTimeoutSeconds
      auto_commit = $autoCommit
    }}
  }} | ConvertTo-Json -Depth 20
}}
exit {exit_code}
"""
    path.write_text(script, encoding="utf-8")


def _write_fake_slow_runtime_flow_script(path: Path) -> None:
    script = """param(
  [switch]$Json
)

Start-Sleep -Milliseconds 1500
if ($Json) {
  @{ exit_code = 0; overall_status = "pass" } | ConvertTo-Json -Depth 8
}
else {
  Write-Host "slow-flow-pass"
}
exit 0
"""
    path.write_text(script, encoding="utf-8")


def _init_clean_git_repo(repo: Path) -> None:
    subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True, text=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Runtime Test",
            "-c",
            "user.email=runtime-test@example.invalid",
            "commit",
            "-m",
            "init",
        ],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )


class RuntimeFlowPresetScriptTests(unittest.TestCase):
    def test_runtime_flow_preset_help_does_not_run_default_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            marker_path = Path(tmp_dir) / "runtime-flow-ran.txt"
            fake_runtime_flow_path = Path(tmp_dir) / "runtime-flow.ps1"
            fake_runtime_flow_path.write_text(
                f"Set-Content -LiteralPath '{marker_path}' -Value ran\nexit 99\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(ROOT / "scripts" / "runtime-flow-preset.ps1"),
                    "-Help",
                    "-RuntimeFlowPath",
                    str(fake_runtime_flow_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("Usage:", completed.stdout)
            self.assertIn("-ListTargets", completed.stdout)
            self.assertFalse(marker_path.exists())

    def test_runtime_flow_preset_list_targets_json_uses_catalog_loader(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_a = workspace / "repo-a"
            repo_b = workspace / "repo-b"
            repo_a.mkdir()
            repo_b.mkdir()
            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "catalog_id": "test",
                    "targets": {
                        "repo-b": {
                            "attachment_root": str(repo_b),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-b"),
                            "repo_id": "repo-b",
                            "display_name": "repo-b",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                        },
                        "repo-a": {
                            "attachment_root": str(repo_a),
                            "attachment_runtime_state_root": str(workspace / "state" / "repo-a"),
                            "repo_id": "repo-a",
                            "display_name": "repo-a",
                            "primary_language": "python",
                            "build_command": "python --version",
                            "test_command": "python --version",
                        },
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
                    "-ListTargets",
                    "-Json",
                    "-CatalogPath",
                    str(catalog_path),
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
            self.assertEqual(Path(payload["catalog_path"]), catalog_path)
            self.assertEqual(payload["targets"], ["repo-a", "repo-b"])

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
                            "quick_test_command": "python -m unittest tests.test_fast",
                            "quick_test_reason": "Focused fast regression slice.",
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
                            "quick_test_skip_reason": "Full test command is already minimal.",
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
            runs_root = workspace / "target-repo-runs"
            _write_json(
                runs_root / "repo-a-daily-20260101000000.json",
                {
                    "overall_status": "pass",
                    "runtime_check": {"payload": {"summary": {"overall_status": "pass"}}},
                },
            )
            _write_json(runs_root / "effect-report-repo-a.json", {"target": "repo-a", "stale": True})

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
                    "-ExportTargetRepoRuns",
                    "-PruneRunsRoot",
                    str(runs_root),
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
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["all_targets"], True)
            self.assertEqual(payload["failure_count"], 0)
            self.assertEqual(payload["target_count"], 2)
            self.assertEqual(len(payload["exported_target_repo_runs"]), 2)
            self.assertEqual(payload["target_repo_speed_kpi"]["status"], "pass")
            self.assertEqual(payload["target_repo_speed_kpi"]["latest"]["status"], "pass")
            self.assertEqual(payload["target_repo_speed_kpi"]["rolling"]["status"], "pass")
            self.assertEqual(payload["target_repo_effect_reports"]["status"], "pass")
            self.assertEqual(payload["target_repo_effect_reports"]["reports"][0]["target"], "repo-a")
            self.assertEqual(payload["outer_ai_recommendation_action"], "none")
            self.assertEqual(payload["outer_ai_recommendation_tasks"], [])
            sources = {result["target"]: result["governance_sync_quick_test_slice_source"] for result in payload["results"]}
            self.assertEqual(sources["repo-a"], "argument")
            self.assertEqual(sources["repo-b"], "argument_skip")
            for result in payload["results"]:
                self.assertEqual(result["governance_sync_status"], "pass")

            for repo in (repo_a, repo_b):
                profile = json.loads((repo / ".governed-ai" / "repo-profile.json").read_text(encoding="utf-8"))
                self.assertEqual(profile["required_entrypoint_policy"]["current_mode"], "targeted_enforced")
                self.assertEqual(profile["auto_commit_policy"]["enabled"], True)
            self.assertEqual(len(list(runs_root.glob("*-onboard-*.json"))), 2)
            self.assertTrue((runs_root / "kpi-latest.json").exists())
            self.assertTrue((runs_root / "kpi-rolling.json").exists())
            latest_kpi = json.loads((runs_root / "kpi-latest.json").read_text(encoding="utf-8"))
            self.assertEqual(latest_kpi["record_count"], 2)
            effect_report = json.loads((runs_root / "effect-report-repo-a.json").read_text(encoding="utf-8"))
            self.assertEqual(effect_report["report_kind"], "target_repo_reuse_effect_feedback")
            self.assertEqual(effect_report["target"], "repo-a")

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
                            "quick_test_command": "python -m unittest tests.test_fast",
                            "quick_test_reason": "Focused fast regression slice.",
                            "contract_command": "python --version",
                            "contract_commands": [
                                {
                                    "id": "contract:powershell-policy",
                                    "command": "python .governed-ai/verify-powershell-policy.py",
                                    "required": True,
                                },
                                {"id": "contract", "command": "python --version", "required": True},
                            ],
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
                encoding="utf-8",
                errors="replace",
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
                            "quick_test_command": "python -m unittest tests.test_fast",
                            "quick_test_reason": "Focused fast regression slice.",
                            "contract_command": "python --version",
                            "contract_commands": [
                                {
                                    "id": "contract:powershell-policy",
                                    "command": "python .governed-ai/verify-powershell-policy.py",
                                    "required": True,
                                },
                                {"id": "contract", "command": "python --version", "required": True},
                            ],
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
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["governance_baseline_sync"]["status"], "pass")
            profile = json.loads((repo_a / ".governed-ai" / "repo-profile.json").read_text(encoding="utf-8"))
            self.assertEqual(profile["required_entrypoint_policy"]["current_mode"], "targeted_enforced")
            self.assertEqual(profile["auto_commit_policy"]["enabled"], True)
            self.assertEqual(
                [gate["id"] for gate in profile["contract_commands"]],
                ["contract:powershell-policy", "contract"],
            )

    def test_runtime_flow_preset_apply_coding_speed_profile_alias_uses_baseline_sync(self) -> None:
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
                            "test_command": "python -m unittest discover",
                            "quick_test_command": "python -m unittest tests.test_fast",
                            "quick_test_reason": "Focused fast regression slice.",
                            "contract_command": "python -m unittest tests.test_contract",
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
                    "sync_revision": "2026-04-26.9",
                    "target_repo_speed_profile_policy": {
                        "enabled": True,
                        "materialize_quick_gate_commands": True,
                        "materialize_full_gate_commands": True,
                        "preserve_existing_gate_commands": True,
                        "refresh_existing_derived_gate_commands": True,
                        "default_gate_timeout_seconds": 90,
                        "quick_gate_timeout_seconds": 30,
                        "full_gate_timeout_seconds": 60,
                    },
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
                    "-AllTargets",
                    "-ApplyCodingSpeedProfile",
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
            self.assertTrue(payload["apply_coding_speed_profile"])
            self.assertTrue(payload["apply_feature_baseline_only"])
            self.assertFalse(payload["apply_governance_baseline_only"])
            self.assertTrue(payload["governance_baseline_sync_active"])
            self.assertEqual(payload["failure_count"], 0)
            self.assertEqual(payload["results"][0]["flow_exit_code"], 0)
            self.assertEqual(payload["results"][0]["governance_sync_status"], "pass")
            self.assertEqual(
                payload["results"][0]["governance_sync_speed_changed"],
                ["quick_gate_commands", "full_gate_commands", "gate_timeout_seconds"],
            )

            profile = json.loads((repo_a / ".governed-ai" / "repo-profile.json").read_text(encoding="utf-8"))
            self.assertEqual(profile["quick_gate_commands"][0]["command"], "python -m unittest tests.test_fast")
            self.assertEqual(profile["quick_gate_commands"][0]["description"], "Focused fast regression slice.")
            self.assertEqual(profile["full_gate_commands"][1]["command"], "python -m unittest discover")

    def test_runtime_flow_preset_apply_governance_baseline_only_bootstraps_blank_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_a = workspace / "repo-a"
            repo_a.mkdir()
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
                            "quick_test_command": "python -m unittest tests.test_fast",
                            "quick_test_reason": "Focused fast regression slice.",
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
                    "sync_revision": "2026-04-26.1",
                    "target_repo_speed_profile_policy": {
                        "enabled": True,
                        "materialize_quick_gate_commands": True,
                        "materialize_full_gate_commands": True,
                        "preserve_existing_gate_commands": True,
                        "default_gate_timeout_seconds": 90,
                        "quick_gate_timeout_seconds": 30,
                        "full_gate_timeout_seconds": 60,
                    },
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
            self.assertEqual(
                payload["governance_baseline_sync"]["speed_changed"],
                ["quick_gate_commands", "full_gate_commands", "gate_timeout_seconds"],
            )
            self.assertEqual(payload["governance_baseline_sync"]["bootstrap"]["status"], "pass")
            self.assertEqual(
                payload["governance_baseline_sync"]["bootstrap"]["reason"],
                "repo_profile_bootstrapped",
            )
            profile = json.loads((repo_a / ".governed-ai" / "repo-profile.json").read_text(encoding="utf-8"))
            self.assertEqual(profile["repo_id"], "repo-a")
            self.assertEqual(profile["required_entrypoint_policy"]["current_mode"], "targeted_enforced")
            self.assertEqual(profile["auto_commit_policy"]["enabled"], True)
            self.assertEqual([gate["id"] for gate in profile["quick_gate_commands"]], ["test", "contract"])
            self.assertEqual(profile["quick_gate_commands"][0]["command"], "python -m unittest tests.test_fast")
            self.assertEqual(profile["quick_gate_commands"][0]["description"], "Focused fast regression slice.")
            self.assertEqual([gate["id"] for gate in profile["full_gate_commands"]], ["build"])
            self.assertEqual(profile["full_gate_commands"][0]["satisfies_gate_ids"], ["build", "test", "contract"])
            self.assertEqual(profile["gate_timeout_seconds"], 90)

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
                encoding="utf-8",
                errors="replace",
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
                encoding="utf-8",
                errors="replace",
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

    def test_runtime_flow_preset_apply_all_features_can_disable_milestone_auto_commit(self) -> None:
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
                    "sync_revision": "2026-05-04.3",
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
                    "-DisableMilestoneAutoCommit",
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
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertTrue(payload["apply_all_features"])
            self.assertTrue(payload["disable_milestone_auto_commit"])
            self.assertEqual(payload["failure_count"], 0)
            result = payload["results"][0]
            self.assertEqual(result["milestone_commit_status"], "pass")
            self.assertEqual(result["auto_commit_status"], "skipped")
            self.assertEqual(result["auto_commit_reason"], "disabled_by_caller")
            self.assertTrue(result["auto_commit_disabled_by_caller"])
            self.assertEqual(result["auto_commit_commit_hash"], "")

    def test_runtime_flow_preset_apply_all_features_syncs_baseline_before_daily_flow(self) -> None:
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
                    "sync_revision": "2026-05-03.1",
                    "required_profile_overrides": {
                        "required_entrypoint_policy": {"current_mode": "targeted_enforced"},
                        "auto_commit_policy": {"enabled": True, "on": ["milestone"]},
                    },
                },
            )

            fake_runtime_flow_path = workspace / "fake-runtime-flow-requires-synced-profile.ps1"
            _write_fake_runtime_flow_requires_synced_profile_script(fake_runtime_flow_path)
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
                    "-Target",
                    "repo-a",
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
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["overall_status"], "pass")
            self.assertEqual(payload["current_mode"], "targeted_enforced")
            self.assertEqual(payload["governance_baseline_sync"]["status"], "pass")
            self.assertEqual(
                payload["governance_baseline_sync"]["changed"],
                ["required_entrypoint_policy", "auto_commit_policy"],
            )
            self.assertGreaterEqual(payload["governance_baseline_sync"]["duration_ms"], 0)

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

    def test_runtime_flow_preset_auto_fast_skips_clean_milestone_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_a = workspace / "repo-a"
            _write_json(
                repo_a / ".governed-ai" / "repo-profile.json",
                {
                    "repo_id": "repo-a",
                    "display_name": "repo-a",
                    "primary_language": "python",
                    "build_commands": [{"id": "build", "command": "python --version", "required": True}],
                    "test_commands": [{"id": "test", "command": "python --version", "required": True}],
                    "contract_commands": [{"id": "contract", "command": "python --version", "required": True}],
                    "required_entrypoint_policy": {"current_mode": "targeted_enforced"},
                    "auto_commit_policy": {"enabled": True, "on": ["milestone"]},
                },
            )
            _init_clean_git_repo(repo_a)

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
                            "quick_test_skip_reason": "Full test command is already tiny.",
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
                    "sync_revision": "2026-04-26.9",
                    "required_profile_overrides": {
                        "required_entrypoint_policy": {"current_mode": "targeted_enforced"},
                        "auto_commit_policy": {"enabled": True, "on": ["milestone"]},
                    },
                },
            )

            fake_runtime_flow_path = workspace / "fake-runtime-flow.ps1"
            _write_fake_runtime_flow_script(fake_runtime_flow_path)
            marker_path = workspace / "fast-gate-ran.txt"
            fake_fast_check_path = workspace / "fake-fast-check.ps1"
            _write_fake_fast_check_marker_script(fake_fast_check_path, marker_path, exit_code=9)

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
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["milestone_gate_mode"], "fast")
            self.assertEqual(payload["clean_milestone_gate_skip_enabled"], True)
            self.assertEqual(payload["clean_milestone_gate_skip_source"], "auto")
            self.assertEqual(payload["failure_count"], 0)
            self.assertFalse(marker_path.exists(), completed.stdout)
            result = payload["results"][0]
            self.assertEqual(result["milestone_commit_status"], "skipped")
            self.assertEqual(result["milestone_commit_reason"], "clean_target_no_pending_changes")
            self.assertEqual(result["milestone_gate_skipped"], True)
            self.assertEqual(result["auto_commit_reason"], "no_pending_changes")

    def test_runtime_flow_preset_auto_fast_runs_gate_when_sync_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_a = workspace / "repo-a"
            _write_json(
                repo_a / ".governed-ai" / "repo-profile.json",
                {
                    "repo_id": "repo-a",
                    "display_name": "repo-a",
                    "primary_language": "python",
                    "build_commands": [{"id": "build", "command": "python --version", "required": True}],
                    "test_commands": [{"id": "test", "command": "python --version", "required": True}],
                    "contract_commands": [{"id": "contract", "command": "python --version", "required": True}],
                    "required_entrypoint_policy": {"current_mode": "advisory"},
                    "auto_commit_policy": {"enabled": False},
                },
            )
            _init_clean_git_repo(repo_a)

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
                            "quick_test_skip_reason": "Full test command is already tiny.",
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
                    "sync_revision": "2026-04-26.9",
                    "required_profile_overrides": {
                        "required_entrypoint_policy": {"current_mode": "targeted_enforced"},
                        "auto_commit_policy": {"enabled": True, "on": ["milestone"]},
                    },
                },
            )

            fake_runtime_flow_path = workspace / "fake-runtime-flow.ps1"
            _write_fake_runtime_flow_script(fake_runtime_flow_path)
            marker_path = workspace / "fast-gate-ran.txt"
            fake_fast_check_path = workspace / "fake-fast-check.ps1"
            _write_fake_fast_check_marker_script(fake_fast_check_path, marker_path, exit_code=0)

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
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["failure_count"], 0)
            self.assertTrue(marker_path.exists(), completed.stdout)
            result = payload["results"][0]
            self.assertEqual(result["governance_sync_changed"], ["required_entrypoint_policy", "auto_commit_policy"])
            self.assertEqual(result["milestone_commit_status"], "pass")
            self.assertEqual(result["milestone_gate_skipped"], False)
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

    def test_runtime_flow_preset_all_targets_json_reports_elapsed_without_batch_timeout(self) -> None:
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
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertGreaterEqual(payload["batch_elapsed_seconds"], 1)
            self.assertGreaterEqual(payload["results"][0]["target_duration_ms"], 1000)
            self.assertGreaterEqual(payload["results"][0]["flow_duration_ms"], 1000)

    def test_runtime_flow_preset_all_targets_json_supports_target_parallelism(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            targets = {}
            for name in ("repo-a", "repo-b", "repo-c"):
                repo = workspace / name
                _write_json(
                    repo / ".governed-ai" / "repo-profile.json",
                    {
                        "repo_id": name,
                        "required_entrypoint_policy": {"current_mode": "advisory"},
                        "auto_commit_policy": {"enabled": False},
                    },
                )
                targets[name] = {
                    "attachment_root": str(repo),
                    "attachment_runtime_state_root": str(workspace / "state" / name),
                    "repo_id": name,
                    "display_name": name,
                    "primary_language": "python",
                    "build_command": "python --version",
                    "test_command": "python --version",
                    "contract_command": "python --version",
                }

            catalog_path = workspace / "catalog.json"
            _write_json(
                catalog_path,
                {
                    "schema_version": "1.0",
                    "catalog_id": "test",
                    "targets": targets,
                },
            )

            slow_runtime_flow_path = workspace / "slow-runtime-flow.ps1"
            _write_fake_slow_runtime_flow_script(slow_runtime_flow_path)

            started = time.perf_counter()
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
                    "-TargetParallelism",
                    "3",
                    "-BatchTimeoutSeconds",
                    "30",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            elapsed = time.perf_counter() - started

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["target_count"], 3)
            self.assertEqual(payload["failure_count"], 0)
            self.assertGreaterEqual(payload["batch_elapsed_seconds"], 1)
            self.assertLess(elapsed, 8.0)
            self.assertEqual({item["target"] for item in payload["results"]}, set(targets))
            self.assertTrue(all(item["target_duration_ms"] > 0 for item in payload["results"]))
            self.assertTrue(all(item["flow_duration_ms"] > 0 for item in payload["results"]))

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

    def test_runtime_flow_preset_single_target_dry_runs_managed_asset_prune_and_uninstall(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_a = workspace / "repo-a"
            source = workspace / "templates" / "managed.py"
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("print('managed')\n", encoding="utf-8")
            (repo_a / ".governed-ai").mkdir(parents=True, exist_ok=True)
            (repo_a / ".governed-ai" / "old.py").write_text("print('managed')\n", encoding="utf-8")
            (repo_a / ".governed-ai" / "managed.py").write_text("print('managed')\n", encoding="utf-8")
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
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "required_managed_files": [
                        {"path": ".governed-ai/managed.py", "source": str(source), "management_mode": "block_on_drift"}
                    ],
                    "generated_managed_files": [],
                    "retired_managed_files": [
                        {
                            "path": ".governed-ai/old.py",
                            "previous_source": str(source),
                            "retire_reason": "obsolete",
                            "replacement": ".governed-ai/managed.py",
                            "safe_delete_when": ["target_sha256_matches_previous_sha256", "no_active_references"],
                            "backup_required": True,
                        }
                    ],
                },
            )
            fake_runtime_flow_path = workspace / "fake-runtime-flow.ps1"
            _write_fake_runtime_flow_script(fake_runtime_flow_path)
            runs_root = workspace / "target-repo-runs"

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
                    "-GovernanceBaselinePath",
                    str(baseline_path),
                    "-PruneRetiredManagedFiles",
                    "-UninstallGovernance",
                    "-ExportTargetRepoRuns",
                    "-PruneRunsRoot",
                    str(runs_root),
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertIn("prune_retired_managed_files", payload)
            self.assertIn("uninstall_governance", payload)
            self.assertEqual(payload["prune_retired_managed_files"]["delete_candidates"], 1)
            self.assertEqual(payload["uninstall_governance"]["delete_candidates"], 1)
            self.assertEqual(payload["prune_retired_managed_files"]["dry_run"], True)
            self.assertEqual(payload["prune_retired_managed_files"]["operation_type"], "retired_managed_files_cleanup")
            self.assertEqual(
                payload["prune_retired_managed_files"]["deletion_policy"],
                "delete_only_registered_hash_matched_unreferenced_retired_managed_files",
            )
            self.assertEqual(payload["prune_retired_managed_files"]["manifest_path"], "")
            self.assertEqual(payload["uninstall_governance"]["dry_run"], True)
            self.assertEqual(payload["prune_retired_managed_files"]["delete_candidate_items"][0]["path"], ".governed-ai/old.py")
            self.assertEqual(payload["uninstall_governance"]["delete_candidate_items"][0]["path"], ".governed-ai/managed.py")
            self.assertEqual(payload["prune_retired_managed_files"]["deleted_files"], [])
            self.assertEqual(payload["uninstall_governance"]["deleted_files"], [])
            exported_files = list(runs_root.glob("repo-a-daily-*.json"))
            self.assertEqual(len(exported_files), 1)
            exported = json.loads(exported_files[0].read_text(encoding="utf-8-sig"))
            self.assertEqual(exported["prune_retired_managed_files"]["dry_run"], True)
            self.assertEqual(exported["uninstall_governance"]["dry_run"], True)
            self.assertEqual(
                exported["prune_retired_managed_files"]["operation_type"],
                "retired_managed_files_cleanup",
            )
            self.assertEqual(exported["uninstall_governance"]["delete_candidate_items"][0]["path"], ".governed-ai/managed.py")
            self.assertTrue((repo_a / ".governed-ai" / "old.py").exists())
            self.assertTrue((repo_a / ".governed-ai" / "managed.py").exists())

    def test_runtime_flow_preset_apply_all_features_defaults_to_retired_managed_file_apply(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_a = workspace / "repo-a"
            source = workspace / "templates" / "managed.py"
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("print('managed')\n", encoding="utf-8")
            (repo_a / ".governed-ai").mkdir(parents=True, exist_ok=True)
            (repo_a / ".governed-ai" / "old.py").write_text("print('managed')\n", encoding="utf-8")
            (repo_a / ".governed-ai" / "managed.py").write_text("print('managed')\n", encoding="utf-8")
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
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-05-02.2",
                    "required_profile_overrides": {
                        "required_entrypoint_policy": {"current_mode": "targeted_enforced"},
                        "auto_commit_policy": {"enabled": True, "on": ["milestone"]},
                    },
                    "required_managed_files": [
                        {"path": ".governed-ai/managed.py", "source": str(source), "management_mode": "block_on_drift"}
                    ],
                    "generated_managed_files": [],
                    "retired_managed_files": [
                        {
                            "path": ".governed-ai/old.py",
                            "previous_source": str(source),
                            "retire_reason": "obsolete",
                            "replacement": ".governed-ai/managed.py",
                            "safe_delete_when": ["target_sha256_matches_previous_sha256", "no_active_references"],
                            "backup_required": True,
                        }
                    ],
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
                    "-Mode",
                    "quick",
                    "-Json",
                    "-CatalogPath",
                    str(catalog_path),
                    "-RuntimeFlowPath",
                    str(fake_runtime_flow_path),
                    "-GovernanceBaselinePath",
                    str(baseline_path),
                    "-GovernanceFullCheckPath",
                    str(fake_full_check_path),
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
            self.assertTrue(payload["apply_all_features"])
            self.assertTrue(payload["prune_retired_managed_files_active"])
            self.assertTrue(payload["apply_managed_asset_removal"])
            result = payload["results"][0]
            self.assertEqual(result["prune_retired_managed_files"]["apply"], True)
            self.assertEqual(result["prune_retired_managed_files"]["deleted"], 1)
            self.assertFalse((repo_a / ".governed-ai" / "old.py").exists())

    def test_runtime_flow_preset_apply_all_features_disable_managed_asset_removal_is_dry_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_a = workspace / "repo-a"
            source = workspace / "templates" / "managed.py"
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("print('managed')\n", encoding="utf-8")
            (repo_a / ".governed-ai").mkdir(parents=True, exist_ok=True)
            (repo_a / ".governed-ai" / "old.py").write_text("print('managed')\n", encoding="utf-8")
            (repo_a / ".governed-ai" / "managed.py").write_text("print('managed')\n", encoding="utf-8")
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
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "schema_version": "1.0",
                    "baseline_id": "test",
                    "sync_revision": "2026-05-02.2",
                    "required_profile_overrides": {
                        "required_entrypoint_policy": {"current_mode": "targeted_enforced"},
                        "auto_commit_policy": {"enabled": True, "on": ["milestone"]},
                    },
                    "required_managed_files": [
                        {"path": ".governed-ai/managed.py", "source": str(source), "management_mode": "block_on_drift"}
                    ],
                    "generated_managed_files": [],
                    "retired_managed_files": [
                        {
                            "path": ".governed-ai/old.py",
                            "previous_source": str(source),
                            "retire_reason": "obsolete",
                            "replacement": ".governed-ai/managed.py",
                            "safe_delete_when": ["target_sha256_matches_previous_sha256", "no_active_references"],
                            "backup_required": True,
                        }
                    ],
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
                    "-DisableManagedAssetRemoval",
                    "-FlowMode",
                    "daily",
                    "-Mode",
                    "quick",
                    "-Json",
                    "-CatalogPath",
                    str(catalog_path),
                    "-RuntimeFlowPath",
                    str(fake_runtime_flow_path),
                    "-GovernanceBaselinePath",
                    str(baseline_path),
                    "-GovernanceFullCheckPath",
                    str(fake_full_check_path),
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                cwd=ROOT,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
            payload = json.loads(completed.stdout)
            self.assertTrue(payload["prune_retired_managed_files_active"])
            self.assertFalse(payload["apply_managed_asset_removal"])
            result = payload["results"][0]
            self.assertEqual(result["prune_retired_managed_files"]["dry_run"], True)
            self.assertEqual(result["prune_retired_managed_files"]["delete_candidates"], 1)
            self.assertTrue((repo_a / ".governed-ai" / "old.py").exists())

    def test_runtime_flow_preset_blocks_managed_asset_apply_after_flow_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            repo_a = workspace / "repo-a"
            source = workspace / "templates" / "managed.py"
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("print('managed')\n", encoding="utf-8")
            (repo_a / ".governed-ai").mkdir(parents=True, exist_ok=True)
            (repo_a / ".governed-ai" / "old.py").write_text("print('managed')\n", encoding="utf-8")
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
            baseline_path = workspace / "baseline.json"
            _write_json(
                baseline_path,
                {
                    "required_managed_files": [],
                    "generated_managed_files": [],
                    "retired_managed_files": [
                        {
                            "path": ".governed-ai/old.py",
                            "previous_source": str(source),
                            "retire_reason": "obsolete",
                            "replacement": ".governed-ai/managed.py",
                            "safe_delete_when": ["target_sha256_matches_previous_sha256", "no_active_references"],
                            "backup_required": True,
                        }
                    ],
                },
            )
            fake_runtime_flow_path = workspace / "fake-runtime-flow.ps1"
            fake_runtime_flow_path.write_text("Write-Host 'fake flow failed'\nexit 7\n", encoding="utf-8")

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
                    "-GovernanceBaselinePath",
                    str(baseline_path),
                    "-PruneRetiredManagedFiles",
                    "-ApplyManagedAssetRemoval",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            self.assertEqual(completed.returncode, 1, completed.stderr)
            payload = json.loads(completed.stdout)
            result = payload["results"][0] if "results" in payload else payload
            self.assertEqual(result["flow_exit_code"], 7)
            self.assertEqual(result["prune_retired_managed_files"]["status"], "blocked")
            self.assertEqual(
                result["prune_retired_managed_files"]["reason"],
                "target_flow_failed_before_managed_asset_apply",
            )
            self.assertEqual(result["prune_retired_managed_files"]["deleted"], 0)
            self.assertTrue((repo_a / ".governed-ai" / "old.py").exists())


if __name__ == "__main__":
    unittest.main()
