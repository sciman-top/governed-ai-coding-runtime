param(
  [string]$Version = "0.1.0-local",

  [ValidateSet("portable")]
  [string]$Channel = "portable"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-FileSha256 {
  param([string]$Path)

  $hash = Get-FileHash -Algorithm SHA256 -Path $Path
  return "sha256:$($hash.Hash.ToLowerInvariant())"
}

function Get-DirectorySha256 {
  param([string]$Root)

  $parts = New-StableFileList -Root $Root | ForEach-Object {
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

function Copy-FileWithRetry {
  param(
    [string]$SourcePath,
    [string]$DestinationPath,
    [int]$MaxAttempts = 8,
    [int]$DelayMilliseconds = 250
  )

  $attempt = 0
  while ($true) {
    $attempt += 1
    try {
      Copy-Item -Force -LiteralPath $SourcePath -Destination $DestinationPath
      return
    }
    catch {
      if ($attempt -ge $MaxAttempts) {
        throw
      }
      Start-Sleep -Milliseconds $DelayMilliseconds
    }
  }
}

function New-StableFileList {
  param([string]$Root)

  return @(Get-ChildItem -Path $Root -Recurse -File -Force | Sort-Object FullName)
}

function Add-ZipEntryFromFileWithRetry {
  param(
    [object]$ZipArchive,
    [string]$SourcePath,
    [string]$EntryName,
    [int]$MaxAttempts = 8,
    [int]$DelayMilliseconds = 250
  )

  $attempt = 0
  while ($true) {
    $attempt += 1
    try {
      [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
        $ZipArchive,
        $SourcePath,
        $EntryName,
        [System.IO.Compression.CompressionLevel]::Optimal
      ) | Out-Null
      return
    }
    catch {
      if ($attempt -ge $MaxAttempts) {
        throw
      }
      Start-Sleep -Milliseconds $DelayMilliseconds
    }
  }
}

function Assert-ReleaseVersion {
  param([string]$Value)

  if ($Value -notmatch '^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$' -or $Value.Contains("..")) {
    throw "Invalid release version: $Value"
  }
}

function Join-ReleasePath {
  param(
    [string]$Prefix,
    [string]$RelativePath
  )

  if ([string]::IsNullOrWhiteSpace($RelativePath)) {
    return ($Prefix -replace '\\', '/').Trim('/')
  }
  return (($Prefix.TrimEnd('\', '/') + "/" + $RelativePath.TrimStart('\', '/')) -replace '\\', '/').Trim('/')
}

function Test-ExcludedReleasePath {
  param([string]$RelativePath)

  $normalized = ($RelativePath -replace '\\', '/').Trim('/')
  $excludedPrefixes = @(
    ".runtime/",
    ".tmp/",
    ".tmp-test/",
    ".pytest_cache/",
    ".playwright-mcp/",
    ".worktrees/",
    ".vs/",
    ".git/",
    "docs/change-evidence/",
    "docs/archive/"
  )
  foreach ($prefix in $excludedPrefixes) {
    if ($normalized.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)) {
      return $true
    }
  }
  return $false
}

function Assert-ReleaseOutputPath {
  param(
    [string]$Path,
    [string]$AllowedRoot
  )

  $resolvedPath = [System.IO.Path]::GetFullPath($Path)
  $resolvedRoot = [System.IO.Path]::GetFullPath($AllowedRoot).TrimEnd('\', '/')
  $rootWithSeparator = $resolvedRoot + [System.IO.Path]::DirectorySeparatorChar
  if (-not $resolvedPath.StartsWith($rootWithSeparator, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "release output path escapes allowed root: $Path"
  }
}

function Copy-FilteredTree {
  param(
    [string]$SourceRoot,
    [string]$TargetRoot,
    [string]$SourcePrefix
  )

  Get-ChildItem -Path $SourceRoot -Recurse -File -Force | Where-Object {
    $relativePath = $_.FullName.Substring($SourceRoot.Length).TrimStart('\', '/')
    $releasePath = Join-ReleasePath -Prefix $SourcePrefix -RelativePath $relativePath
    -not (Test-ExcludedReleasePath -RelativePath $releasePath) -and
    $_.FullName -notmatch '[\\/]+__pycache__[\\/]' -and
    $_.Extension -ne '.pyc'
  } | ForEach-Object {
    $relativePath = $_.FullName.Substring($SourceRoot.Length).TrimStart('\', '/')
    $targetPath = Join-Path $TargetRoot $relativePath
    $targetDirectory = Split-Path -Parent $targetPath
    if (-not (Test-Path $targetDirectory)) {
      New-Item -ItemType Directory -Force -Path $targetDirectory | Out-Null
    }
    Copy-FileWithRetry -SourcePath $_.FullName -DestinationPath $targetPath
  }
}

function New-ZipFromDirectory {
  param(
    [string]$SourceRoot,
    [string]$DestinationPath,
    [string]$AllowedOutputRoot
  )

  Add-Type -AssemblyName System.IO.Compression.FileSystem
  Assert-ReleaseOutputPath -Path $DestinationPath -AllowedRoot $AllowedOutputRoot
  if (Test-Path -LiteralPath $DestinationPath) {
    Remove-Item -Force -LiteralPath $DestinationPath
  }
  $zip = [System.IO.Compression.ZipFile]::Open($DestinationPath, [System.IO.Compression.ZipArchiveMode]::Create)
  try {
    $files = New-StableFileList -Root $SourceRoot
    $files | ForEach-Object {
      $entryName = ($_.FullName.Substring($SourceRoot.Length).TrimStart('\', '/') -replace '\\', '/')
      Add-ZipEntryFromFileWithRetry -ZipArchive $zip -SourcePath $_.FullName -EntryName $entryName
    }
  }
  finally {
    $zip.Dispose()
  }
}

Assert-ReleaseVersion -Value $Version

$root = Split-Path -Parent $PSScriptRoot
$distRoot = Join-Path $root ".runtime/dist/public-usable-release"
$releaseRoot = Join-Path $root ".runtime/dist/releases"
if (Test-Path -LiteralPath $distRoot) {
  Assert-ReleaseOutputPath -Path $distRoot -AllowedRoot (Join-Path $root ".runtime/dist")
  Remove-Item -Recurse -Force -LiteralPath $distRoot
}
New-Item -ItemType Directory -Force -Path $distRoot | Out-Null
New-Item -ItemType Directory -Force -Path $releaseRoot | Out-Null

$copyPaths = @(
  "README.md",
  "README.zh-CN.md",
  "README.en.md",
  "LICENSE",
  "AGENTS.md",
  "CLAUDE.md",
  "GEMINI.md",
  "run.ps1",
  "install.ps1",
  "release.ps1",
  ".githooks",
  "docs",
  "packages",
  "rules",
  "schemas",
  "scripts",
  "tests"
)

$copiedPaths = New-Object System.Collections.Generic.List[string]
foreach ($relativePath in $copyPaths) {
  if (Test-ExcludedReleasePath -RelativePath $relativePath) {
    continue
  }
  $source = Join-Path $root $relativePath
  if (-not (Test-Path -LiteralPath $source)) {
    throw "release source path not found: $relativePath"
  }
  $target = Join-Path $distRoot $relativePath
  if (Test-Path -LiteralPath $source -PathType Container) {
    Copy-FilteredTree -SourceRoot $source -TargetRoot $target -SourcePrefix $relativePath
  } else {
    $targetDirectory = Split-Path -Parent $target
    if (-not (Test-Path $targetDirectory)) {
      New-Item -ItemType Directory -Force -Path $targetDirectory | Out-Null
    }
    Copy-FileWithRetry -SourcePath $source -DestinationPath $target
  }
  [void]$copiedPaths.Add($relativePath)
}

$distDigest = Get-DirectorySha256 -Root $distRoot
$archiveName = "governed-ai-runtime-$Version-$Channel.zip"
$archivePath = Join-Path $releaseRoot $archiveName
New-ZipFromDirectory -SourceRoot $distRoot -DestinationPath $archivePath -AllowedOutputRoot $releaseRoot
$archiveDigest = Get-FileSha256 -Path $archivePath

$sha256Path = Join-Path $releaseRoot "$archiveName.sha256"
"$archiveDigest  $archiveName" | Set-Content -Encoding UTF8 -Path $sha256Path

$excludedPaths = @(
  ".runtime/**",
  ".tmp/**",
  ".tmp-test/**",
  ".pytest_cache/**",
  ".playwright-mcp/**",
  ".worktrees/**",
  ".vs/**",
  ".git/**",
  "docs/change-evidence/**",
  "docs/archive/**",
  "user homes, auth files, provider state, target-repo working trees"
)

$releaseManifestPath = Join-Path $releaseRoot "governed-ai-runtime-$Version-$Channel.manifest.json"
$releaseManifest = @{
  schema_version = "1.0"
  package_id = "governed-ai-runtime"
  version = $Version
  channel = $Channel
  generated_at = (Get-Date).ToUniversalTime().ToString("o")
  distribution_root = ($distRoot -replace '\\', '/')
  archive_name = $archiveName
  archive_path = ($archivePath -replace '\\', '/')
  archive_sha256 = $archiveDigest
  tree_sha256 = $distDigest
  included_paths = @($copiedPaths)
  excluded_paths = $excludedPaths
  install_entrypoint = "install.ps1"
  portable_entrypoint = "run.ps1"
  default_install_mode = "Portable"
  migration_boundary = "Repo sources and governed runtime contracts travel; machine-local runtime state, credentials, provider settings, and target-repo absolute paths are recreated on the new host."
  new_machine_first_run = @(
    ".\install.ps1 -Mode Portable",
    ".\run.ps1 readiness -OpenUi",
    ".\run.ps1 targets"
  )
}
$releaseManifest | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 -Path $releaseManifestPath

$packageScriptRef = "scripts/package-runtime.ps1"
$packageScriptPath = Join-Path $root $packageScriptRef
$provenancePath = Join-Path $releaseRoot "governed-ai-runtime-$Version-$Channel.provenance.json"
$provenance = @{
  schema_version = "1.0"
  attestation_id = "public-usable-release-$Version-$Channel"
  subject_type = "release_archive"
  subject_ref = ($archivePath -replace '\\', '/')
  subject_digest = $archiveDigest
  predicate_type = "local-release-package"
  producer = "scripts/package-runtime.ps1"
  generated_at = (Get-Date).ToUniversalTime().ToString("o")
  materials = @(
    @{
      uri = $packageScriptRef
      version_or_digest = Get-FileSha256 -Path $packageScriptPath
    },
    @{
      uri = "rules/manifest.json"
      version_or_digest = Get-FileSha256 -Path (Join-Path $root "rules/manifest.json")
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
  statement_ref = "docs/product/public-usable-release-criteria.md"
  rollback_ref = "Delete the generated .runtime/dist/public-usable-release staging tree and the matching release files for $archiveName under .runtime/dist/releases."
  build_ref = "scripts/package-runtime.ps1"
  source_ref = "git worktree"
  generator_version = "package-runtime.ps1@2"
  output_digest = $archiveDigest
  tree_digest = $distDigest
  control_pack_ref = "schemas/control-packs/minimum-governance-kernel.control-pack.json"
  notes = "Local portable release provenance; archive is unsigned and excludes machine-local state, credentials, provider settings, and historical evidence."
}
$provenance | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 -Path $provenancePath

$payload = @{
  distribution_root = ($distRoot -replace '\\', '/')
  release_root = ($releaseRoot -replace '\\', '/')
  included_paths = @($copiedPaths)
  excluded_paths = $excludedPaths
  release_zip_path = ($archivePath -replace '\\', '/')
  release_manifest_path = ($releaseManifestPath -replace '\\', '/')
  release_sha256_path = ($sha256Path -replace '\\', '/')
  release_sha256 = $archiveDigest
  provenance_path = ($provenancePath -replace '\\', '/')
  provenance = @{
    attestation_id = $provenance.attestation_id
    subject_digest = $provenance.subject_digest
    verification_status = $provenance.verification_status
    rollback_ref = $provenance.rollback_ref
  }
}

$payload | ConvertTo-Json -Depth 8
