# 20260418 Governance Runtime Strategy Alignment Closeout

## Change Basis
- User asked to continue automatically until the strategic realignment work was fully closed out.
- Earlier in this branch, `GAP-042`, `GAP-043`, and `GAP-044 Task 6` were already landed, but `GAP-040` Task 1, `GAP-041` Task 2 and Task 3 artifacts, and the final closeout wording were still missing.
- Landing point: research, strategy, ADR, entry docs, backlog posture, roadmap posture, plan index, and closeout evidence.
- Target destination: make `Strategy Alignment Gates / GAP-040` through `GAP-044` complete on the current branch baseline while keeping `Interactive Session Productization / GAP-035` through `GAP-039` as the only active implementation queue.
- Active rule path: `D:\OneDrive\CODE\governed-ai-coding-runtime\AGENTS.md`, carrying `GlobalUser/AGENTS.md v9.39`.
- Clarification trace: `issue_id=gap-040-gap-044-closeout`, `attempt_count=1`, `clarification_mode=direct_fix`, `clarification_scenario=n/a`, `clarification_questions=[]`, `clarification_answers=[]`.

## Files Changed
- Added `docs/research/runtime-governance-borrowing-matrix.md`
- Added `docs/strategy/README.md`
- Added `docs/strategy/positioning-and-competitive-layering.md`
- Added `docs/adrs/0007-source-of-truth-and-runtime-contract-bundle.md`
- Updated `README.md`
- Updated `README.zh-CN.md`
- Updated `README.en.md`
- Updated `docs/README.md`
- Updated `docs/backlog/README.md`
- Updated `docs/backlog/full-lifecycle-backlog-seeds.md`
- Updated `docs/backlog/issue-ready-backlog.md`
- Updated `docs/plans/README.md`
- Updated `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- Updated `docs/change-evidence/README.md`

## Summary
- Added a primary-source borrowing matrix that classifies adjacent products by layer and records explicit `Borrow`, `Avoid`, `Impact`, `Confidence`, and `Source` decisions.
- Added a dedicated strategy directory and a durable positioning document so the README surfaces stay short while the competitive-layering logic remains explicit.
- Added `ADR-0007` to keep `docs/`, `schemas/`, and `packages/contracts/` as source-of-truth authoring surfaces while treating repo-local light packs as generated or validated runtime-consumable attachment surfaces.
- Reconciled readmes, docs index, roadmap, plan index, and backlog posture so `GAP-040` through `GAP-044` are recorded as complete on the current branch baseline instead of still appearing as an active gate queue.
- Reconciled the human-readable backlog so `GAP-040` through `GAP-044` show completed status and completed acceptance criteria.

## Reviewed But Left Unchanged
- `docs/backlog/issue-seeds.yaml`
- `scripts/github/create-roadmap-issues.ps1`

Reason:
- earlier work already encoded the `GAP-035` to `GAP-039` dependency edges on `GAP-042` to `GAP-044`
- `-ValidateOnly -RenderAll` still renders the full task set cleanly, so no additional closeout edits were required for the seed file or seeding script

## Primary Source Set Used For Task 1
- Microsoft Agent Governance Toolkit: <https://opensource.microsoft.com/blog/2026/04/02/introducing-the-agent-governance-toolkit-open-source-runtime-security-for-ai-agents/>
- Open Policy Agent: <https://www.openpolicyagent.org/docs/policy-language>
- Keycard: <https://www.keycard.ai/>, <https://docs.keycard.ai/>
- Coder AI Governance: <https://coder.com/docs/ai-coder/ai-governance>
- Model Context Protocol: <https://modelcontextprotocol.io/specification/2025-06-18/architecture>
- GAAI framework: <https://github.com/Fr-e-d/GAAI-framework>
- OpenHands: <https://docs.openhands.dev/openhands/usage/sandboxes/overview>
- SWE-agent: <https://github.com/SWE-agent/SWE-agent>
- Hermes Agent: <https://github.com/NousResearch/hermes-agent>
- oh-my-codex: <https://github.com/Yeachan-Heo/oh-my-codex>
- oh-my-claudecode: <https://github.com/Yeachan-Heo/oh-my-claudecode>
- NVIDIA NeMo Guardrails: <https://developer.nvidia.com/topics/ai/generative-ai>
- Guardrails AI: <https://guardrailsai.com/guardrails/docs/concepts/validators>

## Targeted Verification
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
```

- Exit code: `0`
- Key output: `OK active-markdown-links`, `OK backlog-yaml-ids`, `OK old-project-name-historical-only`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts
```

- Exit code: `0`
- Key output: `OK powershell-parse`, `OK issue-seeding-render`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll
```

- Exit code: `0`
- Key output: `{"issue_seed_version":"3.2","rendered_tasks":27,"rendered_issue_creation_tasks":27,"rendered_epics":7,"rendered_initiative":true}`

## Full Gate Verification
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

- Exit code: `0`
- Key output: `OK python-bytecode`, `OK python-import`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

- Exit code: `0`
- Key output: `OK runtime-unittest`, `Ran 125 tests`, `OK`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

- Exit code: `0`
- Key output: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

- Exit code: `0`
- Key output: `OK runtime-status-surface`, `OK maintenance-policy-visible`, `OK adapter-posture-visible`

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

- Exit code: `0`
- Key output: `OK runtime-build`, `OK runtime-unittest`, `OK schema-catalog-pairing`, `OK runtime-doctor`, `OK active-markdown-links`, `OK issue-seeding-render`, `Ran 125 tests`, `OK`

```powershell
git diff --check
```

- Exit code: `0`
- Key output: no whitespace errors; line-ending warnings only

## Risks
- The strategy alignment is now closed out as documentation and contract-boundary work; the active implementation queue still lives in `GAP-035` through `GAP-039`.
- The borrowing matrix uses representative primary projects for wrapper and host categories; it is a bounded adoption matrix, not an exhaustive market taxonomy.
- The project now depends more explicitly on strategy documents and ADRs for boundary clarity, so future README edits should continue to link out rather than re-inline large positioning arguments.

## Rollback
- Remove `docs/research/runtime-governance-borrowing-matrix.md`, `docs/strategy/README.md`, `docs/strategy/positioning-and-competitive-layering.md`, and `docs/adrs/0007-source-of-truth-and-runtime-contract-bundle.md`.
- Revert the README, docs index, backlog, roadmap, and plans-index wording changes that mark `GAP-040` through `GAP-044` complete on the current branch baseline.
- Remove this evidence file and its index entry.
