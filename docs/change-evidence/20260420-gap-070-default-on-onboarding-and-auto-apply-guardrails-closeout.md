# 20260420 GAP-070 Default-On Onboarding And Auto-Apply Guardrails Closeout

## Goal
Close `GAP-070` by reducing onboarding friction through inferred gate defaults while preserving governed safety boundaries for risky writes.

## Clarification Trace
- `issue_id`: `gap-070-default-on-onboarding-and-auto-apply-guardrails`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `n/a`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Scope
- Enable one-command onboarding without requiring manual build/test/contract command stitching for common languages.
- Surface explicit next actions for unresolved attachment posture through runtime-flow output.
- Keep high-risk write behavior unchanged (approval-bound / fail-closed semantics remain enforced by runtime-check and governed-task paths).

## What Changed
1. Updated `scripts/attach-target-repo.py`:
   - `--build-command`, `--test-command`, `--contract-command` are now optional.
   - Added `--infer-gate-defaults` to infer missing gate commands from `--primary-language`.
   - Supports mixed mode (explicit + inferred for missing fields).
   - Emits output fields:
     - `gate_command_source` (`explicit` or `inferred_defaults`)
     - `inferred_gate_defaults_used` (`true`/`false`)
2. Updated `scripts/runtime-flow.ps1`:
   - `onboard` no longer forces explicit gate commands by default.
   - Added `-RequireExplicitGateCommands` for strict mode.
   - Automatically passes `--infer-gate-defaults` during onboard when strict mode is not requested.
   - Emits/prints onboarding guidance:
     - onboard gate command source
     - `next_actions` (from attachment remediation signals in runtime status payload)
3. Added runtime tests in `tests/runtime/test_repo_attachment.py`:
   - verify inferred python defaults are applied and persisted
   - verify missing commands fail when infer flag is absent
4. Updated operator usage docs (bilingual):
   - `docs/quickstart/use-with-existing-repo.md`
   - `docs/quickstart/use-with-existing-repo.zh-CN.md`
   - reflects new default-on inferred onboarding and strict explicit mode option.
5. Updated backlog execution status:
   - `docs/backlog/issue-ready-backlog.md` marks `GAP-070` complete with checked acceptance criteria.

## Verification
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - `exit_code`: `0`
   - `key_output`: `OK python-bytecode`; `OK python-import`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - `exit_code`: `0`
   - `key_output`: `OK runtime-unittest`; `Ran 252 tests`; `OK`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - `exit_code`: `0`
   - `key_output`: `OK schema-json-parse`; `OK schema-example-validation`; `OK schema-catalog-pairing`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
   - `exit_code`: `0`
   - `key_output`: `OK runtime-status-surface`; `OK codex-capability-ready`; `OK adapter-posture-visible`
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
   - `exit_code`: `0`
   - `key_output`: `OK active-markdown-links`; `OK backlog-yaml-ids`; `OK host-replacement-claim-boundary`
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
   - `exit_code`: `0`
   - `key_output`: `OK powershell-parse`; `OK issue-seeding-render`
7. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
   - `exit_code`: `0`
   - `key_output`: `rendered_issue_creation_tasks=2`; `active_task_count=2`; `completed_task_count=53`

## Risks
- Language-default mapping is currently bounded to a fixed common set (`python`, `javascript/typescript/node`, `go`, `dotnet/csharp`). Additional ecosystems require explicit commands or mapping extension.

## Rollback
- Revert:
  - `scripts/attach-target-repo.py`
  - `scripts/runtime-flow.ps1`
  - `tests/runtime/test_repo_attachment.py`
  - `docs/quickstart/use-with-existing-repo.md`
  - `docs/quickstart/use-with-existing-repo.zh-CN.md`
  - `docs/backlog/issue-ready-backlog.md`
  - `docs/change-evidence/20260420-gap-070-default-on-onboarding-and-auto-apply-guardrails-closeout.md`
- Re-run:
  1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
