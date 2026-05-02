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
  [string]$WriteExpectedSha256 = "",
  [switch]$ExecuteWriteFlow,
  [switch]$SkipVerifyAttachment,

  [switch]$Overwrite,
  [switch]$Json,
  [switch]$ListTargets,
  [switch]$FailFast,
  [switch]$SkipGovernanceBaselineSync,
  [switch]$ApplyAllFeatures,
  [switch]$ApplyCodingSpeedProfile,
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
  [int]$TargetParallelism = 1,
  [switch]$SkipCleanMilestoneGate,
  [switch]$DisableCleanMilestoneGateSkip,
  [string]$CatalogPath = "",
  [string]$GovernanceBaselinePath = "",
  [string]$RuntimeFlowPath = "",
  [string]$GovernanceFullCheckPath = "",
  [string]$GovernanceFastCheckPath = "",
  [switch]$PruneTargetRepoRuns,
  [switch]$ExportTargetRepoRuns,
  [string]$PruneRunsRoot = "",
  [int]$PruneKeepDays = 30,
  [int]$PruneKeepLatestPerTarget = 30,
  [switch]$PruneDryRun,
  [switch]$PruneRetiredManagedFiles,
  [switch]$UninstallGovernance,
  [switch]$ApplyManagedAssetRemoval
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. "$PSScriptRoot\Initialize-WindowsProcessEnvironment.ps1"
Initialize-WindowsProcessEnvironment
. "$PSScriptRoot\lib\RuntimeFlow.Targets.ps1"

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

