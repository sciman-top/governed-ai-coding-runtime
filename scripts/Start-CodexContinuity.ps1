param(
  [Parameter(Mandatory = $true)]
  [string]$Prompt,

  [string]$TaskId = ("codex-continuity-" + (Get-Date -Format "yyyyMMdd-HHmmss")),

  [string]$Repo = (Get-Location).Path,

  [string]$EvidenceDir = "docs/change-evidence/codex-cli-continuity",

  [int]$WaitSeconds = 900,

  [int]$MaxSegments = 3,

  [switch]$Execute,

  [string]$OutputLastMessage
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot ".."))
$runner = Join-Path $repoRoot "scripts/codex-cli-continuity-runner.py"
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
  $python = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $python) {
  throw "Required command not found: python or python3"
}

$argsList = @(
  $runner,
  "--task-id", $TaskId,
  "--repo", $Repo,
  "--prompt", $Prompt,
  "--evidence-dir", $EvidenceDir,
  "--wait-seconds", [string]$WaitSeconds,
  "--max-segments", [string]$MaxSegments,
  "--json"
)
if ($Execute) {
  $argsList += "--execute"
}
if (-not [string]::IsNullOrWhiteSpace($OutputLastMessage)) {
  $argsList += @("--output-last-message", $OutputLastMessage)
}

& $python.Source @argsList
exit $LASTEXITCODE
