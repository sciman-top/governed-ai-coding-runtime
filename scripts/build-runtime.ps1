Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-CheckOk {
  param([string]$Name)
  Write-Host "OK $Name"
}

$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
  $python = Get-Command python3 -ErrorAction SilentlyContinue
}
if (-not $python) {
  throw "Required command not found: python or python3"
}

$sourceRoots = @(
  "packages/contracts/src",
  "scripts"
)

& $python.Source -m compileall @sourceRoots
if ($LASTEXITCODE -ne 0) {
  throw "Python bytecode compilation failed"
}
Write-CheckOk "python-bytecode"

$importScript = @'
from __future__ import annotations

import importlib
import pkgutil
import sys
from pathlib import Path

root = Path.cwd()
contracts_src = root / "packages" / "contracts" / "src"
sys.path.insert(0, str(contracts_src))

package = importlib.import_module("governed_ai_coding_runtime_contracts")
for module_info in pkgutil.iter_modules(package.__path__):
    importlib.import_module(f"governed_ai_coding_runtime_contracts.{module_info.name}")
'@

$importScript | & $python.Source -
if ($LASTEXITCODE -ne 0) {
  throw "Python import validation failed"
}
Write-CheckOk "python-import"
