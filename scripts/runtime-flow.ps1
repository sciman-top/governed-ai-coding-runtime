param(
  [Parameter(Mandatory = $true)]
  [ValidateSet("onboard", "daily")]
  [string]$FlowMode,

  [Parameter(Mandatory = $true)]
  [string]$AttachmentRoot,

  [Parameter(Mandatory = $true)]
  [string]$AttachmentRuntimeStateRoot,

  [string]$EntrypointId = "runtime-flow",

  [ValidateSet("quick", "full", "l1", "l2", "l3")]
  [string]$Mode = "quick",

  [ValidateSet("allow", "escalate", "deny")]
  [string]$PolicyStatus = "allow",

  [string]$TaskId = ("task-" + (Get-Date -Format "yyyyMMddHHmmss")),
  [string]$RunId = ("run-" + (Get-Date -Format "yyyyMMddHHmmss")),
  [string]$CommandId = ("cmd-" + (Get-Date -Format "yyyyMMddHHmmss")),
  [string]$RepoBindingId = "",
  [string]$AdapterId = "codex-cli",
  [string]$SessionId = "",
  [string]$ResumeId = "",
  [string]$ContinuationId = "",

  [string]$WriteTargetPath = "",
  [ValidateSet("low", "medium", "high")]
  [string]$WriteTier = "medium",
  [string]$WriteToolName = "write_file",
  [string]$WriteToolCommand = "",
  [string]$RollbackReference = "",
  [string]$WriteContent = "governed runtime write probe",
  [switch]$ExecuteWriteFlow,

  [switch]$SkipVerifyAttachment,

  [string]$RepoId = "",
  [string]$DisplayName = "",
  [string]$PrimaryLanguage = "python",
  [string]$BuildCommand = "",
  [string]$TestCommand = "",
  [string]$ContractCommand = "",
  [switch]$RequireExplicitGateCommands,
  [ValidateSet("native_attach", "process_bridge", "manual_handoff")]
  [string]$AdapterPreference = "native_attach",
  [string]$GateProfile = "default",
  [switch]$Overwrite,
  [string]$GovernanceBaselinePath = "",

  [switch]$Json
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
}

Initialize-WindowsProcessEnvironment

function Get-PythonCommand {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
  }
  if (-not $python) {
    throw "Required command not found: python or python3"
  }
  return $python.Source
}

