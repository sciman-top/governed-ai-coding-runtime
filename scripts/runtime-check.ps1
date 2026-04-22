param(
  [Parameter(Mandatory = $true)]
  [string]$AttachmentRoot,

  [Parameter(Mandatory = $true)]
  [string]$AttachmentRuntimeStateRoot,

  [string]$EntrypointId = "runtime-check",

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

  [switch]$SkipVerifyAttachment,

  [string]$WriteTargetPath = "",
  [ValidateSet("low", "medium", "high")]
  [string]$WriteTier = "medium",
  [string]$WriteToolName = "write_file",
  [string]$WriteToolCommand = "",
  [string]$RollbackReference = "",
  [string]$WriteContent = "governed runtime write probe",
  [switch]$ExecuteWriteFlow,

  [switch]$SkipSourceStringContractGuard,

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

function Get-OptionalField {
  param(
    [object]$Payload,
    [Parameter(Mandatory = $true)]
    [string]$FieldName
  )
  if ($null -eq $Payload) {
    return ""
  }
  if ($Payload.PSObject.Properties.Name -contains $FieldName -and $null -ne $Payload.$FieldName) {
    return [string]$Payload.$FieldName
  }
  return ""
}

function Get-IdentityField {
  param(
    [object]$Payload,
    [Parameter(Mandatory = $true)]
    [string]$FieldName
  )
  if ($null -eq $Payload) {
    return ""
  }
  if (-not ($Payload.PSObject.Properties.Name -contains "session_identity")) {
    return ""
  }
  $identity = $Payload.session_identity
  if ($null -eq $identity) {
    return ""
  }
  if ($identity.PSObject.Properties.Name -contains $FieldName -and $null -ne $identity.$FieldName) {
    return [string]$identity.$FieldName
  }
  return ""
}

function Add-Ref {
  param(
    [System.Collections.Generic.List[string]]$Refs,
    [string]$Value
  )
  if ($null -eq $Refs) {
    return
  }
  if ([string]::IsNullOrWhiteSpace($Value)) {
    return
  }
  if (-not $Refs.Contains($Value)) {
    $Refs.Add($Value) | Out-Null
  }
}

$python = Get-PythonCommand
$steps = New-Object System.Collections.Generic.List[object]
$hasFailure = $false
$resolvedAttachmentRoot = Resolve-AbsolutePath -PathValue $AttachmentRoot
$resolvedAttachmentRuntimeStateRoot = Resolve-AbsolutePath -PathValue $AttachmentRuntimeStateRoot
$resolvedSessionId = if (-not [string]::IsNullOrWhiteSpace($SessionId)) { $SessionId } else { "session-$TaskId" }
$resolvedResumeId = if (-not [string]::IsNullOrWhiteSpace($ResumeId)) { $ResumeId } else { "resume-$TaskId" }
$resolvedContinuationId = if (-not [string]::IsNullOrWhiteSpace($ContinuationId)) { $ContinuationId } else { "${TaskId}:$RunId" }
$nextActions = New-Object System.Collections.Generic.List[string]

$dependencyBaselineStep = Invoke-CommandCapture -Label "dependency-baseline-target-repo" -Command {
  & $python "scripts/verify-dependency-baseline.py" "--target-repo-root" $resolvedAttachmentRoot "--require-target-repo-baseline"
}
$steps.Add($dependencyBaselineStep) | Out-Null
if ($dependencyBaselineStep.exit_code -ne 0) {
  $hasFailure = $true
  $nextActions.Add("create or refresh target repo baseline metadata via attach flow, then re-run runtime-check") | Out-Null
}
$dependencyBaselinePayload = Try-ParseJson -Raw $dependencyBaselineStep.output
if ($dependencyBaselineStep.exit_code -eq 0 -and -not $dependencyBaselinePayload) {
  $hasFailure = $true
}

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
  if ($statusPayload -and $statusPayload.attachments -and @($statusPayload.attachments).Count -gt 0) {
    $resolvedBindingId = [string]$statusPayload.attachments[0].binding_id
  }
}
if ([string]::IsNullOrWhiteSpace($resolvedBindingId)) {
  throw "Unable to resolve repo binding id. Pass -RepoBindingId explicitly."
}

