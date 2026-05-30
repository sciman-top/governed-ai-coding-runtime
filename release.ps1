param(
  [string]$Version = "0.1.0-local",

  [ValidateSet("portable")]
  [string]$Channel = "portable"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$PackageScript = Join-Path $RepoRoot "scripts/package-runtime.ps1"
if (-not (Test-Path -LiteralPath $PackageScript)) {
  throw "Package script not found: $PackageScript"
}

& pwsh -NoProfile -ExecutionPolicy Bypass -File $PackageScript -Version $Version -Channel $Channel
exit $LASTEXITCODE
