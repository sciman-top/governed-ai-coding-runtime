param(
  [ValidateSet("All", "Global")]
  [string]$Scope = "All",
  [string]$ManifestPath = "rules/manifest.json"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$argsList = @(
  "-NoProfile",
  "-ExecutionPolicy",
  "Bypass",
  "-File",
  "scripts/sync-agent-rules.ps1",
  "-Scope",
  $Scope,
  "-ManifestPath",
  $ManifestPath,
  "-FailOnChange"
)

& pwsh @argsList
exit $LASTEXITCODE
