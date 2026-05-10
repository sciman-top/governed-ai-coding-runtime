[CmdletBinding()]
param(
    [string] $BackupDir,

    [switch] $Latest,

    [string] $BackupRoot,

    [switch] $Force,

    [switch] $Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-DefaultCodexHome {
    if ($env:CODEX_HOME) {
        return $env:CODEX_HOME
    }
    return (Join-Path $HOME '.codex')
}

function Resolve-BackupRoot {
    param([string] $Root)
    if ([string]::IsNullOrWhiteSpace($Root)) {
        $Root = Join-Path (Join-Path (Get-DefaultCodexHome) 'backups') 'codex-app-restart-guard'
    }
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) {
        throw "Backup root does not exist: $Root"
    }
    return (Resolve-Path -LiteralPath $Root).Path
}

function Resolve-LatestBackup {
    param([string] $Root)
    $candidate = Get-ChildItem -LiteralPath $Root -Directory |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'manifest.json') -PathType Leaf } |
        Sort-Object Name -Descending |
        Select-Object -First 1
    if (-not $candidate) {
        throw "No restart guard backups found under: $Root"
    }
    return $candidate.FullName
}

function Test-WithinRoot {
    param([string] $Path, [string] $Root)
    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $fullRoot = [System.IO.Path]::GetFullPath($Root).TrimEnd([System.IO.Path]::DirectorySeparatorChar, [System.IO.Path]::AltDirectorySeparatorChar)
    return ($fullPath.Equals($fullRoot, [System.StringComparison]::OrdinalIgnoreCase) -or
        $fullPath.StartsWith($fullRoot + [System.IO.Path]::DirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase) -or
        $fullPath.StartsWith($fullRoot + [System.IO.Path]::AltDirectorySeparatorChar, [System.StringComparison]::OrdinalIgnoreCase))
}

function Assert-AllowedTarget {
    param([string] $Target, [string[]] $AllowedRoots)
    foreach ($root in $AllowedRoots) {
        if (Test-WithinRoot -Path $Target -Root $root) {
            return
        }
    }
    throw "Refusing to restore outside allowed roots: $Target"
}

function Copy-CurrentToPreimage {
    param([string] $Path, [string] $PreimageRoot, [string[]] $AllowedRoots)
    Assert-AllowedTarget -Target $Path -AllowedRoots $AllowedRoots
    if (-not (Test-Path -LiteralPath $Path)) {
        return
    }

    $root = $AllowedRoots | Where-Object { Test-WithinRoot -Path $Path -Root $_ } | Select-Object -First 1
    $relative = [System.IO.Path]::GetRelativePath($root, [System.IO.Path]::GetFullPath($Path))
    $rootName = if ($root -like '*.codex') { 'codex' } else { 'cockpit' }
    $destination = Join-Path (Join-Path $PreimageRoot $rootName) $relative
    $parent = Split-Path -Parent $destination
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
    Copy-Item -LiteralPath $Path -Destination $destination -Recurse -Force
}

function Get-CodexAppProcesses {
    $codexAppProcessName = 'Codex' + '.exe'
    $codexCliProcessName = 'codex' + '.exe'
    Get-CimInstance Win32_Process |
        Where-Object {
            $_.Name -eq $codexAppProcessName -or
            ($_.Name -eq $codexCliProcessName -and $_.CommandLine -match '(^| )app-server($| )')
        } |
        Select-Object Name, ProcessId, ParentProcessId, CreationDate, CommandLine
}

$backupRootPath = Resolve-BackupRoot -Root $BackupRoot
if ([string]::IsNullOrWhiteSpace($BackupDir)) {
    if (-not $Latest) {
        throw 'Specify -BackupDir <path> or -Latest.'
    }
    $BackupDir = Resolve-LatestBackup -Root $backupRootPath
}
elseif (-not (Test-Path -LiteralPath $BackupDir -PathType Container)) {
    throw "Backup directory does not exist: $BackupDir"
}

$backupPath = (Resolve-Path -LiteralPath $BackupDir).Path
$manifestPath = Join-Path $backupPath 'manifest.json'
if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    throw "Backup manifest does not exist: $manifestPath"
}

