param(
  [Parameter(Position = 0)]
  [string]$Action = "help",

  [Parameter(ValueFromRemainingArguments = $true)]
  [string[]]$RemainingArguments = @()
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$OperatorScript = Join-Path $RepoRoot "scripts/operator.ps1"

function Show-RunHelp {
  @"
Governed runtime short entrypoint

AI 推荐:
  .\run.ps1 readiness -OpenUi
  理由: 一条命令完成本仓 readiness 门禁并打开中文 operator UI。

常用场景:
  .\run.ps1 help                 显示本短指南。
  .\run.ps1 operator-help        显示 scripts/operator.ps1 的完整动作说明。
  .\run.ps1 readiness -OpenUi    执行 build -> test -> contract/invariant -> hotspot，并打开 UI。
  .\run.ps1 ui                   打开本地 operator UI。
  .\run.ps1 targets              列出 active target repos。
  .\run.ps1 rules-check          只检查 Codex/Claude/Gemini 规则漂移，不写入。
  .\run.ps1 rules-apply          同步规则文件，然后复查漂移。
  .\run.ps1 daily                对 active targets 执行 daily flow。
  .\run.ps1 apply-all            执行全部当前目标仓功能。
  .\run.ps1 cleanup-targets      预演清理退役治理文件；加 -ApplyManagedAssetRemoval 才实际删除。
  .\run.ps1 uninstall-governance 预演卸载目标仓治理资产；加 -ApplyManagedAssetRemoval 才实际删除/修补。
  .\run.ps1 feedback             生成 Codex/Claude 功能反馈汇总。

示例:
  .\run.ps1 daily -Mode quick -Target skills-manager -OpenUi
  .\run.ps1 apply-all -Mode quick -TargetParallelism 2 -FailFast
  .\run.ps1 ui -UiLanguage en

说明:
  这个文件只是便捷入口，真实实现仍在 scripts/operator.ps1。
  未识别的 action 会按原样转交给 scripts/operator.ps1，便于继续使用完整动作名。
"@ | Write-Host
}

function Resolve-OperatorAction {
  param([Parameter(Mandatory = $true)][string]$Name)

  $normalized = $Name.Trim().ToLowerInvariant()
  $aliases = @{
    "operator-help" = "Help"
    "readiness" = "Readiness"
    "ready" = "Readiness"
    "ui" = "OperatorUi"
    "operator-ui" = "OperatorUi"
    "targets" = "Targets"
    "list-targets" = "Targets"
    "rules-check" = "RulesDryRun"
    "rules-dry-run" = "RulesDryRun"
    "rules-apply" = "RulesApply"
    "governance-baseline" = "GovernanceBaselineAll"
    "baseline" = "GovernanceBaselineAll"
    "daily" = "DailyAll"
    "daily-all" = "DailyAll"
    "apply-all" = "ApplyAllFeatures"
    "cleanup" = "CleanupTargets"
    "clean" = "CleanupTargets"
    "cleanup-targets" = "CleanupTargets"
    "uninstall" = "UninstallGovernance"
    "uninstall-governance" = "UninstallGovernance"
    "feedback" = "FeedbackReport"
    "feedback-report" = "FeedbackReport"
    "evolution-review" = "EvolutionReview"
    "experience-review" = "ExperienceReview"
    "evolution-materialize" = "EvolutionMaterialize"
    "core-principle" = "CorePrincipleMaterialize"
  }

  if ($aliases.ContainsKey($normalized)) {
    return $aliases[$normalized]
  }

  return $Name
}

if ($Action.Trim().ToLowerInvariant() -in @("help", "-h", "--help", "/?")) {
  Show-RunHelp
  exit 0
}

if (-not (Test-Path -LiteralPath $OperatorScript)) {
  throw "Operator script not found: $OperatorScript"
}

$operatorAction = Resolve-OperatorAction -Name $Action

$pwsh = Get-Command pwsh -ErrorAction SilentlyContinue
if (-not $pwsh) {
  throw "Required command not found: pwsh"
}

& $pwsh.Source -NoProfile -ExecutionPolicy Bypass -File $OperatorScript -Action $operatorAction @RemainingArguments
$exitCode = $LASTEXITCODE
if ($null -eq $exitCode) {
  $exitCode = 0
}
exit $exitCode
