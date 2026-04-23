# Use With An Existing Repo

## Short Answer
Yes, but with the current product boundary.

Today you can use this runtime against an existing repository such as `..\ClassroomToolkit` as a machine-local governance sidecar:
- generate or validate a repo-local light pack under `.governed-ai/`
- keep mutable runtime state machine-local
- inspect attachment posture through `status` and `doctor`
- call the local session bridge for posture and gate-plan requests
- run Codex smoke-trial and multi-repo trial flows against the attached posture

What you do **not** have yet is a universal full-takeover claim across all hosts/environments/repos/high-risk workflows.

## Concrete Assistance For AI Coding In Attached Repos
- pre-execution capability visibility: `status`/`doctor` show adapter posture before risky operations
- runtime-managed gate execution: run canonical verification chain with one bridge surface
- policy and approval for risky writes: medium/high tiers require escalation/approval or fail-closed
- evidence-linked delivery: executed flows emit approval/evidence/handoff/replay refs
- repeatable multi-repo governance: one attach contract, one daily flow, consistent operator behavior

## Recommended Flow

### 1. Attach The Target Repo
From this repository root:

```powershell
python scripts/attach-target-repo.py `
  --target-repo "..\ClassroomToolkit" `
  --runtime-state-root ".runtime\attachments\classroomtoolkit" `
  --repo-id "classroomtoolkit" `
  --display-name "ClassroomToolkit" `
  --primary-language "csharp" `
  --build-command "dotnet build ClassroomToolkit.sln -c Debug" `
  --test-command "dotnet test tests/ClassroomToolkit.Tests/ClassroomToolkit.Tests.csproj -c Debug" `
  --contract-command "dotnet test tests/ClassroomToolkit.Tests/ClassroomToolkit.Tests.csproj -c Debug --filter \"FullyQualifiedName~ArchitectureDependencyTests|FullyQualifiedName~InteropHookLifecycleContractTests|FullyQualifiedName~InteropHookEventDispatchContractTests|FullyQualifiedName~GlobalHookServiceLifecycleContractTests|FullyQualifiedName~CrossPageDisplayLifecycleContractTests\"" `
  --adapter-preference "native_attach"
```

Recommended posture:
- declare `native_attach` as the preferred adapter tier
- keep runtime fallback enabled for `process_bridge` / `manual_handoff` when live probe says native attach is unavailable

PowerShell note:
- if your `--contract-command` contains `|`, wrap the whole value in single quotes, or use a no-filter contract command first and narrow it later.

This creates or validates:

```text
..\ClassroomToolkit\.governed-ai\repo-profile.json
..\ClassroomToolkit\.governed-ai\light-pack.json
```

### 2. Check Attachment Posture

```powershell
python scripts/run-governed-task.py status --json `
  --attachment-root "..\ClassroomToolkit" `
  --attachment-runtime-state-root ".runtime\attachments\classroomtoolkit"
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1 `
  -AttachmentRoot "..\ClassroomToolkit" `
  -RuntimeStateRoot ".runtime\attachments\classroomtoolkit"
```

Expected attachment posture:
- `healthy`
- or one of `missing_light_pack`, `invalid_light_pack`, `stale_binding`

### 3. Use The Session Bridge
Inspect repo posture through the bridge:

```powershell
python scripts/session-bridge.py repo-posture `
  --command-id "cmd-classroom-posture-001" `
  --task-id "task-classroom-001" `
  --repo-binding-id "binding-classroomtoolkit" `
  --adapter-id "codex-cli" `
  --attachment-root "..\ClassroomToolkit" `
  --attachment-runtime-state-root ".runtime\attachments\classroomtoolkit"
```

Run a runtime-managed gate flow (use `--plan-only` if you only need the plan):

```powershell
python scripts/session-bridge.py request-gate `
  --command-id "cmd-classroom-gate-001" `
  --task-id "task-classroom-001" `
  --repo-binding-id "binding-classroomtoolkit" `
  --adapter-id "codex-cli" `
  --mode "quick" `
  --policy-status "allow" `
  --attachment-root "..\ClassroomToolkit" `
  --attachment-runtime-state-root ".runtime\attachments\classroomtoolkit"
