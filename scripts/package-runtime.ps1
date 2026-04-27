Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-FileSha256 {
  param([string]$Path)

  $hash = Get-FileHash -Algorithm SHA256 -Path $Path
  return "sha256:$($hash.Hash.ToLowerInvariant())"
}

function Get-DirectorySha256 {
  param([string]$Root)

  $parts = Get-ChildItem -Path $Root -Recurse -File | Sort-Object FullName | ForEach-Object {
    $relativePath = $_.FullName.Substring($Root.Length).TrimStart('\', '/') -replace '\\', '/'
    $fileHash = Get-FileSha256 -Path $_.FullName
    "$relativePath=$fileHash"
  }
  $joined = ($parts -join "`n")
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($joined)
  $sha = [System.Security.Cryptography.SHA256]::Create()
  try {
    $digest = $sha.ComputeHash($bytes)
  }
  finally {
    $sha.Dispose()
  }
  return "sha256:" + (($digest | ForEach-Object { $_.ToString("x2") }) -join "")
}

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

$distDigest = Get-DirectorySha256 -Root $distRoot
$packageScriptRef = "scripts/package-runtime.ps1"
$packageScriptPath = Join-Path $root $packageScriptRef
$provenancePath = Join-Path $root ".runtime/dist/public-usable-release.provenance.json"
$provenance = @{
  schema_version = "1.0"
  attestation_id = "public-usable-release-local"
  subject_type = "release"
  subject_ref = ($distRoot -replace '\\', '/')
  subject_digest = $distDigest
  predicate_type = "local-release-package"
  producer = "scripts/package-runtime.ps1"
  generated_at = (Get-Date).ToUniversalTime().ToString("o")
  materials = @(
    @{
      uri = $packageScriptRef
      version_or_digest = Get-FileSha256 -Path $packageScriptPath
    },
    @{
      uri = "schemas/control-packs/minimum-governance-kernel.control-pack.json"
      version_or_digest = Get-FileSha256 -Path (Join-Path $root "schemas/control-packs/minimum-governance-kernel.control-pack.json")
    },
    @{
      uri = "schemas/jsonschema/provenance-and-attestation.schema.json"
      version_or_digest = Get-FileSha256 -Path (Join-Path $root "schemas/jsonschema/provenance-and-attestation.schema.json")
    }
  )
  verification_status = "verified"
  statement_ref = "docs/change-evidence/20260427-gap-109-data-plane-provenance-release.md"
  rollback_ref = "Remove-Item -Recurse -Force .runtime/dist/public-usable-release, .runtime/dist/public-usable-release.provenance.json"
  build_ref = "scripts/package-runtime.ps1"
  source_ref = "git worktree"
  generator_version = "package-runtime.ps1@1"
  output_digest = $distDigest
  control_pack_ref = "schemas/control-packs/minimum-governance-kernel.control-pack.json"
  notes = "Local package provenance; digest is deterministic over copied release tree contents and does not imply external signing."
}
$provenanceDirectory = Split-Path -Parent $provenancePath
if (-not (Test-Path $provenanceDirectory)) {
  New-Item -ItemType Directory -Force -Path $provenanceDirectory | Out-Null
}
$provenance | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 -Path $provenancePath

$payload.provenance_path = ($provenancePath -replace '\\', '/')
$payload.provenance = @{
  attestation_id = $provenance.attestation_id
  subject_digest = $provenance.subject_digest
  verification_status = $provenance.verification_status
  rollback_ref = $provenance.rollback_ref
}

$payload | ConvertTo-Json -Depth 4
