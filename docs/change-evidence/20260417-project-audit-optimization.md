# 20260417 Project Audit And Optimization

## Goal
- 在动手实现前完成一次仓库级深度审查。
- 补齐根入口、项目级规则、兼容参考文档，并把路线图/积压/issue 脚本更新到当前真实基线。

## Basis
- `README.md`
- `AGENTS.md`
- `docs/README.md`
- `docs/reviews/2026-04-17-project-audit-and-optimization.md`
- `docs/roadmap/governed-agent-platform-90-day-plan.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/mvp-backlog-seeds.md`
- `docs/FinalStateBestPractices.md`
- `scripts/github/create-roadmap-issues.ps1`

## Commands
- `Get-ChildItem -Force`
- `rg --files`
- `Get-Content -Raw docs/README.md`
- `Get-Content -Raw docs/prd/governed-agent-platform-ai-coding-prd.md`
- `Get-Content -Raw docs/architecture/governed-agent-platform-target-architecture.md`
- `Get-Content -Raw docs/architecture/minimum-viable-governance-loop.md`
- `Get-Content -Raw docs/roadmap/governed-agent-platform-90-day-plan.md`
- `Get-Content -Raw docs/backlog/issue-ready-backlog.md`
- `Get-Content -Raw docs/backlog/mvp-backlog-seeds.md`
- `Get-Content -Raw docs/specs/*.md`
- `Get-Content -Raw schemas/jsonschema/*.json | ConvertFrom-Json`
- `Get-Content -Raw scripts/github/create-roadmap-issues.ps1`
- `[System.Management.Automation.Language.Parser]::ParseFile(...)`
- custom PowerShell scans for missing references and spec/schema alignment

## Changes
- Added root `README.md`
- Added project `AGENTS.md`
- Added `docs/FinalStateBestPractices.md` as a compatibility bridge
- Added `docs/reviews/2026-04-17-project-audit-and-optimization.md`
- Updated `docs/README.md`
- Updated `docs/roadmap/governed-agent-platform-90-day-plan.md`
- Updated `docs/backlog/issue-ready-backlog.md`
- Updated `docs/backlog/mvp-backlog-seeds.md`
- Updated `scripts/github/create-roadmap-issues.ps1`
- Added this evidence file

## Verification

### File / Syntax
- Root `README.md` exists
- Root `AGENTS.md` exists
- `docs/FinalStateBestPractices.md` exists
- `docs/reviews/2026-04-17-project-audit-and-optimization.md` exists
- `Parser::ParseFile(create-roadmap-issues.ps1)` returns no parse errors

### Gate Results
- `build`: `gate_na`
  - reason: runtime build entrypoints still do not exist
  - alternative verification: root README, docs index, roadmap, backlog, and issue script were reconciled
- `test`: `gate_na`
  - reason: no test harness yet
  - alternative verification: PowerShell parser check + missing-reference scan
- `contract/invariant`:
  - `Get-ChildItem schemas/jsonschema/*.json | ForEach-Object { Get-Content -Raw $_.FullName | ConvertFrom-Json > $null }` -> `PASS`
  - active local doc references to `docs/FinalStateBestPractices.md` now resolve -> `PASS`
- `hotspot`: `gate_na`
  - reason: no runtime health script yet
  - alternative verification: planning baseline drift review captured in `docs/reviews/2026-04-17-project-audit-and-optimization.md`

## Risks
- 仓库仍未进入可执行实现阶段；`apps/`、`packages/`、`infra/`、`tests/` 仍是下一步任务。
- 仍缺少 sample contract instances 和自动化 schema validation 脚本；当前验证仍偏“结构完整性”而非“端到端可执行性”。
- 当前工作区未见 `.git`，所以回滚依赖快照副本而不是 `git restore`。

## Rollback
- Modified-file snapshots:
  - `docs/change-evidence/snapshots/20260417-project-audit-optimization/docs-README.md` -> restore to `docs/README.md`
  - `docs/change-evidence/snapshots/20260417-project-audit-optimization/docs-roadmap-governed-agent-platform-90-day-plan.md` -> restore to `docs/roadmap/governed-agent-platform-90-day-plan.md`
  - `docs/change-evidence/snapshots/20260417-project-audit-optimization/docs-backlog-issue-ready-backlog.md` -> restore to `docs/backlog/issue-ready-backlog.md`
  - `docs/change-evidence/snapshots/20260417-project-audit-optimization/docs-backlog-mvp-backlog-seeds.md` -> restore to `docs/backlog/mvp-backlog-seeds.md`
  - `docs/change-evidence/snapshots/20260417-project-audit-optimization/scripts-github-create-roadmap-issues.ps1` -> restore to `scripts/github/create-roadmap-issues.ps1`
- Added files can be removed directly after restoring the snapshot copies:
  - `README.md`
  - `AGENTS.md`
  - `docs/FinalStateBestPractices.md`
  - `docs/reviews/2026-04-17-project-audit-and-optimization.md`
  - `docs/change-evidence/20260417-project-audit-optimization.md`

## issue_id / clarification_mode
- `issue_id`: `governed-agent-platform-project-audit-optimization-20260417`
- `attempt_count`: `0`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `plan`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`
