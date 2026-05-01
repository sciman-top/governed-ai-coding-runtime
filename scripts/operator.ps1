param(
  [ValidateSet("Help", "Targets", "Readiness", "RulesDryRun", "RulesApply", "GovernanceBaselineAll", "DailyAll", "ApplyAllFeatures", "FeedbackReport", "EvolutionReview", "ExperienceReview", "EvolutionMaterialize", "CorePrincipleMaterialize", "OperatorUi")]
  [string]$Action = "Help",

  [ValidateSet("quick", "full", "l1", "l2", "l3")]
  [string]$Mode = "quick",

  [string]$Target = "__all__",
  [int]$TargetParallelism = 1,
  [string]$MilestoneTag = "milestone",
  [ValidateSet("zh-CN", "en")]
  [string]$UiLanguage = "zh-CN",
  [switch]$OpenUi,
  [switch]$OnlineSourceCheck,
  [switch]$ConfirmCorePrincipleProposalWrite,
  [switch]$WriteCorePrincipleDryRunReport,
  [switch]$DryRun,
  [switch]$FailFast
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. "$PSScriptRoot\Initialize-WindowsProcessEnvironment.ps1"
Initialize-WindowsProcessEnvironment

if ($TargetParallelism -lt 1) {
  throw "TargetParallelism must be >= 1."
}

$RepoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))

function Resolve-RequiredCommand {
  param([Parameter(Mandatory = $true)][string[]]$Names)

  foreach ($name in $Names) {
    $command = Get-Command $name -ErrorAction SilentlyContinue
    if ($command) {
      return $command.Source
    }
  }

  throw "Required command not found: $($Names -join ' or ')"
}

function Format-ArgumentForDisplay {
  param([Parameter(Mandatory = $true)][string]$Value)

  if ($Value -notmatch '[\s"]') {
    return $Value
  }

  return '"' + ($Value -replace '"', '\"') + '"'
}

function Format-CommandForDisplay {
  param(
    [Parameter(Mandatory = $true)][string]$Executable,
    [string[]]$Arguments = @()
  )

  $parts = @((Format-ArgumentForDisplay -Value $Executable))
  foreach ($argument in $Arguments) {
    $parts += (Format-ArgumentForDisplay -Value $argument)
  }
  return ($parts -join " ")
}

function Invoke-OperatorStep {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][string]$Executable,
    [string[]]$Arguments = @()
  )

  $display = Format-CommandForDisplay -Executable $Executable -Arguments $Arguments
  if ($DryRun) {
    Write-Host ("DRY-RUN {0}: {1}" -f $Name, $display)
    return
  }

  Write-Host ("operator-step: {0}" -f $Name)
  Write-Host ("command: {0}" -f $display)
  & $Executable @Arguments
  $exitCode = $LASTEXITCODE
  if ($null -eq $exitCode) {
    $exitCode = 0
  }
  if ($exitCode -ne 0) {
    throw "Operator step failed: $Name (exit_code=$exitCode)"
  }
}

