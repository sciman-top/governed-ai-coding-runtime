param(
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
  [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$presetPath = Join-Path $PSScriptRoot "runtime-flow-preset.ps1"
if (-not (Test-Path $presetPath)) {
  throw "Missing runtime-flow-preset.ps1 at $presetPath"
}

$argsList = @(
  "-NoProfile",
  "-ExecutionPolicy", "Bypass",
  "-File", $presetPath,
  "-Target", "classroomtoolkit",
  "-FlowMode", $FlowMode,
  "-Mode", $Mode,
  "-PolicyStatus", $PolicyStatus,
  "-TaskId", $TaskId,
  "-RunId", $RunId,
  "-CommandId", $CommandId,
  "-AdapterId", $AdapterId,
  "-AdapterPreference", $AdapterPreference
)
if (-not [string]::IsNullOrWhiteSpace($RepoBindingId)) {
  $argsList += @("-RepoBindingId", $RepoBindingId)
}
if (-not [string]::IsNullOrWhiteSpace($WriteTargetPath)) {
  $argsList += @("-WriteTargetPath", $WriteTargetPath, "-WriteTier", $WriteTier, "-WriteToolName", $WriteToolName, "-WriteContent", $WriteContent)
  if (-not [string]::IsNullOrWhiteSpace($WriteToolCommand)) {
    $argsList += @("-WriteToolCommand", $WriteToolCommand)
  }
}
if (-not [string]::IsNullOrWhiteSpace($RollbackReference)) {
  $argsList += @("-RollbackReference", $RollbackReference)
}
if ($ExecuteWriteFlow) {
  $argsList += "-ExecuteWriteFlow"
}
if ($SkipVerifyAttachment) {
  $argsList += "-SkipVerifyAttachment"
}
if ($Overwrite) {
  $argsList += "-Overwrite"
}
if ($Json) {
  $argsList += "-Json"
}

& pwsh @argsList
exit $LASTEXITCODE

