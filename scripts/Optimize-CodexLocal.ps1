[CmdletBinding()]
param(
    [string] $CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }),
    [string[]] $TrustedRepoRoot = @(),
    [switch] $Apply,
    [switch] $InstallAccountSwitcher,
    [switch] $SkipInteropCheck,
    [string] $CockpitHome = $(Join-Path $HOME '.antigravity_cockpit')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$reason = 'Optimize-CodexLocal.ps1 is deprecated and no longer writes Codex/Cockpit config, auth projection, launcher shortcuts, provider profiles, or startup state. Cockpit Tools and the official Codex CLI own their own login and launch state; use codex-interop-check.py for read-only diagnostics and Disable-CodexProjectInterop.ps1 only for reversible cleanup of old project shims.'

[pscustomobject]@{
    status = 'deprecated'
    changed = $false
    apply_requested = [bool]$Apply
    install_account_switcher_requested = [bool]$InstallAccountSwitcher
    codex_home = $CodexHome
    cockpit_home = $CockpitHome
    trusted_repo_roots = @($TrustedRepoRoot)
    reason = $reason
    diagnostics = 'python scripts/codex-interop-check.py --codex-home <home> --cc-switch-db <db> --cockpit-home <home> --quick-launch'
    cleanup = 'pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/Disable-CodexProjectInterop.ps1 -Apply -DisableProjectShortcuts'
} | ConvertTo-Json -Depth 5

exit 2
