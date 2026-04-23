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
  [int]$MilestoneGateTimeoutSeconds = 900,
  [string]$CatalogPath = "",
  [string]$GovernanceBaselinePath = "",
  [string]$RuntimeFlowPath = "",
  [string]$GovernanceFullCheckPath = "",
  [switch]$PruneTargetRepoRuns,
  [string]$PruneRunsRoot = "",
  [int]$PruneKeepDays = 30,
  [int]$PruneKeepLatestPerTarget = 30,
  [switch]$PruneDryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

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

function Invoke-CommandCapture {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Executable,
    [string[]]$Arguments = @()
  )

  $output = & $Executable @Arguments 2>&1
  $exitCode = $LASTEXITCODE
  if ($null -eq $exitCode) {
    $exitCode = 0
  }

  return [pscustomobject]@{
    exit_code = [int]$exitCode
    output    = (($output | ForEach-Object { $_.ToString() }) -join [Environment]::NewLine).TrimEnd()
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
    [string]$PythonCommand
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
  $result = Invoke-CommandCapture -Executable $PythonCommand -Arguments $args
  $payload = Try-ParseJson -Raw $result.output
  $status = if ($result.exit_code -eq 0) { "pass" } else { "fail" }

  return [pscustomobject]@{
    target    = $TargetName
    status    = $status
    reason    = if ($status -eq "pass") { "ok" } else { "apply_failed" }
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

  $flowResult = Invoke-CommandCapture -Executable "pwsh" -Arguments $flowArgs
  $flowDurationMs = [int][Math]::Round(((Get-Date) - $flowStartedAt).TotalMilliseconds)
  $flowStatus = if ($flowResult.exit_code -eq 0) { "pass" } else { "fail" }
  Write-BatchProgressLine `
    -Enabled $EmitProgress `
    -TargetName $TargetName `
    -Stage "runtime_flow" `
    -Status $flowStatus `
    -Detail ("duration_ms={0} exit_code={1}" -f $flowDurationMs, $flowResult.exit_code)
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
        -PythonCommand $PythonCommand
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
    [string]$PythonCommand
  )

  $syncResult = Invoke-GovernanceBaselineSync `
    -TargetName $TargetName `
    -TargetConfig $TargetConfig `
    -RepoRoot $RepoRoot `
    -BaselinePath $GovernanceBaselinePathResolved `
    -PythonCommand $PythonCommand
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
    [string]$FullCheckPath,
    [Parameter(Mandatory = $true)]
    [string]$MilestoneTagValue,
    [Parameter(Mandatory = $true)]
    [int]$MilestoneGateTimeoutSeconds
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
    }
  }

  $args = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", $FullCheckPath,
    "-RepoProfilePath", $repoProfilePath,
    "-WorkingDirectory", $TargetConfig.AttachmentRoot,
    "-MilestoneTag", $MilestoneTagValue,
    "-GateTimeoutSeconds", [string]$MilestoneGateTimeoutSeconds,
    "-Json"
  )
  $result = Invoke-CommandCapture -Executable "pwsh" -Arguments $args
  $payload = Try-ParseJson -Raw $result.output
  $status = if ($result.exit_code -eq 0) { "pass" } else { "fail" }
  $reason = if ($status -eq "pass") { "ok" } else { "full_check_failed" }

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
    [string]$GovernanceFullCheckPathResolved,
    [Parameter(Mandatory = $true)]
    [string]$MilestoneTagValue,
    [Parameter(Mandatory = $true)]
    [int]$MilestoneGateTimeoutSeconds,
    [bool]$EmitProgress = $false
  )

  Write-BatchProgressLine -Enabled $EmitProgress -TargetName $TargetName -Stage "governance_sync" -Status "start" -Detail "source=baseline_only"
  $syncStartedAt = Get-Date
  $syncResult = Invoke-GovernanceBaselineSync `
    -TargetName $TargetName `
    -TargetConfig $TargetConfig `
    -RepoRoot $RepoRoot `
    -BaselinePath $GovernanceBaselinePathResolved `
    -PythonCommand $PythonCommand
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
  }
  if ($syncResult.status -eq "pass") {
    Write-BatchProgressLine `
      -Enabled $EmitProgress `
      -TargetName $TargetName `
      -Stage "milestone_commit" `
      -Status "start" `
      -Detail ("milestone_tag={0} timeout_s={1}" -f $MilestoneTagValue, $MilestoneGateTimeoutSeconds)
    $milestoneStartedAt = Get-Date
    $milestoneResult = Invoke-TargetMilestoneAutoCommit `
      -TargetName $TargetName `
      -TargetConfig $TargetConfig `
      -FullCheckPath $GovernanceFullCheckPathResolved `
      -MilestoneTagValue $MilestoneTagValue `
      -MilestoneGateTimeoutSeconds $MilestoneGateTimeoutSeconds
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
    [string]$GovernanceFullCheckPathResolved,
    [Parameter(Mandatory = $true)]
    [string]$MilestoneTagValue,
    [Parameter(Mandatory = $true)]
    [int]$MilestoneGateTimeoutSeconds,
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
        -PythonCommand $PythonCommand
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
  }
  if ($flowResultEnvelope.flow_result.exit_code -eq 0) {
    if ($syncResult.status -eq "pass") {
      Write-BatchProgressLine `
        -Enabled $EmitProgress `
        -TargetName $TargetName `
        -Stage "milestone_commit" `
        -Status "start" `
        -Detail ("milestone_tag={0} timeout_s={1}" -f $MilestoneTagValue, $MilestoneGateTimeoutSeconds)
      $milestoneStartedAt = Get-Date
      $milestoneResult = Invoke-TargetMilestoneAutoCommit `
        -TargetName $TargetName `
        -TargetConfig $TargetConfig `
        -FullCheckPath $GovernanceFullCheckPathResolved `
        -MilestoneTagValue $MilestoneTagValue `
        -MilestoneGateTimeoutSeconds $MilestoneGateTimeoutSeconds
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
if (($applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) -and -not (Test-Path -LiteralPath $governanceFullCheckPathResolved)) {
  throw "Missing full-check.ps1 at $governanceFullCheckPathResolved"
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
$targetIndex = 0
foreach ($targetName in $selectedTargets) {
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
  $targetStartedAt = Get-Date
  Write-BatchProgressLine `
    -Enabled $progressEnabled `
    -TargetName $targetName `
    -Stage "target" `
    -Status "start" `
    -Detail ("index={0}/{1} mode={2}" -f $targetIndex, $targetCount, $runModeLabel)

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
      -GovernanceFullCheckPathResolved $governanceFullCheckPathResolved `
      -MilestoneTagValue $MilestoneTag `
      -MilestoneGateTimeoutSeconds $MilestoneGateTimeoutSeconds `
      -EmitProgress $progressEnabled
  }
  elseif ($applyFeatureBaselineAndMilestoneCommit) {
    $targetRun = Invoke-TargetFeatureBaselineAndMilestoneCommit `
      -TargetName $targetName `
      -TargetConfig $targetConfig `
      -RepoRoot $repoRoot `
      -GovernanceBaselinePathResolved $governanceBaselinePathResolved `
      -PythonCommand $pythonCommand `
      -GovernanceFullCheckPathResolved $governanceFullCheckPathResolved `
      -MilestoneTagValue $MilestoneTag `
      -MilestoneGateTimeoutSeconds $MilestoneGateTimeoutSeconds `
      -EmitProgress $progressEnabled
  }
  elseif ($applyFeatureBaselineOnly) {
    $targetRun = Invoke-TargetGovernanceBaselineOnly `
      -TargetName $targetName `
      -TargetConfig $targetConfig `
      -RepoRoot $repoRoot `
      -GovernanceBaselinePathResolved $governanceBaselinePathResolved `
      -PythonCommand $pythonCommand
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
$overallExitCode = if (($failureCount -gt 0) -or $hasPruneFailure) { 1 } else { 0 }

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
        [ordered]@{
          target                   = $_.target
          exit_code                = $_.exit_code
          flow_exit_code           = $_.flow_result.exit_code
          governance_sync_status   = $_.governance_sync_result.status
          governance_sync_reason   = $_.governance_sync_result.reason
          governance_sync_exit_code = $_.governance_sync_result.exit_code
          governance_sync_changed  = if ($_.governance_sync_result.payload) { @($_.governance_sync_result.payload.changed_fields) } else { @() }
          milestone_commit_status  = $_.milestone_commit_result.status
          milestone_commit_reason  = $_.milestone_commit_result.reason
          milestone_commit_exit_code = $_.milestone_commit_result.exit_code
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
      all_targets                     = [bool]$AllTargets
      flow_mode                       = $FlowMode
      apply_all_features              = [bool]$applyAllFeatures
      apply_feature_baseline_only     = [bool]$applyFeatureBaselineOnly
      apply_governance_baseline_only  = [bool]$ApplyGovernanceBaselineOnly
      apply_feature_baseline_and_milestone_commit = [bool]$applyFeatureBaselineAndMilestoneCommit
      governance_baseline_sync_active = ($applyAllFeatures -or $applyFeatureBaselineOnly -or $applyFeatureBaselineAndMilestoneCommit -or (($FlowMode -eq "onboard") -and -not $SkipGovernanceBaselineSync.IsPresent))
      milestone_tag                   = if ($applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) { $MilestoneTag } else { "" }
      milestone_gate_timeout_seconds  = if ($applyFeatureBaselineAndMilestoneCommit -or $applyAllFeatures) { $MilestoneGateTimeoutSeconds } else { 0 }
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
  Write-Host ("batch-summary: targets={0}, failures={1}" -f @($targetRuns).Count, $failureCount)
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
