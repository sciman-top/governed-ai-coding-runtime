# AI Coding Usage Guide

## Purpose
Show how to use this runtime with Codex/Claude Code style host workflows and what concrete help it provides during real coding tasks.

## Recommended Modes

### Mode A: Governance Sidecar (lowest friction)
Use your host tool normally, and run this runtime for readiness, verification, and traceability.

1. Bootstrap and health checks:
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/install-repo-hooks.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```
2. Inspect runtime/Codex capability posture:
```powershell
python scripts/run-governed-task.py status --json
```

### Mode B: Attach-First Daily Flow (recommended for external repos)
Attach a target repo and run one-command daily governance flow.

1. Attach or validate target repo light pack:
```powershell
python scripts/attach-target-repo.py `
  --target-repo "<target-repo-root>" `
  --runtime-state-root "<machine-local-runtime-state-root>" `
  --repo-id "<repo-id>" `
  --primary-language "<language>" `
  --build-command "<build>" `
  --test-command "<test>" `
  --contract-command "<contract>" `
  --adapter-preference "native_attach"
```
2. Run daily governance chain:
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 `
  -FlowMode "daily" `
  -AttachmentRoot "<target-repo-root>" `
  -AttachmentRuntimeStateRoot "<machine-local-runtime-state-root>" `
  -Mode "quick"
```

### Mode C: Governed Write Flow (for risky edits)
Use runtime-managed request/approve/execute flow for medium/high-risk writes.

1. Evaluate write governance posture:
```powershell
python scripts/run-governed-task.py govern-attachment-write `
  --attachment-root "<target-repo-root>" `
  --attachment-runtime-state-root "<machine-local-runtime-state-root>" `
  --task-id "<task-id>" `
  --tool-name "apply_patch" `
  --target-path "<target-path>" `
  --tier "medium" `
  --rollback-reference "<rollback-ref>" `
  --json
```
2. Approve (if escalated) and execute:
```powershell
python scripts/run-governed-task.py decide-attachment-write `
  --attachment-runtime-state-root "<machine-local-runtime-state-root>" `
  --approval-id "<approval-id>" `
  --decision "approve" `
  --decided-by "operator" `
  --json

python scripts/run-governed-task.py execute-attachment-write `
  --attachment-root "<target-repo-root>" `
  --attachment-runtime-state-root "<machine-local-runtime-state-root>" `
  --task-id "<task-id>" `
  --tool-name "write_file" `
  --target-path "<target-path>" `
  --tier "medium" `
  --rollback-reference "<rollback-ref>" `
  --approval-id "<approval-id>" `
  --content "<content>" `
  --json
```

## Concrete Assistance For AI Coding

| AI coding stage | Runtime assistance | Practical value |
|---|---|---|
| Session readiness | Codex capability probe/readiness and adapter-tier visibility in `status`/`doctor` | detect degrade posture early before execution |
| Repo onboarding | attach-first light-pack generation/validation | consistent repo policy/gate metadata for host sessions |
| Verification | runtime-managed gate flow (`build -> test -> contract/invariant -> hotspot`) | stable acceptance checks and reproducible gate artifacts |
| Risky writes | policy + approval + fail-closed behavior for medium/high tiers | prevents silent high-risk mutations |
| Delivery evidence | evidence/handoff/replay refs linked to task/run | auditable handoff and rollback trail |
| Multi-repo operations | preset/daily flows and multi-repo trial surfaces | repeatable governance posture across repositories |

## Boundary
- This runtime is a governance/runtime layer over upstream hosts, not a replacement host UI.
- Native attach remains environment-dependent and may degrade to `process_bridge` or `manual_handoff`.
- Do not claim universal full takeover across all repos/environments/high-risk workflows.

## Related
- [Use With An Existing Repo](./use-with-existing-repo.md)
- [在现有仓库中使用](./use-with-existing-repo.zh-CN.md)
- [Codex CLI/App Integration Guide](../product/codex-cli-app-integration-guide.md)
- [Codex CLI/App 集成指南](../product/codex-cli-app-integration-guide.zh-CN.md)
