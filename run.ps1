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
  日常编码: .\run.ps1 fast
  交付验收: .\run.ps1 readiness -OpenUi
  理由: 日常先跑快速反馈，交付前再跑完整 readiness，避免每次编码都触发 full gate。

常用场景:
  .\run.ps1 help                 显示本短指南。
  .\run.ps1 operator-help        显示 scripts/operator.ps1 的完整动作说明。
  .\run.ps1 fast                 执行 build + quick feedback tests；不替代交付前 readiness。
  .\run.ps1 readiness -OpenUi    执行 build -> test -> contract/invariant -> hotspot，并打开 UI。
  .\run.ps1 ui                   打开本地 operator UI。
  .\run.ps1 rules-check          只检查 Codex/Claude/Gemini 规则漂移，不写入。
  .\run.ps1 rules-apply          同步规则文件，然后复查漂移。
  .\run.ps1 feedback             生成 Codex/Claude 功能反馈汇总。
  .\run.ps1 self-evolution       主动刷新自演化 readiness/eval/variant/recommendation 报告。
  .\run.ps1 self-evolution-promotion
                                 生成自演化晋升控制器报告；不改 policy、不启用 skill、不同步/推送。

示例:
  .\run.ps1 feedback
  .\run.ps1 rules-apply
  .\run.ps1 ui -UiLanguage en

说明:
  这个文件只是便捷入口，真实实现仍在 scripts/operator.ps1。
  未识别的 action 会按原样转交给 scripts/operator.ps1，便于继续使用完整动作名。
"@ | Write-Host
}

function Throw-RetiredRunAction {
  param([Parameter(Mandatory = $true)][string]$Name)

  throw "Retired run action: $Name. Target-repo governance distribution and attachment bridge were removed from this repository. Use readiness, rules-check/rules-apply, feedback, self-evolution, or ui instead."
}

function Resolve-OperatorAction {
  param([Parameter(Mandatory = $true)][string]$Name)

  $normalized = $Name.Trim().ToLowerInvariant()
  $retired = @(
    "targets",
    "list-targets",
    "governance-baseline",
    "baseline",
    "daily",
    "daily-all",
    "apply-all",
    "cleanup",
    "clean",
    "cleanup-targets",
    "uninstall",
    "uninstall-governance",
    "governancebaselineall",
    "dailyall",
    "applyallfeatures",
    "cleanuptargets",
    "uninstallgovernance"
  )
  if ($retired -contains $normalized) {
    Throw-RetiredRunAction -Name $Name
  }

  $aliases = @{
    "operator-help" = "Help"
    "fast" = "FastFeedback"
    "quick" = "FastFeedback"
    "quick-feedback" = "FastFeedback"
    "qf" = "FastFeedback"
    "readiness" = "Readiness"
    "ready" = "Readiness"
    "ui" = "OperatorUi"
    "operator-ui" = "OperatorUi"
    "rules-check" = "RulesDryRun"
    "rules-dry-run" = "RulesDryRun"
    "rules-apply" = "RulesApply"
    "feedback" = "FeedbackReport"
    "feedback-report" = "FeedbackReport"
    "self-evolution" = "SelfEvolutionRecommend"
    "self-evolution-recommend" = "SelfEvolutionRecommend"
    "evolve-self" = "SelfEvolutionRecommend"
    "self-evolution-promotion" = "SelfEvolutionPromotionPlan"
    "self-evolution-promotion-plan" = "SelfEvolutionPromotionPlan"
    "evolve-promotion" = "SelfEvolutionPromotionPlan"
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
