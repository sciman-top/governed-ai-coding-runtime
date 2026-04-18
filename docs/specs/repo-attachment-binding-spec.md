# Repo Attachment Binding Spec

## Status
Draft

## Purpose
Define the runtime contract that binds one target repository to the machine-local governance kernel without copying runtime implementation code into the target repository.

This contract is the first `GAP-035` boundary: it records where repo-local declarative inputs live, where machine-local mutable runtime state lives, and which adapter/gate posture should be attempted for the attached session.

## Required Fields
- schema_version
- binding_id
- target_repo_root
- repo_profile_ref
- light_pack_path
- runtime_state_root
- mutable_state_roots
- adapter_preference
- gate_profile
- doctor_posture

## Enumerations

### adapter_preference
- native_attach
- process_bridge
- manual_handoff

### doctor_posture
- missing_light_pack
- invalid_light_pack
- stale_binding
- healthy

### mutable_state_roots keys
- tasks
- runs
- approvals
- artifacts
- replay

## Field Semantics

### schema_version
Contract version for serialized binding payloads. The current local contract default is `1.0`.

### binding_id
Stable identifier for the target repository attachment.

### target_repo_root
Resolved filesystem root for the target repository being governed.

### repo_profile_ref
Repo-local path to the repository profile declaration. It must resolve inside `target_repo_root`.

### light_pack_path
Repo-local path to the declarative light pack. It must resolve inside `target_repo_root`.

### runtime_state_root
Machine-local root owned by the governance runtime for this attachment. It must not resolve inside `target_repo_root`.

### mutable_state_roots
Machine-local roots for mutable task, run, approval, artifact, and replay state. Each root must stay under `runtime_state_root` and outside `target_repo_root`.

### adapter_preference
Preferred adapter mode for interactive sessions. The binding may prefer native attach, fall back to process bridge, or declare manual handoff.

### gate_profile
Named verification gate profile to use for the target repository attachment.

### doctor_posture
Current attachment posture reported by doctor-compatible surfaces.

## Invariants
- Repo-local declarations must stay inside `target_repo_root`.
- The runtime kernel, task store, run store, approval store, artifact store, and replay store must remain machine-local.
- `runtime_state_root` must not be placed in the target repository.
- `mutable_state_roots` must include exactly `tasks`, `runs`, `approvals`, `artifacts`, and `replay`.
- Each mutable state root must be outside `target_repo_root`.
- Each mutable state root must stay under `runtime_state_root`.
- Schema enum values and Python contract enum values must remain aligned.

## Non-Goals
- generating the light pack
- validating every repo profile command
- launching a host AI coding tool
- replacing PolicyDecision, task lifecycle, evidence bundle, or verification gate contracts
