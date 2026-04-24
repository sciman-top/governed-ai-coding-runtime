"""Verification runner plans and evidence artifacts."""

from dataclasses import asdict, dataclass, field
import hashlib
from typing import Callable
from typing import Literal
from typing import cast

from governed_ai_coding_runtime_contracts.artifact_store import LocalArtifactStore


VerificationMode = Literal["quick", "full", "l1", "l2", "l3"]
VerificationLevel = Literal["l1", "l2", "l3"]


@dataclass(frozen=True, slots=True)
class VerificationGate:
    gate_id: str
    canonical_name: str
    command: str
    required: bool
    blocking: bool = True


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
    cache_hits: dict[str, bool] = field(default_factory=dict)
    required_gate_ids: list[str] = field(default_factory=list)
    blocking_gate_ids: list[str] = field(default_factory=list)


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
    cache_hits_raw = raw.get("cache_hits")
    cache_hits: dict[str, bool] = {}
    if cache_hits_raw is not None:
        if not isinstance(cache_hits_raw, dict):
            msg = "cache_hits must be an object when provided"
            raise ValueError(msg)
        for key, value in cache_hits_raw.items():
            cache_hits[_required_string(key, "cache_hits")] = bool(value)
    required_gate_ids = _required_string_list(raw.get("required_gate_ids", []), "required_gate_ids")
    blocking_gate_ids = _required_string_list(raw.get("blocking_gate_ids", []), "blocking_gate_ids")
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
        cache_hits=cache_hits,
        required_gate_ids=required_gate_ids,
        blocking_gate_ids=blocking_gate_ids,
        escalation_conditions=escalation_conditions,
        risky_artifact_refs=risky_artifact_refs,
    )


def build_verification_plan(
    mode: VerificationMode,
    *,
    task_id: str | None = None,
    run_id: str | None = None,
) -> VerificationPlan:
    level = _normalized_level(mode)
    if level == "l1":
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
    elif level == "l2":
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
        ]
    elif level == "l3":
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
    cache_hits: dict[str, bool] | None = None,
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
        cache_hits=cache_hits or {},
        required_gate_ids=[gate.gate_id for gate in plan.gates if gate.required],
        blocking_gate_ids=[gate.gate_id for gate in plan.gates if gate.blocking],
        escalation_conditions=plan.escalation_conditions,
        risky_artifact_refs=risky_artifact_refs or [],
    )


def verification_has_blocking_failures(artifact: VerificationArtifact) -> bool:
    if not artifact.blocking_gate_ids:
        return any(result != "pass" for result in artifact.results.values())
    for gate_id in artifact.blocking_gate_ids:
        if artifact.results.get(gate_id, "fail") != "pass":
            return True
    return False


def verification_overall_outcome(artifact: VerificationArtifact) -> str:
    return "fail" if verification_has_blocking_failures(artifact) else "pass"


def run_verification_plan(
    plan: VerificationPlan,
    *,
    artifact_store: LocalArtifactStore,
    execute_gate: Callable[[VerificationGate], tuple[int, str]],
    metadata_store: object | None = None,
    cache_store: object | None = None,
    cache_scope_key: str | None = None,
    continue_on_error: bool = False,
) -> VerificationArtifact:
    if not plan.task_id or not plan.run_id:
        msg = "task_id and run_id are required to run verification"
        raise ValueError(msg)

    results: dict[str, str] = {}
    result_artifact_refs: dict[str, str] = {}
    cache_hits: dict[str, bool] = {}
    risky_artifact_refs: list[str] = []

    last_evidence_link = ""
    for gate in plan.gates:
        cache_key = _verification_cache_key(
            mode=plan.mode,
            gate_id=gate.gate_id,
            command=gate.command,
            scope_key=cache_scope_key,
        )
        cached = _cache_get(cache_store, cache_key)
        cache_hit = False
        if isinstance(cached, dict):
            cached_exit = cached.get("exit_code")
            cached_output = cached.get("output")
            if isinstance(cached_exit, int) and isinstance(cached_output, str):
                exit_code, output = cached_exit, cached_output
                cache_hit = True
            else:
                exit_code, output = execute_gate(gate)
        else:
            exit_code, output = execute_gate(gate)
        _cache_put(cache_store, cache_key, {"exit_code": int(exit_code), "output": str(output)})
        cache_hits[gate.gate_id] = cache_hit
        content = output if not cache_hit else f"[cache-hit]\n{output}"
        artifact = artifact_store.write_text(
            task_id=plan.task_id,
            run_id=plan.run_id,
            kind="verification-output",
            label=gate.gate_id,
            content=content,
        )
        result_artifact_refs[gate.gate_id] = artifact.relative_path
        if artifact.risky:
            risky_artifact_refs.append(artifact.relative_path)
        results[gate.gate_id] = "pass" if exit_code == 0 else "fail"
        last_evidence_link = artifact.relative_path
        if exit_code != 0 and gate.blocking and not continue_on_error:
            break

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
                "cache_hits": cache_hits,
            },
        )

    if not last_evidence_link:
        msg = "verification plan must contain at least one runnable gate"
        raise ValueError(msg)

    return build_verification_artifact(
        plan=plan,
        evidence_link=last_evidence_link,
        results=results,
        result_artifact_refs=result_artifact_refs,
        cache_hits=cache_hits,
        risky_artifact_refs=risky_artifact_refs,
    )


