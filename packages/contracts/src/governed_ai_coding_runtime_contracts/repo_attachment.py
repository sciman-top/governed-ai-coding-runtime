"""Repo attachment binding contract for target repository sessions."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from governed_ai_coding_runtime_contracts.repo_profile import RepoProfile
from governed_ai_coding_runtime_contracts.runtime_roots import resolve_runtime_roots


AdapterPreference = Literal["native_attach", "process_bridge", "manual_handoff"]
DoctorPosture = Literal["missing_light_pack", "invalid_light_pack", "stale_binding", "healthy"]
AttachmentOperation = Literal["created", "validated"]

DEFAULT_SCHEMA_VERSION = "1.0"
LIGHT_PACK_DIR = ".governed-ai"
REPO_PROFILE_FILENAME = "repo-profile.json"
LIGHT_PACK_FILENAME = "light-pack.json"
ADAPTER_PREFERENCES = {"native_attach", "process_bridge", "manual_handoff"}
DOCTOR_POSTURES = {"missing_light_pack", "invalid_light_pack", "stale_binding", "healthy"}
MUTABLE_STATE_ROOT_KEYS = {"tasks", "runs", "approvals", "artifacts", "replay"}


@dataclass(frozen=True, slots=True)
class RepoAttachmentBinding:
    schema_version: str
    binding_id: str
    target_repo_root: str
    repo_profile_ref: str
    light_pack_path: str
    runtime_state_root: str
    mutable_state_roots: dict[str, str]
    adapter_preference: AdapterPreference
    gate_profile: str
    doctor_posture: DoctorPosture


@dataclass(frozen=True, slots=True)
class RepoAttachmentResult:
    operation: AttachmentOperation
    binding: RepoAttachmentBinding
    repo_profile_path: str
    light_pack_path: str
    written_files: list[str]


@dataclass(frozen=True, slots=True)
class RepoAttachmentPosture:
    repo_id: str | None
    binding_id: str | None
    binding_state: DoctorPosture
    light_pack_path: str
    adapter_preference: str | None
    gate_profile: str | None
    reason: str | None = None
    remediation: str | None = None
    fail_closed: bool = False


def build_repo_attachment_binding(
    *,
    binding_id: str,
    target_repo_root: str,
    repo_profile_ref: str,
    light_pack_path: str,
    runtime_state_root: str,
    adapter_preference: AdapterPreference,
    gate_profile: str,
    doctor_posture: DoctorPosture,
    schema_version: str = DEFAULT_SCHEMA_VERSION,
    mutable_state_roots: dict[str, str] | None = None,
) -> RepoAttachmentBinding:
    target_root = _required_path(target_repo_root, "target_repo_root")
    profile_path = _repo_local_path(target_root, repo_profile_ref, "repo_profile_ref")
    light_pack = _repo_local_path(target_root, light_pack_path, "light_pack_path")
    runtime_root = _required_path(runtime_state_root, "runtime_state_root")

    if _is_under(runtime_root, target_root):
        msg = "runtime_state_root must be machine-local and outside target_repo_root"
        raise ValueError(msg)

    resolved_mutable_state_roots = _resolve_mutable_state_roots(
        target_repo_root=target_root,
        runtime_state_root=runtime_root,
        mutable_state_roots=mutable_state_roots,
    )

    return RepoAttachmentBinding(
        schema_version=_required_string(schema_version, "schema_version"),
        binding_id=_required_string(binding_id, "binding_id"),
        target_repo_root=str(target_root),
        repo_profile_ref=str(profile_path),
        light_pack_path=str(light_pack),
        runtime_state_root=str(runtime_root),
        mutable_state_roots=resolved_mutable_state_roots,
        adapter_preference=_required_enum(adapter_preference, "adapter_preference", ADAPTER_PREFERENCES),
        gate_profile=_required_string(gate_profile, "gate_profile"),
        doctor_posture=_required_enum(doctor_posture, "doctor_posture", DOCTOR_POSTURES),
    )


def is_machine_local_state_path(path: str | Path, binding: RepoAttachmentBinding) -> bool:
    candidate = _resolve_path(Path(path), Path(binding.runtime_state_root))
    runtime_root = Path(binding.runtime_state_root).resolve(strict=False)
    target_root = Path(binding.target_repo_root).resolve(strict=False)
    return _is_under(candidate, runtime_root) and not _is_under(candidate, target_root)


def attach_target_repo(
    *,
    target_repo_root: str,
    runtime_state_root: str | None = None,
    repo_id: str,
    display_name: str,
    primary_language: str,
    build_command: str,
    test_command: str,
    contract_command: str,
    adapter_preference: AdapterPreference = "native_attach",
    gate_profile: str = "default",
    overwrite: bool = False,
) -> RepoAttachmentResult:
    target_root = _existing_directory(target_repo_root, "target_repo_root")
    runtime_root = resolve_attachment_runtime_state_root(
        target_repo_root=target_root,
        runtime_state_root=runtime_state_root,
    )
    runtime_root.mkdir(parents=True, exist_ok=True)

    governed_dir = target_root / LIGHT_PACK_DIR
    repo_profile_path = governed_dir / REPO_PROFILE_FILENAME
    light_pack_path = governed_dir / LIGHT_PACK_FILENAME

    if light_pack_path.exists() and not overwrite:
        return validate_light_pack(
            target_repo_root=str(target_root),
            light_pack_path=str(light_pack_path),
            runtime_state_root=str(runtime_root),
        )

    governed_dir.mkdir(parents=True, exist_ok=True)
    written_files: list[str] = []

    if overwrite or not repo_profile_path.exists():
        profile = build_minimal_repo_profile(
            repo_id=repo_id,
            display_name=display_name,
            primary_language=primary_language,
            build_command=build_command,
            test_command=test_command,
            contract_command=contract_command,
        )
        _validate_repo_profile_for_attachment(profile)
        _write_json(repo_profile_path, profile)
        written_files.append(str(repo_profile_path))

    light_pack = build_light_pack_payload(
        repo_id=repo_id,
        adapter_preference=adapter_preference,
        gate_profile=gate_profile,
    )
    _write_json(light_pack_path, light_pack)
    written_files.append(str(light_pack_path))

    result = validate_light_pack(
        target_repo_root=str(target_root),
        light_pack_path=str(light_pack_path),
        runtime_state_root=str(runtime_root),
    )
    return RepoAttachmentResult(
        operation="created",
        binding=result.binding,
        repo_profile_path=result.repo_profile_path,
        light_pack_path=result.light_pack_path,
        written_files=written_files,
    )


def validate_light_pack(
    *,
    target_repo_root: str,
    light_pack_path: str,
    runtime_state_root: str | None = None,
) -> RepoAttachmentResult:
    target_root = _existing_directory(target_repo_root, "target_repo_root")
    runtime_root = resolve_attachment_runtime_state_root(
        target_repo_root=target_root,
        runtime_state_root=runtime_state_root,
    )
    runtime_root.mkdir(parents=True, exist_ok=True)

    resolved_light_pack_path = _repo_local_path(target_root, light_pack_path, "light_pack_path")
    if not resolved_light_pack_path.exists():
        msg = "light_pack_path does not exist"
        raise ValueError(msg)

    light_pack = _load_json_object(resolved_light_pack_path, "light_pack_path")
    pack_kind = _required_string(light_pack.get("pack_kind"), "pack_kind")
    if pack_kind != "repo_attachment_light_pack":
        msg = f"unsupported pack_kind: {pack_kind}"
        raise ValueError(msg)

    repo_profile_ref = _required_string(light_pack.get("repo_profile_ref"), "repo_profile_ref")
    resolved_repo_profile_path = _repo_local_path(target_root, repo_profile_ref, "repo_profile_ref")
    if not resolved_repo_profile_path.exists():
        msg = "repo_profile_ref does not exist"
        raise ValueError(msg)

    profile = _load_json_object(resolved_repo_profile_path, "repo_profile_ref")
    _validate_repo_profile_for_attachment(profile)

    binding = build_repo_attachment_binding(
        binding_id=_required_string(light_pack.get("binding_id"), "binding_id"),
        target_repo_root=str(target_root),
        repo_profile_ref=str(resolved_repo_profile_path),
        light_pack_path=str(resolved_light_pack_path),
        runtime_state_root=str(runtime_root),
        adapter_preference=_required_enum(light_pack.get("adapter_preference"), "adapter_preference", ADAPTER_PREFERENCES),
        gate_profile=_required_string(light_pack.get("gate_profile"), "gate_profile"),
        doctor_posture="healthy",
    )
    return RepoAttachmentResult(
        operation="validated",
        binding=binding,
        repo_profile_path=str(resolved_repo_profile_path),
        light_pack_path=str(resolved_light_pack_path),
        written_files=[],
    )


def build_minimal_repo_profile(
    *,
    repo_id: str,
    display_name: str,
    primary_language: str,
    build_command: str,
    test_command: str,
    contract_command: str,
) -> dict:
    return {
        "schema_version": DEFAULT_SCHEMA_VERSION,
        "repo_id": _required_string(repo_id, "repo_id"),
        "display_name": _required_string(display_name, "display_name"),
        "primary_language": _required_string(primary_language, "primary_language"),
        "repo_root_locator": {"kind": "local_path", "value": "."},
        "rollout_posture": {"current_mode": "observe", "target_mode": "advisory"},
        "build_commands": [{"id": "build", "command": _required_string(build_command, "build_command"), "required": True}],
        "test_commands": [{"id": "test", "command": _required_string(test_command, "test_command"), "required": True}],
        "lint_commands": [],
        "typecheck_commands": [],
        "contract_commands": [
            {"id": "contract", "command": _required_string(contract_command, "contract_command"), "required": True}
        ],
        "invariant_commands": [],
        "risk_defaults": {"default_write_tier": "medium", "blocked_command_patterns": []},
        "approval_defaults": {"medium_write_requires_approval": True, "high_requires_explicit_approval": True},
        "tool_allowlist": ["shell"],
        "path_policies": {"read_allow": ["**/*"], "write_allow": ["src/**", "tests/**", "docs/**"], "blocked": [".git/**"]},
        "branch_policy": {"default_branch": "main", "working_branch_prefix": "governed/", "allow_direct_push": False},
        "delivery_format": {"summary_template": "default", "include_patch": True, "include_pr_body": True},
        "compatibility_signals": [
            {
                "capability": "native_attach",
                "status": "unsupported",
                "degrade_to": "advisory",
                "reason": "native adapter capability has not been detected during attachment",
            }
        ],
    }


def build_light_pack_payload(
    *,
    repo_id: str,
    adapter_preference: AdapterPreference,
    gate_profile: str,
) -> dict:
    return {
        "schema_version": DEFAULT_SCHEMA_VERSION,
        "pack_kind": "repo_attachment_light_pack",
        "binding_id": f"binding-{_required_string(repo_id, 'repo_id')}",
        "repo_profile_ref": f"{LIGHT_PACK_DIR}/{REPO_PROFILE_FILENAME}",
        "adapter_preference": _required_enum(adapter_preference, "adapter_preference", ADAPTER_PREFERENCES),
        "gate_profile": _required_string(gate_profile, "gate_profile"),
        "runtime_contract_refs": {
            "repo_attachment_binding_schema": "schemas/jsonschema/repo-attachment-binding.schema.json",
            "repo_profile_schema": "schemas/jsonschema/repo-profile.schema.json",
        },
    }


def inspect_attachment_posture(
    *,
    target_repo_root: str,
    runtime_state_root: str | None = None,
    light_pack_path: str = f"{LIGHT_PACK_DIR}/{LIGHT_PACK_FILENAME}",
) -> RepoAttachmentPosture:
    target_root = _existing_directory(target_repo_root, "target_repo_root")
    runtime_root = resolve_attachment_runtime_state_root(
        target_repo_root=target_root,
        runtime_state_root=runtime_state_root,
    )
    resolved_light_pack_path = _repo_local_path(target_root, light_pack_path, "light_pack_path")

    if not resolved_light_pack_path.exists():
        return RepoAttachmentPosture(
            repo_id=target_root.name,
            binding_id=None,
            binding_state="missing_light_pack",
            light_pack_path=str(resolved_light_pack_path),
            adapter_preference=None,
            gate_profile=None,
            reason="light pack is missing",
            remediation=_remediation_for_posture(
                binding_state="missing_light_pack",
                target_root=target_root,
                runtime_root=runtime_root,
            ),
            fail_closed=True,
        )

    light_pack: dict = {}
    try:
        light_pack = _load_json_object(resolved_light_pack_path, "light_pack_path")
        repo_profile_ref = _required_string(light_pack.get("repo_profile_ref"), "repo_profile_ref")
        resolved_repo_profile_path = _repo_local_path(target_root, repo_profile_ref, "repo_profile_ref")
        profile = _validate_repo_profile_for_attachment(_load_json_object(resolved_repo_profile_path, "repo_profile_ref"))
        binding = build_repo_attachment_binding(
            binding_id=_required_string(light_pack.get("binding_id"), "binding_id"),
            target_repo_root=str(target_root),
            repo_profile_ref=str(resolved_repo_profile_path),
            light_pack_path=str(resolved_light_pack_path),
            runtime_state_root=str(runtime_root),
            adapter_preference=_required_enum(light_pack.get("adapter_preference"), "adapter_preference", ADAPTER_PREFERENCES),
            gate_profile=_required_string(light_pack.get("gate_profile"), "gate_profile"),
            doctor_posture="healthy",
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return RepoAttachmentPosture(
            repo_id=target_root.name,
            binding_id=_string_or_none(light_pack.get("binding_id")),
            binding_state="invalid_light_pack",
            light_pack_path=str(resolved_light_pack_path),
            adapter_preference=_string_or_none(light_pack.get("adapter_preference")),
            gate_profile=_string_or_none(light_pack.get("gate_profile")),
            reason=str(exc),
            remediation=_remediation_for_posture(
                binding_state="invalid_light_pack",
                target_root=target_root,
                runtime_root=runtime_root,
            ),
            fail_closed=True,
        )

    expected_binding_id = f"binding-{profile.repo_id}"
    if binding.binding_id != expected_binding_id:
        return RepoAttachmentPosture(
            repo_id=profile.repo_id,
            binding_id=binding.binding_id,
            binding_state="stale_binding",
            light_pack_path=binding.light_pack_path,
            adapter_preference=binding.adapter_preference,
            gate_profile=binding.gate_profile,
            reason=f"binding_id should be {expected_binding_id}",
            remediation=_remediation_for_posture(
                binding_state="stale_binding",
                target_root=target_root,
                runtime_root=runtime_root,
            ),
            fail_closed=True,
        )

    return RepoAttachmentPosture(
        repo_id=profile.repo_id,
        binding_id=binding.binding_id,
        binding_state="healthy",
        light_pack_path=binding.light_pack_path,
        adapter_preference=binding.adapter_preference,
        gate_profile=binding.gate_profile,
        remediation=None,
        fail_closed=False,
    )


def _resolve_mutable_state_roots(
    *,
    target_repo_root: Path,
    runtime_state_root: Path,
    mutable_state_roots: dict[str, str] | None,
) -> dict[str, str]:
    if mutable_state_roots is None:
        mutable_state_roots = {key: key for key in MUTABLE_STATE_ROOT_KEYS}
    if not isinstance(mutable_state_roots, dict):
        msg = "mutable_state_roots is required"
        raise ValueError(msg)

    missing = MUTABLE_STATE_ROOT_KEYS - set(mutable_state_roots)
    extra = set(mutable_state_roots) - MUTABLE_STATE_ROOT_KEYS
    if missing:
        msg = f"mutable_state_roots missing keys: {', '.join(sorted(missing))}"
        raise ValueError(msg)
    if extra:
        msg = f"mutable_state_roots unsupported keys: {', '.join(sorted(extra))}"
        raise ValueError(msg)

    resolved: dict[str, str] = {}
    for key in sorted(MUTABLE_STATE_ROOT_KEYS):
        state_root = _resolve_path(Path(_required_string(mutable_state_roots[key], key)), runtime_state_root)
        if _is_under(state_root, target_repo_root):
            msg = f"{key} state root must be machine-local and outside target_repo_root"
            raise ValueError(msg)
        if not _is_under(state_root, runtime_state_root):
            msg = f"{key} state root must stay under runtime_state_root"
            raise ValueError(msg)
        resolved[key] = str(state_root)
    return resolved


def resolve_attachment_runtime_state_root(
    *,
    target_repo_root: str | Path,
    runtime_state_root: str | Path | None,
    host_repo_root: str | Path | None = None,
    compatibility_mode: bool | None = None,
) -> Path:
    target_root = _existing_directory(str(target_repo_root), "target_repo_root")
    if runtime_state_root is not None:
        return _required_path(str(runtime_state_root), "runtime_state_root")
    host_root = Path(host_repo_root).resolve(strict=False) if host_repo_root is not None else target_root.parent
    roots = resolve_runtime_roots(repo_root=host_root, compatibility_mode=compatibility_mode)
    return Path(roots.runtime_root).resolve(strict=False) / "attachments" / target_root.name


def _repo_local_path(target_repo_root: Path, value: str, field_name: str) -> Path:
    candidate = _resolve_path(Path(_required_string(value, field_name)), target_repo_root)
    if not _is_under(candidate, target_repo_root):
        msg = f"{field_name} must stay inside target_repo_root"
        raise ValueError(msg)
    return candidate


def _required_path(value: str, field_name: str) -> Path:
    return Path(_required_string(value, field_name)).resolve(strict=False)


def _resolve_path(path: Path, base: Path) -> Path:
    if not path.is_absolute():
        path = base / path
    return path.resolve(strict=False)


def _existing_directory(value: str, field_name: str) -> Path:
    path = _required_path(value, field_name)
    if not path.is_dir():
        msg = f"{field_name} must be an existing directory"
        raise ValueError(msg)
    return path


def _load_json_object(path: Path, field_name: str) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        msg = f"{field_name} must contain a JSON object"
        raise ValueError(msg)
    return payload


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _validate_repo_profile_for_attachment(raw: dict) -> RepoProfile:
    profile = RepoProfile.from_dict(raw)
    _validate_gate_commands(raw)
    _validate_path_policies(raw)
    return profile


def _validate_gate_commands(raw: dict) -> None:
    for group in ("build_commands", "test_commands", "contract_commands", "invariant_commands"):
        commands = raw.get(group, [])
        if not isinstance(commands, list):
            msg = f"{group} must be a list"
            raise ValueError(msg)
        for index, command in enumerate(commands):
            if not isinstance(command, dict):
                msg = f"{group}[{index}] must be an object"
                raise ValueError(msg)
            _required_string(command.get("id"), f"{group}[{index}].id")
            _required_string(command.get("command"), f"{group}[{index}].command")

    if not raw.get("contract_commands") and not raw.get("invariant_commands"):
        msg = "contract_commands or invariant_commands requires at least one command"
        raise ValueError(msg)


def _validate_path_policies(raw: dict) -> None:
    path_policies = raw.get("path_policies")
    if not isinstance(path_policies, dict):
        msg = "path_policies is required"
        raise ValueError(msg)
    for group in ("read_allow", "write_allow", "blocked"):
        scopes = path_policies.get(group, [])
        if not isinstance(scopes, list):
            msg = f"path_policies.{group} must be a list"
            raise ValueError(msg)
        for index, scope in enumerate(scopes):
            normalized = _required_string(scope, f"path_policies.{group}[{index}]").replace("\\", "/")
            if _is_escaping_scope(normalized):
                msg = f"path_policies.{group}[{index}] must stay repo-relative"
                raise ValueError(msg)


def _is_escaping_scope(scope: str) -> bool:
    return (
        scope == ".."
        or scope.startswith("../")
        or "/../" in scope
        or scope.startswith("/")
        or (len(scope) >= 2 and scope[1] == ":")
    )


def _is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(parent.resolve(strict=False))
    except ValueError:
        return False
    return True


def _required_enum(value: str, field_name: str, valid_values: set[str]) -> str:
    normalized = _required_string(value, field_name)
    if normalized not in valid_values:
        msg = f"unsupported {field_name}: {value}"
        raise ValueError(msg)
    return normalized


def _required_string(value: str, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        msg = f"{field_name} is required"
        raise ValueError(msg)
    return value.strip()


def _string_or_none(value: object) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _remediation_for_posture(*, binding_state: str, target_root: Path, runtime_root: Path) -> str | None:
    docs_ref = "docs/product/target-repo-attachment-flow.md"
    attach_command = (
        "python scripts/attach-target-repo.py "
        f"attach --target-repo-root \"{target_root.as_posix()}\" "
        f"--runtime-state-root \"{runtime_root.as_posix()}\""
    )
    if binding_state == "missing_light_pack":
        return f"{attach_command} (see {docs_ref})"
    if binding_state == "invalid_light_pack":
        return f"Regenerate light pack via attach flow: {attach_command} (see {docs_ref})"
    if binding_state == "stale_binding":
        return f"Refresh binding by re-running attach flow: {attach_command} (see {docs_ref})"
    return None
