"""Verification runner plans and evidence artifacts."""

from dataclasses import dataclass
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

    return build_verification_artifact(
        plan=plan,
        evidence_link=result_artifact_refs[plan.gates[-1].gate_id],
        results=results,
        result_artifact_refs=result_artifact_refs,
        risky_artifact_refs=risky_artifact_refs,
    )
