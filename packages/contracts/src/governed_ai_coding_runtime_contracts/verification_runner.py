"""Verification runner plans and evidence artifacts."""

from dataclasses import asdict, dataclass
from typing import Callable
from typing import Literal

from governed_ai_coding_runtime_contracts.artifact_store import LocalArtifactStore


VerificationMode = Literal["quick", "full"]


@dataclass(frozen=True, slots=True)
class VerificationGate:
    gate_id: str
    canonical_name: str
    command: str
    required: bool


@dataclass(frozen=True, slots=True)
class VerificationPlan:
    mode: VerificationMode
    task_id: str | None
    run_id: str | None
    gates: list[VerificationGate]
    escalation_conditions: list[str]


@dataclass(frozen=True, slots=True)
class VerificationArtifact:
    mode: VerificationMode
    task_id: str | None
    run_id: str | None
    gate_order: list[str]
    evidence_link: str
    results: dict[str, str]
    result_artifact_refs: dict[str, str]
    escalation_conditions: list[str]
    risky_artifact_refs: list[str]


def verification_artifact_to_dict(artifact: VerificationArtifact) -> dict:
    return asdict(artifact)


def verification_artifact_from_dict(raw: dict) -> VerificationArtifact:
    if not isinstance(raw, dict):
        msg = "verification artifact payload must be an object"
        raise ValueError(msg)
    mode = _required_mode(raw.get("mode"))
    task_id = _required_optional_string(raw.get("task_id"), "task_id")
    run_id = _required_optional_string(raw.get("run_id"), "run_id")
    gate_order = _required_string_list(raw.get("gate_order"), "gate_order")
    evidence_link = _required_string(raw.get("evidence_link"), "evidence_link")
    results = _required_string_map(raw.get("results"), "results")
    result_artifact_refs = _required_string_map(raw.get("result_artifact_refs"), "result_artifact_refs")
    escalation_conditions = _required_string_list(raw.get("escalation_conditions"), "escalation_conditions")
    risky_artifact_refs = _required_string_list(raw.get("risky_artifact_refs"), "risky_artifact_refs")
    return VerificationArtifact(
        mode=mode,
        task_id=task_id,
        run_id=run_id,
        gate_order=gate_order,
        evidence_link=evidence_link,
        results=results,
        result_artifact_refs=result_artifact_refs,
        escalation_conditions=escalation_conditions,
        risky_artifact_refs=risky_artifact_refs,
    )


def build_verification_plan(
    mode: VerificationMode,
    *,
    task_id: str | None = None,
    run_id: str | None = None,
) -> VerificationPlan:
    if mode == "quick":
        gates = [
            VerificationGate(
                gate_id="test",
                canonical_name="test",
                command='pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime',
                required=True,
            ),
            VerificationGate(
                gate_id="contract",
                canonical_name="contract_or_invariant",
                command='pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract',
                required=True,
            ),
        ]
    elif mode == "full":
        gates = [
            VerificationGate(
                gate_id="build",
                canonical_name="build",
                command='pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1',
                required=True,
            ),
            VerificationGate(
                gate_id="test",
                canonical_name="test",
                command='pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime',
                required=True,
            ),
            VerificationGate(
                gate_id="contract",
                canonical_name="contract_or_invariant",
                command='pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract',
                required=True,
            ),
            VerificationGate(
                gate_id="doctor",
                canonical_name="hotspot_or_health_check",
                command='pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1',
                required=True,
            ),
        ]
    else:
        msg = f"unsupported verification mode: {mode}"
        raise ValueError(msg)
    return VerificationPlan(
        mode=mode,
        task_id=task_id,
        run_id=run_id,
        gates=gates,
        escalation_conditions=[
            "quick_failure_requires_full_or_root_cause",
            "contract_failure_blocks_delivery",
            "missing_required_gate_blocks_delivery",
        ],
    )


def build_repo_profile_verification_plan(
    mode: VerificationMode,
    *,
    profile_raw: dict,
    task_id: str | None = None,
    run_id: str | None = None,
) -> VerificationPlan:
    gates = _gates_from_repo_profile(profile_raw, mode=mode)
    if not gates:
        return build_verification_plan(mode, task_id=task_id, run_id=run_id)
    return VerificationPlan(
        mode=mode,
        task_id=task_id,
        run_id=run_id,
        gates=gates,
        escalation_conditions=[
            "quick_failure_requires_full_or_root_cause",
            "contract_failure_blocks_delivery",
            "missing_required_gate_blocks_delivery",
        ],
    )


def build_verification_artifact(
    plan: VerificationPlan,
    evidence_link: str,
    results: dict[str, str],
    result_artifact_refs: dict[str, str] | None = None,
    risky_artifact_refs: list[str] | None = None,
) -> VerificationArtifact:
    if not evidence_link.strip():
        msg = "evidence_link is required"
        raise ValueError(msg)
    return VerificationArtifact(
        mode=plan.mode,
        task_id=plan.task_id,
        run_id=plan.run_id,
        gate_order=[gate.gate_id for gate in plan.gates],
        evidence_link=evidence_link,
        results=results,
        result_artifact_refs=result_artifact_refs or {},
        escalation_conditions=plan.escalation_conditions,
        risky_artifact_refs=risky_artifact_refs or [],
    )


