Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

. "$PSScriptRoot\Initialize-WindowsProcessEnvironment.ps1"
Initialize-WindowsProcessEnvironment

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

$runtimeRoot = Join-Path (Get-Location) ".runtime"
$paths = @(
  (Join-Path $runtimeRoot "tasks"),
  (Join-Path $runtimeRoot "artifacts"),
  (Join-Path $runtimeRoot "replay")
)

foreach ($path in $paths) {
  New-Item -ItemType Directory -Force -Path $path | Out-Null
}

[void](Get-Command pwsh -ErrorAction Stop)
$python = Get-PythonCommand
$statusJson = & $python "scripts/run-governed-task.py" status --json
if ($LASTEXITCODE -ne 0) {
  throw "Runtime status command failed during bootstrap"
}

$payload = @{
  runtime_root = (Resolve-Path $runtimeRoot).Path
  bootstrap_paths = $paths
  status = ($statusJson | ConvertFrom-Json)
}

$payload | ConvertTo-Json -Depth 6