```

Execute the declared gate commands inside the attached repo:

```powershell
python scripts/run-governed-task.py verify-attachment `
  --attachment-root "..\ClassroomToolkit" `
  --attachment-runtime-state-root ".runtime\attachments\classroomtoolkit" `
  --mode "quick" `
  --task-id "task-classroom-verify-001" `
  --run-id "run-classroom-verify-001" `
  --json
```

Evaluate write governance posture before real edits:

```powershell
python scripts/run-governed-task.py govern-attachment-write `
  --attachment-root "..\ClassroomToolkit" `
  --attachment-runtime-state-root ".runtime\attachments\classroomtoolkit" `
  --task-id "task-classroom-write-001" `
  --tool-name "apply_patch" `
  --target-path "src/ClassroomToolkit.App/MainWindow.ZOrder.cs" `
  --tier "medium" `
  --rollback-reference "git diff -- src/ClassroomToolkit.App/MainWindow.ZOrder.cs" `
  --json
```

Expected policy posture:
- `allow` for low-tier allowed write paths
- `escalate` with `approval_pending` for medium/high-tier requests
- `deny` for blocked or out-of-scope paths

Approve or reject an escalated write request:

```powershell
python scripts/run-governed-task.py decide-attachment-write `
  --attachment-runtime-state-root ".runtime\attachments\classroomtoolkit" `
  --approval-id "approval-xxxx" `
  --decision "approve" `
  --decided-by "operator" `
  --json
```

Execute an approved write request:

```powershell
python scripts/run-governed-task.py execute-attachment-write `
  --attachment-root "..\ClassroomToolkit" `
  --attachment-runtime-state-root ".runtime\attachments\classroomtoolkit" `
  --task-id "task-classroom-write-001" `
  --tool-name "write_file" `
  --target-path "src/ClassroomToolkit.App/.governed-runtime-probe.txt" `
  --tier "medium" `
  --rollback-reference "git checkout -- src/ClassroomToolkit.App/.governed-runtime-probe.txt" `
  --approval-id "approval-xxxx" `
  --content "governed runtime write probe" `
  --json
```

### 4. One-Command Runtime Check (Recommended For Daily Use)

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-check.ps1 `
  -AttachmentRoot "..\ClassroomToolkit" `
  -AttachmentRuntimeStateRoot ".runtime\attachments\classroomtoolkit" `
  -Mode "quick" `
  -WriteTargetPath "src/ClassroomToolkit.App/MainWindow.ZOrder.cs" `
  -WriteTier "medium" `
  -WriteToolName "write_file" `
  -WriteContent "governed runtime write probe" `
  -ExecuteWriteFlow
```

What this single command runs:
- `status` (with attachment posture)
- `doctor` (with attachment args)
- `session-bridge request-gate`
- `verify-attachment` (unless `-SkipVerifyAttachment`)
- `govern-attachment-write` when `-WriteTargetPath` is provided
- optional `decide-attachment-write` + `execute-attachment-write` when `-ExecuteWriteFlow` is provided

Exit behavior:
- returns exit code `0` only when the chain passes and gate results are all `pass`
- returns exit code `1` when any step fails or any verification gate result is `fail`
- when `-ExecuteWriteFlow` is enabled, output also includes real `handoff_ref` and `replay_ref` for the executed write flow
- runtime-check now emits `summary.session_id` / `summary.resume_id` / `summary.continuation_id` and `live_loop` closure diagnostics (`flow_kind`, continuity booleans, `closure_state`, and linked runtime refs)

Optional identity override flags:
- `-SessionId`
- `-ResumeId`
- `-ContinuationId`

### 5. Two-Mode One-Command Flow

Onboard mode (first-time attach + runtime check):

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 `
  -FlowMode "onboard" `
  -AttachmentRoot "..\ClassroomToolkit" `
  -AttachmentRuntimeStateRoot ".runtime\attachments\classroomtoolkit" `
  -RepoId "classroomtoolkit" `
  -DisplayName "ClassroomToolkit" `
  -PrimaryLanguage "csharp" `
  -Mode "quick"
