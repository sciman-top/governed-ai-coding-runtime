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

    def test_schema_rejects_write_execute_without_policy_decision_reference(self) -> None:
        payload = {
            "schema_version": "1.0",
            "command_id": "cmd-write-execute",
            "command_type": "write_execute",
            "task_id": "task-123",
            "repo_binding_id": "binding-python-service",
            "adapter_id": "codex-cli",
            "risk_tier": "medium",
            "execution_mode": "execute",
            "payload": {
                "tool_name": "write_file",
                "target_path": "docs/plan.md",
                "tier": "medium",
                "rollback_reference": "git diff -- docs/plan.md",
                "content": "patched",
            },
        }

        self.assertFalse(self._schema_accepts(payload))
        payload["policy_decision_ref"] = "artifacts/task-123/policy/write-escalate.json"
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
            payload={"run_id": "run-123", "plan_only": True},
            policy_decision=decision,
        )
        result = module.handle_session_bridge_command(command, task_root=ROOT / ".runtime" / "tasks", repo_root=ROOT)

        self.assertEqual(result.status, "verification_requested")
        self.assertTrue(result.payload["plan_only"])
        self.assertEqual(result.payload["execution_id"], "task-123:run-123")
        self.assertEqual(result.payload["continuation_id"], "task-123:run-123")
        self.assertEqual(result.payload["mode"], "quick")
        self.assertEqual(result.payload["gate_order"], ["test", "contract"])

    def test_local_session_bridge_requests_l2_plan_via_full_gate_command(self) -> None:
        module = self._module()
        decision = self._policy_decision(status="allow", risk_tier="low")

        command = module.build_session_bridge_command(
            command_id="cmd-l2-gate-request",
            command_type="run_full_gate",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="low",
            payload={"run_id": "run-456", "plan_only": True, "gate_level": "l2"},
            policy_decision=decision,
        )
        result = module.handle_session_bridge_command(command, task_root=ROOT / ".runtime" / "tasks", repo_root=ROOT)

        self.assertEqual(result.status, "verification_requested")
        self.assertTrue(result.payload["plan_only"])
        self.assertEqual(result.payload["mode"], "l2")
        self.assertEqual(result.payload["gate_order"], ["build", "test", "contract"])

    def test_local_session_bridge_enforces_required_canonical_entrypoint_policy(self) -> None:
        module = self._module()
        repo_attachment = importlib.import_module("governed_ai_coding_runtime_contracts.repo_attachment")
        decision = self._policy_decision(task_id="task-entrypoint-policy", status="allow", risk_tier="low")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            self._seed_task(workspace, task_id="task-entrypoint-policy")
            target_repo = workspace / "target"
            target_repo.mkdir()
            runtime_state_root = workspace / "runtime-state" / "target"
            repo_attachment.attach_target_repo(
                target_repo_root=str(target_repo),
                runtime_state_root=str(runtime_state_root),
                repo_id="target",
                display_name="Target",
                primary_language="python",
                build_command="cmd /c exit 0",
                test_command="cmd /c exit 0",
                contract_command="cmd /c exit 0",
                adapter_preference="process_bridge",
            )

            profile_path = target_repo / ".governed-ai" / "repo-profile.json"
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            profile["required_entrypoint_policy"]["current_mode"] = "targeted_enforced"
            profile_path.write_text(json.dumps(profile, indent=2, sort_keys=True), encoding="utf-8")

            blocked_command = module.build_session_bridge_command(
                command_id="cmd-entrypoint-policy-blocked",
                command_type="run_quick_gate",
                task_id="task-entrypoint-policy",
                repo_binding_id="binding-target",
                adapter_id="codex-cli",
                risk_tier="low",
                payload={"run_id": "run-entrypoint-policy", "plan_only": True},
                policy_decision=decision,
            )
            blocked_result = module.handle_session_bridge_command(
                blocked_command,
                task_root=workspace / ".runtime" / "tasks",
                repo_root=workspace,
                attachment_root=target_repo,
                attachment_runtime_state_root=runtime_state_root,
            )

            self.assertEqual(blocked_result.status, "denied")
            self.assertTrue(blocked_result.payload["entrypoint_policy"]["blocked"])

            allowed_command = module.build_session_bridge_command(
                command_id="cmd-entrypoint-policy-allowed",
                command_type="run_quick_gate",
                task_id="task-entrypoint-policy",
                repo_binding_id="binding-target",
                adapter_id="codex-cli",
                risk_tier="low",
                payload={
                    "run_id": "run-entrypoint-policy",
                    "plan_only": True,
                    "entrypoint_id": "runtime-flow",
                },
                policy_decision=decision,
            )
            allowed_result = module.handle_session_bridge_command(
                allowed_command,
                task_root=workspace / ".runtime" / "tasks",
                repo_root=workspace,
                attachment_root=target_repo,
                attachment_runtime_state_root=runtime_state_root,
            )

            self.assertEqual(allowed_result.status, "verification_requested")
            self.assertFalse(allowed_result.payload["entrypoint_policy"]["blocked"])

    def test_codex_session_identity_includes_flow_kind_and_preserves_explicit_ids(self) -> None:
        module = self._module()
        decision = self._policy_decision(status="allow", risk_tier="low")

        command = module.build_session_bridge_command(
            command_id="cmd-quick-gate-codex-identity",
            command_type="run_quick_gate",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="low",
            payload={
                "run_id": "run-codex-identity",
                "plan_only": True,
                "session_id": "session-explicit-001",
                "resume_id": "resume-explicit-001",
            },
            policy_decision=decision,
        )
        result = module.handle_session_bridge_command(command, task_root=ROOT / ".runtime" / "tasks", repo_root=ROOT)

        identity = result.payload["session_identity"]
        self.assertEqual(result.status, "verification_requested")
        self.assertEqual(identity["session_id"], "session-explicit-001")
        self.assertEqual(identity["resume_id"], "resume-explicit-001")
        self.assertEqual(identity["continuation_id"], "task-123:run-codex-identity")
        self.assertIn(identity["flow_kind"], {"live_attach", "process_bridge", "manual_handoff"})
        self.assertIn("adapter_tier", identity)

    def test_local_session_bridge_executes_quick_gate_with_runtime_lifecycle(self) -> None:
        module = self._module()
        repo_attachment = importlib.import_module("governed_ai_coding_runtime_contracts.repo_attachment")
        policy_decision = importlib.import_module("governed_ai_coding_runtime_contracts.policy_decision")
        decision = policy_decision.build_policy_decision(
            task_id="task-execute-gate",
            action_id="action-execute-allow",
            risk_tier="low",
            subject="session_command:run_gate",
            status="allow",
            decision_basis=["execute attached repo gate plan"],
            evidence_ref="artifacts/task-execute-gate/policy/allow.json",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            self._seed_task(workspace, task_id="task-execute-gate")
            target_repo = workspace / "target"
            target_repo.mkdir()
            runtime_state_root = workspace / "runtime-state" / "target"
            python = sys.executable.replace("\\", "/")
            repo_attachment.attach_target_repo(
                target_repo_root=str(target_repo),
                runtime_state_root=str(runtime_state_root),
                repo_id="target",
                display_name="Target",
                primary_language="python",
                build_command=f"{python} -c \"print('build-pass')\"",
                test_command=f"{python} -c \"print('test-pass')\"",
                contract_command=f"{python} -c \"print('contract-pass')\"",
                adapter_preference="process_bridge",
            )

            command = module.build_session_bridge_command(
                command_id="cmd-exec-quick-gate",
                command_type="run_quick_gate",
                task_id="task-execute-gate",
                repo_binding_id="binding-target",
                adapter_id="codex-cli",
                risk_tier="low",
                payload={"run_id": "run-exec-1"},
                policy_decision=decision,
            )
            result = module.handle_session_bridge_command(
                command,
                task_root=workspace / ".runtime" / "tasks",
                repo_root=workspace,
                attachment_root=target_repo,
                attachment_runtime_state_root=runtime_state_root,
            )

            self.assertEqual(result.status, "verification_completed")
            self.assertFalse(result.payload["plan_only"])
            self.assertEqual(result.payload["execution_id"], "task-execute-gate:run-exec-1")
            self.assertEqual(result.payload["continuation_id"], "task-execute-gate:run-exec-1")
            self.assertEqual(result.payload["outcome"], "pass")
            self.assertEqual(result.payload["required_gate_ids"], ["test", "contract"])
            self.assertEqual(result.payload["blocking_gate_ids"], ["test", "contract"])
            self.assertEqual(result.payload["results"], {"test": "pass", "contract": "pass"})
            self.assertIn("test", result.payload["result_artifact_refs"])
            self.assertIn("contract", result.payload["result_artifact_refs"])
            self.assertTrue(result.payload["adapter_event_ref"])
            self.assertGreaterEqual(result.payload["adapter_event_summary"]["gate_run_count"], 2)

    def test_non_codex_quick_gate_also_emits_adapter_event_linkage(self) -> None:
        module = self._module()
        repo_attachment = importlib.import_module("governed_ai_coding_runtime_contracts.repo_attachment")
        policy_decision = importlib.import_module("governed_ai_coding_runtime_contracts.policy_decision")
        decision = policy_decision.build_policy_decision(
            task_id="task-exec-generic-gate",
            action_id="action-generic-allow",
            risk_tier="low",
            subject="session_command:run_gate",
            status="allow",
            decision_basis=["attached repo gate plan is allowed for generic adapter"],
            evidence_ref="artifacts/task-exec-generic-gate/policy/allow.json",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            self._seed_task(workspace, task_id="task-exec-generic-gate")
            target_repo = workspace / "target"
            target_repo.mkdir()
            runtime_state_root = workspace / "runtime-state" / "target"
            python = sys.executable.replace("\\", "/")
            repo_attachment.attach_target_repo(
                target_repo_root=str(target_repo),
                runtime_state_root=str(runtime_state_root),
                repo_id="target",
                display_name="Target",
                primary_language="python",
                build_command=f"{python} -c \"print('build-pass')\"",
                test_command=f"{python} -c \"print('test-pass')\"",
                contract_command=f"{python} -c \"print('contract-pass')\"",
                adapter_preference="process_bridge",
            )

            command = module.build_session_bridge_command(
                command_id="cmd-exec-generic-gate",
                command_type="run_quick_gate",
                task_id="task-exec-generic-gate",
                repo_binding_id="binding-target",
                adapter_id="generic.process.cli",
                risk_tier="low",
                payload={"run_id": "run-generic-1"},
                policy_decision=decision,
            )
            result = module.handle_session_bridge_command(
                command,
                task_root=workspace / ".runtime" / "tasks",
                repo_root=workspace,
                attachment_root=target_repo,
                attachment_runtime_state_root=runtime_state_root,
            )

            self.assertEqual(result.status, "verification_completed")
            self.assertTrue(result.payload["adapter_event_ref"])
            self.assertIsInstance(result.payload["adapter_event_summary"], dict)
            self.assertGreaterEqual(result.payload["adapter_event_summary"]["gate_run_count"], 2)
            self.assertEqual(result.payload["session_identity"]["flow_kind"], "manual_handoff")

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
                payload={"run_id": "run-attached-1", "plan_only": True},
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
            self.assertTrue(result.payload["plan_only"])
            self.assertEqual(result.payload["gate_order"], ["test", "contract"])
            self.assertEqual(
                result.payload["commands"],
                [
                    "dotnet test tests/Target.Tests.csproj -c Debug",
                    "dotnet test tests/Target.Tests.csproj -c Debug --filter \"FullyQualifiedName~ArchitectureDependencyTests\"",
                ],
            )

    def test_tool_execution_path_uses_same_governance_surface(self) -> None:
        module = self._module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            self._seed_task(workspace, task_id="task-tool-flow")

            request_command = module.build_session_bridge_command(
                command_id="cmd-tool-request",
                command_type="write_request",
                task_id="task-tool-flow",
                repo_binding_id="binding-local",
                adapter_id="codex-cli",
                risk_tier="low",
                payload={
                    "tool_name": "package",
                    "command": f"{sys.executable} -m pip list --disable-pip-version-check",
                    "rollback_reference": "pip uninstall <pkg>",
                },
            )
            request_result = module.handle_session_bridge_command(
                request_command,
                task_root=workspace / ".runtime" / "tasks",
                repo_root=workspace,
            )

            self.assertEqual(request_result.status, "write_requested")
            self.assertEqual(request_result.payload["policy_status"], "allow")
            self.assertTrue(request_result.payload["policy_decision_ref"])

            execute_command = module.build_session_bridge_command(
                command_id="cmd-tool-execute",
                command_type="write_execute",
                task_id="task-tool-flow",
                repo_binding_id="binding-local",
                adapter_id="codex-cli",
                risk_tier="low",
                payload={
                    "tool_name": "package",
                    "command": f"{sys.executable} -m pip list --disable-pip-version-check",
                    "rollback_reference": "pip uninstall <pkg>",
                    "execution_id": request_result.payload["execution_id"],
                    "continuation_id": request_result.payload["continuation_id"],
                },
                policy_decision_ref=request_result.payload["policy_decision_ref"],
            )
            execute_result = module.handle_session_bridge_command(
                execute_command,
                task_root=workspace / ".runtime" / "tasks",
                repo_root=workspace,
            )

            self.assertEqual(execute_result.status, "write_executed")
            self.assertEqual(execute_result.payload["execution_status"], "executed")
            self.assertTrue(execute_result.payload["artifact_ref"])
            self.assertTrue(execute_result.payload["handoff_ref"])
            self.assertTrue(execute_result.payload["replay_ref"])
            self.assertTrue(execute_result.payload["adapter_event_ref"])
            self.assertGreaterEqual(execute_result.payload["adapter_event_summary"]["tool_call_count"], 1)

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

    def test_inspect_evidence_returns_task_level_refs(self) -> None:
        module = self._module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            task_store, _task_intake = self._task_modules()
            store = task_store.FileTaskStore(workspace / ".runtime" / "tasks")
            record = self._seed_task(workspace, task_id="task-evidence").load("task-evidence")
            record.transition_history.append(
                task_store.TaskTransitionRecord(
                    previous_state="planned",
                    next_state="running",
                    actor_type="runtime",
                    actor_id="session-bridge",
                    reason="started",
                    evidence_ref="docs/change-evidence/task-evidence-start.md",
                    timestamp="2026-04-19T00:00:00+00:00",
                )
            )
            record.run_history.append(
                task_store.TaskRunRecord(
                    run_id="run-evidence",
                    attempt_id="attempt-1",
                    worker_id="worker-1",
                    status="completed",
                    workspace_root=str(workspace / ".governed-workspaces" / "task-evidence"),
                    started_at="2026-04-19T00:00:00+00:00",
                    finished_at="2026-04-19T00:10:00+00:00",
                    summary="evidence ready",
                    evidence_refs=["artifacts/task-evidence/run-evidence/evidence/bundle.json"],
                    approval_ids=["approval-123"],
                    artifact_refs=["artifacts/task-evidence/run-evidence/execution-output/worker.txt"],
                    verification_refs=["artifacts/task-evidence/run-evidence/verification-output/runtime.txt"],
                    rollback_ref="git diff -- docs/plan.md",
                )
            )
            store.save(record)

            command = module.build_session_bridge_command(
                command_id="cmd-inspect-evidence",
                command_type="inspect_evidence",
                task_id="task-evidence",
                repo_binding_id="binding-python-service",
                adapter_id="codex-cli",
                risk_tier="low",
                payload={"run_id": "run-evidence"},
            )

            result = module.handle_session_bridge_command(command, task_root=store.root_path, repo_root=workspace)

            self.assertEqual(result.status, "ok")
            self.assertEqual(result.payload["run_id"], "run-evidence")
            self.assertTrue(result.payload["execution_id"])
            self.assertTrue(result.payload["continuation_id"])
            self.assertIn("artifacts/task-evidence/run-evidence/evidence/bundle.json", result.payload["evidence_refs"])
            self.assertIn("approval-123", result.payload["approval_ids"])
            self.assertIn("docs/change-evidence/task-evidence-start.md", result.payload["transition_evidence_refs"])

    def test_inspect_evidence_keeps_attachment_primary_path_read_only_when_task_missing(self) -> None:
        module = self._module()
        repo_attachment = importlib.import_module("governed_ai_coding_runtime_contracts.repo_attachment")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
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

            command = module.build_session_bridge_command(
                command_id="cmd-inspect-evidence-missing",
                command_type="inspect_evidence",
                task_id="task-missing",
                repo_binding_id="binding-target",
                adapter_id="codex-cli",
                risk_tier="low",
            )

            result = module.handle_session_bridge_command(
                command,
                task_root=workspace / ".runtime" / "tasks",
                repo_root=workspace,
                attachment_root=target_repo,
                attachment_runtime_state_root=runtime_state_root,
            )

            self.assertEqual(result.status, "ok")
            self.assertFalse(result.payload["task_found"])
            self.assertEqual(result.payload["evidence_refs"], [])
            self.assertTrue(result.payload["read_only"])
            self.assertEqual(result.payload["posture_summary"]["binding_state"], "healthy")

    def test_write_request_and_execution_flow_return_runtime_owned_refs(self) -> None:
        module = self._module()
        repo_attachment = importlib.import_module("governed_ai_coding_runtime_contracts.repo_attachment")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            self._seed_task(workspace, task_id="task-write-flow")
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

            write_request = module.build_session_bridge_command(
                command_id="cmd-write-request",
                command_type="write_request",
                task_id="task-write-flow",
                repo_binding_id="binding-target",
                adapter_id="codex-cli",
                risk_tier="medium",
                payload={
                    "tool_name": "write_file",
                    "target_path": "docs/plan.md",
                    "tier": "medium",
                    "rollback_reference": "git diff -- docs/plan.md",
                    "session_id": "session-live-bridge-001",
                    "resume_id": "resume-live-bridge-001",
                },
            )
            request_result = module.handle_session_bridge_command(
                write_request,
                task_root=workspace / ".runtime" / "tasks",
                repo_root=workspace,
                attachment_root=target_repo,
                attachment_runtime_state_root=runtime_state_root,
            )

            self.assertEqual(request_result.status, "approval_required")
            approval_id = request_result.payload["approval_id"]
            self.assertTrue(approval_id)
            self.assertEqual(request_result.payload["policy_status"], "escalate")
            flow_execution_id = request_result.payload["execution_id"]
            self.assertEqual(flow_execution_id, f"task-write-flow:approval:{approval_id}")
            self.assertEqual(request_result.payload["continuation_id"], flow_execution_id)
            self.assertEqual(request_result.payload["adapter_id"], "codex-cli")
            self.assertIn("approval_ref", request_result.payload)
            request_identity = request_result.payload["session_identity"]
            self.assertEqual(request_identity["session_id"], "session-live-bridge-001")
            self.assertEqual(request_identity["resume_id"], "resume-live-bridge-001")
            self.assertEqual(request_identity["continuation_id"], flow_execution_id)

            approval_record = json.loads(
                (runtime_state_root / "approvals" / f"{approval_id}.json").read_text(encoding="utf-8")
            )
            self.assertEqual(approval_record["session_id"], "session-live-bridge-001")
            self.assertEqual(approval_record["resume_id"], "resume-live-bridge-001")
            self.assertEqual(approval_record["continuation_id"], flow_execution_id)

            approve_command = module.build_session_bridge_command(
                command_id="cmd-write-approve",
                command_type="write_approve",
                task_id="task-write-flow",
                repo_binding_id="binding-target",
                adapter_id="codex-cli",
                risk_tier="medium",
                payload={
                    "approval_id": approval_id,
                    "decision": "approve",
                    "decided_by": "operator",
                },
            )
            approve_result = module.handle_session_bridge_command(
                approve_command,
                task_root=workspace / ".runtime" / "tasks",
                repo_root=workspace,
                attachment_runtime_state_root=runtime_state_root,
            )

            self.assertEqual(approve_result.status, "approval_recorded")
            self.assertEqual(approve_result.payload["approval_status"], "approved")
            self.assertEqual(approve_result.payload["execution_id"], flow_execution_id)
            self.assertEqual(approve_result.payload["continuation_id"], flow_execution_id)
            approve_identity = approve_result.payload["session_identity"]
            self.assertEqual(approve_identity["session_id"], request_identity["session_id"])
            self.assertEqual(approve_identity["resume_id"], request_identity["resume_id"])
            self.assertEqual(approve_identity["continuation_id"], flow_execution_id)

            execute_command = module.build_session_bridge_command(
                command_id="cmd-write-execute",
                command_type="write_execute",
                task_id="task-write-flow",
                repo_binding_id="binding-target",
                adapter_id="codex-cli",
                risk_tier="medium",
                payload={
                    "tool_name": "write_file",
                    "target_path": "docs/plan.md",
                    "tier": "medium",
                    "rollback_reference": "git diff -- docs/plan.md",
                    "content": "patched via session bridge",
                    "approval_id": approval_id,
                },
                policy_decision_ref=request_result.payload["policy_decision_ref"],
            )
            execute_result = module.handle_session_bridge_command(
                execute_command,
                task_root=workspace / ".runtime" / "tasks",
                repo_root=workspace,
                attachment_root=target_repo,
                attachment_runtime_state_root=runtime_state_root,
            )

            self.assertEqual(execute_result.status, "write_executed")
            self.assertEqual(execute_result.payload["execution_status"], "executed")
            self.assertTrue(execute_result.payload["artifact_ref"])
            self.assertEqual(execute_result.payload["execution_id"], flow_execution_id)
            self.assertEqual(execute_result.payload["continuation_id"], flow_execution_id)
            self.assertEqual(execute_result.payload["adapter_id"], "codex-cli")
            self.assertTrue(execute_result.payload["handoff_ref"])
            self.assertTrue(execute_result.payload["replay_ref"])
            self.assertIn(execute_result.payload["handoff_ref"], execute_result.payload["artifact_refs"])
            self.assertIn(execute_result.payload["replay_ref"], execute_result.payload["artifact_refs"])
            self.assertTrue(execute_result.payload["adapter_event_ref"])
            self.assertGreaterEqual(execute_result.payload["adapter_event_summary"]["file_change_count"], 1)
            execute_identity = execute_result.payload["session_identity"]
            adapter_event_payload = json.loads(
                (runtime_state_root / execute_result.payload["adapter_event_ref"]).read_text(encoding="utf-8")
            )
            self.assertEqual(execute_identity["session_id"], request_identity["session_id"])
            self.assertEqual(execute_identity["resume_id"], request_identity["resume_id"])
            self.assertEqual(execute_identity["continuation_id"], flow_execution_id)
            self.assertEqual(adapter_event_payload["session_identity"]["session_id"], request_identity["session_id"])
            self.assertEqual(adapter_event_payload["session_identity"]["resume_id"], request_identity["resume_id"])
            self.assertEqual(adapter_event_payload["session_identity"]["continuation_id"], flow_execution_id)
            self.assertEqual(adapter_event_payload["flow_kind"], execute_identity["flow_kind"])
            self.assertEqual((target_repo / "docs" / "plan.md").read_text(encoding="utf-8"), "patched via session bridge")

            status_command = module.build_session_bridge_command(
                command_id="cmd-write-status",
                command_type="write_status",
                task_id="task-write-flow",
                repo_binding_id="binding-target",
                adapter_id="codex-cli",
                risk_tier="medium",
                payload={"approval_id": approval_id, "target_path": "docs/plan.md"},
            )
            status_result = module.handle_session_bridge_command(
                status_command,
                task_root=workspace / ".runtime" / "tasks",
                repo_root=workspace,
                attachment_runtime_state_root=runtime_state_root,
            )

            self.assertEqual(status_result.status, "ok")
            self.assertEqual(status_result.payload["approval_status"], "approved")
            self.assertEqual(status_result.payload["execution_id"], flow_execution_id)
            self.assertEqual(status_result.payload["continuation_id"], flow_execution_id)
            self.assertEqual(status_result.payload["adapter_id"], "codex-cli")
            status_identity = status_result.payload["session_identity"]
            self.assertEqual(status_identity["session_id"], request_identity["session_id"])
            self.assertEqual(status_identity["resume_id"], request_identity["resume_id"])
            self.assertEqual(status_identity["continuation_id"], flow_execution_id)

    def test_write_status_rejects_unsafe_approval_ids(self) -> None:
        module = self._module()

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            self._seed_task(workspace, task_id="task-write-unsafe")
            command = module.build_session_bridge_command(
                command_id="cmd-write-status-unsafe",
                command_type="write_status",
                task_id="task-write-unsafe",
                repo_binding_id="binding-target",
                adapter_id="codex-cli",
                risk_tier="medium",
                payload={"approval_id": "../../escape", "target_path": "docs/plan.md"},
            )

            with self.assertRaisesRegex(ValueError, "approval_id"):
                module.handle_session_bridge_command(
                    command,
                    task_root=workspace / ".runtime" / "tasks",
                    repo_root=workspace,
                    attachment_runtime_state_root=workspace / "runtime-state" / "target",
                )

    def test_write_request_preflight_deny_returns_retry_command(self) -> None:
        module = self._module()
        repo_attachment = importlib.import_module("governed_ai_coding_runtime_contracts.repo_attachment")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            self._seed_task(workspace, task_id="task-write-preflight")
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

            write_request = module.build_session_bridge_command(
                command_id="cmd-write-preflight-deny",
                command_type="write_request",
                task_id="task-write-preflight",
                repo_binding_id="binding-target",
                adapter_id="codex-cli",
                risk_tier="low",
                payload={
                    "tool_name": "write_file",
                    "target_path": "secrets/prod.env",
                    "tier": "low",
                    "rollback_reference": "git diff -- secrets/prod.env",
                    "session_id": "session-preflight",
                    "resume_id": "resume-preflight",
                },
            )
            result = module.handle_session_bridge_command(
                write_request,
                task_root=workspace / ".runtime" / "tasks",
                repo_root=workspace,
                attachment_root=target_repo,
                attachment_runtime_state_root=runtime_state_root,
            )

            self.assertEqual(result.status, "denied")
            self.assertTrue(result.payload["preflight_blocked"])
            self.assertTrue(result.payload["suggested_target_path"])
            self.assertTrue(result.payload["retry_command"])
            self.assertIn("task-write-preflight", result.payload["retry_command"])
            self.assertIn(result.payload["suggested_target_path"], result.payload["retry_command"])

    def test_inspect_handoff_returns_payload_and_known_refs(self) -> None:
        module = self._module()
        task_store, _task_intake = self._task_modules()

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            store = task_store.FileTaskStore(workspace / ".runtime" / "tasks")
            record = self._seed_task(workspace, task_id="task-handoff").load("task-handoff")
            record.run_history.append(
                task_store.TaskRunRecord(
                    run_id="run-handoff",
                    attempt_id="attempt-1",
                    worker_id="worker-1",
                    status="completed",
                    workspace_root=str(workspace / ".governed-workspaces" / "task-handoff"),
                    started_at="2026-04-19T00:00:00+00:00",
                    finished_at="2026-04-19T00:10:00+00:00",
                    artifact_refs=["artifacts/task-handoff/run-handoff/handoff/package.json"],
                    evidence_refs=[],
                    verification_refs=[],
                )
            )
            store.save(record)

            command = module.build_session_bridge_command(
                command_id="cmd-inspect-handoff",
                command_type="inspect_handoff",
                task_id="task-handoff",
                repo_binding_id="binding-python-service",
                adapter_id="codex-cli",
                risk_tier="low",
                payload={"handoff_ref": "artifacts/task-handoff/manual/handoff.json"},
            )

            result = module.handle_session_bridge_command(command, task_root=store.root_path, repo_root=workspace)

            self.assertEqual(result.status, "ok")
            self.assertTrue(result.payload["execution_id"])
            self.assertTrue(result.payload["continuation_id"])
            self.assertIn("artifacts/task-handoff/manual/handoff.json", result.payload["handoff_refs"])
            self.assertIn("artifacts/task-handoff/run-handoff/handoff/package.json", result.payload["handoff_refs"])

    def test_session_bridge_result_reader_fails_on_missing_contract_fields(self) -> None:
        module = self._module()
        parsed = module.session_bridge_result_from_dict(
            {
                "command_id": "cmd",
                "command_type": "inspect_status",
                "status": "ok",
                "payload": {"total_tasks": 0},
            }
        )
        self.assertEqual(parsed.status, "ok")
        with self.assertRaises(ValueError):
            module.session_bridge_result_from_dict(
                {
                    "command_id": "cmd",
                    "command_type": "inspect_status",
                    "status": "ok",
                }
            )

    def test_quick_gate_reports_contract_reader_error_on_incompatible_repo_profile(self) -> None:
        module = self._module()
        repo_attachment = importlib.import_module("governed_ai_coding_runtime_contracts.repo_attachment")
        policy_decision = importlib.import_module("governed_ai_coding_runtime_contracts.policy_decision")

        with tempfile.TemporaryDirectory() as tmp_dir:
            workspace = Path(tmp_dir)
            self._seed_task(workspace, task_id="task-bad-contract")
            target_repo = workspace / "target"
            target_repo.mkdir()
            runtime_state_root = workspace / "runtime-state" / "target"
            attachment = repo_attachment.attach_target_repo(
                target_repo_root=str(target_repo),
                runtime_state_root=str(runtime_state_root),
                repo_id="target",
                display_name="Target",
                primary_language="python",
                build_command="python -m compileall src",
                test_command="python -m unittest discover",
                contract_command="python -m unittest discover -s tests/contracts",
            )
            profile_path = Path(attachment.repo_profile_path)
            profile = json.loads(profile_path.read_text(encoding="utf-8"))
            profile["contract_commands"] = "invalid-contract-shape"
            profile_path.write_text(json.dumps(profile, indent=2, sort_keys=True), encoding="utf-8")

            command = module.build_session_bridge_command(
                command_id="cmd-bad-contract",
                command_type="run_quick_gate",
                task_id="task-bad-contract",
                repo_binding_id="binding-target",
                adapter_id="codex-cli",
                risk_tier="low",
                payload={"run_id": "run-bad-contract"},
                policy_decision=policy_decision.build_policy_decision(
                    task_id="task-bad-contract",
                    action_id="quick-gate",
                    risk_tier="low",
                    subject="run_quick_gate",
                    status="allow",
                    decision_basis=["test"],
                    evidence_ref="artifacts/task-bad-contract/policy/allow.json",
                ),
            )
            result = module.handle_session_bridge_command(
                command,
                task_root=workspace / ".runtime" / "tasks",
                repo_root=workspace,
                attachment_root=target_repo,
                attachment_runtime_state_root=runtime_state_root,
            )
            self.assertEqual(result.status, "degraded")
            self.assertIn("contract_reader_error", result.reason)

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

    def test_launch_mode_captures_deleted_files(self) -> None:
        module = self._module()
        command = module.build_session_bridge_command(
            command_id="cmd-launch-delete",
            command_type="bind_task",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="low",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            cwd = Path(tmp_dir)
            (cwd / "delete-me.txt").write_text("stale", encoding="utf-8")
            result = module.run_launch_mode(
                command,
                argv=[
                    sys.executable,
                    "-c",
                    "from pathlib import Path; Path('delete-me.txt').unlink()",
                ],
                cwd=cwd,
            )

        self.assertEqual(result.payload["exit_code"], 0)
        self.assertIn("delete-me.txt", result.payload["deleted_files"])

    def test_launch_mode_detects_same_size_rewrite(self) -> None:
        module = self._module()
        command = module.build_session_bridge_command(
            command_id="cmd-launch-rewrite",
            command_type="bind_task",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="low",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            cwd = Path(tmp_dir)
            (cwd / "same-size.txt").write_text("abc", encoding="utf-8")
            result = module.run_launch_mode(
                command,
                argv=[
                    sys.executable,
                    "-c",
                    "import time; from pathlib import Path; time.sleep(0.02); Path('same-size.txt').write_text('xyz')",
                ],
                cwd=cwd,
            )

        self.assertEqual(result.payload["exit_code"], 0)
        self.assertIn("same-size.txt", result.payload["changed_files"])

    def test_launch_mode_detects_same_size_rewrite_when_mtime_is_restored(self) -> None:
        module = self._module()
        command = module.build_session_bridge_command(
            command_id="cmd-launch-rewrite-restored-mtime",
            command_type="bind_task",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="low",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            cwd = Path(tmp_dir)
            target = cwd / "same-size.txt"
            target.write_text("abc", encoding="utf-8")
            before = target.stat()
            result = module.run_launch_mode(
                command,
                argv=[
                    sys.executable,
                    "-c",
                    (
                        "import os; "
                        "from pathlib import Path; "
                        "path = Path('same-size.txt'); "
                        "path.write_text('xyz', encoding='utf-8'); "
                        f"os.utime(path, ns=({before.st_atime_ns}, {before.st_mtime_ns}))"
                    ),
                ],
                cwd=cwd,
            )

        self.assertEqual(result.payload["exit_code"], 0)
        self.assertIn("same-size.txt", result.payload["changed_files"])
        self.assertEqual(result.payload["snapshot_mode"], "balanced")

    def test_launch_mode_defaults_to_strict_for_high_risk(self) -> None:
        module = self._module()
        command = module.build_session_bridge_command(
            command_id="cmd-launch-default-strict-high-risk",
            command_type="bind_task",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="high",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            result = module.run_launch_mode(
                command,
                argv=[sys.executable, "-c", "print('launched-high')"],
                cwd=Path(tmp_dir),
            )

        self.assertEqual(result.payload["exit_code"], 0)
        self.assertEqual(result.payload["snapshot_mode"], "strict")

    def test_launch_mode_strict_snapshot_detects_large_file_change_outside_balanced_samples(self) -> None:
        module = self._module()
        command = module.build_session_bridge_command(
            command_id="cmd-launch-rewrite-strict-large-file",
            command_type="bind_task",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="low",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            cwd = Path(tmp_dir)
            target = cwd / "large.txt"
            content = "a" * 20000
            target.write_text(content, encoding="utf-8")
            before = target.stat()
            result = module.run_launch_mode(
                command,
                argv=[
                    sys.executable,
                    "-c",
                    (
                        "import os; "
                        "from pathlib import Path; "
                        "path = Path('large.txt'); "
                        "content = path.read_text(encoding='utf-8'); "
                        "path.write_text(content[:5000] + 'b' + content[5001:], encoding='utf-8'); "
                        f"os.utime(path, ns=({before.st_atime_ns}, {before.st_mtime_ns}))"
                    ),
                ],
                cwd=cwd,
                snapshot_mode="strict",
            )

        self.assertEqual(result.payload["exit_code"], 0)
        self.assertEqual(result.payload["snapshot_mode"], "strict")
        self.assertIn("large.txt", result.payload["changed_files"])

    def test_launch_mode_can_limit_snapshot_scope(self) -> None:
        module = self._module()
        command = module.build_session_bridge_command(
            command_id="cmd-launch-scope",
            command_type="bind_task",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="low",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            cwd = Path(tmp_dir)
            (cwd / "inside").mkdir()
            (cwd / "inside" / "tracked.txt").write_text("old", encoding="utf-8")
            (cwd / "outside.txt").write_text("old", encoding="utf-8")
            result = module.run_launch_mode(
                command,
                argv=[
                    sys.executable,
                    "-c",
                    (
                        "from pathlib import Path; "
                        "Path('inside/tracked.txt').write_text('new'); "
                        "Path('outside.txt').write_text('new')"
                    ),
                ],
                cwd=cwd,
                snapshot_scope="inside",
            )

        self.assertEqual(result.payload["exit_code"], 0)
        self.assertIn("inside/tracked.txt", result.payload["changed_files"])
        self.assertNotIn("outside.txt", result.payload["changed_files"])

    def test_launch_mode_rejects_snapshot_scope_outside_cwd(self) -> None:
        module = self._module()
        command = module.build_session_bridge_command(
            command_id="cmd-launch-scope-outside",
            command_type="bind_task",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="low",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            cwd = Path(tmp_dir)
            with self.assertRaisesRegex(ValueError, "snapshot_scope"):
                module.run_launch_mode(
                    command,
                    argv=[sys.executable, "-c", "print('noop')"],
                    cwd=cwd,
                    snapshot_scope="../outside",
                )

    def test_launch_mode_rejects_unknown_snapshot_mode(self) -> None:
        module = self._module()
        command = module.build_session_bridge_command(
            command_id="cmd-launch-scope-mode-invalid",
            command_type="bind_task",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="low",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            cwd = Path(tmp_dir)
            with self.assertRaisesRegex(ValueError, "snapshot_mode"):
                module.run_launch_mode(
                    command,
                    argv=[sys.executable, "-c", "print('noop')"],
                    cwd=cwd,
                    snapshot_mode="unknown",
                )

    def test_launch_mode_uses_repo_configured_snapshot_mode_when_auto(self) -> None:
        module = self._module()
        command = module.build_session_bridge_command(
            command_id="cmd-launch-repo-snapshot-mode",
            command_type="bind_task",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="low",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            cwd = Path(tmp_dir)
            (cwd / ".governed-ai").mkdir(parents=True, exist_ok=True)
            (cwd / ".governed-ai" / "repo-profile.json").write_text(
                json.dumps({"runtime_preferences": {"launch_snapshot_mode": "strict"}}, indent=2),
                encoding="utf-8",
            )
            result = module.run_launch_mode(
                command,
                argv=[sys.executable, "-c", "print('snapshot-mode')"],
                cwd=cwd,
            )

        self.assertEqual(result.payload["exit_code"], 0)
        self.assertEqual(result.payload["snapshot_mode"], "strict")

    def test_launch_mode_supports_timeout(self) -> None:
        module = self._module()
        command = module.build_session_bridge_command(
            command_id="cmd-launch-timeout",
            command_type="bind_task",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="low",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            result = module.run_launch_mode(
                command,
                argv=[sys.executable, "-c", "import time; time.sleep(2)"],
                cwd=Path(tmp_dir),
                timeout_seconds=1,
            )

        self.assertEqual(result.payload["exit_code"], 124)
        self.assertTrue(result.payload["timed_out"])
        self.assertEqual(result.payload["timeout_seconds"], 1.0)
        self.assertFalse(result.payload["timeout_exempt"])

    def test_launch_mode_timeout_exempt_requires_allowlisted_command(self) -> None:
        module = self._module()
        command = module.build_session_bridge_command(
            command_id="cmd-launch-timeout-exempt-deny",
            command_type="bind_task",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="low",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            with self.assertRaisesRegex(ValueError, "allowlisted"):
                module.run_launch_mode(
                    command,
                    argv=[sys.executable, "-c", "print('no-exempt')"],
                    cwd=Path(tmp_dir),
                    timeout_seconds=1,
                    timeout_exempt=True,
                )

    def test_launch_mode_timeout_exempt_can_use_repo_allowlist(self) -> None:
        module = self._module()
        command = module.build_session_bridge_command(
            command_id="cmd-launch-timeout-exempt-allow",
            command_type="bind_task",
            task_id="task-123",
            repo_binding_id="binding-python-service",
            adapter_id="codex-cli",
            risk_tier="low",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            cwd = Path(tmp_dir)
            (cwd / ".governed-ai").mkdir(parents=True, exist_ok=True)
            (cwd / ".governed-ai" / "repo-profile.json").write_text(
                json.dumps({"runtime_preferences": {"timeout_exempt_allowlist": ["*time.sleep*"]}}, indent=2),
                encoding="utf-8",
            )
            result = module.run_launch_mode(
                command,
                argv=[sys.executable, "-c", "import time; time.sleep(0.2)"],
                cwd=cwd,
                timeout_seconds=1,
                timeout_exempt=True,
            )

        self.assertEqual(result.payload["exit_code"], 0)
        self.assertFalse(result.payload["timed_out"])
        self.assertTrue(result.payload["timeout_exempt"])
        self.assertIsNone(result.payload["timeout_seconds"])

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
        task_id: str = "task-123",
        status: str,
        risk_tier: str,
        required_approval_ref: str | None = None,
        remediation_hint: str | None = None,
    ):
        policy_decision = importlib.import_module("governed_ai_coding_runtime_contracts.policy_decision")
        return policy_decision.build_policy_decision(
            task_id=task_id,
            action_id=f"action-{status}",
            risk_tier=risk_tier,
            subject="session_command:run_gate",
            status=status,
            decision_basis=[f"policy decision is {status}"],
            evidence_ref=f"artifacts/{task_id}/policy/{status}.json",
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
