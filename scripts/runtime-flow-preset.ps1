param(
  [string]$Target = "classroomtoolkit",
  [switch]$AllTargets,

  [ValidateSet("onboard", "daily")]
  [string]$FlowMode = "daily",

  [ValidateSet("quick", "full", "l1", "l2", "l3")]
  [string]$Mode = "quick",

  [ValidateSet("allow", "escalate", "deny")]
  [string]$PolicyStatus = "allow",

  [string]$TaskId = ("task-" + (Get-Date -Format "yyyyMMddHHmmss")),
  [string]$RunId = ("run-" + (Get-Date -Format "yyyyMMddHHmmss")),
  [string]$CommandId = ("cmd-" + (Get-Date -Format "yyyyMMddHHmmss")),
  [string]$RepoBindingId = "",
  [string]$AdapterId = "codex-cli",
  [ValidateSet("native_attach", "process_bridge", "manual_handoff")]
  [string]$AdapterPreference = "native_attach",

  [string]$WriteTargetPath = "",
  [ValidateSet("low", "medium", "high")]
  [string]$WriteTier = "medium",
  [string]$WriteToolName = "write_file",
  [string]$WriteToolCommand = "",
  [string]$RollbackReference = "",
  [string]$WriteContent = "governed runtime write probe",
  [switch]$ExecuteWriteFlow,
  [switch]$SkipVerifyAttachment,

  [switch]$Overwrite,
  [switch]$Json,
  [switch]$ListTargets,
  [switch]$FailFast,
  [switch]$SkipGovernanceBaselineSync,
  [switch]$ApplyAllFeatures,
  [switch]$ApplyFeatureBaselineOnly,
  [switch]$ApplyGovernanceBaselineOnly,
  [switch]$ApplyFeatureBaselineAndMilestoneCommit,
  [string]$MilestoneTag = "milestone",
  [switch]$AutoMilestoneGateMode,
  [string]$TaskType = "",
  [switch]$ReleaseCandidate,
  [ValidateSet("full", "fast")]
  [string]$MilestoneGateMode = "full",
  [int]$MilestoneGateTimeoutSeconds = 900,
  [int]$MilestoneCommandTimeoutSeconds = 0,
  [int]$RuntimeFlowTimeoutSeconds = 0,
  [int]$GovernanceSyncTimeoutSeconds = 0,
  [int]$BatchTimeoutSeconds = 0,
  [string]$CatalogPath = "",
  [string]$GovernanceBaselinePath = "",
  [string]$RuntimeFlowPath = "",
  [string]$GovernanceFullCheckPath = "",
  [string]$GovernanceFastCheckPath = "",
  [switch]$PruneTargetRepoRuns,
  [string]$PruneRunsRoot = "",
  [int]$PruneKeepDays = 30,
  [int]$PruneKeepLatestPerTarget = 30,
  [switch]$PruneDryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Initialize-WindowsProcessEnvironment {
  if (-not $IsWindows) {
    return
  }

  $windowsRoot = $env:SystemRoot
  if ([string]::IsNullOrWhiteSpace($windowsRoot)) {
    $windowsRoot = $env:WINDIR
  }
  if ([string]::IsNullOrWhiteSpace($windowsRoot)) {
    $windowsRoot = "C:\Windows"
  }

  if ([string]::IsNullOrWhiteSpace($env:SystemRoot)) {
    $env:SystemRoot = $windowsRoot
  }
  if ([string]::IsNullOrWhiteSpace($env:WINDIR)) {
    $env:WINDIR = $windowsRoot
  }
  if ([string]::IsNullOrWhiteSpace($env:ComSpec)) {
    $cmdPath = Join-Path $windowsRoot "System32\cmd.exe"
    if (Test-Path -LiteralPath $cmdPath) {
      $env:ComSpec = $cmdPath
    }
  }
  if ([string]::IsNullOrWhiteSpace($env:SystemDrive)) {
    $env:SystemDrive = ([System.IO.Path]::GetPathRoot($windowsRoot)).TrimEnd("\")
  }
  if (-not [string]::IsNullOrWhiteSpace($env:USERPROFILE)) {
    $profileRoot = $env:USERPROFILE
    if ([string]::IsNullOrWhiteSpace($env:HOMEDRIVE)) {
      $env:HOMEDRIVE = ([System.IO.Path]::GetPathRoot($profileRoot)).TrimEnd("\")
    }
    if ([string]::IsNullOrWhiteSpace($env:HOMEPATH)) {
      $env:HOMEPATH = $profileRoot.Substring(([System.IO.Path]::GetPathRoot($profileRoot)).Length - 1)
    }
    if ([string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) {
      $env:LOCALAPPDATA = Join-Path $profileRoot "AppData\Local"
    }
    if ([string]::IsNullOrWhiteSpace($env:APPDATA)) {
      $env:APPDATA = Join-Path $profileRoot "AppData\Roaming"
    }
  }
}

Initialize-WindowsProcessEnvironment

function Resolve-AbsolutePath {
  param([Parameter(Mandatory = $true)][string]$PathValue)
  if ([System.IO.Path]::IsPathRooted($PathValue)) {
    return [System.IO.Path]::GetFullPath($PathValue)
  }
  return [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $PathValue))
}

function Expand-TemplateString {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Value,
    [Parameter(Mandatory = $true)]
    [hashtable]$Variables
  )

  $expanded = $Value
  foreach ($name in $Variables.Keys) {
    $expanded = $expanded.Replace('$' + '{' + $name + '}', [string]$Variables[$name])
  }
  return $expanded
}

function Resolve-PythonCommand {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
  }
  if (-not $python) {
    throw "Required command not found: python or python3"
  }
  return $python.Source
}

function ConvertTo-ProcessArgumentString {
  param([string[]]$ArgumentList)

  $quoted = @()
  foreach ($argument in $ArgumentList) {
    $text = [string]$argument
    if ($text -notmatch '[\s"]') {
      $quoted += $text
      continue
    }
    $quoted += ('"' + ($text -replace '\\(?=\\*")', '$0$0' -replace '"', '\"') + '"')
  }
  return ($quoted -join " ")
}

function Invoke-CommandCapture {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Executable,
    [string[]]$Arguments = @(),
    [int]$TimeoutSeconds = 0,
    [string]$WorkingDirectory = ""
  )

  if ($TimeoutSeconds -lt 0) {
    throw "TimeoutSeconds must be >= 0."
  }

  $resolvedWorkingDirectory = ""
  if (-not [string]::IsNullOrWhiteSpace($WorkingDirectory)) {
    $resolvedWorkingDirectory = Resolve-AbsolutePath -PathValue $WorkingDirectory
    if (-not (Test-Path -LiteralPath $resolvedWorkingDirectory)) {
      throw "WorkingDirectory not found: $resolvedWorkingDirectory"
    }
  }

  $timedOut = $false
  $exitCode = 0
  $outputText = ""
  if ($TimeoutSeconds -gt 0) {
    $stdoutPath = [System.IO.Path]::GetTempFileName()
    $stderrPath = [System.IO.Path]::GetTempFileName()
    try {
      $startArgs = @{
        FilePath               = $Executable
        ArgumentList           = (ConvertTo-ProcessArgumentString -ArgumentList $Arguments)
        NoNewWindow            = $true
        PassThru               = $true
        RedirectStandardOutput = $stdoutPath
        RedirectStandardError  = $stderrPath
      }
      if (-not [string]::IsNullOrWhiteSpace($resolvedWorkingDirectory)) {
        $startArgs["WorkingDirectory"] = $resolvedWorkingDirectory
      }

      $process = Start-Process @startArgs
      $completed = $process.WaitForExit($TimeoutSeconds * 1000)
      if (-not $completed) {
        $timedOut = $true
        try {
          Stop-Process -Id $process.Id -Force -ErrorAction Stop
        }
        catch {
        }
        $null = $process.WaitForExit(5000)
        $exitCode = 124
      }
      else {
        $exitCode = [int]$process.ExitCode
      }

      $stdoutText = Get-Content -LiteralPath $stdoutPath -Raw -ErrorAction SilentlyContinue
      $stderrText = Get-Content -LiteralPath $stderrPath -Raw -ErrorAction SilentlyContinue
      $segments = @()
      if (-not [string]::IsNullOrWhiteSpace($stdoutText)) {
        $segments += $stdoutText.TrimEnd()
      }
      if (-not [string]::IsNullOrWhiteSpace($stderrText)) {
        $segments += $stderrText.TrimEnd()
      }
      if ($timedOut) {
        $segments += ("command timed out after {0}s: {1}" -f $TimeoutSeconds, $Executable)
      }
      $outputText = ($segments -join [Environment]::NewLine).TrimEnd()
    }
    finally {
      Remove-Item -LiteralPath $stdoutPath -ErrorAction SilentlyContinue
      Remove-Item -LiteralPath $stderrPath -ErrorAction SilentlyContinue
    }
  }
  else {
    if (-not [string]::IsNullOrWhiteSpace($resolvedWorkingDirectory)) {
      Push-Location -LiteralPath $resolvedWorkingDirectory
    }
    try {
      $output = & $Executable @Arguments 2>&1
      $exitCode = $LASTEXITCODE
      if ($null -eq $exitCode) {
        $exitCode = 0
      }
      $outputText = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).TrimEnd()
    }
    finally {
      if (-not [string]::IsNullOrWhiteSpace($resolvedWorkingDirectory)) {
        Pop-Location
      }
    }
  }

  return [pscustomobject]@{
    exit_code = [int]$exitCode
    output    = $outputText
    timed_out = [bool]$timedOut
    timeout_seconds = [int]$TimeoutSeconds
  }
}

