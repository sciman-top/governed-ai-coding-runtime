import json
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "verify-target-project-rules.py"
SCHEMA = ROOT / "schemas" / "jsonschema" / "target-project-rule-coordination.schema.json"
VERIFY_REPO = ROOT / "scripts" / "verify-repo.ps1"
WORKFLOW_BYTES = b"name: Agent Rule Contract\n# agent-rule-contract-ci: 2.1\n"


def _workflow_sha256(raw: bytes) -> str:
    normalized = raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _project_body(*, anchor: str = "runtime/main.py", reviewed_release: str = "9.55") -> str:
    return "\n".join(
        [
            "# AGENTS.md - pilot",
            "**项目契约**: 2.0",
            f"**全局规则复核**: {reviewed_release}",
            "",
            "## 1. 范围",
            "- 当前落点：pilot。",
            "- 目标归宿：保持仓库契约可执行。",
            "",
            "## A. 仓库事实",
            f"- `{anchor}` 是运行入口。",
            "",
            "## B. 执行与风险边界",
            "- 只修改当前任务范围。",
            "",
            "## C. 门禁",
            "- fixed order：`build -> test -> contract/invariant -> hotspot`。",
            "- `.github/workflows/agent-rule-contract.yml` 只验证规则契约，不替代产品门禁。",
            "",
            "## D. 证据与回滚",
            "- 证据：`docs/change-evidence/`。",
            "- 回滚：只回滚当前规则切片。",
            "",
        ]
    )


def _write_target(
    repo_root: Path,
    *,
    project_body: str | None = None,
    wrapper: bytes | None = b"@AGENTS.md\n",
    workflow: bytes | None = WORKFLOW_BYTES,
) -> None:
    repo_root.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "init", "--quiet", str(repo_root)],
        check=True,
        capture_output=True,
        text=True,
    )
    (repo_root / "AGENTS.md").write_text(project_body or _project_body(), encoding="utf-8")
    if wrapper is not None:
        (repo_root / "CLAUDE.md").write_bytes(wrapper)
    if workflow is not None:
        workflow_path = repo_root / ".github" / "workflows" / "agent-rule-contract.yml"
        workflow_path.parent.mkdir(parents=True, exist_ok=True)
        workflow_path.write_bytes(workflow)


def _coordination_payload(workspace_root: Path, *, reviewed_release: str = "9.55") -> dict:
    return {
        "schema_version": "2.3",
        "coordination_id": "target-project-rule-coordination",
        "rule_release": "9.55",
        "project_contract_version": "2.0",
        "workspace_root": str(workspace_root),
        "updated_on": "2026-07-10",
        "workspace_inventory": {
            "mode": "direct_git_roots",
            "excluded_directories": [
                "external",
                "governed-ai-coding-runtime",
                "physicist_chinese_poster_batch_tool",
                "文档",
            ],
            "unlisted_repository_policy": "block",
            "missing_allowlisted_repository_policy": "block_on_require_all",
        },
        "ci_contract": {
            "contract_id": "agent-rule-contract-ci",
            "version": "2.1",
            "workflow_hash_mode": "utf8_lf_v1",
            "workflow_sha256": _workflow_sha256(WORKFLOW_BYTES),
        },
        "targets": [
            {
                "repo_id": "pilot",
                "repo_path": "pilot",
                "github_repository": "example/pilot",
                "github_visibility": "public",
                "aggregate_mode": "checkout",
                "ci_workflow_path": ".github/workflows/agent-rule-contract.yml",
                "tools": ["codex", "claude"],
                "project_common_rule": "AGENTS.md",
                "claude_wrapper_rule": "CLAUDE.md",
                "claude_wrapper_mode": "import_only",
                "project_contract_version": "2.0",
                "reviewed_global_release": reviewed_release,
                "required_anchors": ["runtime/main.py"],
                "evidence_path": "docs/change-evidence/",
                "budgets": {
                    "project_max_bytes": 16384,
                    "project_max_lines": 120,
                    "wrapper_max_lines": 20,
                    "effective_context_warning_lines": 180,
                },
                "coordination_mode": "audit_only",
            }
        ],
    }