def _verification_cache_key(*, mode: str, gate_id: str, command: str, scope_key: str | None) -> str:
    seed = f"{mode}|{gate_id}|{command.strip()}|{scope_key or 'default'}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def _cache_get(cache_store: object | None, key: str) -> dict | None:
    if cache_store is None or not hasattr(cache_store, "get"):
        return None
    try:
        value = cache_store.get(namespace="verification_cache", key=key)
    except TypeError:
        value = cache_store.get(key)
    if isinstance(value, dict):
        return value
    return None


def _cache_put(cache_store: object | None, key: str, payload: dict) -> None:
    if cache_store is None:
        return
    if hasattr(cache_store, "upsert"):
        cache_store.upsert(namespace="verification_cache", key=key, payload=payload)
        return
    if hasattr(cache_store, "set"):
        cache_store.set(key, payload)


def _gates_from_repo_profile(raw: dict, *, mode: str) -> list[VerificationGate]:
    if not isinstance(raw, dict):
        msg = "profile_raw must be an object"
        raise ValueError(msg)
    level = _normalized_level(mode)
    if level == "l1":
        command_groups = ["quick_gate_commands", "test_commands", "contract_commands", "invariant_commands"]
    else:
        command_groups = ["full_gate_commands", "build_commands", "test_commands", "contract_commands", "invariant_commands"]

    required_gate_ids = _required_gate_ids_for_level(level)
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
            if level == "l2" and gate_id == "doctor":
                continue
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
                    blocking=bool(command.get("blocking", command.get("required", True))),
                )
            )
            seen_gate_ids.add(gate_id)

        if seen_gate_ids.issuperset(required_gate_ids):
            break

    additional_commands = raw.get("additional_gate_commands", [])
    if additional_commands is not None:
        if not isinstance(additional_commands, list):
            msg = "additional_gate_commands must be a list"
            raise ValueError(msg)
        for index, command in enumerate(additional_commands):
            if not isinstance(command, dict):
                msg = f"additional_gate_commands[{index}] must be an object"
                raise ValueError(msg)
            if not _command_applies_to_mode(command, mode=mode, level=level):
                continue
            gate_id = _gate_id_for_group("additional_gate_commands", command)
            if gate_id in seen_gate_ids:
                continue
            gate_command = command.get("command")
            if not isinstance(gate_command, str) or not gate_command.strip():
                msg = f"additional_gate_commands[{index}] command is missing a runnable command string"
                raise ValueError(msg)
            required = bool(command.get("required", False))
            gates.append(
                VerificationGate(
                    gate_id=gate_id,
                    canonical_name=gate_id,
                    command=gate_command.strip(),
                    required=required,
                    blocking=bool(command.get("blocking", required)),
                )
            )
            seen_gate_ids.add(gate_id)

    if declared_groups_present:
        if not seen_gate_ids.issuperset(required_gate_ids):
            requirement = _required_gate_ids_text(required_gate_ids)
            msg = f"declared {level} gate contract must provide {requirement} gates"
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
    if group == "additional_gate_commands":
        command_id = command.get("id")
        if isinstance(command_id, str) and command_id.strip():
            return command_id.strip()
        msg = "additional_gate_commands entry requires non-empty id"
        raise ValueError(msg)
    command_id = command.get("id")
    if isinstance(command_id, str) and command_id.strip():
        return command_id.strip()
    return group


def _command_applies_to_mode(command: dict, *, mode: str, level: VerificationLevel) -> bool:
    profiles = command.get("profiles")
    if profiles is None:
        return True
    if not isinstance(profiles, list):
        msg = "additional_gate_commands.profiles must be a list when provided"
        raise ValueError(msg)
    if not profiles:
        return True

    normalized_profiles: set[str] = set()
    for profile in profiles:
        if not isinstance(profile, str) or not profile.strip():
            msg = "additional_gate_commands.profiles entries must be non-empty strings"
            raise ValueError(msg)
        normalized_profiles.add(profile.strip().lower())

    if "*" in normalized_profiles or "all" in normalized_profiles:
        return True
    normalized_mode = _required_mode(mode)
    if normalized_mode.lower() in normalized_profiles:
        return True
    if level == "l1" and ("quick" in normalized_profiles or "l1" in normalized_profiles):
        return True
    if level in {"l2", "l3"} and (
        "full" in normalized_profiles
        or "l2" in normalized_profiles
        or "l3" in normalized_profiles
    ):
        return True
    return False


def _required_mode(value: object) -> VerificationMode:
    if isinstance(value, str):
        normalized = value.strip()
        if normalized in {"quick", "full", "l1", "l2", "l3"}:
            return cast(VerificationMode, normalized)
    msg = f"unsupported verification mode: {value}"
    raise ValueError(msg)


def _normalized_level(mode: str) -> VerificationLevel:
    normalized_mode = _required_mode(mode)
    if normalized_mode in {"quick", "l1"}:
        return "l1"
    if normalized_mode == "l2":
        return "l2"
    return "l3"


def _required_gate_ids_for_level(level: VerificationLevel) -> set[str]:
    if level == "l1":
        return {"test", "contract"}
    return {"build", "test", "contract"}


def _required_gate_ids_text(required_gate_ids: set[str]) -> str:
    ordered = [gate_id for gate_id in ["build", "test", "contract"] if gate_id in required_gate_ids]
    if len(ordered) == 2:
        return f"{ordered[0]} and {ordered[1]}"
    if len(ordered) == 3:
        return f"{ordered[0]}, {ordered[1]}, and {ordered[2]}"
    return ", ".join(ordered)


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
