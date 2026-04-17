Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-CheckOk {
  param([string]$Name)
  Write-Host "OK $Name"
}

function Assert-PathExists {
  param(
    [string]$Path,
    [string]$CheckName
  )

  if (-not (Test-Path $Path)) {
    throw "Required path missing: $Path"
  }

  Write-CheckOk $CheckName
}

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
  $python = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $python) {
  throw "Required command not found: python or python3"
}
Write-CheckOk "python-command"

foreach ($pathCheck in @(
  @{ Path = "packages/contracts/src"; Check = "runtime-path-contracts" },
  @{ Path = "schemas/catalog/schema-catalog.yaml"; Check = "runtime-path-schema-catalog" },
  @{ Path = "docs/specs"; Check = "runtime-path-specs" },
  @{ Path = "tests/runtime"; Check = "runtime-path-tests" }
)) {
  Assert-PathExists -Path $pathCheck.Path -CheckName $pathCheck.Check
}

$catalog = Get-Content -Raw "schemas/catalog/schema-catalog.yaml"
if ($catalog -notmatch "repo-profile" -or $catalog -notmatch "clarification-protocol") {
  throw "Schema catalog is missing expected schema families"
}
Write-CheckOk "schema-catalog-visible"

$gateCommands = @(
  @{ Path = "scripts/build-runtime.ps1"; Check = "gate-command-build" },
  @{ Path = "scripts/verify-repo.ps1"; Check = "gate-command-test" },
  @{ Path = "scripts/verify-repo.ps1"; Check = "gate-command-contract" },
  @{ Path = "scripts/doctor-runtime.ps1"; Check = "gate-command-doctor" }
)

foreach ($gateCommand in $gateCommands) {
  Assert-PathExists -Path $gateCommand.Path -CheckName $gateCommand.Check
}
