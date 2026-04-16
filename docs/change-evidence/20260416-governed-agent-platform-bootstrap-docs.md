# 20260416 Governed Agent Platform Bootstrap Docs

## Goal
- 为新项目 `governed-agent-platform` 落地可复用的终态架构文档。
- 为同一项目补齐 90 天实施计划。
- 提供一个可复用的 GitHub issues 创建脚本，便于个人项目初始化 backlog。

## Why Change
- 当前对话已完成架构拍板、阶段计划和 issue 模板设计，但这些内容仍停留在会话上下文中。
- 若不落盘，后续无法复用、审阅、回溯，也无法形成稳定的项目启动资产。
- 本次新增文件属于“架构决策 + 计划 + 工具化脚本”的最小闭环，适合直接沉淀到仓库。

## Basis
- `docs/FinalStateBestPractices.md`
- 本轮对话中已经确认的项目名：`governed-agent-platform`
- 本轮对话中已经确认的输出物：
  - `docs/architecture/governed-agent-platform-target-architecture.md`
  - `docs/roadmap/governed-agent-platform-90-day-plan.md`
  - `scripts/github/create-roadmap-issues.ps1`

## Commands
- `Get-ChildItem -Path docs, scripts -Force | Select-Object FullName, PSIsContainer`
- `Get-Content docs/PLANS.md -TotalCount 120`
- `Get-Content docs/change-evidence/20260415-final-state-best-practices-review.md -TotalCount 120`
- `rg -n "create-roadmap-issues|roadmap|architecture" scripts docs -S`
- `$tokens = $null; $errors = $null; [void][System.Management.Automation.Language.Parser]::ParseFile((Resolve-Path 'scripts/github/create-roadmap-issues.ps1'), [ref]$tokens, [ref]$errors)`
- `powershell -File scripts/verify-kit.ps1`
- `powershell -File tests/repo-governance-hub.optimization.tests.ps1`
- `powershell -File scripts/validate-config.ps1`
- `powershell -File scripts/verify.ps1`
- `powershell -File scripts/doctor.ps1`

## Changes
- Added `docs/architecture/governed-agent-platform-target-architecture.md`
- Added `docs/roadmap/governed-agent-platform-90-day-plan.md`
- Added `scripts/github/create-roadmap-issues.ps1`
- Added this evidence file

## Expected Use
- 架构文档作为新项目的终态拍板说明。
- 90 天计划作为个人项目的落地顺序说明。
- PowerShell 脚本用于自动创建 GitHub milestone、labels、initiative、epics、tasks。

## Verification

### File / Syntax
- `docs/architecture/governed-agent-platform-target-architecture.md` created
- `docs/roadmap/governed-agent-platform-90-day-plan.md` created
- `scripts/github/create-roadmap-issues.ps1` created
- `Parser::ParseFile(create-roadmap-issues.ps1)` -> `PARSE_OK`

### Gate Results
- `build`: `powershell -File scripts/verify-kit.ps1`
  - `PASS`
  - 说明：`custom_governance_distribution.status=PASS`，存在 `_common` baseline 告警但 `actionable_violation_count=0`
- `test`: `powershell -File tests/repo-governance-hub.optimization.tests.ps1`
  - `PASS`
  - `Passed: 158 Failed: 0`
- `contract/invariant`:
  - `powershell -File scripts/validate-config.ps1` -> `PASS`
  - `powershell -File scripts/verify.ps1` -> `PASS`
  - `Verify done. ok=324 fail=0 checked=324`
- `hotspot`: `powershell -File scripts/doctor.ps1`
  - `PASS`
  - `HEALTH=GREEN`

## Risks
- 新脚本依赖 `gh` CLI 和有效登录态；未登录或权限不足时执行会失败。
- 脚本默认创建英文 issue 内容，这是为了降低 Windows PowerShell 编码差异风险。
- GitHub issue 体裁默认是固定模板；若后续要适配不同 issue taxonomy，需要再抽模板层。

## Rollback
- `git restore --source=HEAD -- docs/architecture/governed-agent-platform-target-architecture.md docs/roadmap/governed-agent-platform-90-day-plan.md scripts/github/create-roadmap-issues.ps1 docs/change-evidence/20260416-governed-agent-platform-bootstrap-docs.md`

## issue_id / clarification_mode
- `issue_id`: `governed-agent-platform-bootstrap-docs-20260416`
- `attempt_count`: `0`
- `clarification_mode`: `direct_fix`
- `clarification_scenario`: `plan`
- `clarification_questions`: `[]`
- `clarification_answers`: `[]`
