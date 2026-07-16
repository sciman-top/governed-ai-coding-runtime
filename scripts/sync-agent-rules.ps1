param(
  [ValidateSet("All", "Global")]
  [string]$Scope = "All",
  [switch]$Apply,
  [switch]$Force,
  [switch]$FailOnChange,
  [string]$ManifestPath = "rules/manifest.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$SyncScript = Join-Path $PSScriptRoot "sync-agent-rules.py"

if (-not [System.IO.Path]::IsPathRooted($ManifestPath)) {
  $ManifestPath = Join-Path $RepoRoot $ManifestPath
}

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
  $python = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $python) {
  throw "Required command not found: python or python3"
}

$argsList = @(
  $SyncScript,
  "--scope",
  $Scope,
  "--manifest-path",
  $ManifestPath
)
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
