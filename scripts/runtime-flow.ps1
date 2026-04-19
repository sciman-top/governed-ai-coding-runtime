param(
  [Parameter(Mandatory = $true)]
  [ValidateSet("onboard", "daily")]
  [string]$FlowMode,

  [Parameter(Mandatory = $true)]
  [string]$AttachmentRoot,

  [Parameter(Mandatory = $true)]
  [string]$AttachmentRuntimeStateRoot,

  [ValidateSet("quick", "full")]
  [string]$Mode = "quick",

  [ValidateSet("allow", "escalate", "deny")]
  [string]$PolicyStatus = "allow",

  [string]$TaskId = ("task-" + (Get-Date -Format "yyyyMMddHHmmss")),
  [string]$RunId = ("run-" + (Get-Date -Format "yyyyMMddHHmmss")),
  [string]$CommandId = ("cmd-" + (Get-Date -Format "yyyyMMddHHmmss")),
  [string]$RepoBindingId = "",
  [string]$AdapterId = "codex-cli",

  [string]$WriteTargetPath = "",
  [ValidateSet("low", "medium", "high")]
  [string]$WriteTier = "medium",
  [string]$WriteToolName = "apply_patch",
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
  [ValidateSet("native_attach", "process_bridge", "manual_handoff")]
  [string]$AdapterPreference = "process_bridge",
  [string]$GateProfile = "default",
  [switch]$Overwrite,

  [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

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
$resolvedAttachmentRoot = Resolve-AbsolutePath -PathValue $AttachmentRoot
$resolvedAttachmentRuntimeStateRoot = Resolve-AbsolutePath -PathValue $AttachmentRuntimeStateRoot

if ($FlowMode -eq "onboard") {
  if ([string]::IsNullOrWhiteSpace($BuildCommand) -or [string]::IsNullOrWhiteSpace($TestCommand) -or [string]::IsNullOrWhiteSpace($ContractCommand)) {
    throw "On onboard mode, -BuildCommand -TestCommand -ContractCommand are required."
  }

  $attachArgs = @(
    "scripts/attach-target-repo.py",
    "--target-repo", $resolvedAttachmentRoot,
    "--runtime-state-root", $resolvedAttachmentRuntimeStateRoot,
    "--primary-language", $PrimaryLanguage,
    "--build-command", $BuildCommand,
    "--test-command", $TestCommand,
    "--contract-command", $ContractCommand,
    "--adapter-preference", $AdapterPreference,
    "--gate-profile", $GateProfile
  )
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
}

$checkArgs = @(
  "-NoProfile",
  "-ExecutionPolicy",
  "Bypass",
  "-File",
  "scripts/runtime-check.ps1",
  "-AttachmentRoot", $resolvedAttachmentRoot,
  "-AttachmentRuntimeStateRoot", $resolvedAttachmentRuntimeStateRoot,
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
if (-not [string]::IsNullOrWhiteSpace($WriteTargetPath)) {
  $checkArgs += @("-WriteTargetPath", $WriteTargetPath, "-WriteTier", $WriteTier, "-WriteToolName", $WriteToolName)
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
  } | ConvertTo-Json -Depth 80
}
else {
  if ($FlowMode -eq "onboard") {
    Write-Host "[OK] onboard-attach (exit=0)"
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
}

if ($overallFail) {
  exit 1
}
exit 0
