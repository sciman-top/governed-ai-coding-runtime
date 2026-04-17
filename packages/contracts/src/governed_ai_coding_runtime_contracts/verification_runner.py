"""Verification runner plans and evidence artifacts."""

from dataclasses import dataclass
from typing import Literal


VerificationMode = Literal["quick", "full"]


@dataclass(frozen=True, slots=True)
class VerificationGate:
    name: str
    required: bool


@dataclass(frozen=True, slots=True)
class VerificationPlan:
    mode: VerificationMode
    gates: list[VerificationGate]
    escalation_conditions: list[str]


@dataclass(frozen=True, slots=True)
class VerificationArtifact:
    mode: VerificationMode
    gate_order: list[str]
    evidence_link: str
    results: dict[str, str]
    escalation_conditions: list[str]


def build_verification_plan(mode: VerificationMode) -> VerificationPlan:
    if mode == "quick":
        gates = [
            VerificationGate("test", required=True),
            VerificationGate("contract/invariant", required=True),
        ]
    elif mode == "full":
        gates = [
            VerificationGate("build", required=True),
            VerificationGate("test", required=True),
            VerificationGate("contract/invariant", required=True),
            VerificationGate("hotspot", required=True),
        ]
    else:
        msg = f"unsupported verification mode: {mode}"
        raise ValueError(msg)
    return VerificationPlan(
        mode=mode,
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
) -> VerificationArtifact:
    if not evidence_link.strip():
        msg = "evidence_link is required"
        raise ValueError(msg)
    return VerificationArtifact(
        mode=plan.mode,
        gate_order=[gate.name for gate in plan.gates],
        evidence_link=evidence_link,
        results=results,
        escalation_conditions=plan.escalation_conditions,
    )