$attachmentHealth = "unknown"
if ($statusPayload -and $statusPayload.attachments -and @($statusPayload.attachments).Count -gt 0) {
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
  & $python "scripts/session-bridge.py" "request-gate" "--command-id" $CommandId "--task-id" $TaskId "--repo-binding-id" $resolvedBindingId "--adapter-id" $AdapterId "--entrypoint-id" $EntrypointId "--mode" $Mode "--policy-status" $PolicyStatus "--attachment-root" $resolvedAttachmentRoot "--attachment-runtime-state-root" $resolvedAttachmentRuntimeStateRoot "--session-id" $resolvedSessionId "--resume-id" $resolvedResumeId "--continuation-id" $resolvedContinuationId
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
    & $python "scripts/run-governed-task.py" "verify-attachment" "--entrypoint-id" $EntrypointId "--attachment-root" $resolvedAttachmentRoot "--attachment-runtime-state-root" $resolvedAttachmentRuntimeStateRoot "--mode" $Mode "--task-id" $TaskId "--run-id" $RunId "--json"
  }
  $steps.Add($verifyStep) | Out-Null
  if ($verifyStep.exit_code -ne 0) {
    $hasFailure = $true
  }
  $verifyPayload = Try-ParseJson -Raw $verifyStep.output
  if (-not $verifyPayload) {
    $hasFailure = $true
  }
  else {
    $verifyOutcome = ""
    if ($verifyPayload.PSObject.Properties.Name -contains "outcome") {
      $verifyOutcome = [string]$verifyPayload.outcome
    }
    if (-not [string]::IsNullOrWhiteSpace($verifyOutcome)) {
      if ($verifyOutcome -ne "pass") {
        $hasFailure = $true
      }
    }
    elseif ($verifyPayload.results) {
      $blockingGateIds = @()
      if ($verifyPayload.PSObject.Properties.Name -contains "blocking_gate_ids" -and $verifyPayload.blocking_gate_ids) {
        $blockingGateIds = @($verifyPayload.blocking_gate_ids | ForEach-Object { [string]$_ })
      }
      if (@($blockingGateIds).Count -eq 0) {
        $blockingGateIds = @($verifyPayload.results.PSObject.Properties.Name)
      }
      foreach ($gate in $blockingGateIds) {
        if (-not ($verifyPayload.results.PSObject.Properties.Name -contains $gate)) {
          $hasFailure = $true
          continue
        }
        if ([string]$verifyPayload.results.$gate -ne "pass") {
          $hasFailure = $true
        }
      }
    }
  }
}

