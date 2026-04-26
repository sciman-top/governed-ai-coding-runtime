param(
  [ValidateSet("All", "Global", "Targets")]
  [string]$Scope = "All",
  [string[]]$Target = @(),
  [switch]$Apply,
  [switch]$Force,
  [switch]$FailOnChange,
  [string]$ManifestPath = "rules/manifest.json",
  [string]$CatalogPath = "docs/targets/target-repos-catalog.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. "$PSScriptRoot\Initialize-WindowsProcessEnvironment.ps1"
Initialize-WindowsProcessEnvironment

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
  $python = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $python) {
  throw "Required command not found: python or python3"
}

$argsList = @(
  "scripts/sync-agent-rules.py",
  "--scope",
  $Scope,
  "--manifest-path",
  $ManifestPath,
  "--catalog-path",
  $CatalogPath
)

foreach ($item in $Target) {
  $argsList += @("--target", $item)
}
if ($Apply) {
  $argsList += "--apply"
}
if ($Force) {
  $argsList += "--force"
}
if ($FailOnChange) {
  $argsList += "--fail-on-change"
}

& $python.Source @argsList
exit $LASTEXITCODE
