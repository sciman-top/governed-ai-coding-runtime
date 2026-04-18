# 20260418 Hybrid Final-State Deep Audit Fixes

## Change Basis
- Request: deeply review the adjusted strategy, final state, roadmap, plans, and task lists; identify errors between old and new plans; improve and optimize the artifacts.
- Landing point: active docs/spec/schema/contract surfaces for the hybrid final state.
- Target destination: a coherent hybrid final state centered on repo-local declarations, machine-local runtime state, host adapters, `PolicyDecision`, and same-contract verification/delivery.
- Active rule path: `D:\OneDrive\CODE\governed-ai-coding-runtime\AGENTS.md`, carrying `GlobalUser/AGENTS.md v9.39`.
- Clarification trace: `issue_id=hybrid-final-state-deep-audit`, `attempt_count=1`, `clarification_mode=direct_fix`, `clarification_scenario=n/a`, `clarification_questions=[]`, `clarification_answers=[]`.

## Findings
1. `PolicyDecision` was marked complete, but the Python contract omitted the schema-required `schema_version` field.
2. `policy-decision.schema.json` allowed `required_approval_ref` on `allow` and `deny` decisions, while the spec and Python contract treated approval references as escalation-only.
3. `docs/product/positioning-roadmap-competitive-layers.zh-CN.md` still described a Foundation-era current state and an older service-first phase roadmap.
4. `docs/prd/governed-ai-coding-runtime-prd.md` still said the repository was being created greenfield, despite the landed runtime baseline.
5. Several active architecture and interaction docs carried noisy or typo-prone adapter examples that distracted from capability-based adapter semantics.

## Changes
- Added `schema_version` to `PolicyDecision` and `build_policy_decision(...)`.
- Hardened `policy-decision.schema.json` so only `escalate` can carry `required_approval_ref`; `deny` must carry `remediation_hint`.
- Added PolicyDecision parity tests for schema-required fields and schema rejection of non-escalation approval references.
- Added `schemas/examples/policy-decision/escalate-write.example.json` and documented it in `schemas/examples/README.md`.
- Updated the PRD testing decision from greenfield wording to the current local-runtime-baseline posture.
- Updated the Chinese positioning explainer to align current state, active `GAP-035..039` queue, and the hybrid final-state shorthand.
- Cleaned adapter examples in active architecture/spec/product docs so the kernel remains capability-based rather than vendor-list driven.
- Updated the hybrid final-state review with the follow-up findings.

## Platform Diagnostics
| cmd | exit_code | key_output | timestamp |
|---|---:|---|---|
| `codex --version` | `0` | `codex-cli 0.121.0` | `2026-04-18T20:18:28.8844049+08:00` |
| `codex --help` | `0` | commands include `exec`, `review`, `mcp`, `app-server`, `features` | `2026-04-18T20:18:28.8844049+08:00` |
| `codex status` | `1` | `Error: stdin is not a terminal` | `2026-04-18T20:18:28.8844049+08:00` |

`codex status` is recorded as `platform_na`: non-interactive status failed because stdin is not a terminal. Alternative verification is `codex --version`, `codex --help`, this evidence file, and the active repo rule path above. `expires_at`: `n/a`.

## Verification
| gate | cmd | exit_code | key_output | timestamp |
|---|---|---:|---|---|
| targeted | `python -m unittest tests.runtime.test_policy_decision -v` | `0` | `Ran 8 tests`, `OK` | `2026-04-18T20:18:28.8844049+08:00` |
| targeted | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs` | `0` | `OK active-markdown-links`, `OK backlog-yaml-ids`, `OK old-project-name-historical-only` | `2026-04-18T20:18:28.8844049+08:00` |
| targeted | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll` | `0` | `issue_seed_version=3.2`, `rendered_tasks=27`, `rendered_epics=7` | `2026-04-18T20:18:28.8844049+08:00` |
| build | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` | `0` | `OK python-bytecode`, `OK python-import` | `2026-04-18T20:18:28.8844049+08:00` |
| test | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | `0` | `OK runtime-unittest`, `Ran 127 tests`, `OK` | `2026-04-18T20:18:28.8844049+08:00` |
| contract/invariant | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | `0` | `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing` | `2026-04-18T20:18:28.8844049+08:00` |
| hotspot | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` | `0` | `OK runtime-status-surface`, `OK maintenance-policy-visible`, `OK adapter-posture-visible` | `2026-04-18T20:18:28.8844049+08:00` |
| full | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` | `0` | `OK runtime-build`, `OK runtime-unittest`, `OK schema-catalog-pairing`, `OK issue-seeding-render`, `Ran 127 tests`, `OK` | `2026-04-18T20:20:53.6617757+08:00` |

## Risks
- This change does not implement `GAP-035` through `GAP-039`; it removes plan and contract drift before that work starts.
- Legacy write-side runtime code still emits `allowed` / `paused` internally until the planned `GAP-036` normalization work maps those outcomes to `PolicyDecision`.
- Historical ADRs and evidence retain old examples where they describe past decisions; active docs were cleaned instead of rewriting history.

## Rollback
- Revert the changes to `policy_decision.py`, `test_policy_decision.py`, `policy-decision.schema.json`, and `policy-decision-spec.md`.
- Remove `schemas/examples/policy-decision/escalate-write.example.json` and its `schemas/examples/README.md` index entries.
- Revert the PRD, positioning, architecture, interaction, adapter spec, and review wording changes made in this follow-up.
- Delete this evidence file and remove its index entry from `docs/change-evidence/README.md`.