$writeGovernancePayload = $null
$writeApprovalPayload = $null
$writeExecutePayload = $null
$writeStatusPayload = $null
$inspectEvidencePayload = $null
$inspectHandoffPayload = $null
$writePreflight = $null
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
      "--entrypoint-id", $EntrypointId,
      "--tool-name", $WriteToolName,
      "--target-path", $WriteTargetPath,
      "--tier", $WriteTier,
      "--rollback-reference", $RollbackReference,
      "--session-id", $resolvedSessionId,
      "--resume-id", $resolvedResumeId,
      "--continuation-id", $resolvedContinuationId,
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
  else {
    $preflightBlocked = $false
    if ($writeGovernancePayload.PSObject.Properties.Name -contains "preflight_blocked") {
      $preflightBlocked = ($writeGovernancePayload.preflight_blocked -eq $true)
    }
    if ($preflightBlocked) {
      $writePreflight = @{
        blocked = $true
        reason = $(if ($writeGovernancePayload.reason) { [string]$writeGovernancePayload.reason } else { "" })
        remediation_hint = $(if ($writeGovernancePayload.remediation_hint) { [string]$writeGovernancePayload.remediation_hint } else { "" })
        suggested_target_path = $(if ($writeGovernancePayload.suggested_target_path) { [string]$writeGovernancePayload.suggested_target_path } else { "" })
        retry_command = $(if ($writeGovernancePayload.retry_command) { [string]$writeGovernancePayload.retry_command } else { "" })
      }
      if (-not [string]::IsNullOrWhiteSpace([string]$writePreflight.retry_command)) {
        $nextActions.Add("retry within allowed scope: $([string]$writePreflight.retry_command)") | Out-Null
      }
    }
  }

  $skipExecuteOnPreflight = ($null -ne $writePreflight -and $writePreflight.blocked -eq $true)
  if ($ExecuteWriteFlow -and $writeGovernancePayload -and -not $skipExecuteOnPreflight) {
    $resolvedApprovalId = ""
    if ($writeGovernancePayload.approval_id) {
      $resolvedApprovalId = [string]$writeGovernancePayload.approval_id
      $approveStep = Invoke-CommandCapture -Label "decide-attachment-write" -Command {
        & $python "scripts/run-governed-task.py" "decide-attachment-write" "--attachment-runtime-state-root" $resolvedAttachmentRuntimeStateRoot "--approval-id" $resolvedApprovalId "--decision" "approve" "--decided-by" "runtime-check" "--task-id" $TaskId "--adapter-id" $AdapterId "--session-id" $resolvedSessionId "--resume-id" $resolvedResumeId "--continuation-id" $resolvedContinuationId "--json"
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
      "--entrypoint-id", $EntrypointId,
      "--tool-name", $WriteToolName,
      "--target-path", $WriteTargetPath,
      "--tier", $WriteTier,
      "--rollback-reference", $RollbackReference,
      "--content", $WriteContent,
      "--session-id", $resolvedSessionId,
      "--resume-id", $resolvedResumeId,
      "--continuation-id", $resolvedContinuationId,
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

    $resolvedWriteApprovalId = ""
    if ($writeExecutePayload -and $writeExecutePayload.approval_id) {
      $resolvedWriteApprovalId = [string]$writeExecutePayload.approval_id
    }
    elseif (-not [string]::IsNullOrWhiteSpace($resolvedApprovalId)) {
      $resolvedWriteApprovalId = $resolvedApprovalId
    }

    $writeStatusStep = Invoke-CommandCapture -Label "session-bridge-write-status" -Command {
      $statusArgs = @(
        "scripts/session-bridge.py",
        "write-status",
        "--command-id", "$CommandId-write-status",
        "--task-id", $TaskId,
        "--repo-binding-id", $resolvedBindingId,
        "--adapter-id", $AdapterId,
        "--entrypoint-id", $EntrypointId,
        "--risk-tier", $WriteTier,
        "--attachment-runtime-state-root", $resolvedAttachmentRuntimeStateRoot,
        "--target-path", $WriteTargetPath,
        "--session-id", $resolvedSessionId,
        "--resume-id", $resolvedResumeId,
        "--continuation-id", $resolvedContinuationId
      )
      if (-not [string]::IsNullOrWhiteSpace($resolvedWriteApprovalId)) {
        $statusArgs += @("--approval-id", $resolvedWriteApprovalId)
      }
      & $python @statusArgs
    }
    $steps.Add($writeStatusStep) | Out-Null
    if ($writeStatusStep.exit_code -ne 0) {
      $hasFailure = $true
    }
    $writeStatusPayload = Try-ParseJson -Raw $writeStatusStep.output
    if (-not $writeStatusPayload) {
      $hasFailure = $true
    }
    elseif ($writeStatusPayload.payload) {
      $writeStatusPayload = $writeStatusPayload.payload
    }

    $inspectEvidenceStep = Invoke-CommandCapture -Label "session-bridge-inspect-evidence" -Command {
      & $python "scripts/session-bridge.py" "inspect-evidence" "--command-id" "$CommandId-inspect-evidence" "--task-id" $TaskId "--repo-binding-id" $resolvedBindingId "--adapter-id" $AdapterId "--risk-tier" "low" "--attachment-root" $resolvedAttachmentRoot "--attachment-runtime-state-root" $resolvedAttachmentRuntimeStateRoot "--session-id" $resolvedSessionId "--resume-id" $resolvedResumeId "--continuation-id" $resolvedContinuationId
    }
    $steps.Add($inspectEvidenceStep) | Out-Null
    if ($inspectEvidenceStep.exit_code -ne 0) {
      $hasFailure = $true
    }
    $inspectEvidencePayload = Try-ParseJson -Raw $inspectEvidenceStep.output
    if (-not $inspectEvidencePayload) {
      $hasFailure = $true
    }
    elseif ($inspectEvidencePayload.payload) {
      $inspectEvidencePayload = $inspectEvidencePayload.payload
    }

    $inspectHandoffStep = Invoke-CommandCapture -Label "session-bridge-inspect-handoff" -Command {
      $handoffArgs = @(
        "scripts/session-bridge.py",
        "inspect-handoff",
        "--command-id", "$CommandId-inspect-handoff",
        "--task-id", $TaskId,
        "--repo-binding-id", $resolvedBindingId,
        "--adapter-id", $AdapterId,
        "--risk-tier", "low",
        "--attachment-root", $resolvedAttachmentRoot,
        "--attachment-runtime-state-root", $resolvedAttachmentRuntimeStateRoot,
        "--session-id", $resolvedSessionId,
        "--resume-id", $resolvedResumeId,
        "--continuation-id", $resolvedContinuationId
      )
      if ($writeExecutePayload -and $writeExecutePayload.handoff_ref) {
        $handoffArgs += @("--handoff-ref", [string]$writeExecutePayload.handoff_ref)
      }
      & $python @handoffArgs
    }
    $steps.Add($inspectHandoffStep) | Out-Null
    if ($inspectHandoffStep.exit_code -ne 0) {
      $hasFailure = $true
    }
    $inspectHandoffPayload = Try-ParseJson -Raw $inspectHandoffStep.output
    if (-not $inspectHandoffPayload) {
      $hasFailure = $true
    }
    elseif ($inspectHandoffPayload.payload) {
      $inspectHandoffPayload = $inspectHandoffPayload.payload
    }
  }
  elseif ($ExecuteWriteFlow -and $skipExecuteOnPreflight) {
    $hasFailure = $true
  }
}

$sourceStringContractGuardPayload = $null
if (-not $SkipSourceStringContractGuard) {
  $sourceStringContractGuardStep = Invoke-CommandCapture -Label "source-string-contract-guard" -Command {
    & $python "scripts/check-source-string-contract-guard.py" "--target-repo-root" $resolvedAttachmentRoot "--configuration" "Debug" "--json"
  }
  $steps.Add($sourceStringContractGuardStep) | Out-Null
  if ($sourceStringContractGuardStep.exit_code -ne 0) {
    $hasFailure = $true
  }
  $sourceStringContractGuardPayload = Try-ParseJson -Raw $sourceStringContractGuardStep.output
  if (-not $sourceStringContractGuardPayload) {
    $hasFailure = $true
  }
  else {
    $guardStatus = ""
    if ($sourceStringContractGuardPayload.PSObject.Properties.Name -contains "status") {
      $guardStatus = [string]$sourceStringContractGuardPayload.status
    }
    if ($guardStatus -eq "fail") {
      $hasFailure = $true
      $nextActions.Add("repair source-string contract drift in target repo and rerun runtime-check") | Out-Null
    }
  }
}

$requestGateCommandPayload = $null
if ($requestGatePayload -and $requestGatePayload.payload) {
  $requestGateCommandPayload = $requestGatePayload.payload
}

$payloadsForContinuity = @()
if ($requestGateCommandPayload) { $payloadsForContinuity += $requestGateCommandPayload }
if ($writeGovernancePayload) { $payloadsForContinuity += $writeGovernancePayload }
if ($writeApprovalPayload) { $payloadsForContinuity += $writeApprovalPayload }
if ($writeExecutePayload) { $payloadsForContinuity += $writeExecutePayload }
if ($writeStatusPayload) { $payloadsForContinuity += $writeStatusPayload }

$sessionValues = New-Object System.Collections.Generic.List[string]
$resumeValues = New-Object System.Collections.Generic.List[string]
$continuationValues = New-Object System.Collections.Generic.List[string]
foreach ($payload in $payloadsForContinuity) {
  $sessionValue = Get-IdentityField -Payload $payload -FieldName "session_id"
  if (-not [string]::IsNullOrWhiteSpace($sessionValue)) {
    $sessionValues.Add($sessionValue) | Out-Null
  }
  $resumeValue = Get-IdentityField -Payload $payload -FieldName "resume_id"
  if (-not [string]::IsNullOrWhiteSpace($resumeValue)) {
    $resumeValues.Add($resumeValue) | Out-Null
  }
  $continuationValue = Get-IdentityField -Payload $payload -FieldName "continuation_id"
  if (-not [string]::IsNullOrWhiteSpace($continuationValue)) {
    $continuationValues.Add($continuationValue) | Out-Null
  }
  $directContinuation = Get-OptionalField -Payload $payload -FieldName "continuation_id"
  if (-not [string]::IsNullOrWhiteSpace($directContinuation)) {
    $continuationValues.Add($directContinuation) | Out-Null
  }
}
$sessionIdentityContinuity = (@($sessionValues | Select-Object -Unique).Count -le 1)
$resumeIdentityContinuity = (@($resumeValues | Select-Object -Unique).Count -le 1)
$continuationContinuity = (@($continuationValues | Select-Object -Unique).Count -le 1)

$flowKind = ""
foreach ($payload in @($writeExecutePayload, $writeStatusPayload, $writeGovernancePayload, $requestGateCommandPayload)) {
  $candidateFlowKind = Get-IdentityField -Payload $payload -FieldName "flow_kind"
  if (-not [string]::IsNullOrWhiteSpace($candidateFlowKind)) {
    $flowKind = $candidateFlowKind
    break
  }
}
if ([string]::IsNullOrWhiteSpace($flowKind)) {
  $flowKind = "unknown"
}

$fallbackReason = ""
if ($flowKind -ne "live_attach") {
  foreach ($payload in @($writeExecutePayload, $writeStatusPayload, $writeGovernancePayload, $requestGateCommandPayload)) {
    $candidateReason = Get-IdentityField -Payload $payload -FieldName "posture_reason"
    if (-not [string]::IsNullOrWhiteSpace($candidateReason)) {
      $fallbackReason = $candidateReason
      break
    }
  }
}

$runtimeRefs = New-Object System.Collections.Generic.List[string]
if ($requestGateCommandPayload) {
  Add-Ref -Refs $runtimeRefs -Value (Get-OptionalField -Payload $requestGateCommandPayload -FieldName "adapter_event_ref")
  Add-Ref -Refs $runtimeRefs -Value (Get-OptionalField -Payload $requestGateCommandPayload -FieldName "evidence_link")
  if ($requestGateCommandPayload.result_artifact_refs) {
    foreach ($property in $requestGateCommandPayload.result_artifact_refs.PSObject.Properties) {
      if ($property -and $property.Value) {
        Add-Ref -Refs $runtimeRefs -Value ([string]$property.Value)
      }
    }
  }
}
if ($writeExecutePayload) {
  Add-Ref -Refs $runtimeRefs -Value (Get-OptionalField -Payload $writeExecutePayload -FieldName "artifact_ref")
  Add-Ref -Refs $runtimeRefs -Value (Get-OptionalField -Payload $writeExecutePayload -FieldName "adapter_event_ref")
  Add-Ref -Refs $runtimeRefs -Value (Get-OptionalField -Payload $writeExecutePayload -FieldName "handoff_ref")
  Add-Ref -Refs $runtimeRefs -Value (Get-OptionalField -Payload $writeExecutePayload -FieldName "replay_ref")
}
if ($inspectEvidencePayload -and $inspectEvidencePayload.evidence_refs) {
  foreach ($ref in $inspectEvidencePayload.evidence_refs) {
    Add-Ref -Refs $runtimeRefs -Value ([string]$ref)
  }
}
if ($inspectHandoffPayload -and $inspectHandoffPayload.handoff_refs) {
  foreach ($ref in $inspectHandoffPayload.handoff_refs) {
    Add-Ref -Refs $runtimeRefs -Value ([string]$ref)
  }
}
if ($inspectHandoffPayload -and $inspectHandoffPayload.replay_refs) {
  foreach ($ref in $inspectHandoffPayload.replay_refs) {
    Add-Ref -Refs $runtimeRefs -Value ([string]$ref)
  }
}

$verificationLinked = $false
if ($requestGateCommandPayload -and $requestGateCommandPayload.result_artifact_refs) {
  $verificationLinked = (@($requestGateCommandPayload.result_artifact_refs.PSObject.Properties).Count -gt 0)
}
$writeLinked = $false
if ($writeExecutePayload) {
  $writeLinked = (
    -not [string]::IsNullOrWhiteSpace((Get-OptionalField -Payload $writeExecutePayload -FieldName "handoff_ref")) -and
    -not [string]::IsNullOrWhiteSpace((Get-OptionalField -Payload $writeExecutePayload -FieldName "replay_ref")) -and
    -not [string]::IsNullOrWhiteSpace((Get-OptionalField -Payload $writeExecutePayload -FieldName "adapter_event_ref"))
  )
}
$inspectionLinked = ($null -ne $inspectEvidencePayload -and $null -ne $inspectHandoffPayload)
$evidenceLinkageComplete = $verificationLinked -and (($null -eq $writeExecutePayload) -or ($writeLinked -and $inspectionLinked))

$fallbackExplicit = ($flowKind -ne "live_attach")
$closureState = "incomplete"
if (($flowKind -eq "live_attach") -and $sessionIdentityContinuity -and $resumeIdentityContinuity -and $continuationContinuity -and $evidenceLinkageComplete) {
  $closureState = "live_closure_ready"
}
elseif ($fallbackExplicit -and $sessionIdentityContinuity -and $resumeIdentityContinuity -and $continuationContinuity -and $evidenceLinkageComplete) {
  $closureState = "fallback_explicit"
}

$liveLoopSummary = @{
  flow_kind = $flowKind
  is_live_attach = ($flowKind -eq "live_attach")
  fallback_explicit = $fallbackExplicit
  fallback_reason = $(if (-not [string]::IsNullOrWhiteSpace($fallbackReason)) { $fallbackReason } else { $null })
  session_identity_continuity = $sessionIdentityContinuity
  resume_identity_continuity = $resumeIdentityContinuity
  continuation_continuity = $continuationContinuity
  evidence_linkage_complete = $evidenceLinkageComplete
  closure_state = $closureState
  runtime_refs = @($runtimeRefs)
}

$summary = @{
  attachment_root = $resolvedAttachmentRoot
  attachment_runtime_state_root = $resolvedAttachmentRuntimeStateRoot
  entrypoint_id = $EntrypointId
  mode = $Mode
  task_id = $TaskId
  run_id = $RunId
  command_id = $CommandId
  repo_binding_id = $resolvedBindingId
  session_id = $resolvedSessionId
  resume_id = $resolvedResumeId
  continuation_id = $resolvedContinuationId
  flow_kind = $flowKind
  closure_state = $closureState
  attachment_health = $attachmentHealth
  overall_status = $(if ($hasFailure) { "fail" } else { "pass" })
}

if ($requestGateCommandPayload -and $requestGateCommandPayload.entrypoint_policy) {
  $summary.entrypoint_policy_mode = [string]$requestGateCommandPayload.entrypoint_policy.current_mode
  $summary.entrypoint_drift = [bool]$requestGateCommandPayload.entrypoint_policy.drift_detected
  $summary.entrypoint_blocked = [bool]$requestGateCommandPayload.entrypoint_policy.blocked
}

$result = @{
  summary = $summary
  dependency_baseline = $dependencyBaselinePayload
  status = $statusPayload
  request_gate = $requestGatePayload
  verify_attachment = $verifyPayload
  source_string_contract_guard = $sourceStringContractGuardPayload
  write_governance = $writeGovernancePayload
  write_preflight = $writePreflight
  write_approval = $writeApprovalPayload
  write_execute = $writeExecutePayload
  write_status = $writeStatusPayload
  inspect_evidence = $inspectEvidencePayload
  inspect_handoff = $inspectHandoffPayload
  next_actions = @($nextActions)
  live_loop = $liveLoopSummary
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
  if ($sourceStringContractGuardPayload) {
    $guardStatus = ""
    if ($sourceStringContractGuardPayload.PSObject.Properties.Name -contains "status") {
      $guardStatus = [string]$sourceStringContractGuardPayload.status
    }
    if (-not [string]::IsNullOrWhiteSpace($guardStatus)) {
      Write-Host ("SourceStringContractGuard: " + $guardStatus)
    }
    if ($sourceStringContractGuardPayload.reason) {
      Write-Host ("SourceStringContractGuardReason: " + [string]$sourceStringContractGuardPayload.reason)
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
  if ($writePreflight -and $writePreflight.blocked) {
    Write-Host "Write Preflight: blocked"
    if ($writePreflight.reason) {
      Write-Host ("Write Reason: " + [string]$writePreflight.reason)
    }
    if ($writePreflight.remediation_hint) {
      Write-Host ("Write Remediation: " + [string]$writePreflight.remediation_hint)
    }
    if ($writePreflight.retry_command) {
      Write-Host ("Write Retry Command: " + [string]$writePreflight.retry_command)
    }
  }
  if ($liveLoopSummary) {
    Write-Host ("Flow Kind: " + [string]$liveLoopSummary.flow_kind)
    Write-Host ("Closure State: " + [string]$liveLoopSummary.closure_state)
  }
}

if ($hasFailure) {
  exit 1
}
exit 0