$manifest = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
if ([int] $manifest.schema_version -ne 1) {
    throw "Unsupported manifest schema_version: $($manifest.schema_version)"
}

$runningApp = @(Get-CodexAppProcesses)
if ($runningApp.Count -gt 0 -and -not $Force) {
    $pids = ($runningApp | ForEach-Object { "$($_.Name):$($_.ProcessId)" }) -join ', '
    throw "Codex App/app-server is still running ($pids). Close it first, then rerun this restore command. Use -Force only if you intentionally accept overwriting files while it is running."
}

$codexHome = [string] $manifest.codex_home
$cockpitHome = [string] $manifest.cockpit_home
$allowedRoots = @($codexHome, $cockpitHome)

$preimageRoot = Join-Path $backupRootPath ("restore-preimage-{0}" -f (Get-Date -Format 'yyyyMMdd-HHmmss'))
New-Item -ItemType Directory -Force -Path $preimageRoot | Out-Null

foreach ($item in $manifest.items) {
    Copy-CurrentToPreimage -Path ([string] $item.target) -PreimageRoot $preimageRoot -AllowedRoots $allowedRoots
}

$dbTarget = Join-Path $codexHome 'state_5.sqlite'
$dbIncluded = @($manifest.items | Where-Object { [string] $_.target -eq $dbTarget }).Count -gt 0
if ($dbIncluded) {
    foreach ($suffix in @('-wal', '-shm')) {
        $sidecar = "$dbTarget$suffix"
        $sidecarIncluded = @($manifest.items | Where-Object { [string] $_.target -eq $sidecar }).Count -gt 0
        if ((-not $sidecarIncluded) -and (Test-Path -LiteralPath $sidecar -PathType Leaf)) {
            Assert-AllowedTarget -Target $sidecar -AllowedRoots $allowedRoots
            Copy-CurrentToPreimage -Path $sidecar -PreimageRoot $preimageRoot -AllowedRoots $allowedRoots
            $staleDir = Join-Path $preimageRoot 'stale-sqlite-sidecars'
            New-Item -ItemType Directory -Force -Path $staleDir | Out-Null
            Copy-Item -LiteralPath $sidecar -Destination (Join-Path $staleDir ([System.IO.Path]::GetFileName($sidecar))) -Force
            Rename-Item -LiteralPath $sidecar -NewName ("{0}.restore-stale-{1}" -f ([System.IO.Path]::GetFileName($sidecar), (Get-Date -Format 'yyyyMMdd-HHmmss'))) -Force
        }
    }
}

foreach ($item in $manifest.items) {
    $relativePath = [string] $item.relative_path
    $source = Join-Path $backupPath $relativePath
    $target = [string] $item.target
    Assert-AllowedTarget -Target $target -AllowedRoots $allowedRoots

    if ([string] $item.kind -eq 'file') {
        if (-not (Test-Path -LiteralPath $source -PathType Leaf)) {
            throw "Backup file is missing: $source"
        }
        $targetParent = Split-Path -Parent $target
        New-Item -ItemType Directory -Force -Path $targetParent | Out-Null
        Copy-Item -LiteralPath $source -Destination $target -Force
    }
    elseif ([string] $item.kind -eq 'directory') {
        if (-not (Test-Path -LiteralPath $source -PathType Container)) {
            throw "Backup directory is missing: $source"
        }
        New-Item -ItemType Directory -Force -Path $target | Out-Null
        Get-ChildItem -LiteralPath $source -Force | ForEach-Object {
            Copy-Item -LiteralPath $_.FullName -Destination $target -Recurse -Force
        }
    }
    else {
        throw "Unsupported backup item kind: $($item.kind)"
    }
}

$result = [ordered]@{
    restored_from = $backupPath
    pre_restore_backup = $preimageRoot
    restored_at = (Get-Date).ToString('o')
}

if ($Json) {
    $result | ConvertTo-Json -Depth 4
}
else {
    "RestoredFrom=$backupPath"
    "PreRestoreBackup=$preimageRoot"
}
