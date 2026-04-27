# 20260427 Claude Code First-Class Entrypoint Planning

## Goal
- Record the owner-directed decision that Claude Code is a first-class supported host alongside Codex.
- Add `GAP-115..119` as a bounded queue for dual first-class host support.
- Preserve the boundary that first-class support means equal governance outcome, not unverified identical adapter tier.

## Scope
- Added the Claude Code first-class entrypoint implementation plan.
- Added `GAP-115..119` to the human backlog and issue seeds.
- Updated roadmap, plan index, docs index, master outline, current-source policy, claim catalog, and issue-rendering label mapping.
- Kept full `LTP-04 multi-host-first-class` infrastructure trigger-based.

## Changed Files
- `docs/plans/claude-code-first-class-entrypoint-plan.md`
- `docs/plans/optimized-hybrid-final-state-long-term-implementation-plan.md`
- `docs/roadmap/optimized-hybrid-final-state-long-term-roadmap.md`
- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/architecture/current-source-compatibility-policy.json`
- `docs/backlog/README.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/README.md`
- `docs/plans/README.md`
- `docs/product/claim-catalog.json`
- `docs/change-evidence/README.md`
- `scripts/github/create-roadmap-issues.ps1`
- `rules/projects/vps-ssh-launcher/codex/AGENTS.md`
- `rules/projects/vps-ssh-launcher/claude/CLAUDE.md`
- `rules/projects/vps-ssh-launcher/gemini/GEMINI.md`
- `docs/change-evidence/rule-sync-backups/20260427-225108/`

## Decision
Codex and Claude Code are dual first-class entrypoints for this project.

This means:
- rules, gates, evidence, rollback, risk, and claim-drift requirements are equal
- target-repo sync and drift detection must cover Claude Code first-class surfaces
- Claude Code limitations are recorded through adapter tier, `degrade_reason`, and `platform_na`

This does not mean:
- `CLAUDE.md` alone is enforcement
- Claude Code has unverified `native_attach` parity with Codex
- full `LTP-04` infrastructure starts without a later scope fence

## Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
  - status: pass
  - key_output: `issue_seed_version=4.8`, `rendered_tasks=97`, `rendered_issue_creation_tasks=5`, `active_task_count=5`
- `python scripts/verify-current-source-compatibility.py --as-of 2026-04-27`
  - status: pass
  - key_output: `protocol_ids` includes `claude_code_settings_hooks`; source ids include Claude Code memory, settings, and hooks docs
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - status: pass
  - key_output: `OK current-source-compatibility`, `OK claim-drift-sentinel`, `OK claim-evidence-freshness`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
  - status: pass
  - key_output: `OK powershell-parse`, `OK issue-seeding-render`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope Targets -Target vps-ssh-launcher -Apply -Force`
  - status: pass
  - key_output: updated `D:\CODE\vps-ssh-launcher\CLAUDE.md` and `D:\CODE\vps-ssh-launcher\GEMINI.md`; backups written under `docs/change-evidence/rule-sync-backups/20260427-225108/`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json`
  - status: pass
  - key_output: `target_count=5`, `failure_count=0`
- `python scripts/verify-target-repo-governance-consistency.py`
  - status: pass
  - key_output: `target_count=5`, `drift_count=0`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - status: pass
  - key_output: `OK python-bytecode`, `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - status: pass
  - key_output: `Completed 72 test files`; `failures=0`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - status: pass
  - key_output: `OK target-repo-governance-consistency`, `OK agent-rule-sync`, `OK functional-effectiveness`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - status: pass
  - key_output: `OK codex-capability-ready`, `OK adapter-posture-visible`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
  - status: pass
  - key_output: `OK runtime-build`, `Completed 72 test files`, `failures=0`, `OK agent-rule-sync`, `OK post-closeout-queue-sync`, `OK issue-seeding-render`

## Residual Risks
- Claude Code settings/hooks behavior is still only planned until `GAP-116`.
- Claude Code-specific adapter probe evidence is still planned until `GAP-117`.
- Dual first-class host certification remains planned until `GAP-119`; current wording must not claim completed parity before that evidence exists.

## Rollback
Revert this planning slice and remove `GAP-115..119` from backlog, issue seeds, roadmap, claim catalog, and evidence index. Downgrade Claude Code wording back to generic non-Codex compatibility until fresh evidence exists.
