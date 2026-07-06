param(
  [ValidateSet("l1", "l2", "l3", "quick", "fast", "full")]
  [string]$Level = "l1",
  [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptRoot "..\Initialize-WindowsProcessEnvironment.ps1")
Initialize-WindowsProcessEnvironment

$payload = [ordered]@{
  status = "retired_command"
  command = "level-check"
  requested_level = $Level
  reason = "Layered target-repo gate runs were retired with the target-repo rollout surface."
  remediation_hint = "Use scripts/verify-repo.ps1 or scripts/operator.ps1 for repo-local checks."
}

if ($Json.IsPresent) {
  $payload | ConvertTo-Json -Depth 4
}
else {
  Write-Error ("Retired level-check command: {0} {1}" -f $payload.reason, $payload.remediation_hint)
}

exit 1
