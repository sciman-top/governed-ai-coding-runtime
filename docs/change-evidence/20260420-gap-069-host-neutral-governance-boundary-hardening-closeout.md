# 20260420 GAP-069 Host-Neutral Governance Boundary Hardening Closeout

## Goal
Close `GAP-069` by hardening host-neutral governance positioning so operator-facing docs cannot drift into host-replacement claims.

## Clarification Trace
- `issue_id`: `gap-069-host-neutral-governance-boundary-hardening`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `n/a`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`

## Scope
- Add an automated over-claim guard in docs verification for operator-facing entry docs.
- Normalize ambiguous over-claim examples in bilingual README wording.
- Mark `GAP-069` as complete in the issue-ready backlog.

## What Changed
1. Added `Invoke-HostReplacementClaimBoundaryScan` to `scripts/verify-repo.ps1`.
   - scans operator-facing entry docs only:
     - `README.md`
     - `README.en.md`
     - `README.zh-CN.md`
     - `docs/quickstart/ai-coding-usage-guide.md`
     - `docs/quickstart/ai-coding-usage-guide.zh-CN.md`
     - `docs/product/codex-cli-app-integration-guide.md`
     - `docs/product/codex-cli-app-integration-guide.zh-CN.md`
   - blocks risky host-replacement claim patterns unless explicit negation is present.
   - wired into `Invoke-DocsChecks`.
2. Updated wording in:
   - `README.en.md`
   - `README.zh-CN.md`
   so high-risk sample lines carry explicit negation and do not parse as positive over-claims.
3. Updated `docs/backlog/issue-ready-backlog.md`:
   - `GAP-069` status moved to complete.
   - `GAP-069` acceptance criteria checkboxes moved to checked.

## Verification
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - `exit_code`: `0`
   - `key_output`: `OK python-bytecode`; `OK python-import`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - `exit_code`: `0`
   - `key_output`: `OK runtime-unittest`; `Ran 250 tests`; `OK`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - `exit_code`: `0`
   - `key_output`: `OK schema-json-parse`; `OK schema-example-validation`; `OK schema-catalog-pairing`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
   - `exit_code`: `0`
   - `key_output`: `OK runtime-status-surface`; `OK codex-capability-ready`; `OK adapter-posture-visible`
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
   - `exit_code`: `0`
   - `key_output`: `OK active-markdown-links`; `OK backlog-yaml-ids`; `OK old-project-name-historical-only`; `OK host-replacement-claim-boundary`
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
   - `exit_code`: `0`
   - `key_output`: `OK powershell-parse`; `OK issue-seeding-render`
7. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
   - `exit_code`: `0`
   - `key_output`: `issue_seed_version=3.7`; `rendered_issue_creation_tasks=3`; `active_task_count=3`

## Risks
- The claim-boundary scan currently covers operator-facing entry docs only. If new entry docs are added later, they must be appended to the scan target list.

## Rollback
- Revert:
  - `scripts/verify-repo.ps1`
  - `README.en.md`
  - `README.zh-CN.md`
  - `docs/backlog/issue-ready-backlog.md`
  - `docs/change-evidence/20260420-gap-069-host-neutral-governance-boundary-hardening-closeout.md`
- Re-run:
  1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