function Stop-ProcessTree {
  param(
    [Parameter(Mandatory = $true)]
    [int]$ProcessId
  )

  if ($ProcessId -le 0) {
    return
  }

  $children = @()
  try {
    $children = @(Get-CimInstance Win32_Process -Filter ("ParentProcessId={0}" -f $ProcessId) -ErrorAction Stop)
  }
  catch {
    $children = @()
  }

  foreach ($child in $children) {
    Stop-ProcessTree -ProcessId ([int]$child.ProcessId)
  }

  try {
    Stop-Process -Id $ProcessId -Force -ErrorAction Stop
  }
  catch {
  }
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
  $startedAt = Get-Date
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
        Stop-ProcessTree -ProcessId ([int]$process.Id)
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
    duration_ms = [int][Math]::Round(((Get-Date) - $startedAt).TotalMilliseconds)
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

function ConvertTo-JsonArrayValue {
  param([object]$Value)

  $result = [System.Collections.Generic.List[object]]::new()
  if ($null -eq $Value) {
    return ,$result
  }
  foreach ($item in @($Value)) {
    if ($null -ne $item) {
      [void]$result.Add($item)
    }
  }
  return ,$result
}

function Test-GovernanceSyncHasChanges {
  param([object]$SyncResult)

  if ($null -eq $SyncResult -or $null -eq $SyncResult.payload) {
    return $true
  }

  foreach ($fieldName in @("changed_catalog_fields", "blocked_catalog_fields", "changed_fields", "changed_speed_profile_fields", "changed_managed_files", "blocked_managed_files", "changed_generated_files", "blocked_generated_files")) {
    if (-not ($SyncResult.payload.PSObject.Properties.Name -contains $fieldName)) {
      return $true
    }
    $items = ConvertTo-JsonArrayValue -Value $SyncResult.payload.$fieldName
    if (@($items).Count -gt 0) {
      return $true
    }
  }
  return $false
}

function Get-TargetGitChangeState {
  param(
    [Parameter(Mandatory = $true)]
    [string]$WorkingDirectory
  )

  $gitCommand = Get-Command git -ErrorAction SilentlyContinue
  if (-not $gitCommand) {
    return [pscustomobject]@{
      can_skip            = $false
      is_git_repository   = $false
      has_pending_changes = $true
      reason              = "git_not_found"
      status_text         = ""
    }
  }

  $insideOutput = & git -C $WorkingDirectory rev-parse --is-inside-work-tree 2>$null
  if ($LASTEXITCODE -ne 0) {
    return [pscustomobject]@{
      can_skip            = $false
      is_git_repository   = $false
      has_pending_changes = $true
      reason              = "git_repository_not_detected"
      status_text         = ""
    }
  }
  $insideText = (($insideOutput | Select-Object -First 1) -as [string]).Trim().ToLowerInvariant()
  if ($insideText -ne "true") {
    return [pscustomobject]@{
      can_skip            = $false
      is_git_repository   = $false
      has_pending_changes = $true
      reason              = "git_repository_not_detected"
      status_text         = ""
    }
  }

  $statusOutput = & git -C $WorkingDirectory status --porcelain 2>&1
  if ($LASTEXITCODE -ne 0) {
    return [pscustomobject]@{
      can_skip            = $false
      is_git_repository   = $true
      has_pending_changes = $true
      reason              = "git_status_failed"
      status_text         = (($statusOutput | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
    }
  }

  $statusText = (($statusOutput | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).Trim()
  $hasPendingChanges = -not [string]::IsNullOrWhiteSpace($statusText)
  return [pscustomobject]@{
    can_skip            = -not $hasPendingChanges
    is_git_repository   = $true
    has_pending_changes = $hasPendingChanges
    reason              = if ($hasPendingChanges) { "pending_changes" } else { "no_pending_changes" }
    status_text         = $statusText
  }
}

function Test-CleanMilestoneGateSkip {
  param(
    [Parameter(Mandatory = $true)]
    [bool]$Enabled,
    [Parameter(Mandatory = $true)]
    [hashtable]$TargetConfig,
    [Parameter(Mandatory = $true)]
    [object]$SyncResult,
    [Parameter(Mandatory = $true)]
    [ValidateSet("full", "fast")]
    [string]$GateMode
  )

  if (-not $Enabled) {
    return [pscustomobject]@{ should_skip = $false; reason = "disabled"; git_state = $null }
  }
  if ($GateMode -ne "fast") {
    return [pscustomobject]@{ should_skip = $false; reason = "gate_mode_not_fast"; git_state = $null }
  }
  if (Test-GovernanceSyncHasChanges -SyncResult $SyncResult) {
    return [pscustomobject]@{ should_skip = $false; reason = "governance_sync_changed"; git_state = $null }
  }

  $gitState = Get-TargetGitChangeState -WorkingDirectory $TargetConfig.AttachmentRoot
  if (-not [bool]$gitState.can_skip) {
    return [pscustomobject]@{ should_skip = $false; reason = [string]$gitState.reason; git_state = $gitState }
  }
  return [pscustomobject]@{ should_skip = $true; reason = "clean_target_no_pending_changes"; git_state = $gitState }
}

function New-CleanMilestoneGateSkippedResult {
  param(
    [Parameter(Mandatory = $true)]
    [string]$TargetName,
    [Parameter(Mandatory = $true)]
    [string]$MilestoneTagValue,
    [Parameter(Mandatory = $true)]
    [ValidateSet("full", "fast")]
    [string]$MilestoneGateModeValue,
    [Parameter(Mandatory = $true)]
    [object]$SkipDecision
  )

  return [pscustomobject]@{
    target                  = $TargetName
    status                  = "skipped"
    reason                  = [string]$SkipDecision.reason
    exit_code               = 0
    payload                 = $null
    output                  = ""
    auto_commit_status      = "skipped"
    auto_commit_reason      = "no_pending_changes"
    commit_hash             = ""
    commit_message          = ""
    trigger                 = "milestone"
    milestone_tag           = $MilestoneTagValue
    gate_mode               = $MilestoneGateModeValue
    command_timeout_seconds = 0
    gate_skipped            = $true
    gate_skip_reason        = [string]$SkipDecision.reason
    git_state               = $SkipDecision.git_state
  }
}

function Test-MilestoneResultAccepted {
  param([object]$MilestoneResult)

  if ($null -eq $MilestoneResult) {
    return $false
  }
  if ([string]$MilestoneResult.status -eq "pass") {
    return $true
  }
  return ([string]$MilestoneResult.reason -eq "clean_target_no_pending_changes" -and [int]$MilestoneResult.exit_code -eq 0)
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

function New-ManagedAssetActionSkippedResult {
  param([Parameter(Mandatory = $true)][string]$TargetRoot)

  return [pscustomobject]@{
    status      = "skipped"
    reason      = "not_requested"
    exit_code   = 0
    target_root = $TargetRoot
    payload     = $null
    output      = ""
  }
}

function New-ManagedAssetActionBlockedResult {
  param(
    [Parameter(Mandatory = $true)][string]$TargetRoot,
    [Parameter(Mandatory = $true)][string]$Reason,
    [int]$FlowExitCode = 0
  )

  $payload = [pscustomobject]@{
    status      = "blocked"
    reason      = $Reason
    dry_run     = $true
    apply       = $false
    backup_root = ""
    summary     = [pscustomobject]@{
      delete_candidates        = 0
      deleted                  = 0
      blocked                  = 1
      missing                  = 0
      shared_patch_candidates  = 0
      shared_patched           = 0
      profile_patch_candidates = 0
      profile_patched          = 0
    }
    delete_candidates        = @()
    deleted_files            = @()
    blocked_files            = @(
      [pscustomobject]@{
        path           = ""
        reason         = $Reason
        flow_exit_code = [int]$FlowExitCode
      }
    )
    missing_files            = @()
    shared_patch_candidates  = @()
    patched_shared_files     = @()
    profile_patch_candidates = @()
    patched_profile_files    = @()
    modified                 = $false
  }

  return [pscustomobject]@{
    status      = "blocked"
    reason      = $Reason
    exit_code   = 2
    target_root = $TargetRoot
    payload     = $payload
    output      = ($payload | ConvertTo-Json -Depth 20)
  }
}

function Invoke-ManagedAssetAction {
  param(
    [Parameter(Mandatory = $true)]
    [string]$RepoRoot,
    [Parameter(Mandatory = $true)]
    [string]$ScriptName,
    [Parameter(Mandatory = $true)]
    [string]$TargetRoot,
    [Parameter(Mandatory = $true)]
    [string]$BaselinePath,
    [Parameter(Mandatory = $true)]
    [string]$PythonCommand,
    [Parameter(Mandatory = $true)]
    [bool]$Apply
  )

  $scriptPath = Join-Path $RepoRoot ("scripts\{0}" -f $ScriptName)
  if (-not (Test-Path -LiteralPath $scriptPath)) {
    return [pscustomobject]@{
      status      = "fail"
      reason      = "managed_asset_script_not_found"
      exit_code   = 1
      target_root = $TargetRoot
      payload     = $null
      output      = ("managed asset script not found: {0}" -f $scriptPath)
    }
  }

  $args = @(
    $scriptPath,
    "--target-repo", $TargetRoot,
    "--baseline-path", $BaselinePath
  )
  if ($Apply) {
    $args += "--apply"
  }
  else {
    $args += "--dry-run"
  }

  $result = Invoke-CommandCapture -Executable $PythonCommand -Arguments $args
  $payload = Try-ParseJson -Raw $result.output
  $status = if ($result.exit_code -eq 0) { "pass" } elseif ($result.exit_code -eq 2) { "blocked" } else { "fail" }
  $reason = if ($status -eq "pass") { "ok" } elseif ($status -eq "blocked") { "blocked" } else { "managed_asset_action_failed" }
  if ($payload -and ($payload.PSObject.Properties.Name -contains "reason") -and -not [string]::IsNullOrWhiteSpace([string]$payload.reason)) {
    $reason = [string]$payload.reason
  }

  return [pscustomobject]@{
    status      = $status
    reason      = $reason
    exit_code   = $result.exit_code
    target_root = $TargetRoot
    payload     = $payload
    output      = $result.output
  }
}

function Convert-ManagedAssetActionForJson {
  param([Parameter(Mandatory = $true)][object]$ActionResult)

  $summary = $null
  if ($ActionResult.payload -and ($ActionResult.payload.PSObject.Properties.Name -contains "summary")) {
    $summary = $ActionResult.payload.summary
  }

  return [ordered]@{
    status                  = [string]$ActionResult.status
    reason                  = [string]$ActionResult.reason
    exit_code               = [int]$ActionResult.exit_code
    target_root             = [string]$ActionResult.target_root
    dry_run                 = $(if ($ActionResult.payload -and ($ActionResult.payload.PSObject.Properties.Name -contains "dry_run")) { [bool]$ActionResult.payload.dry_run } else { $true })
    apply                   = $(if ($ActionResult.payload -and ($ActionResult.payload.PSObject.Properties.Name -contains "apply")) { [bool]$ActionResult.payload.apply } else { $false })
    backup_root             = $(if ($ActionResult.payload -and ($ActionResult.payload.PSObject.Properties.Name -contains "backup_root")) { [string]$ActionResult.payload.backup_root } else { "" })
    manifest_path           = $(if ($ActionResult.payload -and ($ActionResult.payload.PSObject.Properties.Name -contains "manifest_path")) { [string]$ActionResult.payload.manifest_path } else { "" })
    operation_type          = $(if ($ActionResult.payload -and ($ActionResult.payload.PSObject.Properties.Name -contains "operation_type")) { [string]$ActionResult.payload.operation_type } else { "" })
    deletion_policy         = $(if ($ActionResult.payload -and ($ActionResult.payload.PSObject.Properties.Name -contains "deletion_policy")) { [string]$ActionResult.payload.deletion_policy } else { "" })
    delete_candidates       = $(if ($summary -and ($summary.PSObject.Properties.Name -contains "delete_candidates")) { [int]$summary.delete_candidates } else { 0 })
    deleted                 = $(if ($summary -and ($summary.PSObject.Properties.Name -contains "deleted")) { [int]$summary.deleted } else { 0 })
    blocked                 = $(if ($summary -and ($summary.PSObject.Properties.Name -contains "blocked")) { [int]$summary.blocked } else { 0 })
    missing                 = $(if ($summary -and ($summary.PSObject.Properties.Name -contains "missing")) { [int]$summary.missing } else { 0 })
    shared_patch_candidates = $(if ($summary -and ($summary.PSObject.Properties.Name -contains "shared_patch_candidates")) { [int]$summary.shared_patch_candidates } else { 0 })
    shared_patched          = $(if ($summary -and ($summary.PSObject.Properties.Name -contains "shared_patched")) { [int]$summary.shared_patched } else { 0 })
    profile_patch_candidates = $(if ($summary -and ($summary.PSObject.Properties.Name -contains "profile_patch_candidates")) { [int]$summary.profile_patch_candidates } else { 0 })
    profile_patched         = $(if ($summary -and ($summary.PSObject.Properties.Name -contains "profile_patched")) { [int]$summary.profile_patched } else { 0 })
    delete_candidate_items  = $(if ($ActionResult.payload -and ($ActionResult.payload.PSObject.Properties.Name -contains "delete_candidates")) { ConvertTo-JsonArrayValue -Value $ActionResult.payload.delete_candidates } else { @() })
    deleted_files           = $(if ($ActionResult.payload -and ($ActionResult.payload.PSObject.Properties.Name -contains "deleted_files")) { ConvertTo-JsonArrayValue -Value $ActionResult.payload.deleted_files } else { @() })
    blocked_files           = $(if ($ActionResult.payload -and ($ActionResult.payload.PSObject.Properties.Name -contains "blocked_files")) { ConvertTo-JsonArrayValue -Value $ActionResult.payload.blocked_files } else { @() })
    missing_files           = $(if ($ActionResult.payload -and ($ActionResult.payload.PSObject.Properties.Name -contains "missing_files")) { ConvertTo-JsonArrayValue -Value $ActionResult.payload.missing_files } else { @() })
    shared_patch_candidate_items = $(if ($ActionResult.payload -and ($ActionResult.payload.PSObject.Properties.Name -contains "shared_patch_candidates")) { ConvertTo-JsonArrayValue -Value $ActionResult.payload.shared_patch_candidates } else { @() })
    patched_shared_files    = $(if ($ActionResult.payload -and ($ActionResult.payload.PSObject.Properties.Name -contains "patched_shared_files")) { ConvertTo-JsonArrayValue -Value $ActionResult.payload.patched_shared_files } else { @() })
    profile_patch_candidate_items = $(if ($ActionResult.payload -and ($ActionResult.payload.PSObject.Properties.Name -contains "profile_patch_candidates")) { ConvertTo-JsonArrayValue -Value $ActionResult.payload.profile_patch_candidates } else { @() })
    patched_profile_files   = $(if ($ActionResult.payload -and ($ActionResult.payload.PSObject.Properties.Name -contains "patched_profile_files")) { ConvertTo-JsonArrayValue -Value $ActionResult.payload.patched_profile_files } else { @() })
  }
}

function Export-TargetRunEvidence {
  param(
    [Parameter(Mandatory = $true)]
    [object[]]$TargetRuns,
    [Parameter(Mandatory = $true)]
    [string]$RunsRoot,
    [Parameter(Mandatory = $true)]
    [string]$FlowModeValue
  )

  $exported = @()
  if (@($TargetRuns).Count -eq 0) {
    return $exported
  }

  $stamp = Get-Date -Format "yyyyMMddHHmmss"
  New-Item -ItemType Directory -Force -Path $RunsRoot | Out-Null
  foreach ($targetRun in $TargetRuns) {
    if ($null -eq $targetRun.flow_payload) {
      continue
    }
    $targetName = [string]$targetRun.target
    if ([string]::IsNullOrWhiteSpace($targetName)) {
      continue
    }

    $payload = [ordered]@{}
    foreach ($property in $targetRun.flow_payload.PSObject.Properties) {
      $payload[$property.Name] = $property.Value
    }
    $payload["exported_at"] = (Get-Date).ToString("o")
    $payload["export_source"] = "runtime-flow-preset"
    $payload["export_target"] = $targetName
    $payload["target_duration_ms"] = if ($targetRun.PSObject.Properties.Name -contains "target_duration_ms") { [int]$targetRun.target_duration_ms } else { 0 }
    $payload["flow_duration_ms"] = if ($targetRun.PSObject.Properties.Name -contains "flow_duration_ms") { [int]$targetRun.flow_duration_ms } elseif ($targetRun.flow_result -and ($targetRun.flow_result.PSObject.Properties.Name -contains "duration_ms")) { [int]$targetRun.flow_result.duration_ms } else { 0 }
    $payload["governance_sync_duration_ms"] = if ($targetRun.PSObject.Properties.Name -contains "governance_sync_duration_ms") { [int]$targetRun.governance_sync_duration_ms } else { 0 }

    $fileName = "{0}-{1}-{2}.json" -f $targetName, $FlowModeValue, $stamp
    $path = Join-Path $RunsRoot $fileName
    ($payload | ConvertTo-Json -Depth 80) | Set-Content -LiteralPath $path -Encoding UTF8
    $exported += [ordered]@{
      target = $targetName
      path = $path
      file_name = $fileName
      status = $(if ($targetRun.exit_code -eq 0) { "pass" } else { "fail" })
    }
  }
  return $exported
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

  $bootstrapResult = [pscustomobject]@{
    status    = "skipped"
    reason    = "repo_profile_exists"
    exit_code = 0
    payload   = $null
    output    = ""
  }
  $repoProfilePath = Join-Path $TargetConfig.AttachmentRoot ".governed-ai\repo-profile.json"
  if (-not (Test-Path -LiteralPath $repoProfilePath)) {
    $attachScriptPath = Join-Path $RepoRoot "scripts\attach-target-repo.py"
    if (-not (Test-Path -LiteralPath $attachScriptPath)) {
      throw "Missing attach-target-repo.py at $attachScriptPath"
    }

    $primaryLanguage = if ([string]::IsNullOrWhiteSpace($TargetConfig.PrimaryLanguage)) { "unknown" } else { $TargetConfig.PrimaryLanguage }
    $attachArgs = @(
      $attachScriptPath,
      "--target-repo", $TargetConfig.AttachmentRoot,
      "--runtime-state-root", $TargetConfig.AttachmentRuntimeStateRoot,
      "--primary-language", $primaryLanguage
    )
    if (-not [string]::IsNullOrWhiteSpace($TargetConfig.RepoId)) {
      $attachArgs += @("--repo-id", $TargetConfig.RepoId)
    }
    if (-not [string]::IsNullOrWhiteSpace($TargetConfig.DisplayName)) {
      $attachArgs += @("--display-name", $TargetConfig.DisplayName)
    }
    if (-not [string]::IsNullOrWhiteSpace($TargetConfig.BuildCommand)) {
      $attachArgs += @("--build-command", $TargetConfig.BuildCommand)
    }
    if (-not [string]::IsNullOrWhiteSpace($TargetConfig.TestCommand)) {
      $attachArgs += @("--test-command", $TargetConfig.TestCommand)
    }
    if (-not [string]::IsNullOrWhiteSpace($TargetConfig.ContractCommand)) {
      $attachArgs += @("--contract-command", $TargetConfig.ContractCommand)
    }
    $hasContractGate = (-not [string]::IsNullOrWhiteSpace($TargetConfig.ContractCommand)) -or
      (-not [string]::IsNullOrWhiteSpace($TargetConfig.ContractCommandsJson))
    if ([string]::IsNullOrWhiteSpace($TargetConfig.BuildCommand) -or
        [string]::IsNullOrWhiteSpace($TargetConfig.TestCommand) -or
        (-not $hasContractGate)) {
      $attachArgs += "--infer-gate-defaults"
    }

    $attachResult = Invoke-CommandCapture `
      -Executable $PythonCommand `
      -Arguments $attachArgs `
      -TimeoutSeconds $CommandTimeoutSeconds `
      -WorkingDirectory $RepoRoot
    $attachPayload = Try-ParseJson -Raw $attachResult.output
    $bootstrapStatus = if ($attachResult.exit_code -eq 0) { "pass" } else { "fail" }
    $bootstrapReason = if ($bootstrapStatus -eq "pass") {
      "repo_profile_bootstrapped"
    }
    elseif ($attachResult.timed_out) {
      "attach_timed_out"
    }
    else {
      "attach_failed"
    }
    $bootstrapResult = [pscustomobject]@{
      status    = $bootstrapStatus
      reason    = $bootstrapReason
      exit_code = $attachResult.exit_code
      payload   = $attachPayload
      output    = $attachResult.output
    }
    if ($attachResult.exit_code -ne 0) {
      return [pscustomobject]@{
        target    = $TargetName
        status    = "fail"
        reason    = $bootstrapReason
        exit_code = $attachResult.exit_code
        payload   = $attachPayload
        output    = $attachResult.output
        bootstrap = $bootstrapResult
      }
    }
  }

  $args = @(
    $syncScriptPath,
    "--target-repo", $TargetConfig.AttachmentRoot,
    "--baseline-path", $BaselinePath
  )
  if (-not [string]::IsNullOrWhiteSpace($TargetConfig.RepoId)) {
    $args += @("--repo-id", $TargetConfig.RepoId)
  }
  if (-not [string]::IsNullOrWhiteSpace($TargetConfig.DisplayName)) {
    $args += @("--display-name", $TargetConfig.DisplayName)
  }
  if (-not [string]::IsNullOrWhiteSpace($TargetConfig.PrimaryLanguage)) {
    $args += @("--primary-language", $TargetConfig.PrimaryLanguage)
  }
  if (-not [string]::IsNullOrWhiteSpace($TargetConfig.BuildCommand)) {
    $args += @("--build-command", $TargetConfig.BuildCommand)
  }
  if (-not [string]::IsNullOrWhiteSpace($TargetConfig.TestCommand)) {
    $args += @("--test-command", $TargetConfig.TestCommand)
  }
  if (-not [string]::IsNullOrWhiteSpace($TargetConfig.ContractCommandsJson)) {
    $args += @("--contract-commands-json", $TargetConfig.ContractCommandsJson)
  }
  elseif (-not [string]::IsNullOrWhiteSpace($TargetConfig.ContractCommand)) {
    $args += @("--contract-command", $TargetConfig.ContractCommand)
  }
  if (-not [string]::IsNullOrWhiteSpace($TargetConfig.QuickTestCommand)) {
    $args += @("--quick-test-command", $TargetConfig.QuickTestCommand)
  }
  if (-not [string]::IsNullOrWhiteSpace($TargetConfig.QuickTestReason)) {
    $args += @("--quick-test-reason", $TargetConfig.QuickTestReason)
  }
  if ($TargetConfig.QuickTestTimeoutSeconds -gt 0) {
    $args += @("--quick-test-timeout-seconds", ([string]$TargetConfig.QuickTestTimeoutSeconds))
  }
  if (-not [string]::IsNullOrWhiteSpace($TargetConfig.QuickTestSkipReason)) {
    $args += @("--quick-test-skip-reason", $TargetConfig.QuickTestSkipReason)
  }
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
  elseif ($payload -and ($payload.PSObject.Properties.Name -contains "blocked_catalog_fields") -and (@(ConvertTo-JsonArrayValue -Value $payload.blocked_catalog_fields).Count -gt 0)) {
    "catalog_field_blocked"
  }
  elseif ($payload -and ($payload.PSObject.Properties.Name -contains "blocked_generated_files") -and (@(ConvertTo-JsonArrayValue -Value $payload.blocked_generated_files).Count -gt 0)) {
    "generated_file_blocked"
  }
  elseif ($payload -and ($payload.PSObject.Properties.Name -contains "blocked_managed_files") -and (@(ConvertTo-JsonArrayValue -Value $payload.blocked_managed_files).Count -gt 0)) {
    "managed_file_blocked"
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
    bootstrap = $bootstrapResult
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
    if (-not [string]::IsNullOrWhiteSpace($WriteExpectedSha256)) {
      $flowArgs += @("-WriteExpectedSha256", $WriteExpectedSha256)
    }
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

  $syncDurationMs = 0
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
    flow_duration_ms       = $flowDurationMs
    flow_payload           = $flowPayload
    governance_sync_result = $syncResult
    governance_sync_duration_ms = $syncDurationMs
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

  $syncStartedAt = Get-Date
  $syncResult = Invoke-GovernanceBaselineSync `
    -TargetName $TargetName `
    -TargetConfig $TargetConfig `
    -RepoRoot $RepoRoot `
    -BaselinePath $GovernanceBaselinePathResolved `
    -PythonCommand $PythonCommand `
    -CommandTimeoutSeconds $GovernanceSyncCommandTimeoutSeconds
  $syncDurationMs = [int][Math]::Round(((Get-Date) - $syncStartedAt).TotalMilliseconds)
  $exitCode = if ($syncResult.status -eq "fail") { 1 } else { 0 }

  return [pscustomobject]@{
    target                 = $TargetName
    attachment_root        = $TargetConfig.AttachmentRoot
    runtime_state_root     = $TargetConfig.AttachmentRuntimeStateRoot
    flow_result            = [pscustomobject]@{ exit_code = 0; output = "" }
    flow_duration_ms       = 0
    flow_payload           = $null
    governance_sync_result = $syncResult
    governance_sync_duration_ms = $syncDurationMs
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
    [bool]$CleanMilestoneGateSkipEnabled = $false,
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
    $skipDecision = Test-CleanMilestoneGateSkip `
      -Enabled $CleanMilestoneGateSkipEnabled `
      -TargetConfig $TargetConfig `
      -SyncResult $syncResult `
      -GateMode $MilestoneGateModeValue
    if ($skipDecision.should_skip) {
      $milestoneResult = New-CleanMilestoneGateSkippedResult `
        -TargetName $TargetName `
        -MilestoneTagValue $MilestoneTagValue `
        -MilestoneGateModeValue $MilestoneGateModeValue `
        -SkipDecision $skipDecision
      Write-BatchProgressLine `
        -Enabled $EmitProgress `
        -TargetName $TargetName `
        -Stage "milestone_commit" `
        -Status "skipped" `
        -Detail ("reason={0}" -f $milestoneResult.reason)
    }
    else {
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
  }
  else {
    Write-BatchProgressLine -Enabled $EmitProgress -TargetName $TargetName -Stage "milestone_commit" -Status "skipped" -Detail "reason=baseline_sync_failed"
  }

  $exitCode = 0
  if ($syncResult.status -ne "pass") {
    $exitCode = 1
  }
  elseif (-not (Test-MilestoneResultAccepted -MilestoneResult $milestoneResult)) {
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
    [bool]$CleanMilestoneGateSkipEnabled = $false,
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
      $skipDecision = Test-CleanMilestoneGateSkip `
        -Enabled $CleanMilestoneGateSkipEnabled `
        -TargetConfig $TargetConfig `
        -SyncResult $syncResult `
        -GateMode $MilestoneGateModeValue
      if ($skipDecision.should_skip) {
        $milestoneResult = New-CleanMilestoneGateSkippedResult `
          -TargetName $TargetName `
          -MilestoneTagValue $MilestoneTagValue `
          -MilestoneGateModeValue $MilestoneGateModeValue `
          -SkipDecision $skipDecision
        Write-BatchProgressLine `
          -Enabled $EmitProgress `
          -TargetName $TargetName `
          -Stage "milestone_commit" `
          -Status "skipped" `
          -Detail ("reason={0}" -f $milestoneResult.reason)
      }
      else {
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
  elseif (-not (Test-MilestoneResultAccepted -MilestoneResult $milestoneResult)) {
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
$applyCodingSpeedProfile = [bool]$ApplyCodingSpeedProfile
$applyFeatureBaselineOnly = ($ApplyGovernanceBaselineOnly -or $ApplyFeatureBaselineOnly -or $applyCodingSpeedProfile)
$applyFeatureBaselineAndMilestoneCommit = [bool]$ApplyFeatureBaselineAndMilestoneCommit
$managedAssetRemovalActive = ($PruneRetiredManagedFiles.IsPresent -or $UninstallGovernance.IsPresent)
if ($applyAllFeatures -and ($applyFeatureBaselineOnly -or $applyFeatureBaselineAndMilestoneCommit)) {
  throw "-ApplyAllFeatures is mutually exclusive with -ApplyCodingSpeedProfile/-ApplyFeatureBaselineOnly/-ApplyGovernanceBaselineOnly and -ApplyFeatureBaselineAndMilestoneCommit."
}
if ($applyFeatureBaselineOnly -and $applyFeatureBaselineAndMilestoneCommit) {
  throw "-ApplyCodingSpeedProfile/-ApplyFeatureBaselineOnly/-ApplyGovernanceBaselineOnly and -ApplyFeatureBaselineAndMilestoneCommit are mutually exclusive."
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
if ($TargetParallelism -lt 1) {
  throw "-TargetParallelism must be >= 1."
}
if ($SkipCleanMilestoneGate.IsPresent -and $DisableCleanMilestoneGateSkip.IsPresent) {
  throw "-SkipCleanMilestoneGate and -DisableCleanMilestoneGateSkip are mutually exclusive."
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
$autoCleanMilestoneGateSkipEnabled = (
  $AutoMilestoneGateMode.IsPresent -and
  $effectiveMilestoneGateMode -eq "fast" -and
  $FlowMode -eq "daily" -and
  $PolicyStatus -eq "allow" -and
  $WriteTier -ne "high" -and
  -not $ExecuteWriteFlow.IsPresent -and
  -not $ReleaseCandidate.IsPresent
)
$cleanMilestoneGateSkipEnabled = (
  -not $DisableCleanMilestoneGateSkip.IsPresent -and
  ($SkipCleanMilestoneGate.IsPresent -or $autoCleanMilestoneGateSkipEnabled)
)
$cleanMilestoneGateSkipSource = if ($DisableCleanMilestoneGateSkip.IsPresent) {
  "disabled"
}
elseif ($SkipCleanMilestoneGate.IsPresent) {
  "manual"
}
elseif ($autoCleanMilestoneGateSkipEnabled) {
  "auto"
}
else {
  "off"
}
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

$parallelBatchEligible = (
  $AllTargets.IsPresent -and
  $Json.IsPresent -and
  $TargetParallelism -gt 1 -and
  -not $FailFast.IsPresent -and
  -not $applyAllFeatures -and
  -not $applyFeatureBaselineOnly -and
  -not $applyFeatureBaselineAndMilestoneCommit -and
  -not $PruneTargetRepoRuns.IsPresent -and
  -not $managedAssetRemovalActive
)

if ($parallelBatchEligible) {
  $parallelArgsBase = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", $PSCommandPath,
    "-FlowMode", $FlowMode,
    "-Mode", $Mode,
    "-PolicyStatus", $PolicyStatus,
    "-TaskId", $TaskId,
    "-RunId", $RunId,
    "-CommandId", $CommandId,
    "-AdapterId", $AdapterId,
    "-AdapterPreference", $AdapterPreference,
    "-WriteTier", $WriteTier,
    "-WriteToolName", $WriteToolName,
    "-WriteContent", $WriteContent,
    "-CatalogPath", $catalogPath,
    "-GovernanceBaselinePath", $governanceBaselinePathResolved,
    "-RuntimeFlowPath", $runtimeFlowPath,
    "-GovernanceFullCheckPath", $governanceFullCheckPathResolved,
    "-GovernanceFastCheckPath", $governanceFastCheckPathResolved,
    "-RuntimeFlowTimeoutSeconds", ([string]$RuntimeFlowTimeoutSeconds),
    "-GovernanceSyncTimeoutSeconds", ([string]$GovernanceSyncTimeoutSeconds),
    "-Json"
  )
  if ($SkipVerifyAttachment.IsPresent) { $parallelArgsBase += "-SkipVerifyAttachment" }
  if ($Overwrite.IsPresent) { $parallelArgsBase += "-Overwrite" }
  if ($SkipGovernanceBaselineSync.IsPresent) { $parallelArgsBase += "-SkipGovernanceBaselineSync" }
  if ($ExecuteWriteFlow.IsPresent) { $parallelArgsBase += "-ExecuteWriteFlow" }
  if (-not [string]::IsNullOrWhiteSpace($RepoBindingId)) { $parallelArgsBase += @("-RepoBindingId", $RepoBindingId) }
  if (-not [string]::IsNullOrWhiteSpace($WriteTargetPath)) { $parallelArgsBase += @("-WriteTargetPath", $WriteTargetPath) }
  if (-not [string]::IsNullOrWhiteSpace($WriteExpectedSha256)) { $parallelArgsBase += @("-WriteExpectedSha256", $WriteExpectedSha256) }
  if (-not [string]::IsNullOrWhiteSpace($WriteToolCommand)) { $parallelArgsBase += @("-WriteToolCommand", $WriteToolCommand) }
  if (-not [string]::IsNullOrWhiteSpace($RollbackReference)) { $parallelArgsBase += @("-RollbackReference", $RollbackReference) }

  function New-ParallelTargetRun {
    param(
      [Parameter(Mandatory = $true)]
      [string]$TargetName,
      [Parameter(Mandatory = $true)]
      [int]$ExitCode,
      [Parameter(Mandatory = $true)]
      [string]$OutputText,
      [Parameter(Mandatory = $true)]
      [bool]$TimedOut,
      [Parameter(Mandatory = $true)]
      [int]$DurationMs
    )

    $flowPayload = Try-ParseJson -Raw $OutputText
    if ($flowPayload -and ($flowPayload.PSObject.Properties.Name -contains "exit_code")) {
      $ExitCode = [int]$flowPayload.exit_code
    }

    return [pscustomobject]@{
      target = $TargetName
      target_duration_ms = $DurationMs
      exit_code = $ExitCode
      flow_result = [pscustomobject]@{
        exit_code = $ExitCode
        output = $OutputText
        timed_out = $TimedOut
        duration_ms = $DurationMs
      }
      flow_duration_ms = $DurationMs
      flow_payload = $flowPayload
      governance_sync_result = [pscustomobject]@{
        status = "skipped"
        reason = if ($FlowMode -eq "onboard" -and -not $SkipGovernanceBaselineSync.IsPresent) { "single_target_worker_owned" } else { "flow_mode_not_onboard" }
        exit_code = 0
        payload = $null
        output = ""
      }
      governance_sync_duration_ms = 0
      milestone_commit_result = [pscustomobject]@{
        status = "skipped"
        reason = "not_requested"
        exit_code = 0
        auto_commit_status = ""
        auto_commit_reason = ""
        commit_hash = ""
        commit_message = ""
        trigger = ""
        milestone_tag = ""
      }
      prune_retired_managed_files_result = New-ManagedAssetActionSkippedResult -TargetRoot $TargetName
      uninstall_governance_result = New-ManagedAssetActionSkippedResult -TargetRoot $TargetName
    }
  }

  $pendingTargets = [System.Collections.Queue]::new()
  foreach ($targetName in $selectedTargets) {
    $pendingTargets.Enqueue($targetName)
  }
  $activeProcesses = @()
  while ($pendingTargets.Count -gt 0 -or @($activeProcesses).Count -gt 0) {
    while ($pendingTargets.Count -gt 0 -and @($activeProcesses).Count -lt $TargetParallelism) {
      $targetName = [string]$pendingTargets.Dequeue()
      $targetArgs = @($parallelArgsBase + @("-Target", $targetName))
      $stdoutPath = [System.IO.Path]::GetTempFileName()
      $stderrPath = [System.IO.Path]::GetTempFileName()
      $process = Start-Process `
        -FilePath "pwsh" `
        -ArgumentList (ConvertTo-ProcessArgumentString -ArgumentList $targetArgs) `
        -WorkingDirectory $repoRoot `
        -NoNewWindow `
        -PassThru `
        -RedirectStandardOutput $stdoutPath `
        -RedirectStandardError $stderrPath
      $activeProcesses += [pscustomobject]@{
        target = $targetName
        process = $process
        stdout_path = $stdoutPath
        stderr_path = $stderrPath
        started_at = Get-Date
      }
    }

    if ($BatchTimeoutSeconds -gt 0) {
      $batchElapsedSeconds = [int][Math]::Floor(((Get-Date) - $batchStartedAt).TotalSeconds)
      if ($batchElapsedSeconds -ge $BatchTimeoutSeconds) {
        $batchTimedOut = $true
        break
      }
    }

    $completedEntries = @($activeProcesses | Where-Object { $_.process.HasExited })
    if (@($completedEntries).Count -eq 0) {
      Start-Sleep -Milliseconds 200
      continue
    }

    foreach ($entry in $completedEntries) {
      $targetDurationMs = [int][Math]::Round(((Get-Date) - $entry.started_at).TotalMilliseconds)
      $stdoutText = Get-Content -LiteralPath $entry.stdout_path -Raw -ErrorAction SilentlyContinue
      $stderrText = Get-Content -LiteralPath $entry.stderr_path -Raw -ErrorAction SilentlyContinue
      $segments = @()
      if (-not [string]::IsNullOrWhiteSpace($stdoutText)) {
        $segments += $stdoutText.TrimEnd()
      }
      if (-not [string]::IsNullOrWhiteSpace($stderrText)) {
        $segments += $stderrText.TrimEnd()
      }
      $targetRuns += New-ParallelTargetRun `
        -TargetName ([string]$entry.target) `
        -ExitCode ([int]$entry.process.ExitCode) `
        -OutputText (($segments -join [Environment]::NewLine).TrimEnd()) `
        -TimedOut $false `
        -DurationMs $targetDurationMs
      Remove-Item -LiteralPath $entry.stdout_path -ErrorAction SilentlyContinue
      Remove-Item -LiteralPath $entry.stderr_path -ErrorAction SilentlyContinue
    }
    $completedIds = @($completedEntries | ForEach-Object { $_.process.Id })
    $activeProcesses = @($activeProcesses | Where-Object { $completedIds -notcontains $_.process.Id })
  }

  if ($batchTimedOut) {
    foreach ($entry in $activeProcesses) {
      $targetDurationMs = [int][Math]::Round(((Get-Date) - $entry.started_at).TotalMilliseconds)
      Stop-ProcessTree -ProcessId ([int]$entry.process.Id)
      $stdoutText = Get-Content -LiteralPath $entry.stdout_path -Raw -ErrorAction SilentlyContinue
      $stderrText = Get-Content -LiteralPath $entry.stderr_path -Raw -ErrorAction SilentlyContinue
      $segments = @()
      if (-not [string]::IsNullOrWhiteSpace($stdoutText)) {
        $segments += $stdoutText.TrimEnd()
      }
      if (-not [string]::IsNullOrWhiteSpace($stderrText)) {
        $segments += $stderrText.TrimEnd()
      }
      $segments += ("target parallel worker timed out because batch timeout {0}s was exceeded" -f $BatchTimeoutSeconds)
      $targetRuns += New-ParallelTargetRun `
        -TargetName ([string]$entry.target) `
        -ExitCode 124 `
        -OutputText (($segments -join [Environment]::NewLine).TrimEnd()) `
        -TimedOut $true `
        -DurationMs $targetDurationMs
      Remove-Item -LiteralPath $entry.stdout_path -ErrorAction SilentlyContinue
      Remove-Item -LiteralPath $entry.stderr_path -ErrorAction SilentlyContinue
    }
  }
}
else {
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
  elseif ($applyCodingSpeedProfile) {
    "coding_speed_profile"
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
      -CleanMilestoneGateSkipEnabled $cleanMilestoneGateSkipEnabled `
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
      -CleanMilestoneGateSkipEnabled $cleanMilestoneGateSkipEnabled `
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

  $flowFailedBeforeManagedRemoval = ($targetRun.exit_code -ne 0)
  $blockManagedAssetApplyAfterFlowFailure = ($ApplyManagedAssetRemoval.IsPresent -and $flowFailedBeforeManagedRemoval)
  $managedAssetBlockedReason = "target_flow_failed_before_managed_asset_apply"

  $pruneRetiredManagedFilesResult = New-ManagedAssetActionSkippedResult -TargetRoot $targetConfig.AttachmentRoot
  if ($PruneRetiredManagedFiles -and $blockManagedAssetApplyAfterFlowFailure) {
    $pruneRetiredManagedFilesResult = New-ManagedAssetActionBlockedResult `
      -TargetRoot $targetConfig.AttachmentRoot `
      -Reason $managedAssetBlockedReason `
      -FlowExitCode ([int]$targetRun.exit_code)
  }
  elseif ($PruneRetiredManagedFiles) {
    $pruneRetiredManagedFilesResult = Invoke-ManagedAssetAction `
      -RepoRoot $repoRoot `
      -ScriptName "prune-retired-managed-files.py" `
      -TargetRoot $targetConfig.AttachmentRoot `
      -BaselinePath $governanceBaselinePathResolved `
      -PythonCommand $pythonCommand `
      -Apply $ApplyManagedAssetRemoval.IsPresent
  }
  $uninstallGovernanceResult = New-ManagedAssetActionSkippedResult -TargetRoot $targetConfig.AttachmentRoot
  if ($UninstallGovernance -and $blockManagedAssetApplyAfterFlowFailure) {
    $uninstallGovernanceResult = New-ManagedAssetActionBlockedResult `
      -TargetRoot $targetConfig.AttachmentRoot `
      -Reason $managedAssetBlockedReason `
      -FlowExitCode ([int]$targetRun.exit_code)
  }
  elseif ($UninstallGovernance) {
    $uninstallGovernanceResult = Invoke-ManagedAssetAction `
      -RepoRoot $repoRoot `
      -ScriptName "uninstall-target-repo-governance.py" `
      -TargetRoot $targetConfig.AttachmentRoot `
      -BaselinePath $governanceBaselinePathResolved `
      -PythonCommand $pythonCommand `
      -Apply $ApplyManagedAssetRemoval.IsPresent
  }
  $targetRun | Add-Member -NotePropertyName "prune_retired_managed_files_result" -NotePropertyValue $pruneRetiredManagedFilesResult -Force
  $targetRun | Add-Member -NotePropertyName "uninstall_governance_result" -NotePropertyValue $uninstallGovernanceResult -Force
  if (($targetRun.exit_code -eq 0) -and (($pruneRetiredManagedFilesResult.status -in @("fail", "blocked")) -or ($uninstallGovernanceResult.status -in @("fail", "blocked")))) {
    $targetRun.exit_code = 2
  }
  $targetRuns += $targetRun

  $targetDurationMs = [int][Math]::Round(((Get-Date) - $targetStartedAt).TotalMilliseconds)
  $targetRun | Add-Member -NotePropertyName "target_duration_ms" -NotePropertyValue $targetDurationMs -Force
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
      $changedSpeedProfileFields = @()
      if ($targetRun.governance_sync_result.payload -and $targetRun.governance_sync_result.payload.changed_fields) {
        $changedFields = ConvertTo-JsonArrayValue -Value $targetRun.governance_sync_result.payload.changed_fields
      }
      if ($targetRun.governance_sync_result.payload -and $targetRun.governance_sync_result.payload.changed_speed_profile_fields) {
        $changedSpeedProfileFields = ConvertTo-JsonArrayValue -Value $targetRun.governance_sync_result.payload.changed_speed_profile_fields
      }
      Write-Host ("governance_sync: status=pass target={0} changed_fields={1} changed_speed_profile_fields={2}" -f $targetName, (@($changedFields) -join ","), (@($changedSpeedProfileFields) -join ","))
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
    elseif ($targetRun.milestone_commit_result.status -eq "skipped") {
      Write-Host ("milestone_commit: status=skipped target={0} reason={1}" -f $targetName, $targetRun.milestone_commit_result.reason)
    }
    elseif ($targetRun.milestone_commit_result.status -eq "fail") {
      Write-Host ("milestone_commit: status=fail target={0} reason={1}" -f $targetName, $targetRun.milestone_commit_result.reason)
      if (-not [string]::IsNullOrWhiteSpace($targetRun.milestone_commit_result.output)) {
        Write-Host $targetRun.milestone_commit_result.output
      }
    }
    if ($PruneRetiredManagedFiles) {
      Write-Host ("prune_retired_managed_files: status={0} target={1} reason={2}" -f $pruneRetiredManagedFilesResult.status, $targetName, $pruneRetiredManagedFilesResult.reason)
      if (-not [string]::IsNullOrWhiteSpace($pruneRetiredManagedFilesResult.output)) {
        Write-Host $pruneRetiredManagedFilesResult.output
      }
    }
    if ($UninstallGovernance) {
      Write-Host ("uninstall_governance: status={0} target={1} reason={2}" -f $uninstallGovernanceResult.status, $targetName, $uninstallGovernanceResult.reason)
      if (-not [string]::IsNullOrWhiteSpace($uninstallGovernanceResult.output)) {
        Write-Host $uninstallGovernanceResult.output
      }
    }
  }

  if ($FailFast -and $targetRun.exit_code -ne 0) {
    break
  }
}
}

$failureCount = @($targetRuns | Where-Object { $_.exit_code -ne 0 }).Count
$exportedTargetRepoRuns = @()
if ($ExportTargetRepoRuns) {
  $exportedTargetRepoRuns = Export-TargetRunEvidence `
    -TargetRuns $targetRuns `
    -RunsRoot $pruneRunsRootResolved `
    -FlowModeValue $FlowMode
}
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
    $singlePruneRetiredForJson = Convert-ManagedAssetActionForJson -ActionResult $single.prune_retired_managed_files_result
    $singleUninstallForJson = Convert-ManagedAssetActionForJson -ActionResult $single.uninstall_governance_result
    $syncStatus = [string]$single.governance_sync_result.status
    $syncReason = [string]$single.governance_sync_result.reason
    if (($syncStatus -eq "skipped") -and ($syncReason -in @("flow_mode_not_onboard", "explicit_skip", "runtime_flow_failed"))) {
      if (-not [string]::IsNullOrWhiteSpace($single.flow_result.output)) {
        if (-not ($PruneTargetRepoRuns -or $managedAssetRemovalActive)) {
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
            if ($PruneRetiredManagedFiles) {
              $wrappedFlowOnly["prune_retired_managed_files"] = $singlePruneRetiredForJson
            }
            if ($UninstallGovernance) {
              $wrappedFlowOnly["uninstall_governance"] = $singleUninstallForJson
            }
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
            if ($PruneRetiredManagedFiles) {
              $flowOnlyFallback["prune_retired_managed_files"] = $singlePruneRetiredForJson
            }
            if ($UninstallGovernance) {
              $flowOnlyFallback["uninstall_governance"] = $singleUninstallForJson
            }
            Write-Host ($flowOnlyFallback | ConvertTo-Json -Depth 20)
          }
        }
      }
      elseif ($PruneTargetRepoRuns -or $managedAssetRemovalActive) {
        $flowOnlyEmpty = [ordered]@{
          target                 = $single.target
          exit_code              = $single.exit_code
          flow_exit_code         = $single.flow_result.exit_code
          flow_output            = ""
          prune_target_repo_runs = $pruneForJson
        }
        if ($PruneRetiredManagedFiles) {
          $flowOnlyEmpty["prune_retired_managed_files"] = $singlePruneRetiredForJson
        }
        if ($UninstallGovernance) {
          $flowOnlyEmpty["uninstall_governance"] = $singleUninstallForJson
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
          catalog_changed = if ($single.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $single.governance_sync_result.payload.changed_catalog_fields } else { @() }
          catalog_blocked = if ($single.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $single.governance_sync_result.payload.blocked_catalog_fields } else { @() }
          changed      = if ($single.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $single.governance_sync_result.payload.changed_fields } else { @() }
          speed_changed = if ($single.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $single.governance_sync_result.payload.changed_speed_profile_fields } else { @() }
          managed_changed = if ($single.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $single.governance_sync_result.payload.changed_managed_files } else { @() }
          managed_blocked = if ($single.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $single.governance_sync_result.payload.blocked_managed_files } else { @() }
          generated_changed = if ($single.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $single.governance_sync_result.payload.changed_generated_files } else { @() }
          generated_blocked = if ($single.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $single.governance_sync_result.payload.blocked_generated_files } else { @() }
          sync_revision = if ($single.governance_sync_result.payload) { $single.governance_sync_result.payload.sync_revision } else { $null }
          quick_test_slice_source = if ($single.governance_sync_result.payload) { $single.governance_sync_result.payload.quick_test_slice_source } else { "" }
          outer_ai_action = if ($single.governance_sync_result.payload) { $single.governance_sync_result.payload.outer_ai_action } else { "" }
          quick_test_prompt_path = if ($single.governance_sync_result.payload) { $single.governance_sync_result.payload.quick_test_prompt_path } else { "" }
          outer_ai_instruction = if ($single.governance_sync_result.payload) { $single.governance_sync_result.payload.outer_ai_instruction } else { "" }
          bootstrap    = if ($single.governance_sync_result.PSObject.Properties.Name -contains "bootstrap") { $single.governance_sync_result.bootstrap } else { $null }
        }
        $wrapped["milestone_commit"] = [ordered]@{
          status             = $single.milestone_commit_result.status
          reason             = $single.milestone_commit_result.reason
          exit_code          = $single.milestone_commit_result.exit_code
          gate_mode          = if ($single.milestone_commit_result.PSObject.Properties.Name -contains "gate_mode") { $single.milestone_commit_result.gate_mode } else { "" }
          gate_mode_source   = $milestoneGateModeSource
          gate_mode_reason   = $milestoneGateModeReason
          command_timeout_seconds = if ($single.milestone_commit_result.PSObject.Properties.Name -contains "command_timeout_seconds") { $single.milestone_commit_result.command_timeout_seconds } else { 0 }
          gate_skipped       = if ($single.milestone_commit_result.PSObject.Properties.Name -contains "gate_skipped") { [bool]$single.milestone_commit_result.gate_skipped } else { $false }
          gate_skip_reason   = if ($single.milestone_commit_result.PSObject.Properties.Name -contains "gate_skip_reason") { $single.milestone_commit_result.gate_skip_reason } else { "" }
          auto_commit_status = $single.milestone_commit_result.auto_commit_status
          auto_commit_reason = $single.milestone_commit_result.auto_commit_reason
          commit_hash        = $single.milestone_commit_result.commit_hash
          commit_message     = $single.milestone_commit_result.commit_message
          trigger            = $single.milestone_commit_result.trigger
          milestone_tag      = $single.milestone_commit_result.milestone_tag
        }
        if ($applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) {
          $wrapped["clean_milestone_gate_skip_enabled"] = [bool]$cleanMilestoneGateSkipEnabled
          $wrapped["clean_milestone_gate_skip_source"] = $cleanMilestoneGateSkipSource
        }
        if ($PruneTargetRepoRuns) {
          $wrapped["prune_target_repo_runs"] = $pruneForJson
        }
        if ($PruneRetiredManagedFiles) {
          $wrapped["prune_retired_managed_files"] = $singlePruneRetiredForJson
        }
        if ($UninstallGovernance) {
          $wrapped["uninstall_governance"] = $singleUninstallForJson
        }
        Write-Host ($wrapped | ConvertTo-Json -Depth 20)
      }
      else {
        $fallback = [ordered]@{
          target                  = $single.target
          exit_code               = $single.exit_code
          flow_exit_code          = $single.flow_result.exit_code
          flow_output             = $single.flow_result.output
          governance_baseline_sync = [ordered]@{
            status       = $single.governance_sync_result.status
            reason       = $single.governance_sync_result.reason
            exit_code    = $single.governance_sync_result.exit_code
            catalog_changed = if ($single.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $single.governance_sync_result.payload.changed_catalog_fields } else { @() }
            catalog_blocked = if ($single.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $single.governance_sync_result.payload.blocked_catalog_fields } else { @() }
            changed      = if ($single.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $single.governance_sync_result.payload.changed_fields } else { @() }
            speed_changed = if ($single.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $single.governance_sync_result.payload.changed_speed_profile_fields } else { @() }
            managed_changed = if ($single.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $single.governance_sync_result.payload.changed_managed_files } else { @() }
            managed_blocked = if ($single.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $single.governance_sync_result.payload.blocked_managed_files } else { @() }
            generated_changed = if ($single.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $single.governance_sync_result.payload.changed_generated_files } else { @() }
            generated_blocked = if ($single.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $single.governance_sync_result.payload.blocked_generated_files } else { @() }
            sync_revision = if ($single.governance_sync_result.payload) { $single.governance_sync_result.payload.sync_revision } else { $null }
            quick_test_slice_source = if ($single.governance_sync_result.payload) { $single.governance_sync_result.payload.quick_test_slice_source } else { "" }
            outer_ai_action = if ($single.governance_sync_result.payload) { $single.governance_sync_result.payload.outer_ai_action } else { "" }
            quick_test_prompt_path = if ($single.governance_sync_result.payload) { $single.governance_sync_result.payload.quick_test_prompt_path } else { "" }
            outer_ai_instruction = if ($single.governance_sync_result.payload) { $single.governance_sync_result.payload.outer_ai_instruction } else { "" }
            bootstrap    = if ($single.governance_sync_result.PSObject.Properties.Name -contains "bootstrap") { $single.governance_sync_result.bootstrap } else { $null }
          }
          milestone_commit        = $single.milestone_commit_result
        }
        if ($applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) {
          $fallback["clean_milestone_gate_skip_enabled"] = [bool]$cleanMilestoneGateSkipEnabled
          $fallback["clean_milestone_gate_skip_source"] = $cleanMilestoneGateSkipSource
        }
        if ($PruneTargetRepoRuns) {
          $fallback["prune_target_repo_runs"] = $pruneForJson
        }
        if ($PruneRetiredManagedFiles) {
          $fallback["prune_retired_managed_files"] = $singlePruneRetiredForJson
        }
        if ($UninstallGovernance) {
          $fallback["uninstall_governance"] = $singleUninstallForJson
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
        $targetDurationMs = if ($_.PSObject.Properties.Name -contains "target_duration_ms") { [int]$_.target_duration_ms } else { 0 }
        $pruneRetiredForJson = Convert-ManagedAssetActionForJson -ActionResult $_.prune_retired_managed_files_result
        $uninstallForJson = Convert-ManagedAssetActionForJson -ActionResult $_.uninstall_governance_result
        $flowDurationMs = if ($_.PSObject.Properties.Name -contains "flow_duration_ms") {
          [int]$_.flow_duration_ms
        }
        elseif ($_.flow_result -and ($_.flow_result.PSObject.Properties.Name -contains "duration_ms")) {
          [int]$_.flow_result.duration_ms
        }
        else {
          0
        }
        $governanceSyncDurationMs = if ($_.PSObject.Properties.Name -contains "governance_sync_duration_ms") {
          [int]$_.governance_sync_duration_ms
        }
        elseif ($_.governance_sync_result -and ($_.governance_sync_result.PSObject.Properties.Name -contains "duration_ms")) {
          [int]$_.governance_sync_result.duration_ms
        }
        else {
          0
        }
        [ordered]@{
          target                   = $_.target
          exit_code                = $_.exit_code
          target_duration_ms       = $targetDurationMs
          flow_exit_code           = $_.flow_result.exit_code
          flow_timed_out           = $flowTimedOut
          flow_duration_ms         = $flowDurationMs
          governance_sync_status   = $_.governance_sync_result.status
          governance_sync_reason   = $_.governance_sync_result.reason
          governance_sync_exit_code = $_.governance_sync_result.exit_code
          governance_sync_duration_ms = $governanceSyncDurationMs
          governance_sync_catalog_changed = if ($_.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $_.governance_sync_result.payload.changed_catalog_fields } else { @() }
          governance_sync_catalog_blocked = if ($_.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $_.governance_sync_result.payload.blocked_catalog_fields } else { @() }
          governance_sync_changed  = if ($_.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $_.governance_sync_result.payload.changed_fields } else { @() }
          governance_sync_speed_changed = if ($_.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $_.governance_sync_result.payload.changed_speed_profile_fields } else { @() }
          governance_sync_managed_changed = if ($_.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $_.governance_sync_result.payload.changed_managed_files } else { @() }
          governance_sync_managed_blocked = if ($_.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $_.governance_sync_result.payload.blocked_managed_files } else { @() }
          governance_sync_generated_changed = if ($_.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $_.governance_sync_result.payload.changed_generated_files } else { @() }
          governance_sync_generated_blocked = if ($_.governance_sync_result.payload) { ConvertTo-JsonArrayValue -Value $_.governance_sync_result.payload.blocked_generated_files } else { @() }
          governance_sync_quick_test_slice_source = if ($_.governance_sync_result.payload) { $_.governance_sync_result.payload.quick_test_slice_source } else { "" }
          governance_sync_outer_ai_action = if ($_.governance_sync_result.payload) { $_.governance_sync_result.payload.outer_ai_action } else { "" }
          governance_sync_quick_test_prompt_path = if ($_.governance_sync_result.payload) { $_.governance_sync_result.payload.quick_test_prompt_path } else { "" }
          governance_sync_outer_ai_instruction = if ($_.governance_sync_result.payload) { $_.governance_sync_result.payload.outer_ai_instruction } else { "" }
          milestone_commit_status  = $_.milestone_commit_result.status
          milestone_commit_reason  = $_.milestone_commit_result.reason
          milestone_commit_exit_code = $_.milestone_commit_result.exit_code
          milestone_gate_mode      = if ($_.milestone_commit_result.PSObject.Properties.Name -contains "gate_mode") { $_.milestone_commit_result.gate_mode } else { "" }
          milestone_gate_mode_source = $milestoneGateModeSource
          milestone_gate_mode_reason = $milestoneGateModeReason
          milestone_command_timeout_seconds = if ($_.milestone_commit_result.PSObject.Properties.Name -contains "command_timeout_seconds") { $_.milestone_commit_result.command_timeout_seconds } else { 0 }
          milestone_gate_skipped = if ($_.milestone_commit_result.PSObject.Properties.Name -contains "gate_skipped") { [bool]$_.milestone_commit_result.gate_skipped } else { $false }
          milestone_gate_skip_reason = if ($_.milestone_commit_result.PSObject.Properties.Name -contains "gate_skip_reason") { $_.milestone_commit_result.gate_skip_reason } else { "" }
          auto_commit_status       = $_.milestone_commit_result.auto_commit_status
          auto_commit_reason       = $_.milestone_commit_result.auto_commit_reason
          auto_commit_commit_hash  = $_.milestone_commit_result.commit_hash
          auto_commit_trigger      = $_.milestone_commit_result.trigger
          prune_retired_managed_files = if ($PruneRetiredManagedFiles) { $pruneRetiredForJson } else { $null }
          uninstall_governance     = if ($UninstallGovernance) { $uninstallForJson } else { $null }
        }
      }
    )
    $outerAiRecommendationTasks = @(
      $results | Where-Object {
        $_.governance_sync_outer_ai_action -in @("prompt_written", "prompt_available")
      } | ForEach-Object {
        $recommendationPath = ""
        if (-not [string]::IsNullOrWhiteSpace([string]$_.governance_sync_quick_test_prompt_path)) {
          $recommendationPath = ([string]$_.governance_sync_quick_test_prompt_path).Replace("quick-test-slice.prompt.md", "quick-test-slice.recommendation.json")
        }
        [ordered]@{
          target = $_.target
          action = "read_prompt_and_write_recommendation"
          prompt_path = $_.governance_sync_quick_test_prompt_path
          recommendation_path = $recommendationPath
          instruction = $_.governance_sync_outer_ai_instruction
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
      apply_coding_speed_profile      = [bool]$applyCodingSpeedProfile
      apply_feature_baseline_only     = [bool]$applyFeatureBaselineOnly
      apply_governance_baseline_only  = [bool]$ApplyGovernanceBaselineOnly
      apply_feature_baseline_and_milestone_commit = [bool]$applyFeatureBaselineAndMilestoneCommit
      prune_retired_managed_files_active = [bool]$PruneRetiredManagedFiles
      uninstall_governance_active     = [bool]$UninstallGovernance
      apply_managed_asset_removal     = [bool]$ApplyManagedAssetRemoval
      governance_baseline_sync_active = ($applyAllFeatures -or $applyFeatureBaselineOnly -or $applyFeatureBaselineAndMilestoneCommit -or (($FlowMode -eq "onboard") -and -not $SkipGovernanceBaselineSync.IsPresent))
      milestone_gate_mode             = if ($applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) { $effectiveMilestoneGateMode } else { "" }
      milestone_gate_mode_source      = if ($applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) { $milestoneGateModeSource } else { "" }
      milestone_gate_mode_reason      = if ($applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) { $milestoneGateModeReason } else { "" }
      milestone_tag                   = if ($applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) { $MilestoneTag } else { "" }
      milestone_gate_timeout_seconds  = if ($applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) { $MilestoneGateTimeoutSeconds } else { 0 }
      milestone_command_timeout_seconds = if ($applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) { $MilestoneCommandTimeoutSeconds } else { 0 }
      auto_milestone_gate_mode        = [bool]$AutoMilestoneGateMode
      clean_milestone_gate_skip_enabled = if ($applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) { [bool]$cleanMilestoneGateSkipEnabled } else { $false }
      clean_milestone_gate_skip_source = if ($applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) { $cleanMilestoneGateSkipSource } else { "off" }
      task_type                       = $TaskType
      release_candidate               = [bool]$ReleaseCandidate
      runtime_flow_timeout_seconds    = $RuntimeFlowTimeoutSeconds
      governance_sync_timeout_seconds = $GovernanceSyncTimeoutSeconds
      batch_timeout_seconds           = $BatchTimeoutSeconds
      batch_timed_out                 = $batchTimedOut
      batch_elapsed_seconds           = [int][Math]::Floor(((Get-Date) - $batchStartedAt).TotalSeconds)
      target_count                    = @($targetRuns).Count
      failure_count                   = $failureCount
      exported_target_repo_runs       = $exportedTargetRepoRuns
      outer_ai_recommendation_action  = if (@($outerAiRecommendationTasks).Count -gt 0) { "read_prompt_and_write_recommendation" } else { "none" }
      outer_ai_recommendation_tasks   = $outerAiRecommendationTasks
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