function Write-BatchProgressLine {
  param(
    [Parameter(Mandatory = $true)]
    [bool]$Enabled,
    [Parameter(Mandatory = $true)]
    [string]$TargetName,
    [Parameter(Mandatory = $true)]
    [string]$Stage,
    [Parameter(Mandatory = $true)]
    [string]$Status,
    [string]$Detail = ""
  )

  if (-not $Enabled) {
    return
  }

  $line = "batch-progress: target={0} stage={1} status={2} at={3}" -f $TargetName, $Stage, $Status, (Get-Date).ToString("o")
  if (-not [string]::IsNullOrWhiteSpace($Detail)) {
    $line = "{0} {1}" -f $line, $Detail.Trim()
  }
  Write-Host $line
}

function Resolve-MilestoneGateStrategy {
  param(
    [Parameter(Mandatory = $true)]
    [bool]$AutoEnabled,
    [Parameter(Mandatory = $true)]
    [ValidateSet("full", "fast")]
    [string]$RequestedMode,
    [Parameter(Mandatory = $true)]
    [ValidateSet("onboard", "daily")]
    [string]$FlowModeValue,
    [Parameter(Mandatory = $true)]
    [ValidateSet("quick", "full", "l1", "l2", "l3")]
    [string]$VerificationModeValue,
    [Parameter(Mandatory = $true)]
    [ValidateSet("allow", "escalate", "deny")]
    [string]$PolicyStatusValue,
    [Parameter(Mandatory = $true)]
    [ValidateSet("low", "medium", "high")]
    [string]$WriteTierValue,
    [Parameter(Mandatory = $true)]
    [bool]$ExecuteWriteFlowEnabled,
    [Parameter(Mandatory = $true)]
    [bool]$ReleaseCandidateEnabled,
    [string]$TaskTypeValue = ""
  )

  if (-not $AutoEnabled) {
    return [pscustomobject]@{
      mode   = $RequestedMode
      source = "manual"
      reason = "manual_override"
    }
  }

  $normalizedTaskType = ""
  if (-not [string]::IsNullOrWhiteSpace($TaskTypeValue)) {
    $normalizedTaskType = $TaskTypeValue.Trim().ToLowerInvariant()
  }
  $highRiskTaskTypes = @("release", "schema", "contract", "migration", "security", "hotfix", "incident", "rollback")
  $lowRiskTaskTypes = @("docs", "documentation", "chore", "style", "comment", "spelling", "format", "refactor_low_risk")

  if ($ReleaseCandidateEnabled) {
    return [pscustomobject]@{
      mode   = "full"
      source = "auto"
      reason = "release_candidate_full"
    }
  }
  if ($FlowModeValue -eq "onboard") {
    return [pscustomobject]@{
      mode   = "full"
      source = "auto"
      reason = "onboard_requires_full"
    }
  }
  if ($VerificationModeValue -in @("full", "l3")) {
    return [pscustomobject]@{
      mode   = "full"
      source = "auto"
      reason = "verification_mode_high"
    }
  }
  if ($PolicyStatusValue -ne "allow") {
    return [pscustomobject]@{
      mode   = "full"
      source = "auto"
      reason = "policy_not_allow"
    }
  }
  if ($WriteTierValue -eq "high") {
    return [pscustomobject]@{
      mode   = "full"
      source = "auto"
      reason = "write_tier_high"
    }
  }
  if ($ExecuteWriteFlowEnabled) {
    return [pscustomobject]@{
      mode   = "full"
      source = "auto"
      reason = "execute_write_flow_enabled"
    }
  }
  if (-not [string]::IsNullOrWhiteSpace($normalizedTaskType)) {
    if ($normalizedTaskType -in $highRiskTaskTypes) {
      return [pscustomobject]@{
        mode   = "full"
        source = "auto"
        reason = "task_type_high_risk"
      }
    }
    if ($normalizedTaskType -in $lowRiskTaskTypes) {
      return [pscustomobject]@{
        mode   = "fast"
        source = "auto"
        reason = "task_type_low_risk"
      }
    }
    if ($normalizedTaskType -eq "bugfix") {
      return [pscustomobject]@{
        mode   = "fast"
        source = "auto"
        reason = "task_type_bugfix"
      }
    }
  }

  if (($FlowModeValue -eq "daily") -and ($VerificationModeValue -in @("quick", "l1", "l2")) -and ($WriteTierValue -in @("low", "medium"))) {
    return [pscustomobject]@{
      mode   = "fast"
      source = "auto"
      reason = "daily_low_to_medium_risk"
    }
  }

  return [pscustomobject]@{
    mode   = "full"
    source = "auto"
    reason = "fallback_full"
  }
}

function Try-ParseJson {
  param([string]$Raw)

  if ([string]::IsNullOrWhiteSpace($Raw)) {
    return $null
  }

  try {
    return ($Raw | ConvertFrom-Json -Depth 80)
  }
  catch {
    return $null
  }
}

function Invoke-PruneTargetRepoRuns {
  param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [Parameter(Mandatory = $true)]
    [string]$RunsRoot,
    [Parameter(Mandatory = $true)]
    [string]$PythonCommand,
    [Parameter(Mandatory = $true)]
    [int]$KeepDays,
    [Parameter(Mandatory = $true)]
    [int]$KeepLatestPerTarget,
    [Parameter(Mandatory = $true)]
    [bool]$DryRun
  )

  $pruneScriptPath = Join-Path $RepoRoot "scripts\prune-target-repo-runs.py"
  if (-not (Test-Path -LiteralPath $pruneScriptPath)) {
    return [pscustomobject]@{
      status    = "fail"
      reason    = "prune_script_not_found"
      exit_code = 1
      runs_root = $RunsRoot
      payload   = $null
      output    = ("prune script not found: {0}" -f $pruneScriptPath)
    }
  }

  $args = @(
    $pruneScriptPath,
    "--runs-root", $RunsRoot,
    "--keep-days", [string]$KeepDays,
    "--keep-latest-per-target", [string]$KeepLatestPerTarget
  )
  if ($DryRun) {
    $args += "--dry-run"
  }

  $result = Invoke-CommandCapture -Executable $PythonCommand -Arguments $args
  $payload = Try-ParseJson -Raw $result.output
  $status = if ($result.exit_code -eq 0) { "pass" } else { "fail" }
  $reason = if ($status -eq "pass") { "ok" } else { "prune_failed" }
  if ($payload -and $payload.PSObject.Properties.Name -contains "reason" -and -not [string]::IsNullOrWhiteSpace([string]$payload.reason)) {
    $reason = [string]$payload.reason
  }

  return [pscustomobject]@{
    status    = $status
    reason    = $reason
    exit_code = $result.exit_code
    runs_root = $RunsRoot
    payload   = $payload
    output    = $result.output
  }
}

function Convert-PruneResultForJson {
  param(
    [Parameter(Mandatory = $true)]
    [object]$PruneResult,
    [Parameter(Mandatory = $true)]
    [int]$KeepDays,
    [Parameter(Mandatory = $true)]
    [int]$KeepLatestPerTarget,
    [Parameter(Mandatory = $true)]
    [bool]$DryRun
  )

  $summary = $null
  if ($PruneResult.payload -and $PruneResult.payload.PSObject.Properties.Name -contains "summary") {
    $summary = $PruneResult.payload.summary
  }

  return [ordered]@{
    status                 = [string]$PruneResult.status
    reason                 = [string]$PruneResult.reason
    exit_code              = [int]$PruneResult.exit_code
    runs_root              = [string]$PruneResult.runs_root
    keep_days              = $KeepDays
    keep_latest_per_target = $KeepLatestPerTarget
    dry_run                = $DryRun
    total_run_files        = $(if ($summary -and ($summary.PSObject.Properties.Name -contains "total_run_files")) { [int]$summary.total_run_files } else { 0 })
    kept                   = $(if ($summary -and ($summary.PSObject.Properties.Name -contains "kept")) { [int]$summary.kept } else { 0 })
    delete_candidates      = $(if ($summary -and ($summary.PSObject.Properties.Name -contains "delete_candidates")) { [int]$summary.delete_candidates } else { 0 })
    deleted                = $(if ($summary -and ($summary.PSObject.Properties.Name -contains "deleted")) { [int]$summary.deleted } else { 0 })
    failed_deletions       = $(if ($summary -and ($summary.PSObject.Properties.Name -contains "failed_deletions")) { [int]$summary.failed_deletions } else { 0 })
  }
}