```

Notes:
- `onboard` now infers missing build/test/contract commands from `-PrimaryLanguage` by default.
- If you want strict explicit-gate mode, add `-RequireExplicitGateCommands` and pass all three commands.

Daily mode (skip attach, run check chain directly):

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 `
  -FlowMode "daily" `
  -AttachmentRoot "..\ClassroomToolkit" `
  -AttachmentRuntimeStateRoot ".runtime\attachments\classroomtoolkit" `
  -Mode "quick"
```

ClassroomToolkit preset shortcut:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-classroomtoolkit.ps1 -FlowMode "daily"
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-classroomtoolkit.ps1 -FlowMode "onboard"
```

Multi-target preset shortcut (`classroomtoolkit` / `github-toolkit` / `self-runtime` / `skills-manager` / `vps-ssh-launcher`):

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -Target "skills-manager" `
  -FlowMode "daily" `
  -SkipVerifyAttachment
```

Preset single source of truth:
- `scripts/runtime-flow-preset.ps1` now reads targets from `docs/targets/target-repos-catalog.json`.
- `docs/targets/target-repos-catalog.json` is the persistent registry for active preset target-repo facts.
- List available targets:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -ListTargets
```

One-command apply across all active targets (includes canonical entrypoint policy + milestone auto-commit baseline):

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -AllTargets `
  -FlowMode "onboard" `
  -Mode "quick" `
  -Overwrite `
  -Json
```

If you only need to force-sync governance features (without running target-repo onboard checks), use:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -AllTargets `
  -ApplyGovernanceBaselineOnly `
  -Json
```

If you need one-click "feature baseline sync + milestone auto-commit" across all active targets, use:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -AllTargets `
  -ApplyFeatureBaselineAndMilestoneCommit `
  -MilestoneTag "milestone" `
  -Json
```

If you need one-click apply for all current features (legacy runtime-flow + feature baseline sync + milestone auto-commit), use:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -AllTargets `
  -ApplyAllFeatures `
  -FlowMode "daily" `
  -MilestoneTag "milestone" `
  -Json
```

If you want to automatically prune old target-repo problem traces after the one-click run:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -AllTargets `
  -ApplyAllFeatures `
  -FlowMode "daily" `
  -MilestoneTag "milestone" `
  -PruneTargetRepoRuns `
  -PruneKeepDays 30 `
  -PruneKeepLatestPerTarget 30 `
  -Json
```

Baseline sync behavior:
- In `onboard` mode, `runtime-flow-preset.ps1` now syncs governance feature blocks from `docs/targets/target-repo-governance-baseline.json` by default.
- The default baseline includes `required_entrypoint_policy` and milestone `auto_commit_policy`.
- If you intentionally need a raw onboard run without sync, pass `-SkipGovernanceBaselineSync`.

Consistency hard gate:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

- Contract checks now include `target-repo-governance-consistency`.
- If any active target repo is missing baseline governance features, the gate fails closed.

### 6. Enable The Canonical Entrypoint Policy

If you want to standardize daily usage around one governed entrypoint, add `required_entrypoint_policy` to the target repo's `.governed-ai/repo-profile.json`.

Recommended starter policy:

```json
"required_entrypoint_policy": {
  "current_mode": "advisory",
  "target_mode": "repo_wide_enforced",
  "canonical_entrypoints": [
    "runtime-flow",
    "runtime-flow-preset"
  ],
  "allow_direct_entrypoints": [
    "run-governed-task.status",
    "session-bridge.inspect_status",
    "session-bridge.inspect_evidence",
    "session-bridge.inspect_handoff",
    "verify-repo"
  ],
  "targeted_enforcement_scopes": [
    "run_quick_gate",
    "run_full_gate",
    "verify_attachment",
    "govern_attachment_write",
    "write_request",
    "write_execute",
    "execute_attachment_write"
  ],
  "promotion_condition_ref": "docs/governance/entrypoint-promotion.md"
}
```

