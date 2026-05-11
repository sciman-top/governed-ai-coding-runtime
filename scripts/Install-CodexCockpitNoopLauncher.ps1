param(
    [string]$CockpitHome = "$env:USERPROFILE\.antigravity_cockpit",
    [string]$LauncherPath = "$env:USERPROFILE\.local\bin\codex-cockpit-noop-launcher.exe"
)

$ErrorActionPreference = 'Stop'

function Backup-File {
    param([Parameter(Mandatory = $true)][string]$Path, [Parameter(Mandatory = $true)][string]$Suffix)
    if (-not (Test-Path -LiteralPath $Path)) {
        return $null
    }
    $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $backupPath = "$Path.$Suffix.$timestamp.bak"
    Copy-Item -LiteralPath $Path -Destination $backupPath -Force
    return $backupPath
}

function Find-CSharpCompiler {
    $candidates = @(
        "$env:WINDIR\Microsoft.NET\Framework64\v4.0.30319\csc.exe",
        "$env:WINDIR\Microsoft.NET\Framework\v4.0.30319\csc.exe"
    )
    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate) {
            return $candidate
        }
    }
    $cmd = Get-Command csc.exe -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }
    throw 'csc.exe not found; cannot build no-op launcher.'
}

$launcherFullPath = [System.IO.Path]::GetFullPath($LauncherPath)
$launcherDir = Split-Path -Parent $launcherFullPath
New-Item -ItemType Directory -Path $launcherDir -Force | Out-Null

$sourcePath = Join-Path $env:TEMP 'codex-cockpit-noop-launcher.cs'
$source = @'
using System;

namespace CodexCockpitNoopLauncher
{
    internal static class Program
    {
        [STAThread]
        private static void Main(string[] args)
        {
            // Intentionally empty: Cockpit Tools may invoke this after a Codex
            // account switch, but the real Codex App must stay untouched.
        }
    }
}
'@
Set-Content -LiteralPath $sourcePath -Value $source -Encoding UTF8

$compiler = Find-CSharpCompiler
& $compiler /nologo /target:winexe "/out:$launcherFullPath" $sourcePath | Out-String | Write-Verbose
if ($LASTEXITCODE -ne 0) {
    throw "Failed to build no-op launcher with $compiler"
}

$configPath = Join-Path $CockpitHome 'config.json'
if (-not (Test-Path -LiteralPath $configPath)) {
    throw "Cockpit config not found: $configPath"
}

$backupPath = Backup-File -Path $configPath -Suffix 'codex_noop_launcher'
$config = Get-Content -LiteralPath $configPath -Raw | ConvertFrom-Json
$config.codex_app_path = $launcherFullPath
$config.codex_specified_app_path = ''
$config.codex_launch_on_switch = $false
$config.codex_restart_specified_app_on_switch = $false
$config.antigravity_dual_switch_no_restart_enabled = $true
$config | ConvertTo-Json -Depth 100 | Set-Content -LiteralPath $configPath -Encoding UTF8

[pscustomobject]@{
    status = 'ok'
    launcher_path = $launcherFullPath
    compiler = $compiler
    cockpit_config = $configPath
    backup_path = $backupPath
    codex_app_path = $config.codex_app_path
    codex_launch_on_switch = $config.codex_launch_on_switch
    codex_restart_specified_app_on_switch = $config.codex_restart_specified_app_on_switch
    antigravity_dual_switch_no_restart_enabled = $config.antigravity_dual_switch_no_restart_enabled
} | ConvertTo-Json -Depth 10