function Load-TargetConfigMap {
  param(
    [Parameter(Mandatory = $true)]
    [string]$CatalogPath,
    [Parameter(Mandatory = $true)]
    [hashtable]$Variables
  )

  if (-not (Test-Path -LiteralPath $CatalogPath)) {
    throw "Target catalog not found: $CatalogPath"
  }

  $catalog = Get-Content -Raw -LiteralPath $CatalogPath | ConvertFrom-Json
  if (-not ($catalog -and $catalog.targets)) {
    throw "Target catalog is missing 'targets': $CatalogPath"
  }

  $map = @{}
  foreach ($entry in $catalog.targets.PSObject.Properties) {
    $name = [string]$entry.Name
    $rawConfig = $entry.Value
    $map[$name] = @{
      AttachmentRoot = Resolve-AbsolutePath -PathValue (Expand-TemplateString -Value ([string]$rawConfig.attachment_root) -Variables $Variables)
      AttachmentRuntimeStateRoot = Resolve-AbsolutePath -PathValue (Expand-TemplateString -Value ([string]$rawConfig.attachment_runtime_state_root) -Variables $Variables)
      RepoId = [string]$rawConfig.repo_id
      DisplayName = [string]$rawConfig.display_name
      PrimaryLanguage = [string]$rawConfig.primary_language
      BuildCommand = [string]$rawConfig.build_command
      TestCommand = [string]$rawConfig.test_command
      ContractCommand = [string]$rawConfig.contract_command
    }
  }

  return $map
}

function Invoke-GovernanceBaselineSync {
  param(
    [Parameter(Mandatory = $true)]
    [string]$TargetName,
    [Parameter(Mandatory = $true)]
    [hashtable]$TargetConfig,
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [Parameter(Mandatory = $true)]
    [string]$BaselinePath,
    [Parameter(Mandatory = $true)]
    [string]$PythonCommand,
    [int]$CommandTimeoutSeconds = 0
  )

  $syncScriptPath = Join-Path $RepoRoot "scripts\apply-target-repo-governance.py"
  if (-not (Test-Path -LiteralPath $syncScriptPath)) {
    throw "Missing apply-target-repo-governance.py at $syncScriptPath"
  }

  $args = @(
    $syncScriptPath,
    "--target-repo", $TargetConfig.AttachmentRoot,
    "--baseline-path", $BaselinePath
  )
  $result = Invoke-CommandCapture `
    -Executable $PythonCommand `
    -Arguments $args `
    -TimeoutSeconds $CommandTimeoutSeconds `
    -WorkingDirectory $RepoRoot
  $payload = Try-ParseJson -Raw $result.output
  $status = if ($result.exit_code -eq 0) { "pass" } else { "fail" }
  $reason = if ($status -eq "pass") {
    "ok"
  }
  elseif ($result.timed_out) {
    "apply_timed_out"
  }
  else {
    "apply_failed"
  }

  return [pscustomobject]@{
    target    = $TargetName
    status    = $status
    reason    = $reason
    exit_code = $result.exit_code
    payload   = $payload
    output    = $result.output
  }
}

function Invoke-TargetPresetFlow {
  param(
    [Parameter(Mandatory = $true)]
    [string]$TargetName,
    [Parameter(Mandatory = $true)]
    [hashtable]$TargetConfig,
    [Parameter(Mandatory = $true)]
    [string]$RuntimeFlowPathResolved,
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [Parameter(Mandatory = $true)]
    [string]$GovernanceBaselinePathResolved,
    [Parameter(Mandatory = $true)]
    [bool]$ShouldSyncGovernanceBaseline,
    [Parameter(Mandatory = $true)]
    [bool]$IsBatchMode,
    [Parameter(Mandatory = $true)]
    [string]$PythonCommand,
    [int]$RuntimeFlowCommandTimeoutSeconds = 0,
    [int]$GovernanceSyncCommandTimeoutSeconds = 0,
    [bool]$EmitProgress = $false
  )

  $flowStartedAt = Get-Date
  Write-BatchProgressLine -Enabled $EmitProgress -TargetName $TargetName -Stage "runtime_flow" -Status "start" -Detail ("flow_mode={0}" -f $FlowMode)

  $taskIdForTarget = if ($IsBatchMode) { "$TaskId-$TargetName" } else { $TaskId }
  $runIdForTarget = if ($IsBatchMode) { "$RunId-$TargetName" } else { $RunId }
  $commandIdForTarget = if ($IsBatchMode) { "$CommandId-$TargetName" } else { $CommandId }

  $flowArgs = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", $RuntimeFlowPathResolved,
    "-EntrypointId", "runtime-flow-preset",
    "-FlowMode", $FlowMode,
    "-AttachmentRoot", $TargetConfig.AttachmentRoot,
    "-AttachmentRuntimeStateRoot", $TargetConfig.AttachmentRuntimeStateRoot,
    "-Mode", $Mode,
    "-PolicyStatus", $PolicyStatus,
    "-TaskId", $taskIdForTarget,
    "-RunId", $runIdForTarget,
    "-CommandId", $commandIdForTarget,
    "-AdapterId", $AdapterId
  )

  if (-not [string]::IsNullOrWhiteSpace($RepoBindingId)) {
    $flowArgs += @("-RepoBindingId", $RepoBindingId)
  }
  if (-not [string]::IsNullOrWhiteSpace($WriteTargetPath)) {
    $flowArgs += @("-WriteTargetPath", $WriteTargetPath, "-WriteTier", $WriteTier, "-WriteToolName", $WriteToolName, "-WriteContent", $WriteContent)
    if (-not [string]::IsNullOrWhiteSpace($WriteToolCommand)) {
      $flowArgs += @("-WriteToolCommand", $WriteToolCommand)
    }
  }
  if (-not [string]::IsNullOrWhiteSpace($RollbackReference)) {
    $flowArgs += @("-RollbackReference", $RollbackReference)
  }
  if ($ExecuteWriteFlow) {
    $flowArgs += "-ExecuteWriteFlow"
  }
  if ($SkipVerifyAttachment) {
    $flowArgs += "-SkipVerifyAttachment"
  }
  if ($FlowMode -eq "onboard") {
    $flowArgs += @(
      "-RepoId", $TargetConfig.RepoId,
      "-DisplayName", $TargetConfig.DisplayName,
      "-PrimaryLanguage", $TargetConfig.PrimaryLanguage,
      "-BuildCommand", $TargetConfig.BuildCommand,
      "-TestCommand", $TargetConfig.TestCommand,
      "-ContractCommand", $TargetConfig.ContractCommand,
      "-AdapterPreference", $AdapterPreference
    )
    if ($ShouldSyncGovernanceBaseline) {
      $flowArgs += @("-GovernanceBaselinePath", $GovernanceBaselinePathResolved)
    }
    if ($Overwrite) {
      $flowArgs += "-Overwrite"
    }
  }
  if ($Json) {
    $flowArgs += "-Json"
  }

  $flowResult = Invoke-CommandCapture `
    -Executable "pwsh" `
    -Arguments $flowArgs `
    -TimeoutSeconds $RuntimeFlowCommandTimeoutSeconds `
    -WorkingDirectory $RepoRoot
  $flowDurationMs = [int][Math]::Round(((Get-Date) - $flowStartedAt).TotalMilliseconds)
  $flowStatus = if ($flowResult.exit_code -eq 0) { "pass" } else { "fail" }
  $flowTimeoutTag = if ($flowResult.timed_out) { " timed_out=true" } else { "" }
  Write-BatchProgressLine `
    -Enabled $EmitProgress `
    -TargetName $TargetName `
    -Stage "runtime_flow" `
    -Status $flowStatus `
    -Detail ("duration_ms={0} exit_code={1}{2}" -f $flowDurationMs, $flowResult.exit_code, $flowTimeoutTag)
  $flowPayload = Try-ParseJson -Raw $flowResult.output

  $syncResult = [pscustomobject]@{
    target    = $TargetName
    status    = "skipped"
    reason    = "flow_mode_not_onboard"
    exit_code = 0
    payload   = $null
    output    = ""
  }
  if ($ShouldSyncGovernanceBaseline) {
    if ($flowResult.exit_code -eq 0) {
      Write-BatchProgressLine -Enabled $EmitProgress -TargetName $TargetName -Stage "governance_sync" -Status "start" -Detail "source=runtime_flow"
      $syncStartedAt = Get-Date
      $syncResult = Invoke-GovernanceBaselineSync `
        -TargetName $TargetName `
        -TargetConfig $TargetConfig `
        -RepoRoot $RepoRoot `
        -BaselinePath $GovernanceBaselinePathResolved `
        -PythonCommand $PythonCommand `
        -CommandTimeoutSeconds $GovernanceSyncCommandTimeoutSeconds
      $syncDurationMs = [int][Math]::Round(((Get-Date) - $syncStartedAt).TotalMilliseconds)
      Write-BatchProgressLine `
        -Enabled $EmitProgress `
        -TargetName $TargetName `
        -Stage "governance_sync" `
        -Status ([string]$syncResult.status) `
        -Detail ("source=runtime_flow duration_ms={0} exit_code={1}" -f $syncDurationMs, $syncResult.exit_code)
    }
    else {
      $syncResult = [pscustomobject]@{
        target    = $TargetName
        status    = "skipped"
        reason    = "runtime_flow_failed"
        exit_code = $flowResult.exit_code
        payload   = $null
        output    = ""
      }
      Write-BatchProgressLine -Enabled $EmitProgress -TargetName $TargetName -Stage "governance_sync" -Status "skipped" -Detail "reason=runtime_flow_failed"
    }
  }
  elseif ($FlowMode -eq "onboard") {
    $syncResult = [pscustomobject]@{
      target    = $TargetName
      status    = "skipped"
      reason    = "explicit_skip"
      exit_code = 0
      payload   = $null
      output    = ""
    }
    Write-BatchProgressLine -Enabled $EmitProgress -TargetName $TargetName -Stage "governance_sync" -Status "skipped" -Detail "reason=explicit_skip"
  }

  $exitCode = 0
  if ($flowResult.exit_code -ne 0) {
    $exitCode = $flowResult.exit_code
  }
  elseif ($syncResult.status -eq "fail") {
    $exitCode = 1
  }

  return [pscustomobject]@{
    target                 = $TargetName
    attachment_root        = $TargetConfig.AttachmentRoot
    runtime_state_root     = $TargetConfig.AttachmentRuntimeStateRoot
    flow_result            = $flowResult
    flow_payload           = $flowPayload
    governance_sync_result = $syncResult
    milestone_commit_result = [pscustomobject]@{
      target             = $TargetName
      status             = "skipped"
      reason             = "not_requested"
      exit_code          = 0
      payload            = $null
      output             = ""
      auto_commit_status = ""
      auto_commit_reason = ""
      commit_hash        = ""
      commit_message     = ""
      trigger            = ""
      milestone_tag      = ""
      gate_mode          = ""
      command_timeout_seconds = 0
    }
    exit_code              = $exitCode
  }
}

