# 2026-04-18 Interactive Session Productization Realignment

## Goal
- Correct the repository-wide product boundary after the earlier local-runtime closeout.
- Reframe `GAP-033` through `GAP-034` as baseline maintenance rather than final lifecycle completion.
- Open the active next-step queue as `Interactive Session Productization / GAP-035` through `GAP-039`.

## Basis
- The local runtime baseline is useful and verifiable, but it does not yet provide:
  - generic target-repo attachment
  - attach-first interactive session bridging
  - a direct Codex adapter
  - capability-tiered integration for non-Codex tools
  - multi-repo trial feedback as a first-class product loop
- The new final-state direction is:
  - generic and portable across repositories
  - interactive AI-session first
  - `attach-first`, `launch-second`
  - repo-local light pack plus machine-wide runtime sidecar
  - Codex-first but not Codex-only

## Changed Documents
- Added:
  - `docs/architecture/generic-target-repo-attachment-blueprint.md`
  - `docs/plans/interactive-session-productization-plan.md`
- Rebased active product and planning docs:
  - `README.md`
  - `README.zh-CN.md`
  - `README.en.md`
  - `docs/README.md`
  - `docs/prd/governed-ai-coding-runtime-prd.md`
  - `docs/product/interaction-model.md`
  - `docs/architecture/README.md`
  - `docs/architecture/governed-ai-coding-runtime-target-architecture.md`
  - `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
  - `docs/backlog/README.md`
  - `docs/backlog/full-lifecycle-backlog-seeds.md`
  - `docs/backlog/issue-ready-backlog.md`
  - `docs/backlog/issue-seeds.yaml`
  - `docs/plans/README.md`
  - `docs/change-evidence/README.md`
  - `scripts/github/create-roadmap-issues.ps1`

## New Active Queue
- `GAP-035` Generic Target-Repo Attachment Pack And Onboarding Flow
- `GAP-036` Attach-First Session Bridge And Governed Interaction Surface
- `GAP-037` Direct Codex Adapter And Evidence Mapping
- `GAP-038` Capability-Tiered Adapter Framework For Multiple AI Tools
- `GAP-039` Multi-Repo Trial Loop And Generic Onboarding Kit

## Verification Commands
| step | command | exit_code | key_output |
|---|---|---:|---|
| build | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` | 0 | `OK python-bytecode`, `OK python-import` |
| runtime test | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` | 0 | `Ran 109 tests`, `OK runtime-unittest` |
| contract | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` | 0 | `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing` |
| hotspot | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` | 0 | `OK runtime-status-surface`, `OK maintenance-policy-visible`, `OK adapter-posture-visible` |
| full verify | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` | 0 | all gates, docs, links, YAML drift, and PowerShell parse checks passed |

## Evidence Summary
- The repository no longer describes `GAP-034` as the final lifecycle endpoint.
- Entry docs now distinguish between the landed local baseline and the true end-state product boundary.
- Roadmap, backlog, issue seeds, and GitHub issue seeding now all point at `Interactive Session Productization / GAP-035..039`.
- The new canonical architecture artifact for future implementation is:
  - `docs/architecture/generic-target-repo-attachment-blueprint.md`

## Risks
- Current runtime docs now distinguish more clearly between landed baseline and final target, which exposes follow-up implementation gaps more explicitly than before.
- `scripts/github/create-roadmap-issues.ps1` still owns issue body text directly; it remains aligned after this change, but future edits can drift unless the script is eventually driven from machine-readable seeds.

## Rollback
- Revert this planning changeset.
- Restore the prior roadmap, backlog, README, and docs index wording that treated `GAP-034` as the lifecycle endpoint.
- Remove the new blueprint and active plan documents if the product direction is intentionally rolled back.

## Evidence Fields
- `issue_id`: `GAP-035..GAP-039`
- `attempt_count`: `1`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `plan`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`
