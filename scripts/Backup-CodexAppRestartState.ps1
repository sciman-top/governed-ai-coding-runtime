[CmdletBinding()]
param(
    [string] $CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }),

    [string] $CockpitHome = $(Join-Path $HOME '.antigravity_cockpit'),

    [string] $BackupRoot,

    [switch] $Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-ExistingDirectory {
    param([string] $Path, [string] $Name)
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        throw "$Name does not exist: $Path"
    }
    return (Resolve-Path -LiteralPath $Path).Path
}

function Copy-BackupFile {
    param([string] $Source, [string] $RelativePath, [string] $TargetPath)
    if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
        return
    }

    $destination = Join-Path $script:BackupDir $RelativePath
    $destinationParent = Split-Path -Parent $destination
    New-Item -ItemType Directory -Force -Path $destinationParent | Out-Null
    Copy-Item -LiteralPath $Source -Destination $destination -Force

    $script:Items.Add([pscustomobject]@{
        kind = 'file'
        source = $Source
        target = $TargetPath
        relative_path = $RelativePath
        sha256 = (Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLowerInvariant()
    }) | Out-Null
}

function Copy-BackupDirectory {
    param([string] $Source, [string] $RelativePath, [string] $TargetPath)
    if (-not (Test-Path -LiteralPath $Source -PathType Container)) {
        return
    }

    $destination = Join-Path $script:BackupDir $RelativePath
    New-Item -ItemType Directory -Force -Path $destination | Out-Null
    Get-ChildItem -LiteralPath $Source -Force | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $destination -Recurse -Force
    }

    $script:Items.Add([pscustomobject]@{
        kind = 'directory'
        source = $Source
        target = $TargetPath
        relative_path = $RelativePath
    }) | Out-Null
}

$codexHomePath = Resolve-ExistingDirectory -Path $CodexHome -Name 'Codex home'
$cockpitHomePath = Resolve-ExistingDirectory -Path $CockpitHome -Name 'Cockpit home'

if ([string]::IsNullOrWhiteSpace($BackupRoot)) {
    $BackupRoot = Join-Path (Join-Path $codexHomePath 'backups') 'codex-app-restart-guard'
}

New-Item -ItemType Directory -Force -Path $BackupRoot | Out-Null
$backupRootPath = (Resolve-Path -LiteralPath $BackupRoot).Path
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$script:BackupDir = Join-Path $backupRootPath $timestamp
New-Item -ItemType Directory -Force -Path $script:BackupDir | Out-Null
$script:Items = [System.Collections.Generic.List[object]]::new()

$codexFiles = @(
    'config.toml',
    'auth.json',
    'state_5.sqlite',
    'state_5.sqlite-wal',
    'state_5.sqlite-shm'
)
foreach ($fileName in $codexFiles) {
    $path = Join-Path $codexHomePath $fileName
    Copy-BackupFile -Source $path -RelativePath (Join-Path 'codex' $fileName) -TargetPath $path
}

$cockpitFiles = @(
    'codex_accounts.json',
    'codex_instances.json',
    'codex_model_providers.json',
    'settings.json'
)
foreach ($fileName in $cockpitFiles) {
    $path = Join-Path $cockpitHomePath $fileName
    Copy-BackupFile -Source $path -RelativePath (Join-Path 'cockpit' $fileName) -TargetPath $path
}

$cockpitAccountsPath = Join-Path $cockpitHomePath 'codex_accounts'
Copy-BackupDirectory -Source $cockpitAccountsPath -RelativePath (Join-Path 'cockpit' 'codex_accounts') -TargetPath $cockpitAccountsPath

$processSnapshotPath = Join-Path $script:BackupDir 'process-snapshot.json'
try {
    $codexAppProcessName = 'Codex' + '.exe'
    $codexCliProcessName = 'codex' + '.exe'
    Get-CimInstance Win32_Process |
        Where-Object { $_.Name -in @($codexAppProcessName, $codexCliProcessName, 'cockpit-tools.exe') } |
        Select-Object Name, ProcessId, ParentProcessId, CreationDate, CommandLine |
        ConvertTo-Json -Depth 4 |
        Set-Content -LiteralPath $processSnapshotPath -Encoding UTF8
}
catch {
    [pscustomobject]@{ error = $_.Exception.Message } |
        ConvertTo-Json -Depth 3 |
        Set-Content -LiteralPath $processSnapshotPath -Encoding UTF8
}

$restoreScript = Join-Path $PSScriptRoot 'Restore-CodexAppRestartState.ps1'
$manifest = [ordered]@{
    schema_version = 1
    created_at = (Get-Date).ToString('o')
    backup_dir = $script:BackupDir
    codex_home = $codexHomePath
    cockpit_home = $cockpitHomePath
    process_snapshot = $processSnapshotPath
    restore_command = "pwsh -NoProfile -ExecutionPolicy Bypass -File `"$restoreScript`" -BackupDir `"$script:BackupDir`""
    latest_restore_command = "pwsh -NoProfile -ExecutionPolicy Bypass -File `"$restoreScript`" -Latest"
    items = @($script:Items)
}

$manifestPath = Join-Path $script:BackupDir 'manifest.json'
$manifest | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

if ($Json) {
    $manifest | ConvertTo-Json -Depth 8
}
else {
    "BackupDir=$script:BackupDir"
    "Manifest=$manifestPath"
    "RestoreCommand=$($manifest.restore_command)"
    "LatestRestoreCommand=$($manifest.latest_restore_command)"
}
