# Target Repo Attachment Flow

## Purpose
Describe how a target repository receives or validates the repo-local light pack used by the machine-local governed runtime.

This flow implements the first concrete `GAP-035` onboarding path. It keeps target repositories declarative and keeps mutable runtime state outside the target repository.

## Default Command
Use:

```powershell
python scripts/attach-target-repo.py `
  --target-repo <target-repo-root> `
  --runtime-state-root <machine-local-runtime-state-root> `
  --repo-id <repo-id> `
  --primary-language <language> `
  --build-command "<build command>" `
  --test-command "<test command>" `
  --contract-command "<contract command>"
```

If `.governed-ai/light-pack.json` already exists, the command validates it by default and does not overwrite it. Use `--overwrite` only when the attachment files should be regenerated intentionally.

## ClassroomToolkit Example
The current branch can already attach an existing external repo such as `D:\OneDrive\CODE\ClassroomToolkit`:

```powershell
python scripts/attach-target-repo.py `
  --target-repo "D:\OneDrive\CODE\ClassroomToolkit" `
  --runtime-state-root "D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\classroomtoolkit" `
  --repo-id "classroomtoolkit" `
  --display-name "ClassroomToolkit" `
  --primary-language "csharp" `
  --build-command "dotnet build ClassroomToolkit.sln -c Debug" `
  --test-command "dotnet test tests/ClassroomToolkit.Tests/ClassroomToolkit.Tests.csproj -c Debug" `
  --contract-command "dotnet test tests/ClassroomToolkit.Tests/ClassroomToolkit.Tests.csproj -c Debug --filter \"FullyQualifiedName~ArchitectureDependencyTests|FullyQualifiedName~InteropHookLifecycleContractTests|FullyQualifiedName~InteropHookEventDispatchContractTests|FullyQualifiedName~GlobalHookServiceLifecycleContractTests|FullyQualifiedName~CrossPageDisplayLifecycleContractTests\"" `
  --adapter-preference "process_bridge"
```

This is the current recommended posture for an external Codex-driven repo: attach-first metadata plus explicit `process_bridge` preference.

## Repo-Local Files
The generated target-repo light pack lives under:

```text
.governed-ai/
  repo-profile.json
  light-pack.json
```

These files are declarative:
- repo profile
- gate command declarations
- path policy scopes
- approval and risk defaults
- adapter preference
- contract references

They must not contain:
- copied runtime implementation code
- task or run state
- approval ledgers
- artifact payloads
- replay bundles

## Machine-Local State
The attachment binding points at a machine-local `runtime_state_root`. The runtime keeps mutable state there:
- tasks
- runs
- approvals
- artifacts
- replay

The `RepoAttachmentBinding` contract rejects runtime state roots inside the target repository.

## Validation Rules
Attachment validation fails when:
- `repo_profile_ref` resolves outside the target repository
- `light_pack_path` resolves outside the target repository
- build, test, contract, or invariant gate declarations have empty ids or commands
- path policies use absolute or parent-escaping scopes
- mutable runtime state is placed under the target repository

## Runtime Consumption
Successful generation or validation returns a `RepoAttachmentBinding` with:
- target repo root
- repo profile path
- light-pack path
- runtime state root
- adapter preference
- gate profile
- doctor posture

This binding is the input for the later doctor/status and session bridge slices.

## Status And Doctor
Status can inspect a specific attached repository without changing existing local-baseline output:

```powershell
python scripts/run-governed-task.py status --json `
  --attachment-root <target-repo-root> `
  --attachment-runtime-state-root <machine-local-runtime-state-root>
```

Doctor can inspect attachment posture explicitly:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1 `
  -AttachmentRoot <target-repo-root> `
  -RuntimeStateRoot <machine-local-runtime-state-root>
```

Attachment posture values:
- `missing_light_pack`
- `invalid_light_pack`
- `stale_binding`
- `healthy`

Remediation behavior:
- `missing_light_pack`: re-run `scripts/attach-target-repo.py attach ...` for the target repo and runtime-state root.
- `invalid_light_pack`: regenerate `.governed-ai/light-pack.json` via the attach flow.
- `stale_binding`: re-run attach flow to refresh `binding_id`.
- `healthy`: no remediation required.

Fail-closed behavior:
- doctor reports unhealthy posture as `FAIL attachment-posture-<state>` and exits non-zero when attachment arguments are provided.
- attachment execution paths should not continue while posture is fail-closed.

## Self-Attachment
The runtime repo itself can also be attached as a target repo.

The rule does not change:
- `runtime_state_root` must stay outside the target repo root

Example:
- invalid: `D:\OneDrive\CODE\governed-ai-coding-runtime\.runtime\attachments\self-runtime`
- valid: `D:\OneDrive\CODE\governed-ai-runtime-state\self-runtime`

## Related
- [Repo Attachment Binding Spec](../specs/repo-attachment-binding-spec.md)
- [Generic Target-Repo Attachment Blueprint](../architecture/generic-target-repo-attachment-blueprint.md)
- [Use With An Existing Repo](../quickstart/use-with-existing-repo.md)
- [在现有仓库中使用](../quickstart/use-with-existing-repo.zh-CN.md)
- [Chinese Version](./target-repo-attachment-flow.zh-CN.md)
