param(
  [ValidateSet("classroomtoolkit", "self-runtime", "skills-manager")]
  [string]$Target = "classroomtoolkit",

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
  [string]$WriteContent = "governed runtime write probe",
  [switch]$ExecuteWriteFlow,
  [switch]$SkipVerifyAttachment,

  [switch]$Overwrite,
  [switch]$Json
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

$repoRoot = Resolve-AbsolutePath -PathValue (Join-Path $PSScriptRoot "..")
$codeRoot = Split-Path $repoRoot -Parent
$runtimeStateBase = Join-Path $repoRoot ".runtime\attachments"

$targetConfigMap = @{
  "classroomtoolkit" = @{
    AttachmentRoot = Join-Path $codeRoot "ClassroomToolkit"
    AttachmentRuntimeStateRoot = Join-Path $runtimeStateBase "classroomtoolkit"
    RepoId = "classroomtoolkit"
    DisplayName = "ClassroomToolkit"
    PrimaryLanguage = "csharp"
    BuildCommand = "dotnet build ClassroomToolkit.sln -c Debug"
    TestCommand = "dotnet test tests/ClassroomToolkit.Tests/ClassroomToolkit.Tests.csproj -c Debug"
    ContractCommand = "dotnet test tests/ClassroomToolkit.Tests/ClassroomToolkit.Tests.csproj -c Debug"
  }
  "self-runtime" = @{
    AttachmentRoot = $repoRoot
    AttachmentRuntimeStateRoot = Join-Path $codeRoot "governed-ai-runtime-state\self-runtime"
    RepoId = "governed-ai-coding-runtime"
    DisplayName = "Governed AI Coding Runtime"
    PrimaryLanguage = "python"
    BuildCommand = "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1"
    TestCommand = "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime"
    ContractCommand = "pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract"
  }
  "skills-manager" = @{
    AttachmentRoot = Join-Path $codeRoot "skills-manager"
    AttachmentRuntimeStateRoot = Join-Path $runtimeStateBase "skills-manager"
    RepoId = "skills-manager"
    DisplayName = "skills-manager"
    PrimaryLanguage = "python"
    BuildCommand = "python --version"
    TestCommand = "python --version"
    ContractCommand = "python --version"
  }
}

$targetConfig = $targetConfigMap[$Target]
if (-not $targetConfig) {
  throw "Unsupported target preset: $Target"
}

$runtimeFlowPath = Join-Path $PSScriptRoot "runtime-flow.ps1"
if (-not (Test-Path $runtimeFlowPath)) {
  throw "Missing runtime-flow.ps1 at $runtimeFlowPath"
}

$flowArgs = @(
  "-NoProfile",
  "-ExecutionPolicy", "Bypass",
  "-File", $runtimeFlowPath,
  "-FlowMode", $FlowMode,
  "-AttachmentRoot", $targetConfig.AttachmentRoot,
  "-AttachmentRuntimeStateRoot", $targetConfig.AttachmentRuntimeStateRoot,
  "-Mode", $Mode,
  "-PolicyStatus", $PolicyStatus,
  "-TaskId", $TaskId,
  "-RunId", $RunId,
  "-CommandId", $CommandId,
  "-AdapterId", $AdapterId
)

if (-not [string]::IsNullOrWhiteSpace($RepoBindingId)) {
  $flowArgs += @("-RepoBindingId", $RepoBindingId)
}
if (-not [string]::IsNullOrWhiteSpace($WriteTargetPath)) {
  $flowArgs += @("-WriteTargetPath", $WriteTargetPath, "-WriteTier", $WriteTier, "-WriteToolName", $WriteToolName, "-WriteContent", $WriteContent)
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
    "-RepoId", $targetConfig.RepoId,
    "-DisplayName", $targetConfig.DisplayName,
    "-PrimaryLanguage", $targetConfig.PrimaryLanguage,
    "-BuildCommand", $targetConfig.BuildCommand,
    "-TestCommand", $targetConfig.TestCommand,
    "-ContractCommand", $targetConfig.ContractCommand,
    "-AdapterPreference", "process_bridge"
  )
  if ($Overwrite) {
    $flowArgs += "-Overwrite"
  }
}
if ($Json) {
  $flowArgs += "-Json"
}

& pwsh @flowArgs
exit $LASTEXITCODE