def run_verification_plan(
    plan: VerificationPlan,
    *,
    artifact_store: LocalArtifactStore,
    execute_gate: Callable[[VerificationGate], tuple[int, str]],
    metadata_store: object | None = None,
) -> VerificationArtifact:
    if not plan.task_id or not plan.run_id:
        msg = "task_id and run_id are required to run verification"
        raise ValueError(msg)

    results: dict[str, str] = {}
    result_artifact_refs: dict[str, str] = {}
    risky_artifact_refs: list[str] = []

    for gate in plan.gates:
        exit_code, output = execute_gate(gate)
        artifact = artifact_store.write_text(
            task_id=plan.task_id,
            run_id=plan.run_id,
            kind="verification-output",
            label=gate.gate_id,
            content=output,
        )
        result_artifact_refs[gate.gate_id] = artifact.relative_path
        if artifact.risky:
            risky_artifact_refs.append(artifact.relative_path)
        results[gate.gate_id] = "pass" if exit_code == 0 else "fail"

    if metadata_store is not None and hasattr(metadata_store, "upsert"):
        metadata_store.upsert(
            namespace="verification_runs",
            key=f"{plan.task_id}:{plan.run_id}",
            payload={
                "task_id": plan.task_id,
                "run_id": plan.run_id,
                "mode": plan.mode,
                "results": results,
                "result_artifact_refs": result_artifact_refs,
            },
        )

    return build_verification_artifact(
        plan=plan,
        evidence_link=result_artifact_refs[plan.gates[-1].gate_id],
        results=results,
        result_artifact_refs=result_artifact_refs,
        risky_artifact_refs=risky_artifact_refs,
    )


def _gates_from_repo_profile(raw: dict, *, mode: str) -> list[VerificationGate]:
    if not isinstance(raw, dict):
        msg = "profile_raw must be an object"
        raise ValueError(msg)
    if mode == "quick":
        command_groups = ["quick_gate_commands", "test_commands", "contract_commands", "invariant_commands"]
    else:
        command_groups = ["full_gate_commands", "build_commands", "test_commands", "contract_commands", "invariant_commands"]

    gates: list[VerificationGate] = []
    seen_gate_ids: set[str] = set()
    declared_groups_present = False
    for group in command_groups:
        if group not in raw:
            continue
        declared_groups_present = True
        commands = raw.get(group)
        if not isinstance(commands, list):
            msg = f"{group} must be a list"
            raise ValueError(msg)
        for command in commands:
            if not isinstance(command, dict):
                msg = f"{group} entries must be objects"
                raise ValueError(msg)
            gate_id = _gate_id_for_group(group, command)
            if gate_id in seen_gate_ids:
                continue
            gate_command = command.get("command")
            if not isinstance(gate_command, str) or not gate_command.strip():
                msg = f"{group} command is missing a runnable command string"
                raise ValueError(msg)
            gates.append(
                VerificationGate(
                    gate_id=gate_id,
                    canonical_name=gate_id,
                    command=gate_command.strip(),
                    required=bool(command.get("required", True)),
                )
            )
            seen_gate_ids.add(gate_id)

        if mode == "quick" and seen_gate_ids.issuperset({"test", "contract"}):
            break
        if mode == "full" and seen_gate_ids.issuperset({"build", "test", "contract"}):
            break
    if declared_groups_present:
        if mode == "quick" and not seen_gate_ids.issuperset({"test", "contract"}):
            msg = "declared quick gate contract must provide test and contract gates"
            raise ValueError(msg)
        if mode == "full" and not seen_gate_ids.issuperset({"build", "test", "contract"}):
            msg = "declared full gate contract must provide build, test, and contract gates"
            raise ValueError(msg)
    return gates


def _gate_id_for_group(group: str, command: dict) -> str:
    if group in {"quick_gate_commands", "test_commands"}:
        return "test"
    if group in {"contract_commands", "invariant_commands"}:
        return "contract"
    if group == "build_commands":
        return "build"
    if group == "full_gate_commands":
        command_id = command.get("id")
        if isinstance(command_id, str) and command_id.strip() in {"build", "test", "contract", "doctor", "hotspot"}:
            normalized = command_id.strip()
            return "doctor" if normalized == "hotspot" else normalized
    command_id = command.get("id")
    if isinstance(command_id, str) and command_id.strip():
        return command_id.strip()
    return group


def _required_mode(value: object) -> VerificationMode:
    if value in {"quick", "full"}:
        return value
    msg = f"unsupported verification mode: {value}"
    raise ValueError(msg)


def _required_optional_string(value: object, field_name: str) -> str | None:
    if value is None:
        return None
    return _required_string(value, field_name)


def _required_string(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()


def _required_string_list(value: object, field_name: str) -> list[str]:
    if not isinstance(value, list):
        msg = f"{field_name} must be a list"
        raise ValueError(msg)
    return [_required_string(item, field_name) for item in value]


def _required_string_map(value: object, field_name: str) -> dict[str, str]:
    if not isinstance(value, dict):
        msg = f"{field_name} must be an object"
        raise ValueError(msg)
    normalized: dict[str, str] = {}
    for key, item in value.items():
        normalized[_required_string(key, field_name)] = _required_string(item, field_name)
    return normalized