Mode selection:
- `advisory`: record drift, do not block direct entrypoints
- `targeted_enforced`: block direct gate/write entrypoints, keep read-only inspection entrypoints usable
- `repo_wide_enforced`: block all non-canonical non-read-only entrypoints repo-wide

Recommended promotion path:
1. Start with `advisory`
2. Move to `targeted_enforced` after the team is routinely using `runtime-flow` or `runtime-flow-preset`
3. Move to `repo_wide_enforced` only after direct-call exceptions are intentionally allowlisted

Canonical daily commands:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 `
  -FlowMode "daily" `
  -AttachmentRoot "..\ClassroomToolkit" `
  -AttachmentRuntimeStateRoot ".runtime\attachments\classroomtoolkit" `
  -Mode "quick"
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 `
  -Target "skills-manager" `
  -FlowMode "daily" `
  -SkipVerifyAttachment
```

What changes after enforcement:
- direct `session-bridge request-gate`, `run-governed-task verify-attachment`, `govern-attachment-write`, and `execute-attachment-write` calls will surface `entrypoint_policy` in their payload
- when policy mode blocks the call, CLI wrappers return a denial payload instead of silently continuing
- `runtime-check.ps1` surfaces `entrypoint_policy_mode`, `entrypoint_drift`, and `entrypoint_blocked` in its summary

What remains intentionally allowed:
- `run-governed-task.py status`
- `session-bridge.py status`
- `session-bridge.py inspect-evidence`
- `session-bridge.py inspect-handoff`
- `verify-repo.ps1`

## What Happens If Paths Change
- If the target repo moves:
  - the `.governed-ai` files move with it
  - pass the new location as `--attachment-root`
- If the machine-local runtime state root moves:
  - pass the new location as `--attachment-runtime-state-root`
  - or re-run attach intentionally
- If the runtime repo itself moves:
  - the feature semantics do not change
  - but operator commands must point at the runtime scripts in the new location

The behavior is not permanently tied to one old absolute path, but every invocation must use the current valid paths.

Relative-path note:
- `runtime-check.ps1` and `runtime-flow.ps1` accept relative paths and normalize them to absolute paths at runtime.

## Can This Repo Attach To Itself
Yes.

The runtime repo itself can be attached as a target repo, but the same invariant still applies:
- `runtime_state_root` must stay outside the target repo root

Invalid self-attachment example:
- `.runtime\attachments\self-runtime`

Valid self-attachment example:
- `..\governed-ai-runtime-state\self-runtime`

The special case is operational, not architectural:
- no separate contract path exists for self-attachment
- the same attachment, doctor, status, session-bridge, and verify-attachment flow still applies
- the main risk is accidentally placing machine-local runtime state inside the repo, which the validator rejects

### 4. Use Codex-Related Trial Surfaces Honestly
Codex smoke trial:

```powershell
python scripts/run-codex-adapter-trial.py `
  --repo-id "classroomtoolkit" `
  --task-id "task-classroom-codex-trial" `
  --binding-id "binding-classroomtoolkit"
```

Profile-based multi-repo trial:

```powershell
python scripts/run-multi-repo-trial.py `
  --repo-profile "..\ClassroomToolkit\.governed-ai\repo-profile.json"
```

## Current Boundary
- good for attachment, posture inspection, attached gate planning, and executing declared verification gates inside the target repo
- good for establishing a governed repo profile for an external repository and running runtime-managed write governance flows
- still not a claim that every host/environment/repo has full runtime-owned takeover semantics

## Related
- [Target Repo Attachment Flow](../product/target-repo-attachment-flow.md)
- [Target Repo 接入流程](../product/target-repo-attachment-flow.zh-CN.md)
- [Single-Machine Runtime Quickstart](./single-machine-runtime-quickstart.md)
- [单机 Runtime 快速开始](./single-machine-runtime-quickstart.zh-CN.md)
- [Multi-Repo Trial Quickstart](./multi-repo-trial-quickstart.md)
- [多仓试运行快速开始](./multi-repo-trial-quickstart.zh-CN.md)
- [Codex Direct Adapter](../product/codex-direct-adapter.md)
- [Chinese Version](./use-with-existing-repo.zh-CN.md)