function Invoke-Captured {
  param(
    [Parameter(Mandatory = $true)]
    [scriptblock]$Command
  )

  $output = & $Command 2>&1
  $exitCode = $LASTEXITCODE
  if ($null -eq $exitCode) {
    $exitCode = 0
  }
  return @{
    exit_code = [int]$exitCode
    output = ($output -join "`n").Trim()
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

function Resolve-AbsolutePath {
  param([Parameter(Mandatory = $true)][string]$PathValue)
  if ([string]::IsNullOrWhiteSpace($PathValue)) {
    throw "PathValue is required"
  }
  if ([System.IO.Path]::IsPathRooted($PathValue)) {
    return [System.IO.Path]::GetFullPath($PathValue)
  }
  return [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $PathValue))
}

$python = Get-PythonCommand
$attachPayload = $null
$attachResult = $null
$governanceSyncPayload = $null
$governanceSyncExitCode = 0
$resolvedAttachmentRoot = Resolve-AbsolutePath -PathValue $AttachmentRoot
$resolvedAttachmentRuntimeStateRoot = Resolve-AbsolutePath -PathValue $AttachmentRuntimeStateRoot

if ($FlowMode -eq "onboard") {
  if ($RequireExplicitGateCommands -and (
      [string]::IsNullOrWhiteSpace($BuildCommand) -or
      [string]::IsNullOrWhiteSpace($TestCommand) -or
      [string]::IsNullOrWhiteSpace($ContractCommand)
    )) {
    throw "On onboard mode, -BuildCommand -TestCommand -ContractCommand are required."
  }

  $attachArgs = @(
    "scripts/attach-target-repo.py",
    "--target-repo", $resolvedAttachmentRoot,
    "--runtime-state-root", $resolvedAttachmentRuntimeStateRoot,
    "--primary-language", $PrimaryLanguage,
    "--adapter-preference", $AdapterPreference,
    "--gate-profile", $GateProfile
  )
  if (-not [string]::IsNullOrWhiteSpace($BuildCommand)) {
    $attachArgs += @("--build-command", $BuildCommand)
  }
  if (-not [string]::IsNullOrWhiteSpace($TestCommand)) {
    $attachArgs += @("--test-command", $TestCommand)
  }
  if (-not [string]::IsNullOrWhiteSpace($ContractCommand)) {
    $attachArgs += @("--contract-command", $ContractCommand)
  }
  if ($RequireExplicitGateCommands -eq $false) {
    $attachArgs += "--infer-gate-defaults"
  }
  if (-not [string]::IsNullOrWhiteSpace($RepoId)) {
    $attachArgs += @("--repo-id", $RepoId)
  }
  if (-not [string]::IsNullOrWhiteSpace($DisplayName)) {
    $attachArgs += @("--display-name", $DisplayName)
  }
  if ($Overwrite) {
    $attachArgs += "--overwrite"
  }

  $attachResult = Invoke-Captured -Command { & $python @attachArgs }
  if ($attachResult.exit_code -ne 0) {
    if ($Json) {
      @{
        flow_mode = $FlowMode
        overall_status = "fail"
        onboard_attach = @{
          exit_code = $attachResult.exit_code
          payload = $null
        }
      } | ConvertTo-Json -Depth 80
    }
    else {
      Write-Host "[FAIL] onboard-attach"
      if ($attachResult.output) {
        Write-Host $attachResult.output
      }
    }
    exit 1
  }

  $attachPayload = Try-ParseJson -Raw $attachResult.output

  if (-not [string]::IsNullOrWhiteSpace($GovernanceBaselinePath)) {
    $resolvedGovernanceBaselinePath = Resolve-AbsolutePath -PathValue $GovernanceBaselinePath
    if (-not (Test-Path -LiteralPath $resolvedGovernanceBaselinePath)) {
      if ($Json) {
        @{
          flow_mode = $FlowMode
          overall_status = "fail"
          onboard_attach = @{
            exit_code = $attachResult.exit_code
            payload = $attachPayload
          }
          governance_baseline_sync = @{
            exit_code = 1
            payload = $null
            reason = "baseline_file_not_found"
          }
        } | ConvertTo-Json -Depth 80
      }
      else {
        Write-Host "[FAIL] governance-baseline-sync"
        Write-Host ("Missing governance baseline file: " + $resolvedGovernanceBaselinePath)
      }
      exit 1
    }

    $governanceSyncArgs = @(
      "scripts/apply-target-repo-governance.py",
      "--target-repo", $resolvedAttachmentRoot,
      "--baseline-path", $resolvedGovernanceBaselinePath
    )
    $governanceSyncResult = Invoke-Captured -Command { & $python @governanceSyncArgs }
    $governanceSyncExitCode = $governanceSyncResult.exit_code
    $governanceSyncPayload = Try-ParseJson -Raw $governanceSyncResult.output

    if ($governanceSyncResult.exit_code -ne 0) {
      if ($Json) {
        @{
          flow_mode = $FlowMode
          overall_status = "fail"
          onboard_attach = @{
            exit_code = $attachResult.exit_code
            payload = $attachPayload
          }
          governance_baseline_sync = @{
            exit_code = $governanceSyncResult.exit_code
            payload = $governanceSyncPayload
            reason = "sync_failed"
          }
        } | ConvertTo-Json -Depth 80
      }
      else {
        Write-Host "[FAIL] governance-baseline-sync"
        if ($governanceSyncResult.output) {
          Write-Host $governanceSyncResult.output
        }
      }
      exit 1
    }
  }
}

$checkArgs = @(
  "-NoProfile",
  "-ExecutionPolicy",
  "Bypass",
  "-File",
  "scripts/runtime-check.ps1",
  "-AttachmentRoot", $resolvedAttachmentRoot,
  "-AttachmentRuntimeStateRoot", $resolvedAttachmentRuntimeStateRoot,
  "-EntrypointId", $EntrypointId,
  "-Mode", $Mode,
  "-PolicyStatus", $PolicyStatus,
  "-TaskId", $TaskId,
  "-RunId", $RunId,
  "-CommandId", $CommandId,
  "-AdapterId", $AdapterId
)
if (-not [string]::IsNullOrWhiteSpace($RepoBindingId)) {
  $checkArgs += @("-RepoBindingId", $RepoBindingId)
}
if (-not [string]::IsNullOrWhiteSpace($SessionId)) {
  $checkArgs += @("-SessionId", $SessionId)
}
if (-not [string]::IsNullOrWhiteSpace($ResumeId)) {
  $checkArgs += @("-ResumeId", $ResumeId)
}
if (-not [string]::IsNullOrWhiteSpace($ContinuationId)) {
  $checkArgs += @("-ContinuationId", $ContinuationId)
}
if (-not [string]::IsNullOrWhiteSpace($WriteTargetPath)) {
  $checkArgs += @("-WriteTargetPath", $WriteTargetPath, "-WriteTier", $WriteTier, "-WriteToolName", $WriteToolName)
  if (-not [string]::IsNullOrWhiteSpace($WriteToolCommand)) {
    $checkArgs += @("-WriteToolCommand", $WriteToolCommand)
  }
  $checkArgs += @("-WriteContent", $WriteContent)
}
if (-not [string]::IsNullOrWhiteSpace($RollbackReference)) {
  $checkArgs += @("-RollbackReference", $RollbackReference)
}
if ($ExecuteWriteFlow) {
  $checkArgs += "-ExecuteWriteFlow"
}
if ($SkipVerifyAttachment) {
  $checkArgs += "-SkipVerifyAttachment"
}
$checkArgs += "-Json"

$checkResult = Invoke-Captured -Command { & pwsh @checkArgs }
$checkPayload = Try-ParseJson -Raw $checkResult.output
$overallFail = ($checkResult.exit_code -ne 0)
$nextActions = New-Object System.Collections.Generic.List[string]

if ($checkPayload -and $checkPayload.status -and $checkPayload.status.attachments) {
  foreach ($attachment in $checkPayload.status.attachments) {
    $bindingState = ""
    $remediation = ""
    if ($attachment.PSObject.Properties.Name -contains "binding_state") {
      $bindingState = [string]$attachment.binding_state
    }
    if ($attachment.PSObject.Properties.Name -contains "remediation") {
      $remediation = [string]$attachment.remediation
    }
    if ($bindingState -and $bindingState -ne "healthy" -and -not [string]::IsNullOrWhiteSpace($remediation)) {
      $nextActions.Add("attachment remediation ($bindingState): $remediation") | Out-Null
    }
  }
}

if ($Json) {
  @{
    flow_mode = $FlowMode
    overall_status = $(if ($overallFail) { "fail" } else { "pass" })
    onboard_attach = if ($FlowMode -eq "onboard") {
      @{
        exit_code = $attachResult.exit_code
        payload = $attachPayload
      }
    } else { $null }
    runtime_check = @{
      exit_code = $checkResult.exit_code
      payload = $checkPayload
    }
    governance_baseline_sync = @{
      exit_code = $governanceSyncExitCode
      payload = $governanceSyncPayload
    }
    next_actions = @($nextActions)
  } | ConvertTo-Json -Depth 80
}
else {
  if ($FlowMode -eq "onboard") {
    Write-Host "[OK] onboard-attach (exit=0)"
    if ($attachPayload -and $attachPayload.gate_command_source) {
      Write-Host ("Onboard gate command source: " + [string]$attachPayload.gate_command_source)
    }
    if (-not [string]::IsNullOrWhiteSpace($GovernanceBaselinePath)) {
      Write-Host ("Governance baseline sync: exit=" + $governanceSyncExitCode)
    }
  }
  if ($checkPayload -and $checkPayload.summary) {
    Write-Host ("Overall: " + [string]$checkPayload.summary.overall_status)
    Write-Host ("Attachment: " + [string]$checkPayload.summary.attachment_health)
  }
  else {
    Write-Host ("runtime-check exit=" + $checkResult.exit_code)
  }
  if ($checkResult.output) {
    Write-Host $checkResult.output
  }
  if ($nextActions.Count -gt 0) {
    foreach ($action in $nextActions) {
      Write-Host ("Next Action: " + $action)
    }
  }
}

if ($overallFail) {
  exit 1
}
exit 0