function Invoke-TargetGovernanceBaselineOnly {
  param(
    [Parameter(Mandatory = $true)]
    [string]$TargetName,
    [Parameter(Mandatory = $true)]
    [hashtable]$TargetConfig,
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [Parameter(Mandatory = $true)]
    [string]$GovernanceBaselinePathResolved,
    [Parameter(Mandatory = $true)]
    [string]$PythonCommand,
    [int]$GovernanceSyncCommandTimeoutSeconds = 0
  )

  $syncResult = Invoke-GovernanceBaselineSync `
    -TargetName $TargetName `
    -TargetConfig $TargetConfig `
    -RepoRoot $RepoRoot `
    -BaselinePath $GovernanceBaselinePathResolved `
    -PythonCommand $PythonCommand `
    -CommandTimeoutSeconds $GovernanceSyncCommandTimeoutSeconds
  $exitCode = if ($syncResult.status -eq "fail") { 1 } else { 0 }

  return [pscustomobject]@{
    target                 = $TargetName
    attachment_root        = $TargetConfig.AttachmentRoot
    runtime_state_root     = $TargetConfig.AttachmentRuntimeStateRoot
    flow_result            = [pscustomobject]@{ exit_code = 0; output = "" }
    flow_payload           = $null
    governance_sync_result = $syncResult
    milestone_commit_result = [pscustomobject]@{
      target            = $TargetName
      status            = "skipped"
      reason            = "not_requested"
      exit_code         = 0
      payload           = $null
      output            = ""
      auto_commit_status = ""
      auto_commit_reason = ""
      commit_hash       = ""
      commit_message    = ""
      trigger           = ""
      milestone_tag     = ""
      gate_mode         = ""
      command_timeout_seconds = 0
    }
    exit_code              = $exitCode
  }
}

function Invoke-TargetMilestoneAutoCommit {
  param(
    [Parameter(Mandatory = $true)]
    [string]$TargetName,
    [Parameter(Mandatory = $true)]
    [hashtable]$TargetConfig,
    [Parameter(Mandatory = $true)]
    [string]$GateCheckPath,
    [Parameter(Mandatory = $true)]
    [ValidateSet("full", "fast")]
    [string]$GateMode,
    [Parameter(Mandatory = $true)]
    [string]$MilestoneTagValue,
    [Parameter(Mandatory = $true)]
    [int]$MilestoneGateTimeoutSeconds,
    [int]$MilestoneCommandTimeoutSeconds = 0
  )

  $repoProfilePath = Join-Path $TargetConfig.AttachmentRoot ".governed-ai\repo-profile.json"
  if (-not (Test-Path -LiteralPath $repoProfilePath)) {
    return [pscustomobject]@{
      target             = $TargetName
      status             = "fail"
      reason             = "repo_profile_not_found"
      exit_code          = 1
      payload            = $null
      output             = ("repo profile not found: {0}" -f $repoProfilePath)
      auto_commit_status = ""
      auto_commit_reason = ""
      commit_hash        = ""
      commit_message     = ""
      trigger            = ""
      milestone_tag      = $MilestoneTagValue
      gate_mode          = $GateMode
      command_timeout_seconds = 0
    }
  }

  $effectiveMilestoneCommandTimeoutSeconds = 0
  if ($MilestoneCommandTimeoutSeconds -gt 0) {
    $effectiveMilestoneCommandTimeoutSeconds = $MilestoneCommandTimeoutSeconds
  }
  elseif ($MilestoneGateTimeoutSeconds -gt 0) {
    $effectiveMilestoneCommandTimeoutSeconds = $MilestoneGateTimeoutSeconds + 120
  }

  $args = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", $GateCheckPath,
    "-RepoProfilePath", $repoProfilePath,
    "-WorkingDirectory", $TargetConfig.AttachmentRoot,
    "-MilestoneTag", $MilestoneTagValue,
    "-GateTimeoutSeconds", [string]$MilestoneGateTimeoutSeconds,
    "-Json"
  )
  $result = Invoke-CommandCapture `
    -Executable "pwsh" `
    -Arguments $args `
    -TimeoutSeconds $effectiveMilestoneCommandTimeoutSeconds `
    -WorkingDirectory $TargetConfig.AttachmentRoot
  $payload = Try-ParseJson -Raw $result.output
  $status = if ($result.exit_code -eq 0) { "pass" } else { "fail" }
  $reason = if ($status -eq "pass") {
    "ok"
  }
  elseif ($result.timed_out) {
    "gate_check_timed_out"
  }
  else {
    "{0}_check_failed" -f $GateMode
  }

  $autoCommitStatus = ""
  $autoCommitReason = ""
  $commitHash = ""
  $commitMessage = ""
  $trigger = ""
  if ($payload -and $payload.summary -and $payload.summary.auto_commit) {
    if ($payload.summary.auto_commit.PSObject.Properties.Name -contains "status" -and $null -ne $payload.summary.auto_commit.status) {
      $autoCommitStatus = [string]$payload.summary.auto_commit.status
    }
    if ($payload.summary.auto_commit.PSObject.Properties.Name -contains "reason" -and $null -ne $payload.summary.auto_commit.reason) {
      $autoCommitReason = [string]$payload.summary.auto_commit.reason
    }
    if ($payload.summary.auto_commit.PSObject.Properties.Name -contains "commit_hash" -and $null -ne $payload.summary.auto_commit.commit_hash) {
      $commitHash = [string]$payload.summary.auto_commit.commit_hash
    }
    if ($payload.summary.auto_commit.PSObject.Properties.Name -contains "commit_message" -and $null -ne $payload.summary.auto_commit.commit_message) {
      $commitMessage = [string]$payload.summary.auto_commit.commit_message
    }
    if ($payload.summary.auto_commit.PSObject.Properties.Name -contains "trigger" -and $null -ne $payload.summary.auto_commit.trigger) {
      $trigger = [string]$payload.summary.auto_commit.trigger
    }
  }

  return [pscustomobject]@{
    target             = $TargetName
    status             = $status
    reason             = $reason
    exit_code          = $result.exit_code
    payload            = $payload
    output             = $result.output
    auto_commit_status = $autoCommitStatus
    auto_commit_reason = $autoCommitReason
    commit_hash        = $commitHash
    commit_message     = $commitMessage
    trigger            = $trigger
    milestone_tag      = $MilestoneTagValue
    gate_mode          = $GateMode
    command_timeout_seconds = $effectiveMilestoneCommandTimeoutSeconds
  }
}

