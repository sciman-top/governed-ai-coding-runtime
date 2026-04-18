param(
  [ValidateSet("onboard", "daily")]
  [string]$FlowMode = "daily",

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
  "-AdapterId", $AdapterId
)
if (-not [string]::IsNullOrWhiteSpace($RepoBindingId)) {
  $argsList += @("-RepoBindingId", $RepoBindingId)
}
if (-not [string]::IsNullOrWhiteSpace($WriteTargetPath)) {
  $argsList += @("-WriteTargetPath", $WriteTargetPath, "-WriteTier", $WriteTier, "-WriteToolName", $WriteToolName)
}
if (-not [string]::IsNullOrWhiteSpace($RollbackReference)) {
  $argsList += @("-RollbackReference", $RollbackReference)
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

