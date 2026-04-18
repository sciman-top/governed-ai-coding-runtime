import importlib
import json
import subprocess
import sys
import tempfile
import unittest
from dataclasses import fields
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class SessionBridgeCommandTests(unittest.TestCase):
    def test_session_bridge_api_exists(self) -> None:
        module = self._module()
        if not hasattr(module, "SessionBridgeCommand"):
            self.fail("SessionBridgeCommand is not implemented")
        if not hasattr(module, "build_session_bridge_command"):
            self.fail("build_session_bridge_command is not implemented")
        if not hasattr(module, "is_execution_command"):
            self.fail("is_execution_command is not implemented")
        if not hasattr(module, "requires_human_approval"):
            self.fail("requires_human_approval is not implemented")

    def test_read_only_command_carries_core_session_identity(self) -> None:
        module = self._module()

        command = module.build_session_bridge_command(
            command_id="cmd-show-posture",
            command_type="show_repo_posture",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="low",
            payload={"format": "summary"},
        )

        self.assertEqual(command.schema_version, "1.0")
        self.assertEqual(command.command_type, "show_repo_posture")
        self.assertEqual(command.task_id, "task-123")
        self.assertEqual(command.repo_binding_id, "binding-python-service")
        self.assertEqual(command.adapter_id, "codex-cli")
        self.assertEqual(command.risk_tier, "low")
        self.assertEqual(command.execution_mode, "read_only")
        self.assertIsNone(command.policy_decision_ref)
        self.assertFalse(module.is_execution_command(command))

    def test_quick_gate_requires_allow_policy_decision_to_execute(self) -> None:
        module = self._module()
        decision = self._policy_decision(status="allow", risk_tier="low")

        command = module.build_session_bridge_command(
            command_id="cmd-quick-gate",
            command_type="run_quick_gate",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="low",
            payload={"gate_level": "quick"},
            policy_decision=decision,
        )

        self.assertEqual(command.execution_mode, "execute")
        self.assertEqual(command.policy_decision_ref, decision.evidence_ref)
        self.assertIsNone(command.escalation_context)
        self.assertTrue(module.is_execution_command(command))

    def test_execution_command_fails_closed_when_policy_decision_denies(self) -> None:
        module = self._module()
        decision = self._policy_decision(
            status="deny",
            risk_tier="high",
            remediation_hint="run only declared gates",
        )

        with self.assertRaisesRegex(ValueError, "deny"):
            module.build_session_bridge_command(
                command_id="cmd-full-gate-denied",
                command_type="run_full_gate",
                task_id="task-123",
                repo_binding_id="binding-python-service",
                adapter_id="codex-cli",
                risk_tier="high",
                payload={"gate_level": "full"},
                policy_decision=decision,
            )

    def test_escalating_policy_decision_pauses_execution_with_context(self) -> None:
        module = self._module()
        decision = self._policy_decision(
            status="escalate",
            risk_tier="high",
            required_approval_ref="approval-123",
        )

        command = module.build_session_bridge_command(
            command_id="cmd-full-gate-escalate",
            command_type="run_full_gate",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="high",
            payload={"gate_level": "full"},
            policy_decision=decision,
        )

        self.assertEqual(command.execution_mode, "requires_approval")
        self.assertEqual(command.policy_decision_ref, decision.evidence_ref)
        self.assertEqual(command.escalation_context["required_approval_ref"], "approval-123")
        self.assertFalse(module.is_execution_command(command))
        self.assertTrue(module.requires_human_approval(command))

    def test_request_approval_requires_escalation_context(self) -> None:
        module = self._module()

        with self.assertRaisesRegex(ValueError, "escalation_context"):
            module.build_session_bridge_command(
                command_id="cmd-request-approval-missing-context",
                command_type="request_approval",
                task_id="task-123",
                repo_binding_id="binding-python-service",
                adapter_id="codex-cli",
                risk_tier="high",
            )

        command = module.build_session_bridge_command(
            command_id="cmd-request-approval",
            command_type="request_approval",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="high",
            escalation_context={
                "required_approval_ref": "approval-123",
                "reason": "high-risk gate requires human confirmation",
            },
        )

        self.assertEqual(command.execution_mode, "requires_approval")
        self.assertTrue(module.requires_human_approval(command))

    def test_schema_and_python_required_fields_and_enums_match(self) -> None:
        module = self._module()
        schema = json.loads(
            (ROOT / "schemas" / "jsonschema" / "session-bridge-command.schema.json").read_text(encoding="utf-8")
        )

        dataclass_fields = {field.name for field in fields(module.SessionBridgeCommand)}
        for required_field in schema["required"]:
            self.assertIn(required_field, dataclass_fields)

        self.assertEqual(set(schema["properties"]["command_type"]["enum"]), module.COMMAND_TYPES)
        self.assertEqual(set(schema["properties"]["risk_tier"]["enum"]), module.RISK_TIERS)
        self.assertEqual(set(schema["properties"]["execution_mode"]["enum"]), module.EXECUTION_MODES)

    def test_schema_rejects_execution_without_policy_decision_reference(self) -> None:
        payload = {
            "schema_version": "1.0",
            "command_id": "cmd-quick-gate",
            "command_type": "run_quick_gate",
            "task_id": "task-123",
            "repo_binding_id": "binding-python-service",
            "adapter_id": "codex-cli",
            "risk_tier": "low",
            "execution_mode": "execute",
            "payload": {"gate_level": "quick"},
        }

        self.assertFalse(self._schema_accepts(payload))
        payload["policy_decision_ref"] = "artifacts/task-123/policy/allow.json"
        self.assertTrue(self._schema_accepts(payload))

    def test_session_bridge_exports_from_package_root(self) -> None:
        package = importlib.import_module("governed_ai_coding_runtime_contracts")
        if not hasattr(package, "SessionBridgeCommand"):
            self.fail("SessionBridgeCommand is not exported from package root")
        if not hasattr(package, "build_session_bridge_command"):
            self.fail("build_session_bridge_command is not exported from package root")

    def test_local_session_bridge_binds_existing_task_to_repo(self) -> None:
        module = self._module()
        task_store, _task_intake = self._task_modules()

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = self._seed_task(Path(tmp_dir), task_id="task-bind")
            command = module.build_session_bridge_command(
                command_id="cmd-bind",
                command_type="bind_task",
                task_id="task-bind",
                repo_binding_id="binding-target",
                adapter_id="codex-cli",
                risk_tier="low",
            )

            result = module.handle_session_bridge_command(
                command,
                task_root=store.root_path,
                repo_root=Path(tmp_dir),
            )

            self.assertEqual(result.status, "bound")
            self.assertEqual(result.payload["task_id"], "task-bind")
            self.assertEqual(result.payload["repo_binding_id"], "binding-target")
            self.assertEqual(store.load("task-bind").current_state, "planned")

    def test_local_session_bridge_reads_repo_posture_and_status_without_mutation(self) -> None:
        module = self._module()
        repo_attachment = importlib.import_module("governed_ai_coding_runtime_contracts.repo_attachment")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            store = self._seed_task(workspace, task_id="task-read")
            target_repo = workspace / "target"
            target_repo.mkdir()
            runtime_state_root = workspace / "runtime-state" / "target"
            repo_attachment.attach_target_repo(
                target_repo_root=str(target_repo),
                runtime_state_root=str(runtime_state_root),
                repo_id="target",
                display_name="Target",
                primary_language="python",
                build_command="python -m compileall src",
                test_command="python -m unittest discover",
                contract_command="python -m unittest discover -s tests/contracts",
            )
            before = (store.root_path / "task-read.json").read_text(encoding="utf-8")

            posture_command = module.build_session_bridge_command(
                command_id="cmd-posture",
                command_type="show_repo_posture",
                task_id="task-read",
                repo_binding_id="binding-target",
                adapter_id="codex-cli",
                risk_tier="low",
            )
            posture = module.handle_session_bridge_command(
                posture_command,
                task_root=store.root_path,
                repo_root=workspace,
                attachment_root=target_repo,
                attachment_runtime_state_root=runtime_state_root,
            )

            status_command = module.build_session_bridge_command(
                command_id="cmd-status",
                command_type="inspect_status",
                task_id="task-read",
                repo_binding_id="binding-target",
                adapter_id="codex-cli",
                risk_tier="low",
            )
            status = module.handle_session_bridge_command(
                status_command,
                task_root=store.root_path,
                repo_root=workspace,
                attachment_root=target_repo,
                attachment_runtime_state_root=runtime_state_root,
            )

            after = (store.root_path / "task-read.json").read_text(encoding="utf-8")
            self.assertEqual(posture.status, "ok")
            self.assertEqual(posture.payload["binding_state"], "healthy")
            self.assertEqual(status.status, "ok")
            self.assertEqual(status.payload["total_tasks"], 1)
            self.assertEqual(before, after)

    def test_local_session_bridge_requests_gate_plans_through_verification_runner(self) -> None:
        module = self._module()
        decision = self._policy_decision(status="allow", risk_tier="low")

        command = module.build_session_bridge_command(
            command_id="cmd-quick-gate-request",
            command_type="run_quick_gate",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="low",
            payload={"run_id": "run-123"},
            policy_decision=decision,
        )
        result = module.handle_session_bridge_command(command, task_root=ROOT / ".runtime" / "tasks", repo_root=ROOT)

        self.assertEqual(result.status, "verification_requested")
        self.assertEqual(result.payload["mode"], "quick")
        self.assertEqual(result.payload["gate_order"], ["test", "contract"])

    def test_attached_repo_quick_gate_prefers_target_repo_declared_commands(self) -> None:
        module = self._module()
        repo_attachment = importlib.import_module("governed_ai_coding_runtime_contracts.repo_attachment")
        policy_decision = importlib.import_module("governed_ai_coding_runtime_contracts.policy_decision")
        decision = policy_decision.build_policy_decision(
            task_id="task-attached-gate",
            action_id="action-attached-allow",
            risk_tier="low",
            subject="session_command:run_gate",
            status="allow",
            decision_basis=["attached repo gate plan is allowed"],
            evidence_ref="artifacts/task-attached-gate/policy/allow.json",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            self._seed_task(workspace, task_id="task-attached-gate")
            target_repo = workspace / "target"
            target_repo.mkdir()
            runtime_state_root = workspace / "runtime-state" / "target"
            repo_attachment.attach_target_repo(
                target_repo_root=str(target_repo),
                runtime_state_root=str(runtime_state_root),
                repo_id="target",
                display_name="Target",
                primary_language="csharp",
                build_command="dotnet build Target.sln -c Debug",
                test_command="dotnet test tests/Target.Tests.csproj -c Debug",
                contract_command="dotnet test tests/Target.Tests.csproj -c Debug --filter \"FullyQualifiedName~ArchitectureDependencyTests\"",
                adapter_preference="process_bridge",
            )

            command = module.build_session_bridge_command(
                command_id="cmd-attached-quick-gate",
                command_type="run_quick_gate",
                task_id="task-attached-gate",
                repo_binding_id="binding-target",
                adapter_id="codex-cli",
                risk_tier="low",
                payload={"run_id": "run-attached-1"},
                policy_decision=decision,
            )
            result = module.handle_session_bridge_command(
                command,
                task_root=workspace / ".runtime" / "tasks",
                repo_root=workspace,
                attachment_root=target_repo,
                attachment_runtime_state_root=runtime_state_root,
            )

            self.assertEqual(result.status, "verification_requested")
            self.assertEqual(result.payload["gate_order"], ["test", "contract"])
            self.assertEqual(
                result.payload["commands"],
                [
                    "dotnet test tests/Target.Tests.csproj -c Debug",
                    "dotnet test tests/Target.Tests.csproj -c Debug --filter \"FullyQualifiedName~ArchitectureDependencyTests\"",
                ],
            )

    def test_write_governance_results_normalize_to_policy_decision(self) -> None:
        write_tool_runner = importlib.import_module("governed_ai_coding_runtime_contracts.write_tool_runner")

        allowed = write_tool_runner.policy_decision_from_write_governance(
            write_tool_runner.WriteGovernanceDecision(
                task_id="task-123",
                tool_name="apply_patch",
                target_path="src/service.py",
                tier="low",
                status="allowed",
                rollback_reference="git diff -- src/service.py",
            )
        )
        paused = write_tool_runner.policy_decision_from_write_governance(
            write_tool_runner.WriteGovernanceDecision(
                task_id="task-123",
                tool_name="apply_patch",
                target_path="src/service.py",
                tier="high",
                status="paused",
                rollback_reference="git diff -- src/service.py",
                approval_id="approval-123",
            )
        )
        denied = write_tool_runner.policy_decision_from_write_denial(
            task_id="task-123",
            tool_name="apply_patch",
            target_path="secrets/prod.env",
            tier="high",
            reason="path is blocked",
        )

        self.assertEqual(allowed.status, "allow")
        self.assertEqual(paused.status, "escalate")
        self.assertEqual(paused.required_approval_ref, "approval-123")
        self.assertEqual(denied.status, "deny")

    def test_unsupported_session_bridge_command_returns_degrade_result(self) -> None:
        module = self._module()
        command = module.build_session_bridge_command(
            command_id="cmd-inspect-evidence",
            command_type="inspect_evidence",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="low",
        )

        result = module.handle_session_bridge_command(command, task_root=ROOT / ".runtime" / "tasks", repo_root=ROOT)

        self.assertEqual(result.status, "degraded")
        self.assertEqual(result.unsupported_capability_behavior, "manual_handoff")

    def test_session_bridge_cli_help(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/session-bridge.py", "--help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Local governed session bridge", completed.stdout)

    def test_launch_mode_is_explicit_and_not_native_attach(self) -> None:
        module = self._module()
        command = module.build_session_bridge_command(
            command_id="cmd-launch",
            command_type="bind_task",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="low",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            result = module.run_launch_mode(
                command,
                argv=[sys.executable, "-c", "print('launched')"],
                cwd=Path(tmp_dir),
            )

        self.assertEqual(result.status, "launch_completed")
        self.assertEqual(result.payload["launch_mode"], "process_bridge")
        self.assertEqual(result.payload["adapter_tier"], "process_bridge")
        self.assertFalse(result.payload["native_attach"])

    def test_launch_mode_captures_process_output_changed_files_and_verification_refs(self) -> None:
        module = self._module()
        command = module.build_session_bridge_command(
            command_id="cmd-launch-capture",
            command_type="bind_task",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="low",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            result = module.run_launch_mode(
                command,
                argv=[
                    sys.executable,
                    "-c",
                    "from pathlib import Path; print('launch-output'); Path('changed.txt').write_text('changed')",
                ],
                cwd=Path(tmp_dir),
                verification_refs=["artifacts/task-123/run-1/verification-output/test.txt"],
            )

        self.assertEqual(result.payload["exit_code"], 0)
        self.assertIn("launch-output", result.payload["stdout"])
        self.assertIn("changed.txt", result.payload["changed_files"])
        self.assertEqual(
            result.payload["verification_refs"],
            ["artifacts/task-123/run-1/verification-output/test.txt"],
        )

    def test_manual_handoff_remains_available_when_process_bridge_unavailable(self) -> None:
        adapter_registry = importlib.import_module("governed_ai_coding_runtime_contracts.adapter_registry")
        module = self._module()
        command = module.build_session_bridge_command(
            command_id="cmd-manual-handoff",
            command_type="bind_task",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="low",
        )

        capability = adapter_registry.resolve_launch_fallback(
            adapter_id="codex-cli",
            native_attach_available=False,
            process_bridge_available=False,
        )
        result = module.manual_handoff_result(command, reason=capability.reason)

        self.assertEqual(capability.tier, "manual_handoff")
        self.assertEqual(result.status, "manual_handoff")
        self.assertEqual(result.unsupported_capability_behavior, "manual_handoff")

    def test_session_bridge_launch_cli_help(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/session-bridge.py", "launch", "--help"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Launch a process bridge fallback", completed.stdout)

    def _module(self):
        try:
            return importlib.import_module("governed_ai_coding_runtime_contracts.session_bridge")
        except ModuleNotFoundError as exc:
            self.fail(f"session_bridge module is not implemented: {exc}")

    def _policy_decision(
        self,
        *,
        status: str,
        risk_tier: str,
        required_approval_ref: str | None = None,
        remediation_hint: str | None = None,
    ):
        policy_decision = importlib.import_module("governed_ai_coding_runtime_contracts.policy_decision")
        return policy_decision.build_policy_decision(
            task_id="task-123",
            action_id=f"action-{status}",
            risk_tier=risk_tier,
            subject="session_command:run_gate",
            status=status,
            decision_basis=[f"policy decision is {status}"],
            evidence_ref=f"artifacts/task-123/policy/{status}.json",
            required_approval_ref=required_approval_ref,
            remediation_hint=remediation_hint,
        )

    def _task_modules(self):
        task_store = importlib.import_module("governed_ai_coding_runtime_contracts.task_store")
        task_intake = importlib.import_module("governed_ai_coding_runtime_contracts.task_intake")
        return task_store, task_intake

    def _seed_task(self, workspace: Path, *, task_id: str):
        task_store, task_intake = self._task_modules()
        store = task_store.FileTaskStore(workspace / ".runtime" / "tasks")
        store.save(
            task_store.TaskRecord(
                task_id=task_id,
                task=task_intake.TaskIntake(
                    goal="bridge task",
                    scope="session bridge",
                    acceptance=["bridge can inspect task"],
                    repo="target",
                    budgets={"max_steps": 5, "max_minutes": 10},
                ),
                current_state="planned",
            )
        )
        return store

    def _schema_accepts(self, payload: dict) -> bool:
        schema_path = ROOT / "schemas" / "jsonschema" / "session-bridge-command.schema.json"
        command = (
            "$json = [Console]::In.ReadToEnd(); "
            f"if (Test-Json -Json $json -SchemaFile '{schema_path}') "
            "{ Write-Output 'true' } else { Write-Output 'false' }"
        )
        completed = subprocess.run(
            ["pwsh", "-NoProfile", "-Command", command],
            input=json.dumps(payload),
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        return completed.stdout.strip().lower() == "true"


if __name__ == "__main__":
    unittest.main()
