param(
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

  [switch]$SkipVerifyAttachment,

  [string]$WriteTargetPath = "",
  [ValidateSet("low", "medium", "high")]
  [string]$WriteTier = "medium",
  [string]$WriteToolName = "write_file",
  [string]$WriteToolCommand = "",
  [string]$RollbackReference = "",
  [string]$WriteContent = "governed runtime write probe",
  [switch]$ExecuteWriteFlow,

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

function Invoke-CommandCapture {
  param(
    [Parameter(Mandatory = $true)]
    [string]$Label,
    [Parameter(Mandatory = $true)]
    [scriptblock]$Command
  )

  $output = & $Command 2>&1
  $exitCode = $LASTEXITCODE
  if ($null -eq $exitCode) {
    $exitCode = 0
  }

  return @{
    label = $Label
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
    return ($Raw | ConvertFrom-Json -Depth 40)
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

function Build-WriteToolCommand {
  param(
    [Parameter(Mandatory = $true)]
    [string]$ToolName,
    [Parameter(Mandatory = $true)]
    [string]$TargetPath,
    [Parameter(Mandatory = $true)]
    [string]$Content,
    [string]$ExplicitCommand = ""
  )

  if (-not [string]::IsNullOrWhiteSpace($ExplicitCommand)) {
    return $ExplicitCommand
  }

  $normalizedTool = $ToolName.Trim().ToLowerInvariant()
  if ($normalizedTool -eq "shell") {
    if ([string]::IsNullOrWhiteSpace($TargetPath)) {
      throw "WriteTargetPath is required when WriteToolName is shell."
    }
    $escapedTarget = $TargetPath.Replace("'", "''")
    $escapedContent = $Content.Replace("'", "''")
    return "Set-Content -LiteralPath '$escapedTarget' -Value '$escapedContent' -Encoding utf8"
  }

  if ($normalizedTool -eq "git" -or $normalizedTool -eq "package") {
    throw "WriteToolCommand is required when WriteToolName is git or package."
  }

  return ""
}

$python = Get-PythonCommand
$steps = New-Object System.Collections.Generic.List[object]
$hasFailure = $false
$resolvedAttachmentRoot = Resolve-AbsolutePath -PathValue $AttachmentRoot
$resolvedAttachmentRuntimeStateRoot = Resolve-AbsolutePath -PathValue $AttachmentRuntimeStateRoot

$statusStep = Invoke-CommandCapture -Label "status" -Command {
  & $python "scripts/run-governed-task.py" "status" "--json" "--attachment-root" $resolvedAttachmentRoot "--attachment-runtime-state-root" $resolvedAttachmentRuntimeStateRoot
}
$steps.Add($statusStep) | Out-Null
if ($statusStep.exit_code -ne 0) {
  $hasFailure = $true
}

$statusPayload = Try-ParseJson -Raw $statusStep.output
if (-not $statusPayload) {
  $hasFailure = $true
}

$resolvedBindingId = $RepoBindingId
if ([string]::IsNullOrWhiteSpace($resolvedBindingId)) {
  if ($statusPayload -and $statusPayload.attachments -and $statusPayload.attachments.Count -gt 0) {
    $resolvedBindingId = [string]$statusPayload.attachments[0].binding_id
  }
}
if ([string]::IsNullOrWhiteSpace($resolvedBindingId)) {
  throw "Unable to resolve repo binding id. Pass -RepoBindingId explicitly."
}

$attachmentHealth = "unknown"
if ($statusPayload -and $statusPayload.attachments -and $statusPayload.attachments.Count -gt 0) {
  $attachmentHealth = [string]$statusPayload.attachments[0].binding_state
  if ($attachmentHealth -ne "healthy") {
    $hasFailure = $true
  }
}

$doctorStep = Invoke-CommandCapture -Label "doctor" -Command {
  & pwsh "-NoProfile" "-ExecutionPolicy" "Bypass" "-File" "scripts/doctor-runtime.ps1" "-AttachmentRoot" $resolvedAttachmentRoot "-RuntimeStateRoot" $resolvedAttachmentRuntimeStateRoot
}
$steps.Add($doctorStep) | Out-Null
if ($doctorStep.exit_code -ne 0) {
  $hasFailure = $true
}

$requestGateStep = Invoke-CommandCapture -Label "session-bridge-request-gate" -Command {
  & $python "scripts/session-bridge.py" "request-gate" "--command-id" $CommandId "--task-id" $TaskId "--repo-binding-id" $resolvedBindingId "--adapter-id" $AdapterId "--mode" $Mode "--policy-status" $PolicyStatus "--attachment-root" $resolvedAttachmentRoot "--attachment-runtime-state-root" $resolvedAttachmentRuntimeStateRoot
}
$steps.Add($requestGateStep) | Out-Null
if ($requestGateStep.exit_code -ne 0) {
  $hasFailure = $true
}
$requestGatePayload = Try-ParseJson -Raw $requestGateStep.output
if (-not $requestGatePayload) {
  $hasFailure = $true
}

$verifyPayload = $null
if (-not $SkipVerifyAttachment) {
  $verifyStep = Invoke-CommandCapture -Label "verify-attachment" -Command {
    & $python "scripts/run-governed-task.py" "verify-attachment" "--attachment-root" $resolvedAttachmentRoot "--attachment-runtime-state-root" $resolvedAttachmentRuntimeStateRoot "--mode" $Mode "--task-id" $TaskId "--run-id" $RunId "--json"
  }
  $steps.Add($verifyStep) | Out-Null
  if ($verifyStep.exit_code -ne 0) {
    $hasFailure = $true
  }
  $verifyPayload = Try-ParseJson -Raw $verifyStep.output
  if (-not $verifyPayload) {
    $hasFailure = $true
  }
  elseif ($verifyPayload.results) {
    foreach ($gate in $verifyPayload.results.PSObject.Properties.Name) {
      if ([string]$verifyPayload.results.$gate -ne "pass") {
        $hasFailure = $true
      }
    }
  }
}

$writeGovernancePayload = $null
$writeApprovalPayload = $null
$writeExecutePayload = $null
if (-not [string]::IsNullOrWhiteSpace($WriteTargetPath)) {
  $resolvedWriteToolCommand = Build-WriteToolCommand -ToolName $WriteToolName -TargetPath $WriteTargetPath -Content $WriteContent -ExplicitCommand $WriteToolCommand
  if ([string]::IsNullOrWhiteSpace($RollbackReference)) {
    $RollbackReference = "git diff -- $WriteTargetPath"
  }
  $writeStep = Invoke-CommandCapture -Label "govern-attachment-write" -Command {
    $governArgs = @(
      "scripts/run-governed-task.py",
      "govern-attachment-write",
      "--attachment-root", $resolvedAttachmentRoot,
      "--attachment-runtime-state-root", $resolvedAttachmentRuntimeStateRoot,
      "--task-id", $TaskId,
      "--adapter-id", $AdapterId,
      "--tool-name", $WriteToolName,
      "--target-path", $WriteTargetPath,
      "--tier", $WriteTier,
      "--rollback-reference", $RollbackReference,
      "--json"
    )
    if (-not [string]::IsNullOrWhiteSpace($resolvedWriteToolCommand)) {
      $governArgs += @("--tool-command", $resolvedWriteToolCommand)
    }
    & $python @governArgs
  }
  $steps.Add($writeStep) | Out-Null
  if ($writeStep.exit_code -ne 0) {
    $hasFailure = $true
  }
  $writeGovernancePayload = Try-ParseJson -Raw $writeStep.output
  if (-not $writeGovernancePayload) {
    $hasFailure = $true
  }

  if ($ExecuteWriteFlow -and $writeGovernancePayload) {
    $resolvedApprovalId = ""
    if ($writeGovernancePayload.approval_id) {
      $resolvedApprovalId = [string]$writeGovernancePayload.approval_id
      $approveStep = Invoke-CommandCapture -Label "decide-attachment-write" -Command {
        & $python "scripts/run-governed-task.py" "decide-attachment-write" "--attachment-runtime-state-root" $resolvedAttachmentRuntimeStateRoot "--approval-id" $resolvedApprovalId "--decision" "approve" "--decided-by" "runtime-check" "--adapter-id" $AdapterId "--json"
      }
      $steps.Add($approveStep) | Out-Null
      if ($approveStep.exit_code -ne 0) {
        $hasFailure = $true
      }
      $writeApprovalPayload = Try-ParseJson -Raw $approveStep.output
      if (-not $writeApprovalPayload) {
        $hasFailure = $true
      }
    }

    $executeArgs = @(
      "scripts/run-governed-task.py",
      "execute-attachment-write",
      "--attachment-root", $resolvedAttachmentRoot,
      "--attachment-runtime-state-root", $resolvedAttachmentRuntimeStateRoot,
      "--task-id", $TaskId,
      "--adapter-id", $AdapterId,
      "--tool-name", $WriteToolName,
      "--target-path", $WriteTargetPath,
      "--tier", $WriteTier,
      "--rollback-reference", $RollbackReference,
      "--content", $WriteContent,
      "--json"
    )
    if (-not [string]::IsNullOrWhiteSpace($resolvedWriteToolCommand)) {
      $executeArgs += @("--tool-command", $resolvedWriteToolCommand)
    }
    if (-not [string]::IsNullOrWhiteSpace($resolvedApprovalId)) {
      $executeArgs += @("--approval-id", $resolvedApprovalId)
    }
    $executeStep = Invoke-CommandCapture -Label "execute-attachment-write" -Command {
      & $python @executeArgs
    }
    $steps.Add($executeStep) | Out-Null
    if ($executeStep.exit_code -ne 0) {
      $hasFailure = $true
    }
    $writeExecutePayload = Try-ParseJson -Raw $executeStep.output
    if (-not $writeExecutePayload) {
      $hasFailure = $true
    }
    elseif ($writeExecutePayload.execution_status -ne "executed") {
      $hasFailure = $true
    }
  }
}

$summary = @{
  attachment_root = $resolvedAttachmentRoot
  attachment_runtime_state_root = $resolvedAttachmentRuntimeStateRoot
  mode = $Mode
  task_id = $TaskId
  run_id = $RunId
  command_id = $CommandId
  repo_binding_id = $resolvedBindingId
  attachment_health = $attachmentHealth
  overall_status = $(if ($hasFailure) { "fail" } else { "pass" })
}

$result = @{
  summary = $summary
  status = $statusPayload
  request_gate = $requestGatePayload
  verify_attachment = $verifyPayload
  write_governance = $writeGovernancePayload
  write_approval = $writeApprovalPayload
  write_execute = $writeExecutePayload
  steps = $steps
}

if ($Json) {
  $result | ConvertTo-Json -Depth 40
}
else {
  Write-Host ("Overall: " + $summary.overall_status)
  Write-Host ("Attachment: " + $summary.attachment_health)
  foreach ($step in $steps) {
    $flag = if ($step.exit_code -eq 0) { "OK" } else { "FAIL" }
    Write-Host ("[{0}] {1} (exit={2})" -f $flag, $step.label, $step.exit_code)
  }
  if ($verifyPayload -and $verifyPayload.results) {
    $gatePairs = @()
    foreach ($name in $verifyPayload.results.PSObject.Properties.Name) {
      $gatePairs += ("{0}={1}" -f $name, [string]$verifyPayload.results.$name)
    }
    Write-Host ("Verification: " + ($gatePairs -join ", "))
    if ($verifyPayload.evidence_link) {
      Write-Host ("Evidence: " + [string]$verifyPayload.evidence_link)
    }
  }
  if ($writeGovernancePayload -and $writeGovernancePayload.policy_decision) {
    if ($writeGovernancePayload.policy_decision.status) {
      Write-Host ("Write Governance: " + [string]$writeGovernancePayload.policy_decision.status)
    }
    elseif ($writeGovernancePayload.policy_status) {
      Write-Host ("Write Governance: " + [string]$writeGovernancePayload.policy_status)
    }
    if ($writeGovernancePayload.reason) {
      Write-Host ("Write Reason: " + [string]$writeGovernancePayload.reason)
    }
  }
  if ($writeExecutePayload) {
    Write-Host ("Write Execute: " + [string]$writeExecutePayload.execution_status)
    if ($writeExecutePayload.handoff_ref) {
      Write-Host ("Handoff Ref: " + [string]$writeExecutePayload.handoff_ref)
    }
    if ($writeExecutePayload.replay_ref) {
      Write-Host ("Replay Ref: " + [string]$writeExecutePayload.replay_ref)
    }
  }
}

if ($hasFailure) {
  exit 1
}
exit 0