function Invoke-PwshScript {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][string]$ScriptPath,
    [string[]]$ScriptArguments = @()
  )

  $pwsh = Resolve-RequiredCommand -Names @("pwsh")
  Invoke-OperatorStep `
    -Name $Name `
    -Executable $pwsh `
    -Arguments (@("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $ScriptPath) + $ScriptArguments)
}

function Invoke-PythonScript {
  param(
    [Parameter(Mandatory = $true)][string]$Name,
    [Parameter(Mandatory = $true)][string]$ScriptPath,
    [string[]]$ScriptArguments = @()
  )

  $python = Resolve-RequiredCommand -Names @("python", "python3")
  Invoke-OperatorStep -Name $Name -Executable $python -Arguments (@($ScriptPath) + $ScriptArguments)
}

function Get-OperatorPreflightDecision {
  $fixture = $env:GOVERNED_RUNTIME_OPERATOR_PREFLIGHT_JSON
  if (-not [string]::IsNullOrWhiteSpace($fixture)) {
    try {
      return $fixture | ConvertFrom-Json -Depth 10
    }
    catch {
      throw "Invalid GOVERNED_RUNTIME_OPERATOR_PREFLIGHT_JSON: $($_.Exception.Message)"
    }
  }

  $python = Resolve-RequiredCommand -Names @("python", "python3")
  $scriptPath = Join-Path $RepoRoot "scripts/select-next-work.py"
  $arguments = @($scriptPath, "--as-of", (Get-Date -Format "yyyy-MM-dd"))

  if ($DryRun) {
    Write-Host ("operator-preflight-command: {0}" -f (Format-CommandForDisplay -Executable $python -Arguments $arguments))
  }

  $output = & $python @arguments 2>&1
  $exitCode = $LASTEXITCODE
  if ($null -eq $exitCode) {
    $exitCode = 0
  }
  if ($exitCode -ne 0) {
    $rendered = (($output | ForEach-Object { $_.ToString().TrimEnd() }) -join [Environment]::NewLine).Trim()
    if ([string]::IsNullOrWhiteSpace($rendered)) {
      $rendered = "no output"
    }
    throw "Operator preflight failed (exit_code=$exitCode): $rendered"
  }

  $json = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
  try {
    return $json | ConvertFrom-Json -Depth 20
  }
  catch {
    throw "Operator preflight returned invalid JSON: $($_.Exception.Message)"
  }
}

function Show-OperatorPreflight {
  param(
    [Parameter(Mandatory = $true)]$Decision,
    [Parameter(Mandatory = $true)][string]$ActionName
  )

  $nextAction = [string]$Decision.next_action
  $why = [string]$Decision.why
  $gateState = [string]$Decision.gate_state
  $sourceState = [string]$Decision.source_state
  $evidenceState = [string]$Decision.evidence_state
  Write-Host ("operator-preflight: action={0} next_action={1}" -f $ActionName, $nextAction)
  Write-Host ("operator-preflight-state: gate={0} source={1} evidence={2}" -f $gateState, $sourceState, $evidenceState)
  if (-not [string]::IsNullOrWhiteSpace($why)) {
    Write-Host ("operator-preflight-why: {0}" -f $why)
  }
}

function Assert-OperatorPreflight {
  param(
    [Parameter(Mandatory = $true)][string]$ActionName
  )

  $decision = Get-OperatorPreflightDecision
  Show-OperatorPreflight -Decision $decision -ActionName $ActionName

  $blockingActions = @{
    "Readiness"            = @()
    "DailyAll"             = @("repair_gate_first", "refresh_evidence_first")
    "ApplyAllFeatures"     = @("repair_gate_first", "refresh_evidence_first", "owner_directed_scope_required")
    "EvolutionMaterialize" = @("repair_gate_first", "refresh_evidence_first", "owner_directed_scope_required")
  }

  $blockedBy = @($blockingActions[$ActionName])
  if ($blockedBy.Count -eq 0) {
    return
  }

  $nextAction = [string]$decision.next_action
  if ($blockedBy -contains $nextAction) {
    $message = "operator-preflight blocked: $ActionName requires '$nextAction' first."
    $why = [string]$decision.why
    if (-not [string]::IsNullOrWhiteSpace($why)) {
      $message += " $why"
    }
    throw $message
  }
}

function Get-BatchFlowArguments {
  param(
    [string[]]$BaseArguments = @()
  )

  $arguments = @(Get-TargetSelectionArguments) + @($BaseArguments)
  if ($TargetParallelism -gt 1) {
    $arguments += @("-TargetParallelism", [string]$TargetParallelism)
  }
  if ($FailFast) {
    $arguments += "-FailFast"
  }
  return $arguments
}

function Get-TargetSelectionArguments {
  if ([string]::IsNullOrWhiteSpace($Target) -or $Target -in @("__all__", "all", "*")) {
    return @("-AllTargets")
  }
  return @("-Target", $Target)
}

function Show-OperatorHelp {
  @"
Governed runtime operator entrypoint

长期核心原则:
  综合效率优先 = 少打扰 / 自动连续执行 / 节省 token / 成本 / 高效率
  说明: 当前模型、provider、compact 与自动化细节都只是阶段性实现，不高于该原则本身。

AI 推荐:
  pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action Readiness -OpenUi
  理由: 按本仓硬门禁顺序执行 build -> test -> contract/invariant -> hotspot，并刷新默认中文 operator UI。

常用动作:
  Help                   显示本指南。
  Targets                列出 target catalog 中的 active target repos。
  Readiness              执行 build -> test -> contract/invariant -> hotspot，然后生成 operator UI。
  RulesDryRun            只检查全局/项目级规则漂移，不写入。
  RulesApply             应用规则 manifest 同步，然后复查漂移。
  GovernanceBaselineAll  对所有 active targets 下发治理基线，然后验证目标仓治理一致性。
  DailyAll               对所有 active targets 执行 daily flow，并刷新 operator UI。
  ApplyAllFeatures       执行全部当前目标仓功能、目标仓一致性检查，并刷新 operator UI。
  FeedbackReport         生成 Codex/Claude 功能反馈汇总报告，并写入 runtime artifacts。
  EvolutionReview        执行 runtime 自我演进 dry-run，只生成候选和证据，不自动改代码。
  ExperienceReview       从 AI 编码证据/指标中生成 dry-run knowledge/memory 记录、改进提案和 skill manifest 候选。
  EvolutionMaterialize   将低风险候选物化为 proposal 文件和禁用态 skill candidate 文件，不启用技能。
  CorePrincipleMaterialize 默认只报告核心原则变更候选；加 -ConfirmCorePrincipleProposalWrite 才写 reviewable proposal/manifest，不改 active policy。
                           加 -WriteCorePrincipleDryRunReport 只写审计用 dry-run report，不写 proposal/manifest。
  OperatorUi             只生成本地 operator HTML；加 -OpenUi 会用默认浏览器打开。

UI:
  默认中文: -UiLanguage zh-CN
  English: -UiLanguage en
  输出文件: .runtime/artifacts/operator-ui/index.html
  常驻打开: pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action OperatorUi -OpenUi
  服务状态: pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action Status
  开机自启: pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator-ui-service.ps1 -Action EnableAutoStart

便捷参数:
  -DryRun                只打印将执行的命令，不执行。
  -Target <id|__all__>   目标仓动作默认 __all__，可指定单个 target id。
  -Mode <quick|full|l1|l2|l3>
  -TargetParallelism <n>
  -FailFast
  -OpenUi
  -OnlineSourceCheck      EvolutionReview 时执行轻量在线 source probe；默认不联网。
  -ConfirmCorePrincipleProposalWrite
                          CorePrincipleMaterialize 时才允许写 proposal/manifest；仍不改 active policy。
  -WriteCorePrincipleDryRunReport
                          CorePrincipleMaterialize 时只允许写 dry-run report；不能与 -ConfirmCorePrincipleProposalWrite 同用。
  -UiLanguage <zh-CN|en>
"@ | Write-Host
}

function Invoke-OperatorUi {
  if ($OpenUi) {
    Invoke-PwshScript -Name "operator-ui-service" -ScriptPath "scripts/operator-ui-service.ps1" -ScriptArguments @("-Action", "Start", "-UiLanguage", $UiLanguage, "-OpenUi")
    return
  }

  $arguments = @("--lang", $UiLanguage)
  Invoke-PythonScript -Name "operator-ui" -ScriptPath "scripts/serve-operator-ui.py" -ScriptArguments $arguments
}

function Invoke-Readiness {
  Assert-OperatorPreflight -ActionName "Readiness"
  Invoke-PwshScript -Name "build" -ScriptPath "scripts/build-runtime.ps1"
  Invoke-PwshScript -Name "test" -ScriptPath "scripts/verify-repo.ps1" -ScriptArguments @("-Check", "Runtime")
  Invoke-PwshScript -Name "contract-invariant" -ScriptPath "scripts/verify-repo.ps1" -ScriptArguments @("-Check", "Contract")
  Invoke-PwshScript -Name "hotspot" -ScriptPath "scripts/doctor-runtime.ps1"
  Invoke-OperatorUi
}

function Invoke-Targets {
  Invoke-PwshScript -Name "target-list" -ScriptPath "scripts/runtime-flow-preset.ps1" -ScriptArguments @("-ListTargets")
}

function Invoke-RulesDryRun {
  Invoke-PwshScript -Name "rules-drift-check" -ScriptPath "scripts/sync-agent-rules.ps1" -ScriptArguments @("-Scope", "All", "-FailOnChange")
}

function Invoke-RulesApply {
  Invoke-PwshScript -Name "rules-apply" -ScriptPath "scripts/sync-agent-rules.ps1" -ScriptArguments @("-Scope", "All", "-Apply")
  Invoke-RulesDryRun
}

function Invoke-GovernanceBaselineAll {
  $arguments = Get-BatchFlowArguments -BaseArguments @("-ApplyGovernanceBaselineOnly", "-Json")
  Invoke-PwshScript -Name "governance-baseline-all" -ScriptPath "scripts/runtime-flow-preset.ps1" -ScriptArguments $arguments
  Invoke-PythonScript -Name "target-governance-consistency" -ScriptPath "scripts/verify-target-repo-governance-consistency.py"
}

function Invoke-DailyAll {
  Assert-OperatorPreflight -ActionName "DailyAll"
  $arguments = Get-BatchFlowArguments -BaseArguments @("-FlowMode", "daily", "-Mode", $Mode, "-Json", "-ExportTargetRepoRuns")
  Invoke-PwshScript -Name "daily-all-targets" -ScriptPath "scripts/runtime-flow-preset.ps1" -ScriptArguments $arguments
  Invoke-OperatorUi
}

function Invoke-ApplyAllFeatures {
  Assert-OperatorPreflight -ActionName "ApplyAllFeatures"
  $arguments = Get-BatchFlowArguments -BaseArguments @(
    "-ApplyAllFeatures",
    "-FlowMode",
    "daily",
    "-Mode",
    $Mode,
    "-MilestoneTag",
    $MilestoneTag,
    "-Json"
  )
  Invoke-PwshScript -Name "apply-all-features" -ScriptPath "scripts/runtime-flow-preset.ps1" -ScriptArguments $arguments
  Invoke-PythonScript -Name "target-governance-consistency" -ScriptPath "scripts/verify-target-repo-governance-consistency.py"
  Invoke-OperatorUi
}

function Invoke-FeedbackReport {
  Invoke-PythonScript -Name "host-feedback-summary" -ScriptPath "scripts/host-feedback-summary.py" -ScriptArguments @(
    "--assert-minimum",
    "--write-markdown",
    ".runtime/artifacts/host-feedback-summary/latest.md"
  )
}

function Invoke-EvolutionReview {
  $arguments = @("-WriteArtifacts")
  if ($OnlineSourceCheck) {
    $arguments += "-OnlineSourceCheck"
  }
  Invoke-PwshScript -Name "runtime-evolution-review" -ScriptPath "scripts/evolve-runtime.ps1" -ScriptArguments $arguments
}

function Invoke-ExperienceReview {
  Invoke-PwshScript -Name "ai-coding-experience-review" -ScriptPath "scripts/extract-ai-coding-experience.ps1" -ScriptArguments @("-WriteArtifacts")
}

function Invoke-EvolutionMaterialize {
  Assert-OperatorPreflight -ActionName "EvolutionMaterialize"
  Invoke-PwshScript -Name "runtime-evolution-materialize" -ScriptPath "scripts/materialize-runtime-evolution.ps1" -ScriptArguments @("-Apply")
}

function Invoke-CorePrincipleMaterialize {
  if ($ConfirmCorePrincipleProposalWrite -and $WriteCorePrincipleDryRunReport) {
    throw "ConfirmCorePrincipleProposalWrite and WriteCorePrincipleDryRunReport cannot be used together."
  }

  $arguments = @()
  if ($ConfirmCorePrincipleProposalWrite) {
    $arguments += "-Apply"
  }
  if ($WriteCorePrincipleDryRunReport) {
    $arguments += "-WriteDryRunReport"
  }
  Invoke-PwshScript -Name "core-principle-change-materialize" -ScriptPath "scripts/materialize-core-principle-change.ps1" -ScriptArguments $arguments
}

Push-Location -LiteralPath $RepoRoot
try {
  switch ($Action) {
    "Help" { Show-OperatorHelp }
    "Targets" { Invoke-Targets }
    "Readiness" { Invoke-Readiness }
    "RulesDryRun" { Invoke-RulesDryRun }
    "RulesApply" { Invoke-RulesApply }
    "GovernanceBaselineAll" { Invoke-GovernanceBaselineAll }
    "DailyAll" { Invoke-DailyAll }
    "ApplyAllFeatures" { Invoke-ApplyAllFeatures }
    "FeedbackReport" { Invoke-FeedbackReport }
    "EvolutionReview" { Invoke-EvolutionReview }
    "ExperienceReview" { Invoke-ExperienceReview }
    "EvolutionMaterialize" { Invoke-EvolutionMaterialize }
    "CorePrincipleMaterialize" { Invoke-CorePrincipleMaterialize }
    "OperatorUi" { Invoke-OperatorUi }
  }
}
finally {
  Pop-Location
}
