# 20260427 GAP-107 Non-Codex Adapter Parity Batch

## Goal
- Close `GAP-107` with fresh post-`GAP-106` evidence that at least one non-Codex adapter path passes the same runtime-owned governance chain as Codex.
- Keep the posture honest: the selected generic non-Codex adapter is explicitly degraded to `manual_handoff`, not promoted to live attach.

## Selected Path
- Adapter: `generic.process.cli`
- Host family: generic non-Codex process fallback
- Expected posture: `manual_handoff`
- Expected closure: `fallback_explicit`

## Evidence
- Command:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow.ps1 -FlowMode daily -AttachmentRoot . -AttachmentRuntimeStateRoot "$env:LOCALAPPDATA\governed-ai-coding-runtime\gap-107-non-codex-loop" -Mode quick -TaskId gap-107-non-codex-loop -RunId gap-107-non-codex-loop -CommandId cmd-gap-107-non-codex-loop -RepoBindingId binding-governed-ai-coding-runtime -AdapterId generic.process.cli -WriteTargetPath docs/change-evidence/gap-107-non-codex-loop-probe.txt -WriteTier medium -WriteToolName write_file -RollbackReference "git checkout -- docs/change-evidence/gap-107-non-codex-loop-probe.txt" -WriteContent "GAP-107 non-Codex loop probe executed on 2026-04-27." -ExecuteWriteFlow -Json`
- Result:
  - `overall_status=pass`
  - `summary.flow_kind=manual_handoff`
  - `summary.closure_state=fallback_explicit`
  - `live_loop.fallback_explicit=true`
  - `live_loop.evidence_linkage_complete=true`
  - `session_identity_continuity=true`
  - `resume_identity_continuity=true`
  - `continuation_continuity=true`
- Medium-risk write behavior:
  - `policy_status=escalate`
  - `governance_status=paused`
  - approval decided as `approved`
  - `execution_status=executed`
  - `service_boundary=control-plane`
- Evidence linkage:
  - request adapter events
  - verification output refs
  - write execution artifact
  - adapter events
  - handoff package
  - replay package

## Documentation Updates
- `docs/product/adapter-conformance-parity-matrix.md` now carries a 2026-04-27 snapshot with the fresh Codex canonical runtime-flow evidence from `GAP-106` and the generic non-Codex degraded runtime-flow evidence from `GAP-107`.
- Planning docs now mark `GAP-107` complete and keep `GAP-108..111` active.

## Verification
- The representative runtime-flow command above passed with `overall_status=pass`.
- Follow-up repository gates for this batch are recorded in the commit and must include:
  - `python -m unittest tests.runtime.test_adapter_conformance tests.runtime.test_attached_repo_e2e`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`

## Risks And Boundaries
- This closes parity for one non-Codex degraded path. It does not claim broad first-class host productization for Claude, Gemini, MCP, A2A, or any other host protocol.
- `GAP-108..111` remain active. Complete hybrid final-state closure is still not certified.

## Rollback
- Revert this change set and remove `docs/change-evidence/gap-107-non-codex-loop-probe.txt`.
- Delete the machine-local evidence root if needed: `$env:LOCALAPPDATA\governed-ai-coding-runtime\gap-107-non-codex-loop`.
