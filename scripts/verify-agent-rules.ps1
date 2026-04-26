param(
  [ValidateSet("All", "Global", "Targets")]
  [string]$Scope = "All",
  [string[]]$Target = @(),
  [string]$ManifestPath = "rules/manifest.json",
  [string]$CatalogPath = "docs/targets/target-repos-catalog.json"
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
  "-CatalogPath",
  $CatalogPath,
  "-FailOnChange"
)

foreach ($item in $Target) {
  $argsList += @("-Target", $item)
}

& pwsh @argsList
exit $LASTEXITCODE
