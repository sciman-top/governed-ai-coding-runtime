param(
  [switch]$Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $scriptRoot "Initialize-WindowsProcessEnvironment.ps1")
Initialize-WindowsProcessEnvironment

$payload = [ordered]@{
  status = "retired_command"
  command = "runtime-check"
  reason = "Target-repo attachment and session-bridge runtime checks were retired from the current repo scope."
  remediation_hint = "Use scripts/build-runtime.ps1, scripts/verify-repo.ps1, scripts/doctor-runtime.ps1, or scripts/operator.ps1 for repo-local verification."
}

if ($Json.IsPresent) {
  $payload | ConvertTo-Json -Depth 4
}
else {
  Write-Error ("Retired runtime-check command: {0} {1}" -f $payload.reason, $payload.remediation_hint)
}

exit 1
