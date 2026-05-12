[CmdletBinding(PositionalBinding = $false)]
param(
    [ValidateSet('cli', 'exec', 'app', 'resume')]
    [string] $Surface = 'cli',

    [string] $Profile = '',
    [switch] $UseCockpitCurrentAccount,
    [string] $CockpitAccountId = '',
    [switch] $RestartExistingCodexApp,

    [Parameter(Position = 0, ValueFromRemainingArguments = $true)]
    [string[]] $Prompt
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$reason = 'Start-CodexShared.ps1 is deprecated and blocked. This project must not project Cockpit auth, rewrite Codex config, stop/restart Codex App, or wrap Codex CLI/App startup. Use the official codex command directly, or use Cockpit Tools native controls when intentionally switching accounts.'

[pscustomobject]@{
    status = 'deprecated'
    changed = $false
    surface = $Surface
    profile = $Profile
    use_cockpit_current_account = [bool]$UseCockpitCurrentAccount
    cockpit_account_id = $CockpitAccountId
    restart_existing_codex_app = [bool]$RestartExistingCodexApp
    reason = $reason
} | ConvertTo-Json -Depth 4

exit 2
