Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Copy-FilteredTree {
  param(
    [string]$SourceRoot,
    [string]$TargetRoot
  )

  Get-ChildItem -Path $SourceRoot -Recurse -File | Where-Object {
    $_.FullName -notmatch '[\\/]+__pycache__[\\/]' -and
    $_.Extension -ne '.pyc'
  } | ForEach-Object {
    $relativePath = $_.FullName.Substring($SourceRoot.Length).TrimStart('\', '/')
    $targetPath = Join-Path $TargetRoot $relativePath
    $targetDirectory = Split-Path -Parent $targetPath
    if (-not (Test-Path $targetDirectory)) {
      New-Item -ItemType Directory -Force -Path $targetDirectory | Out-Null
    }
    Copy-Item -Force $_.FullName $targetPath
  }
}

$root = Get-Location
$distRoot = Join-Path $root ".runtime/dist/public-usable-release"
if (Test-Path $distRoot) {
  Remove-Item -Recurse -Force $distRoot
}
New-Item -ItemType Directory -Force -Path $distRoot | Out-Null

$copyPaths = @(
  "README.md",
  "README.zh-CN.md",
  "README.en.md",
  "docs",
  "packages",
  "schemas",
  "scripts",
  "tests"
)

foreach ($relativePath in $copyPaths) {
  $source = Join-Path $root $relativePath
  $target = Join-Path $distRoot $relativePath
  if (Test-Path $source -PathType Container) {
    Copy-FilteredTree -SourceRoot $source -TargetRoot $target
  } else {
    $targetDirectory = Split-Path -Parent $target
    if (-not (Test-Path $targetDirectory)) {
      New-Item -ItemType Directory -Force -Path $targetDirectory | Out-Null
    }
    Copy-Item -Force $source $target
  }
}

$payload = @{
  distribution_root = ($distRoot -replace '\\', '/')
  included_paths = $copyPaths
}

$payload | ConvertTo-Json -Depth 4
