param(
  [string]$Target = "classroomtoolkit",

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
  [switch]$ListTargets
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

$repoRoot = Resolve-AbsolutePath -PathValue (Join-Path $PSScriptRoot "..")
$codeRoot = Split-Path $repoRoot -Parent
$runtimeStateBase = Join-Path $repoRoot ".runtime\attachments"
$catalogPath = Join-Path $repoRoot "docs\targets\target-repos-catalog.json"
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
      targets = $targetNames
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

$targetConfig = $targetConfigMap[$Target]
if (-not $targetConfig) {
  $available = @($targetConfigMap.Keys | Sort-Object) -join ", "
  throw "Unsupported target preset: $Target. Available targets: $available"
}

$runtimeFlowPath = Join-Path $PSScriptRoot "runtime-flow.ps1"
if (-not (Test-Path $runtimeFlowPath)) {
  throw "Missing runtime-flow.ps1 at $runtimeFlowPath"
}

$flowArgs = @(
  "-NoProfile",
  "-ExecutionPolicy", "Bypass",
  "-File", $runtimeFlowPath,
  "-EntrypointId", "runtime-flow-preset",
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
    "-RepoId", $targetConfig.RepoId,
    "-DisplayName", $targetConfig.DisplayName,
    "-PrimaryLanguage", $targetConfig.PrimaryLanguage,
    "-BuildCommand", $targetConfig.BuildCommand,
    "-TestCommand", $targetConfig.TestCommand,
    "-ContractCommand", $targetConfig.ContractCommand,
    "-AdapterPreference", $AdapterPreference
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