function Invoke-TargetFeatureBaselineAndMilestoneCommit {
  param(
    [Parameter(Mandatory = $true)]
    [string]$TargetName,
    [Parameter(Mandatory = $true)]
    [hashtable]$TargetConfig,
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [Parameter(Mandatory = $true)]
    [string]$GovernanceBaselinePathResolved,
    [Parameter(Mandatory = $true)]
    [string]$PythonCommand,
    [Parameter(Mandatory = $true)]
    [string]$MilestoneGateCheckPathResolved,
    [Parameter(Mandatory = $true)]
    [string]$MilestoneTagValue,
    [Parameter(Mandatory = $true)]
    [int]$MilestoneGateTimeoutSeconds,
    [Parameter(Mandatory = $true)]
    [ValidateSet("full", "fast")]
    [string]$MilestoneGateModeValue,
    [int]$MilestoneCommandTimeoutSeconds = 0,
    [int]$GovernanceSyncCommandTimeoutSeconds = 0,
    [bool]$EmitProgress = $false
  )

  Write-BatchProgressLine -Enabled $EmitProgress -TargetName $TargetName -Stage "governance_sync" -Status "start" -Detail "source=baseline_only"
  $syncStartedAt = Get-Date
  $syncResult = Invoke-GovernanceBaselineSync `
    -TargetName $TargetName `
    -TargetConfig $TargetConfig `
    -RepoRoot $RepoRoot `
    -BaselinePath $GovernanceBaselinePathResolved `
    -PythonCommand $PythonCommand `
    -CommandTimeoutSeconds $GovernanceSyncCommandTimeoutSeconds
  $syncDurationMs = [int][Math]::Round(((Get-Date) - $syncStartedAt).TotalMilliseconds)
  Write-BatchProgressLine `
    -Enabled $EmitProgress `
    -TargetName $TargetName `
    -Stage "governance_sync" `
    -Status ([string]$syncResult.status) `
    -Detail ("source=baseline_only duration_ms={0} exit_code={1}" -f $syncDurationMs, $syncResult.exit_code)

  $milestoneResult = [pscustomobject]@{
    target             = $TargetName
    status             = "skipped"
    reason             = "baseline_sync_failed"
    exit_code          = 1
    payload            = $null
    output             = ""
    auto_commit_status = ""
    auto_commit_reason = ""
    commit_hash        = ""
    commit_message     = ""
    trigger            = ""
    milestone_tag      = $MilestoneTagValue
    gate_mode          = $MilestoneGateModeValue
    command_timeout_seconds = $(if ($MilestoneCommandTimeoutSeconds -gt 0) { $MilestoneCommandTimeoutSeconds } elseif ($MilestoneGateTimeoutSeconds -gt 0) { $MilestoneGateTimeoutSeconds + 120 } else { 0 })
  }
  if ($syncResult.status -eq "pass") {
    Write-BatchProgressLine `
      -Enabled $EmitProgress `
      -TargetName $TargetName `
      -Stage "milestone_commit" `
      -Status "start" `
      -Detail ("mode={0} milestone_tag={1} gate_timeout_s={2}" -f $MilestoneGateModeValue, $MilestoneTagValue, $MilestoneGateTimeoutSeconds)
    $milestoneStartedAt = Get-Date
    $milestoneResult = Invoke-TargetMilestoneAutoCommit `
      -TargetName $TargetName `
      -TargetConfig $TargetConfig `
      -GateCheckPath $MilestoneGateCheckPathResolved `
      -GateMode $MilestoneGateModeValue `
      -MilestoneTagValue $MilestoneTagValue `
      -MilestoneGateTimeoutSeconds $MilestoneGateTimeoutSeconds `
      -MilestoneCommandTimeoutSeconds $MilestoneCommandTimeoutSeconds
    $milestoneDurationMs = [int][Math]::Round(((Get-Date) - $milestoneStartedAt).TotalMilliseconds)
    Write-BatchProgressLine `
      -Enabled $EmitProgress `
      -TargetName $TargetName `
      -Stage "milestone_commit" `
      -Status ([string]$milestoneResult.status) `
      -Detail ("duration_ms={0} exit_code={1} auto_commit_status={2}" -f $milestoneDurationMs, $milestoneResult.exit_code, $milestoneResult.auto_commit_status)
  }
  else {
    Write-BatchProgressLine -Enabled $EmitProgress -TargetName $TargetName -Stage "milestone_commit" -Status "skipped" -Detail "reason=baseline_sync_failed"
  }

  $exitCode = 0
  if ($syncResult.status -ne "pass") {
    $exitCode = 1
  }
  elseif ($milestoneResult.status -ne "pass") {
    $exitCode = 1
  }

  return [pscustomobject]@{
    target                  = $TargetName
    attachment_root         = $TargetConfig.AttachmentRoot
    runtime_state_root      = $TargetConfig.AttachmentRuntimeStateRoot
    flow_result             = [pscustomobject]@{ exit_code = 0; output = "" }
    flow_payload            = $null
    governance_sync_result  = $syncResult
    milestone_commit_result = $milestoneResult
    exit_code               = $exitCode
  }
}