def _run(coordination_path: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--coordination-path", str(coordination_path), *extra],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


class VerifyTargetProjectRulesTests(unittest.TestCase):
    def test_schema_requires_explicit_wrapper_mode(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

        self.assertIn("claude_wrapper_mode", schema["$defs"]["target"]["required"])

    def test_schema_requires_ci_contract_and_target_ci_metadata(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

        self.assertEqual(schema["properties"]["schema_version"]["const"], "2.3")
        self.assertIn("ci_contract", schema["required"])
        self.assertIn("workspace_inventory", schema["required"])
        self.assertIn("workflow_hash_mode", schema["$defs"]["ci_contract"]["required"])
        self.assertIn("github_repository", schema["$defs"]["target"]["required"])
        self.assertIn("ci_workflow_path", schema["$defs"]["target"]["required"])

    def test_coordination_metadata_is_required(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "workspace"
            _write_target(workspace / "pilot")
            payload = _coordination_payload(workspace)
            payload.pop("workspace_root")
            payload.pop("updated_on")
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(json.dumps(payload), encoding="utf-8")

            completed = _run(coordination_path, "--require-all")

        self.assertEqual(completed.returncode, 1)
        findings = json.loads(completed.stdout)["blocking_findings"]
        self.assertIn("workspace_root_missing", findings)
        self.assertIn("updated_on_invalid:missing", findings)

    def test_control_contract_gate_wires_schema_and_target_audit(self) -> None:
        verifier = VERIFY_REPO.read_text(encoding="utf-8")
        contract_body = verifier.split("function Invoke-ContractChecks", 1)[1].split(
            "function Invoke-DependencyBaselineChecks", 1
        )[0]
        target_audit_body = verifier.split("function Invoke-TargetProjectRuleChecks", 1)[1].split(
            "function Invoke-PreChangeReviewChecks", 1
        )[0]

        self.assertIn("Invoke-TargetProjectRuleCoordinationSchemaCheck", verifier)
        self.assertIn("Invoke-TargetProjectRuleChecks", verifier)
        self.assertIn("Invoke-TargetProjectRuleCoordinationSchemaCheck", contract_body)
        self.assertIn("Invoke-TargetProjectRuleChecks", contract_body)
        self.assertIn("GACR_TARGET_PROJECT_RULE_WORKSPACE_ROOT", target_audit_body)
        self.assertIn('"--workspace-root"', target_audit_body)
        self.assertIn('"--require-all"', target_audit_body)

    def test_v2_contract_passes_with_relative_repo_and_one_line_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "workspace"
            _write_target(workspace / "pilot")
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(
                json.dumps(_coordination_payload(workspace), ensure_ascii=False), encoding="utf-8"
            )

            completed = _run(coordination_path, "--require-all")

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["project_contract_version"], "2.0")
        self.assertEqual(payload["results"][0]["status"], "pass")
        self.assertEqual(payload["results"][0]["blocking_findings"], [])

    def test_cli_emits_json_when_stdout_uses_cp1252(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "workspace"
            _write_target(workspace / "pilot")
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(
                json.dumps(_coordination_payload(workspace), ensure_ascii=False), encoding="utf-8"
            )
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "cp1252"

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--coordination-path",
                    str(coordination_path),
                    "--require-all",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                env=env,
            )

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertIn("文档", json.dumps(payload, ensure_ascii=False))

    def test_workspace_root_override_supports_ci_checkout_layout(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "ci-workspace"
            _write_target(workspace / "pilot")
            payload = _coordination_payload(Path("D:/stale-local-workspace"))
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(json.dumps(payload), encoding="utf-8")

            completed = _run(
                coordination_path,
                "--workspace-root",
                str(workspace),
                "--require-all",
            )

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertEqual(json.loads(completed.stdout)["workspace_root"], str(workspace).replace("\\", "/"))

    def test_ci_workflow_hash_drift_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "workspace"
            _write_target(workspace / "pilot", workflow=b"name: drifted\n")
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(
                json.dumps(_coordination_payload(workspace)), encoding="utf-8"
            )

            completed = _run(coordination_path, "--require-all")

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertIn("ci_workflow_hash_mismatch", payload["results"][0]["blocking_findings"])

    def test_ci_workflow_hash_normalizes_crlf_to_lf(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "workspace"
            crlf_workflow = WORKFLOW_BYTES.replace(b"\n", b"\r\n")
            _write_target(workspace / "pilot", workflow=crlf_workflow)
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(
                json.dumps(_coordination_payload(workspace)), encoding="utf-8"
            )

            completed = _run(coordination_path, "--require-all")

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        details = json.loads(completed.stdout)["results"][0]["details"]
        self.assertEqual(details["ci_workflow_sha256"], _workflow_sha256(WORKFLOW_BYTES))
        self.assertEqual(details["ci_workflow_line_endings"], "crlf")

    def test_unlisted_direct_child_git_repository_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "workspace"
            _write_target(workspace / "pilot")
            _write_target(workspace / "unlisted")
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(
                json.dumps(_coordination_payload(workspace)), encoding="utf-8"
            )

            completed = _run(coordination_path, "--require-all")

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertIn("unlisted_workspace_repository:unlisted", payload["blocking_findings"])
        self.assertEqual(payload["workspace_inventory"]["discovered_repositories"], ["pilot", "unlisted"])

    def test_excluded_direct_child_git_repository_is_not_discovered(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "workspace"
            _write_target(workspace / "pilot")
            _write_target(workspace / "external")
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(
                json.dumps(_coordination_payload(workspace)), encoding="utf-8"
            )

            completed = _run(coordination_path, "--require-all")

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        inventory = json.loads(completed.stdout)["workspace_inventory"]
        self.assertEqual(inventory["discovered_repositories"], ["pilot"])

    def test_filtered_ci_audit_skips_workspace_inventory_comparison(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "workspace"
            _write_target(workspace / "pilot")
            _write_target(workspace / "unlisted")
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(
                json.dumps(_coordination_payload(workspace)), encoding="utf-8"
            )

            completed = _run(
                coordination_path,
                "--workspace-root",
                str(workspace),
                "--targets",
                "pilot",
                "--require-all",
            )

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        inventory = json.loads(completed.stdout)["workspace_inventory"]
        self.assertEqual(inventory["status"], "skipped")
        self.assertEqual(inventory["reason"], "target_filters")

    def test_allowlisted_directory_must_be_its_own_git_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "workspace"
            repo_root = workspace / "pilot"
            _write_target(repo_root)
            git_dir = repo_root / ".git"
            if git_dir.is_dir():
                for path in sorted(git_dir.rglob("*"), reverse=True):
                    if path.is_file():
                        path.unlink()
                    elif path.is_dir():
                        path.rmdir()
                git_dir.rmdir()
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(
                json.dumps(_coordination_payload(workspace)), encoding="utf-8"
            )

            completed = _run(coordination_path, "--require-all")

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertIn("target_not_git_root", payload["results"][0]["blocking_findings"])

    def test_na_contract_requires_recovery_condition(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "workspace"
            body = _project_body().replace(
                "- fixed order：`build -> test -> contract/invariant -> hotspot`。",
                "- fixed order：`build -> test -> contract/invariant -> hotspot`。\n"
                "- build：`gate_na`，`reason=docs`、`alternative_verification=parse`、"
                "`evidence_link=docs/evidence.md`、`expires_at=task_end`。",
            )
            _write_target(workspace / "pilot", project_body=body)
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(
                json.dumps(_coordination_payload(workspace)), encoding="utf-8"
            )

            completed = _run(coordination_path, "--require-all")

        self.assertEqual(completed.returncode, 1)
        findings = json.loads(completed.stdout)["results"][0]["blocking_findings"]
        self.assertIn("na_contract_fields_missing:recovery_condition", findings)

    def test_na_contract_rejects_similar_field_names_without_backticks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "workspace"
            body = _project_body().replace(
                "- fixed order：`build -> test -> contract/invariant -> hotspot`。",
                "- fixed order：`build -> test -> contract/invariant -> hotspot`。\n"
                "- build：gate_na，reasoning=docs、alternative_verification=parse、"
                "evidence_link=docs/evidence.md、expires_at=task_end、"
                "recovery_condition=add_build。",
            )
            _write_target(workspace / "pilot", project_body=body)
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(
                json.dumps(_coordination_payload(workspace)), encoding="utf-8"
            )

            completed = _run(coordination_path, "--require-all")

        self.assertEqual(completed.returncode, 1)
        findings = json.loads(completed.stdout)["results"][0]["blocking_findings"]
        self.assertIn("na_contract_fields_missing:reason", findings)

    def test_project_rule_must_reference_its_ci_contract_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "workspace"
            body = _project_body().replace(
                "- `.github/workflows/agent-rule-contract.yml` 只验证规则契约，不替代产品门禁。\n",
                "",
            )
            _write_target(workspace / "pilot", project_body=body)
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(
                json.dumps(_coordination_payload(workspace)), encoding="utf-8"
            )

            completed = _run(coordination_path, "--require-all")

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertIn(
            "project_contract_token_missing:.github/workflows/agent-rule-contract.yml",
            payload["results"][0]["blocking_findings"],
        )

    def test_wrapper_requires_raw_first_physical_line(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "workspace"
            _write_target(workspace / "pilot", wrapper=b"# heading\n@AGENTS.md\n")
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(json.dumps(_coordination_payload(workspace)), encoding="utf-8")

            completed = _run(coordination_path, "--require-all")

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertIn("wrapper_first_line_invalid", payload["results"][0]["blocking_findings"])

    def test_wrapper_rejects_utf8_bom(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "workspace"
            _write_target(workspace / "pilot", wrapper=b"\xef\xbb\xbf@AGENTS.md\n")
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(json.dumps(_coordination_payload(workspace)), encoding="utf-8")

            completed = _run(coordination_path, "--require-all")

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertIn("wrapper_utf8_bom", payload["results"][0]["blocking_findings"])

    def test_project_rule_rejects_host_specific_platform_section(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "workspace"
            body = _project_body().replace(
                "## B. 执行与风险边界", "## B. Codex 平台差异\n- `codex --version`。"
            )
            _write_target(workspace / "pilot", project_body=body)
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(json.dumps(_coordination_payload(workspace)), encoding="utf-8")

            completed = _run(coordination_path, "--require-all")

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertIn("project_rule_not_host_neutral", payload["results"][0]["blocking_findings"])

    def test_missing_target_anchor_is_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "workspace"
            _write_target(workspace / "pilot", project_body=_project_body(anchor="src/other.py"))
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(json.dumps(_coordination_payload(workspace)), encoding="utf-8")

            completed = _run(coordination_path, "--require-all")

        self.assertEqual(completed.returncode, 1)
        payload = json.loads(completed.stdout)
        self.assertIn("required_anchor_missing:runtime/main.py", payload["results"][0]["blocking_findings"])

    def test_reviewed_release_lag_is_observed_not_blocking(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "workspace"
            _write_target(workspace / "pilot", project_body=_project_body(reviewed_release="9.54"))
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(
                json.dumps(_coordination_payload(workspace, reviewed_release="9.54")), encoding="utf-8"
            )

            completed = _run(coordination_path, "--require-all")

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertIn("global_review_lag:9.54->9.55", payload["results"][0]["observations"])

    def test_missing_target_only_blocks_with_require_all(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "workspace"
            workspace.mkdir()
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(json.dumps(_coordination_payload(workspace)), encoding="utf-8")

            observed = _run(coordination_path)
            enforced = _run(coordination_path, "--require-all")

        self.assertEqual(observed.returncode, 0, observed.stdout + observed.stderr)
        self.assertEqual(json.loads(observed.stdout)["results"][0]["status"], "unavailable")
        self.assertEqual(enforced.returncode, 1)

    def test_generated_transaction_rule_files_are_outside_managed_observation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir) / "workspace"
            repo_root = workspace / "pilot"
            _write_target(repo_root)
            generated_rule = repo_root / ".txn" / "vendor-cache" / "AGENTS.md"
            generated_rule.parent.mkdir(parents=True)
            generated_rule.write_text("# third-party cache\n", encoding="utf-8")
            coordination_path = Path(tmp_dir) / "coordination.json"
            coordination_path.write_text(
                json.dumps(_coordination_payload(workspace), ensure_ascii=False), encoding="utf-8"
            )

            completed = _run(coordination_path, "--require-all")

        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        observations = json.loads(completed.stdout)["results"][0]["observations"]
        self.assertFalse(any(item.startswith("nested_rule_files:") for item in observations))


if __name__ == "__main__":
    unittest.main()