function Invoke-TargetAllFeatures {
  param(
    [Parameter(Mandatory = $true)]
    [string]$TargetName,
    [Parameter(Mandatory = $true)]
    [hashtable]$TargetConfig,
    [Parameter(Mandatory = $true)]
    [string]$RuntimeFlowPathResolved,
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [Parameter(Mandatory = $true)]
    [string]$GovernanceBaselinePathResolved,
    [Parameter(Mandatory = $true)]
    [bool]$IsBatchMode,
    [Parameter(Mandatory = $true)]
    [string]$PythonCommand,
    [Parameter(Mandatory = $true)]
    [string]$MilestoneGateCheckPathResolved,
    [Parameter(Mandatory = $true)]
    [string]$MilestoneTagValue,
    [Parameter(Mandatory = $true)]
    [int]$MilestoneGateTimeoutSeconds,
    [Parameter(Mandatory = $true)]
    [ValidateSet("full", "fast")]
    [string]$MilestoneGateModeValue,
    [int]$MilestoneCommandTimeoutSeconds = 0,
    [int]$RuntimeFlowCommandTimeoutSeconds = 0,
    [int]$GovernanceSyncCommandTimeoutSeconds = 0,
    [bool]$EmitProgress = $false
  )

  $flowResultEnvelope = Invoke-TargetPresetFlow `
    -TargetName $TargetName `
    -TargetConfig $TargetConfig `
    -RuntimeFlowPathResolved $RuntimeFlowPathResolved `
    -RepoRoot $RepoRoot `
    -GovernanceBaselinePathResolved $GovernanceBaselinePathResolved `
    -ShouldSyncGovernanceBaseline ($FlowMode -eq "onboard") `
    -IsBatchMode $IsBatchMode `
    -PythonCommand $PythonCommand `
    -RuntimeFlowCommandTimeoutSeconds $RuntimeFlowCommandTimeoutSeconds `
    -GovernanceSyncCommandTimeoutSeconds $GovernanceSyncCommandTimeoutSeconds `
    -EmitProgress $EmitProgress

  $syncResult = $flowResultEnvelope.governance_sync_result
  if ($flowResultEnvelope.flow_result.exit_code -eq 0) {
    $flowSyncStatus = if ($null -ne $syncResult -and $syncResult.PSObject.Properties.Name -contains "status") { [string]$syncResult.status } else { "" }
    if ($flowSyncStatus -ne "pass") {
      Write-BatchProgressLine -Enabled $EmitProgress -TargetName $TargetName -Stage "governance_sync" -Status "start" -Detail "source=all_features_fallback"
      $syncStartedAt = Get-Date
      $syncResult = Invoke-GovernanceBaselineSync `
        -TargetName $TargetName `
        -TargetConfig $TargetConfig `
        -RepoRoot $RepoRoot `
        -BaselinePath $GovernanceBaselinePathResolved `
        -PythonCommand $PythonCommand `
        -CommandTimeoutSeconds $GovernanceSyncCommandTimeoutSeconds
      $syncDurationMs = [int][Math]::Round(((Get-Date) - $syncStartedAt).TotalMilliseconds)
      Write-BatchProgressLine `
        -Enabled $EmitProgress `
        -TargetName $TargetName `
        -Stage "governance_sync" `
        -Status ([string]$syncResult.status) `
        -Detail ("source=all_features_fallback duration_ms={0} exit_code={1}" -f $syncDurationMs, $syncResult.exit_code)
    }
  }
  else {
    Write-BatchProgressLine -Enabled $EmitProgress -TargetName $TargetName -Stage "governance_sync" -Status "skipped" -Detail "reason=runtime_flow_failed"
  }

  $milestoneResult = [pscustomobject]@{
    target             = $TargetName
    status             = "skipped"
    reason             = "runtime_flow_failed"
    exit_code          = 1
    payload            = $null
    output             = ""
    auto_commit_status = ""
    auto_commit_reason = ""
    commit_hash        = ""
    commit_message     = ""
    trigger            = ""
    milestone_tag      = $MilestoneTagValue
    gate_mode          = $MilestoneGateModeValue
    command_timeout_seconds = $(if ($MilestoneCommandTimeoutSeconds -gt 0) { $MilestoneCommandTimeoutSeconds } elseif ($MilestoneGateTimeoutSeconds -gt 0) { $MilestoneGateTimeoutSeconds + 120 } else { 0 })
  }
  if ($flowResultEnvelope.flow_result.exit_code -eq 0) {
    if ($syncResult.status -eq "pass") {
      Write-BatchProgressLine `
        -Enabled $EmitProgress `
        -TargetName $TargetName `
        -Stage "milestone_commit" `
        -Status "start" `
        -Detail ("mode={0} milestone_tag={1} gate_timeout_s={2}" -f $MilestoneGateModeValue, $MilestoneTagValue, $MilestoneGateTimeoutSeconds)
      $milestoneStartedAt = Get-Date
      $milestoneResult = Invoke-TargetMilestoneAutoCommit `
        -TargetName $TargetName `
        -TargetConfig $TargetConfig `
        -GateCheckPath $MilestoneGateCheckPathResolved `
        -GateMode $MilestoneGateModeValue `
        -MilestoneTagValue $MilestoneTagValue `
        -MilestoneGateTimeoutSeconds $MilestoneGateTimeoutSeconds `
        -MilestoneCommandTimeoutSeconds $MilestoneCommandTimeoutSeconds
      $milestoneDurationMs = [int][Math]::Round(((Get-Date) - $milestoneStartedAt).TotalMilliseconds)
      Write-BatchProgressLine `
        -Enabled $EmitProgress `
        -TargetName $TargetName `
        -Stage "milestone_commit" `
        -Status ([string]$milestoneResult.status) `
        -Detail ("duration_ms={0} exit_code={1} auto_commit_status={2}" -f $milestoneDurationMs, $milestoneResult.exit_code, $milestoneResult.auto_commit_status)
    }
    else {
      $milestoneResult = [pscustomobject]@{
        target             = $TargetName
        status             = "skipped"
        reason             = "baseline_sync_failed"
        exit_code          = 1
        payload            = $null
        output             = ""
        auto_commit_status = ""
        auto_commit_reason = ""
        commit_hash        = ""
        commit_message     = ""
        trigger            = ""
        milestone_tag      = $MilestoneTagValue
        gate_mode          = $MilestoneGateModeValue
        command_timeout_seconds = $(if ($MilestoneCommandTimeoutSeconds -gt 0) { $MilestoneCommandTimeoutSeconds } elseif ($MilestoneGateTimeoutSeconds -gt 0) { $MilestoneGateTimeoutSeconds + 120 } else { 0 })
      }
      Write-BatchProgressLine -Enabled $EmitProgress -TargetName $TargetName -Stage "milestone_commit" -Status "skipped" -Detail "reason=baseline_sync_failed"
    }
  }
  else {
    Write-BatchProgressLine -Enabled $EmitProgress -TargetName $TargetName -Stage "milestone_commit" -Status "skipped" -Detail "reason=runtime_flow_failed"
  }

  $exitCode = 0
  if ($flowResultEnvelope.flow_result.exit_code -ne 0) {
    $exitCode = $flowResultEnvelope.flow_result.exit_code
  }
  elseif ($syncResult.status -ne "pass") {
    $exitCode = 1
  }
  elseif ($milestoneResult.status -ne "pass") {
    $exitCode = 1
  }

  return [pscustomobject]@{
    target                  = $TargetName
    attachment_root         = $TargetConfig.AttachmentRoot
    runtime_state_root      = $TargetConfig.AttachmentRuntimeStateRoot
    flow_result             = $flowResultEnvelope.flow_result
    flow_payload            = $flowResultEnvelope.flow_payload
    governance_sync_result  = $syncResult
    milestone_commit_result = $milestoneResult
    exit_code               = $exitCode
  }
}

$repoRoot = Resolve-AbsolutePath -PathValue (Join-Path $PSScriptRoot "..")
$codeRoot = Split-Path $repoRoot -Parent
$runtimeStateBase = Join-Path $repoRoot ".runtime\attachments"
$catalogPath = if ([string]::IsNullOrWhiteSpace($CatalogPath)) {
  Join-Path $repoRoot "docs\targets\target-repos-catalog.json"
}
else {
  Resolve-AbsolutePath -PathValue $CatalogPath
}
$governanceBaselinePathResolved = if ([string]::IsNullOrWhiteSpace($GovernanceBaselinePath)) {
  Join-Path $repoRoot "docs\targets\target-repo-governance-baseline.json"
}
else {
  Resolve-AbsolutePath -PathValue $GovernanceBaselinePath
}
$runtimeFlowPath = if ([string]::IsNullOrWhiteSpace($RuntimeFlowPath)) {
  Join-Path $PSScriptRoot "runtime-flow.ps1"
}
else {
  Resolve-AbsolutePath -PathValue $RuntimeFlowPath
}
$governanceFullCheckPathResolved = if ([string]::IsNullOrWhiteSpace($GovernanceFullCheckPath)) {
  Join-Path $repoRoot "scripts\governance\full-check.ps1"
}
else {
  Resolve-AbsolutePath -PathValue $GovernanceFullCheckPath
}
$governanceFastCheckPathResolved = if ([string]::IsNullOrWhiteSpace($GovernanceFastCheckPath)) {
  Join-Path $repoRoot "scripts\governance\fast-check.ps1"
}
else {
  Resolve-AbsolutePath -PathValue $GovernanceFastCheckPath
}
$pruneRunsRootResolved = if ([string]::IsNullOrWhiteSpace($PruneRunsRoot)) {
  Join-Path $repoRoot "docs\change-evidence\target-repo-runs"
}
else {
  Resolve-AbsolutePath -PathValue $PruneRunsRoot
}
$applyAllFeatures = [bool]$ApplyAllFeatures
$applyFeatureBaselineOnly = ($ApplyGovernanceBaselineOnly -or $ApplyFeatureBaselineOnly)
$applyFeatureBaselineAndMilestoneCommit = [bool]$ApplyFeatureBaselineAndMilestoneCommit
if ($applyAllFeatures -and ($applyFeatureBaselineOnly -or $applyFeatureBaselineAndMilestoneCommit)) {
  throw "-ApplyAllFeatures is mutually exclusive with -ApplyFeatureBaselineOnly/-ApplyGovernanceBaselineOnly and -ApplyFeatureBaselineAndMilestoneCommit."
}
if ($applyFeatureBaselineOnly -and $applyFeatureBaselineAndMilestoneCommit) {
  throw "-ApplyFeatureBaselineOnly/-ApplyGovernanceBaselineOnly and -ApplyFeatureBaselineAndMilestoneCommit are mutually exclusive."
}
if ($PruneKeepDays -lt 0) {
  throw "-PruneKeepDays must be >= 0."
}
if ($PruneKeepLatestPerTarget -lt 0) {
  throw "-PruneKeepLatestPerTarget must be >= 0."
}
if ($MilestoneGateTimeoutSeconds -lt 0) {
  throw "-MilestoneGateTimeoutSeconds must be >= 0."
}
if ($MilestoneCommandTimeoutSeconds -lt 0) {
  throw "-MilestoneCommandTimeoutSeconds must be >= 0."
}
if ($RuntimeFlowTimeoutSeconds -lt 0) {
  throw "-RuntimeFlowTimeoutSeconds must be >= 0."
}
if ($GovernanceSyncTimeoutSeconds -lt 0) {
  throw "-GovernanceSyncTimeoutSeconds must be >= 0."
}
if ($BatchTimeoutSeconds -lt 0) {
  throw "-BatchTimeoutSeconds must be >= 0."
}
$milestoneGateStrategy = Resolve-MilestoneGateStrategy `
  -AutoEnabled $AutoMilestoneGateMode.IsPresent `
  -RequestedMode $MilestoneGateMode `
  -FlowModeValue $FlowMode `
  -VerificationModeValue $Mode `
  -PolicyStatusValue $PolicyStatus `
  -WriteTierValue $WriteTier `
  -ExecuteWriteFlowEnabled $ExecuteWriteFlow.IsPresent `
  -ReleaseCandidateEnabled $ReleaseCandidate.IsPresent `
  -TaskTypeValue $TaskType
$effectiveMilestoneGateMode = [string]$milestoneGateStrategy.mode
$milestoneGateModeSource = [string]$milestoneGateStrategy.source
$milestoneGateModeReason = [string]$milestoneGateStrategy.reason
$milestoneGateCheckPathResolved = if ($effectiveMilestoneGateMode -eq "fast") {
  $governanceFastCheckPathResolved
}
else {
  $governanceFullCheckPathResolved
}
$pythonCommand = Resolve-PythonCommand
$templateVariables = @{
  repo_root = $repoRoot
  code_root = $codeRoot
  runtime_state_base = $runtimeStateBase
}
$targetConfigMap = Load-TargetConfigMap -CatalogPath $catalogPath -Variables $templateVariables

if ($ListTargets) {
  $targetNames = @($targetConfigMap.Keys | Sort-Object)
  if ($Json) {
    @{
      catalog_path = $catalogPath
      targets      = $targetNames
    } | ConvertTo-Json -Depth 4
  }
  else {
    Write-Host ("catalog={0}" -f $catalogPath)
    foreach ($name in $targetNames) {
      Write-Host ("- {0}" -f $name)
    }
  }
  exit 0
}

if ((-not (Test-Path -LiteralPath $runtimeFlowPath)) -and (-not $applyFeatureBaselineOnly) -and (-not $applyFeatureBaselineAndMilestoneCommit)) {
  throw "Missing runtime-flow.ps1 at $runtimeFlowPath"
}
if ((((($FlowMode -eq "onboard") -and -not $SkipGovernanceBaselineSync.IsPresent)) -or $applyFeatureBaselineOnly -or $applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) -and -not (Test-Path -LiteralPath $governanceBaselinePathResolved)) {
  throw "Missing target-repo-governance-baseline.json at $governanceBaselinePathResolved"
}
if (($applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) -and -not (Test-Path -LiteralPath $milestoneGateCheckPathResolved)) {
  throw ("Missing milestone gate script ({0}) at {1}" -f $effectiveMilestoneGateMode, $milestoneGateCheckPathResolved)
}

$selectedTargets = @()
if ($AllTargets) {
  $selectedTargets = @($targetConfigMap.Keys | Sort-Object)
}
else {
  $targetConfig = $targetConfigMap[$Target]
  if (-not $targetConfig) {
    $available = @($targetConfigMap.Keys | Sort-Object) -join ", "
    throw "Unsupported target preset: $Target. Available targets: $available"
  }
  $selectedTargets = @($Target)
}
$targetRuns = @()
$targetCount = @($selectedTargets).Count
$progressEnabled = ($AllTargets -and -not $Json)
$batchStartedAt = Get-Date
$batchTimedOut = $false
$batchElapsedSeconds = 0
$targetIndex = 0
foreach ($targetName in $selectedTargets) {
  if ($BatchTimeoutSeconds -gt 0) {
    $batchElapsedSeconds = [int][Math]::Floor(((Get-Date) - $batchStartedAt).TotalSeconds)
    if ($batchElapsedSeconds -ge $BatchTimeoutSeconds) {
      $batchTimedOut = $true
      Write-BatchProgressLine `
        -Enabled $progressEnabled `
        -TargetName "__batch__" `
        -Stage "batch" `
        -Status "fail" `
        -Detail ("reason=batch_timeout_exceeded elapsed_s={0} timeout_s={1}" -f $batchElapsedSeconds, $BatchTimeoutSeconds)
      break
    }
  }

  $targetIndex += 1
  $targetConfig = $targetConfigMap[$targetName]
  if (-not $targetConfig) {
    throw "Target config not found in catalog for target: $targetName"
  }

  $runModeLabel = if ($applyAllFeatures) {
    "apply_all_features"
  }
  elseif ($applyFeatureBaselineAndMilestoneCommit) {
    "baseline_and_milestone"
  }
  elseif ($applyFeatureBaselineOnly) {
    "baseline_only"
  }
  else {
    "runtime_flow_only"
  }
  $gateStrategyTag = ""
  if ($applyAllFeatures -or $applyFeatureBaselineAndMilestoneCommit) {
    $gateStrategyTag = (" milestone_gate_mode={0} source={1} reason={2}" -f $effectiveMilestoneGateMode, $milestoneGateModeSource, $milestoneGateModeReason)
  }
  $targetStartedAt = Get-Date
  Write-BatchProgressLine `
    -Enabled $progressEnabled `
    -TargetName $targetName `
    -Stage "target" `
    -Status "start" `
    -Detail ("index={0}/{1} mode={2}{3}" -f $targetIndex, $targetCount, $runModeLabel, $gateStrategyTag)

  if ($AllTargets -and -not $Json) {
    Write-Host ("==> target={0} ({1}/{2})" -f $targetName, $targetIndex, $targetCount)
  }

  $targetRun = $null
  if ($applyAllFeatures) {
    $targetRun = Invoke-TargetAllFeatures `
      -TargetName $targetName `
      -TargetConfig $targetConfig `
      -RuntimeFlowPathResolved $runtimeFlowPath `
      -RepoRoot $repoRoot `
      -GovernanceBaselinePathResolved $governanceBaselinePathResolved `
      -IsBatchMode $AllTargets.IsPresent `
      -PythonCommand $pythonCommand `
      -MilestoneGateCheckPathResolved $milestoneGateCheckPathResolved `
      -MilestoneTagValue $MilestoneTag `
      -MilestoneGateTimeoutSeconds $MilestoneGateTimeoutSeconds `
      -MilestoneGateModeValue $effectiveMilestoneGateMode `
      -MilestoneCommandTimeoutSeconds $MilestoneCommandTimeoutSeconds `
      -RuntimeFlowCommandTimeoutSeconds $RuntimeFlowTimeoutSeconds `
      -GovernanceSyncCommandTimeoutSeconds $GovernanceSyncTimeoutSeconds `
      -EmitProgress $progressEnabled
  }
  elseif ($applyFeatureBaselineAndMilestoneCommit) {
    $targetRun = Invoke-TargetFeatureBaselineAndMilestoneCommit `
      -TargetName $targetName `
      -TargetConfig $targetConfig `
      -RepoRoot $repoRoot `
      -GovernanceBaselinePathResolved $governanceBaselinePathResolved `
      -PythonCommand $pythonCommand `
      -MilestoneGateCheckPathResolved $milestoneGateCheckPathResolved `
      -MilestoneTagValue $MilestoneTag `
      -MilestoneGateTimeoutSeconds $MilestoneGateTimeoutSeconds `
      -MilestoneGateModeValue $effectiveMilestoneGateMode `
      -MilestoneCommandTimeoutSeconds $MilestoneCommandTimeoutSeconds `
      -GovernanceSyncCommandTimeoutSeconds $GovernanceSyncTimeoutSeconds `
      -EmitProgress $progressEnabled
  }
  elseif ($applyFeatureBaselineOnly) {
    $targetRun = Invoke-TargetGovernanceBaselineOnly `
      -TargetName $targetName `
      -TargetConfig $targetConfig `
      -RepoRoot $repoRoot `
      -GovernanceBaselinePathResolved $governanceBaselinePathResolved `
      -PythonCommand $pythonCommand `
      -GovernanceSyncCommandTimeoutSeconds $GovernanceSyncTimeoutSeconds
  }
  else {
    $targetRun = Invoke-TargetPresetFlow `
      -TargetName $targetName `
      -TargetConfig $targetConfig `
      -RuntimeFlowPathResolved $runtimeFlowPath `
      -RepoRoot $repoRoot `
      -GovernanceBaselinePathResolved $governanceBaselinePathResolved `
      -ShouldSyncGovernanceBaseline (($FlowMode -eq "onboard") -and -not $SkipGovernanceBaselineSync.IsPresent) `
      -IsBatchMode $AllTargets.IsPresent `
      -PythonCommand $pythonCommand `
      -RuntimeFlowCommandTimeoutSeconds $RuntimeFlowTimeoutSeconds `
      -GovernanceSyncCommandTimeoutSeconds $GovernanceSyncTimeoutSeconds `
      -EmitProgress $progressEnabled
  }
  $targetRuns += $targetRun

  $targetDurationMs = [int][Math]::Round(((Get-Date) - $targetStartedAt).TotalMilliseconds)
  $targetStatus = if ($targetRun.exit_code -eq 0) { "pass" } else { "fail" }
  Write-BatchProgressLine `
    -Enabled $progressEnabled `
    -TargetName $targetName `
    -Stage "target" `
    -Status $targetStatus `
    -Detail ("index={0}/{1} duration_ms={2} exit_code={3}" -f $targetIndex, $targetCount, $targetDurationMs, $targetRun.exit_code)

  if (-not $Json) {
    if (-not [string]::IsNullOrWhiteSpace($targetRun.flow_result.output)) {
      Write-Host $targetRun.flow_result.output
    }
    if ($targetRun.governance_sync_result.status -eq "pass") {
      $changedFields = @()
      if ($targetRun.governance_sync_result.payload -and $targetRun.governance_sync_result.payload.changed_fields) {
        $changedFields = @($targetRun.governance_sync_result.payload.changed_fields)
      }
      Write-Host ("governance_sync: status=pass target={0} changed_fields={1}" -f $targetName, (@($changedFields) -join ","))
    }
    elseif ($targetRun.governance_sync_result.status -eq "fail") {
      Write-Host ("governance_sync: status=fail target={0} reason={1}" -f $targetName, $targetRun.governance_sync_result.reason)
      if (-not [string]::IsNullOrWhiteSpace($targetRun.governance_sync_result.output)) {
        Write-Host $targetRun.governance_sync_result.output
      }
    }
    if ($targetRun.milestone_commit_result.status -eq "pass") {
      Write-Host (
        "milestone_commit: status=pass target={0} auto_commit_status={1} auto_commit_reason={2} hash={3}" -f
          $targetName,
          $targetRun.milestone_commit_result.auto_commit_status,
          $targetRun.milestone_commit_result.auto_commit_reason,
          $targetRun.milestone_commit_result.commit_hash
      )
    }
    elseif ($targetRun.milestone_commit_result.status -eq "fail") {
      Write-Host ("milestone_commit: status=fail target={0} reason={1}" -f $targetName, $targetRun.milestone_commit_result.reason)
      if (-not [string]::IsNullOrWhiteSpace($targetRun.milestone_commit_result.output)) {
        Write-Host $targetRun.milestone_commit_result.output
      }
    }
  }

  if ($FailFast -and $targetRun.exit_code -ne 0) {
    break
  }
}

$failureCount = @($targetRuns | Where-Object { $_.exit_code -ne 0 }).Count
$pruneResult = [pscustomobject]@{
  status    = "skipped"
  reason    = "not_requested"
  exit_code = 0
  runs_root = $pruneRunsRootResolved
  payload   = $null
  output    = ""
}
if ($PruneTargetRepoRuns) {
  $pruneResult = Invoke-PruneTargetRepoRuns `
    -RepoRoot $repoRoot `
    -RunsRoot $pruneRunsRootResolved `
    -PythonCommand $pythonCommand `
    -KeepDays $PruneKeepDays `
    -KeepLatestPerTarget $PruneKeepLatestPerTarget `
    -DryRun $PruneDryRun.IsPresent
}

$pruneForJson = Convert-PruneResultForJson `
  -PruneResult $pruneResult `
  -KeepDays $PruneKeepDays `
  -KeepLatestPerTarget $PruneKeepLatestPerTarget `
  -DryRun $PruneDryRun.IsPresent

$hasPruneFailure = ($PruneTargetRepoRuns -and $pruneResult.status -eq "fail")
$overallExitCode = if (($failureCount -gt 0) -or $hasPruneFailure -or $batchTimedOut) { 1 } else { 0 }

if ($Json) {
  if (-not $AllTargets -and @($targetRuns).Count -eq 1) {
    $single = $targetRuns[0]
    $syncStatus = [string]$single.governance_sync_result.status
    $syncReason = [string]$single.governance_sync_result.reason
    if (($syncStatus -eq "skipped") -and ($syncReason -in @("flow_mode_not_onboard", "explicit_skip", "runtime_flow_failed"))) {
      if (-not [string]::IsNullOrWhiteSpace($single.flow_result.output)) {
        if (-not $PruneTargetRepoRuns) {
          Write-Host $single.flow_result.output
        }
        else {
          $flowOnlyPayload = Try-ParseJson -Raw $single.flow_result.output
          if ($null -ne $flowOnlyPayload) {
            $wrappedFlowOnly = [ordered]@{}
            foreach ($property in $flowOnlyPayload.PSObject.Properties) {
              $wrappedFlowOnly[$property.Name] = $property.Value
            }
            $wrappedFlowOnly["prune_target_repo_runs"] = $pruneForJson
            Write-Host ($wrappedFlowOnly | ConvertTo-Json -Depth 20)
          }
          else {
            $flowOnlyFallback = [ordered]@{
              target                 = $single.target
              exit_code              = $single.exit_code
              flow_exit_code         = $single.flow_result.exit_code
              flow_output            = $single.flow_result.output
              prune_target_repo_runs = $pruneForJson
            }
            Write-Host ($flowOnlyFallback | ConvertTo-Json -Depth 20)
          }
        }
      }
      elseif ($PruneTargetRepoRuns) {
        $flowOnlyEmpty = [ordered]@{
          target                 = $single.target
          exit_code              = $single.exit_code
          flow_exit_code         = $single.flow_result.exit_code
          flow_output            = ""
          prune_target_repo_runs = $pruneForJson
        }
        Write-Host ($flowOnlyEmpty | ConvertTo-Json -Depth 20)
      }
      else {
        $flowOnlyFallback = [ordered]@{
          target         = $single.target
          exit_code      = $single.exit_code
          flow_exit_code = $single.flow_result.exit_code
          flow_timed_out = if ($single.flow_result.PSObject.Properties.Name -contains "timed_out") { [bool]$single.flow_result.timed_out } else { $false }
          flow_output    = $single.flow_result.output
        }
        Write-Host ($flowOnlyFallback | ConvertTo-Json -Depth 20)
      }
    }
    else {
      $flowPayload = $single.flow_payload
      if ($null -ne $flowPayload) {
        $wrapped = [ordered]@{}
        foreach ($property in $flowPayload.PSObject.Properties) {
          $wrapped[$property.Name] = $property.Value
        }
        $wrapped["governance_baseline_sync"] = [ordered]@{
          status       = $single.governance_sync_result.status
          reason       = $single.governance_sync_result.reason
          exit_code    = $single.governance_sync_result.exit_code
          changed      = if ($single.governance_sync_result.payload) { @($single.governance_sync_result.payload.changed_fields) } else { @() }
          sync_revision = if ($single.governance_sync_result.payload) { $single.governance_sync_result.payload.sync_revision } else { $null }
        }
        $wrapped["milestone_commit"] = [ordered]@{
          status             = $single.milestone_commit_result.status
          reason             = $single.milestone_commit_result.reason
          exit_code          = $single.milestone_commit_result.exit_code
          gate_mode          = if ($single.milestone_commit_result.PSObject.Properties.Name -contains "gate_mode") { $single.milestone_commit_result.gate_mode } else { "" }
          gate_mode_source   = $milestoneGateModeSource
          gate_mode_reason   = $milestoneGateModeReason
          command_timeout_seconds = if ($single.milestone_commit_result.PSObject.Properties.Name -contains "command_timeout_seconds") { $single.milestone_commit_result.command_timeout_seconds } else { 0 }
          auto_commit_status = $single.milestone_commit_result.auto_commit_status
          auto_commit_reason = $single.milestone_commit_result.auto_commit_reason
          commit_hash        = $single.milestone_commit_result.commit_hash
          commit_message     = $single.milestone_commit_result.commit_message
          trigger            = $single.milestone_commit_result.trigger
          milestone_tag      = $single.milestone_commit_result.milestone_tag
        }
        if ($PruneTargetRepoRuns) {
          $wrapped["prune_target_repo_runs"] = $pruneForJson
        }
        Write-Host ($wrapped | ConvertTo-Json -Depth 20)
      }
      else {
        $fallback = [ordered]@{
          target                  = $single.target
          exit_code               = $single.exit_code
          flow_exit_code          = $single.flow_result.exit_code
          flow_output             = $single.flow_result.output
          governance_baseline_sync = $single.governance_sync_result
          milestone_commit        = $single.milestone_commit_result
        }
        if ($PruneTargetRepoRuns) {
          $fallback["prune_target_repo_runs"] = $pruneForJson
        }
        Write-Host ($fallback | ConvertTo-Json -Depth 20)
      }
    }
  }
  else {
    $results = @(
      $targetRuns | ForEach-Object {
        $flowTimedOut = $false
        if ($_.flow_result -and ($_.flow_result.PSObject.Properties.Name -contains "timed_out")) {
          $flowTimedOut = [bool]$_.flow_result.timed_out
        }
        [ordered]@{
          target                   = $_.target
          exit_code                = $_.exit_code
          flow_exit_code           = $_.flow_result.exit_code
          flow_timed_out           = $flowTimedOut
          governance_sync_status   = $_.governance_sync_result.status
          governance_sync_reason   = $_.governance_sync_result.reason
          governance_sync_exit_code = $_.governance_sync_result.exit_code
          governance_sync_changed  = if ($_.governance_sync_result.payload) { @($_.governance_sync_result.payload.changed_fields) } else { @() }
          milestone_commit_status  = $_.milestone_commit_result.status
          milestone_commit_reason  = $_.milestone_commit_result.reason
          milestone_commit_exit_code = $_.milestone_commit_result.exit_code
          milestone_gate_mode      = if ($_.milestone_commit_result.PSObject.Properties.Name -contains "gate_mode") { $_.milestone_commit_result.gate_mode } else { "" }
          milestone_gate_mode_source = $milestoneGateModeSource
          milestone_gate_mode_reason = $milestoneGateModeReason
          milestone_command_timeout_seconds = if ($_.milestone_commit_result.PSObject.Properties.Name -contains "command_timeout_seconds") { $_.milestone_commit_result.command_timeout_seconds } else { 0 }
          auto_commit_status       = $_.milestone_commit_result.auto_commit_status
          auto_commit_reason       = $_.milestone_commit_result.auto_commit_reason
          auto_commit_commit_hash  = $_.milestone_commit_result.commit_hash
          auto_commit_trigger      = $_.milestone_commit_result.trigger
        }
      }
    )
    $payload = [ordered]@{
      catalog_path                    = $catalogPath
      runtime_flow_path               = $runtimeFlowPath
      governance_baseline_path        = $governanceBaselinePathResolved
      governance_full_check_path      = $governanceFullCheckPathResolved
      governance_fast_check_path      = $governanceFastCheckPathResolved
      all_targets                     = [bool]$AllTargets
      flow_mode                       = $FlowMode
      apply_all_features              = [bool]$applyAllFeatures
      apply_feature_baseline_only     = [bool]$applyFeatureBaselineOnly
      apply_governance_baseline_only  = [bool]$ApplyGovernanceBaselineOnly
      apply_feature_baseline_and_milestone_commit = [bool]$applyFeatureBaselineAndMilestoneCommit
      governance_baseline_sync_active = ($applyAllFeatures -or $applyFeatureBaselineOnly -or $applyFeatureBaselineAndMilestoneCommit -or (($FlowMode -eq "onboard") -and -not $SkipGovernanceBaselineSync.IsPresent))
      milestone_gate_mode             = if ($applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) { $effectiveMilestoneGateMode } else { "" }
      milestone_gate_mode_source      = if ($applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) { $milestoneGateModeSource } else { "" }
      milestone_gate_mode_reason      = if ($applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) { $milestoneGateModeReason } else { "" }
      milestone_tag                   = if ($applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) { $MilestoneTag } else { "" }
      milestone_gate_timeout_seconds  = if ($applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) { $MilestoneGateTimeoutSeconds } else { 0 }
      milestone_command_timeout_seconds = if ($applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) { $MilestoneCommandTimeoutSeconds } else { 0 }
      auto_milestone_gate_mode        = [bool]$AutoMilestoneGateMode
      task_type                       = $TaskType
      release_candidate               = [bool]$ReleaseCandidate
      runtime_flow_timeout_seconds    = $RuntimeFlowTimeoutSeconds
      governance_sync_timeout_seconds = $GovernanceSyncTimeoutSeconds
      batch_timeout_seconds           = $BatchTimeoutSeconds
      batch_timed_out                 = $batchTimedOut
      batch_elapsed_seconds           = if ($BatchTimeoutSeconds -gt 0) { [int][Math]::Floor(((Get-Date) - $batchStartedAt).TotalSeconds) } else { 0 }
      target_count                    = @($targetRuns).Count
      failure_count                   = $failureCount
      results                         = $results
    }
    if ($PruneTargetRepoRuns) {
      $payload["prune_target_repo_runs"] = $pruneForJson
    }
    Write-Host ($payload | ConvertTo-Json -Depth 20)
  }
}
elseif ($AllTargets) {
  Write-Host ("batch-summary: targets={0}, failures={1}, timed_out={2}" -f @($targetRuns).Count, $failureCount, $batchTimedOut)
}

if ((-not $Json) -and $PruneTargetRepoRuns) {
  Write-Host (
    "prune_target_repo_runs: status={0} delete_candidates={1} deleted={2} failed_deletions={3}" -f
      $pruneForJson.status,
      $pruneForJson.delete_candidates,
      $pruneForJson.deleted,
      $pruneForJson.failed_deletions
  )
}

exit $overallExitCode
