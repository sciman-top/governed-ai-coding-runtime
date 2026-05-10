[CmdletBinding()]
param(
    [string] $Label = 'manual',

    [string] $CodexHome = $(if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME '.codex' }),

    [string] $CockpitHome = $(Join-Path $HOME '.antigravity_cockpit'),

    [string] $OutputRoot,

    [double] $WatchSeconds = 0,

    [switch] $Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-JsonPropertyOrNull {
    param([object] $Object, [string] $Name)
    if ($null -eq $Object) {
        return $null
    }
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) {
        return $null
    }
    return $property.Value
}

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $OutputRoot = Join-Path $repoRoot 'docs/change-evidence/codex-cockpit-snapshots'
}

$safeLabel = ($Label -replace '[^A-Za-z0-9._-]+', '-').Trim('-')
if ([string]::IsNullOrWhiteSpace($safeLabel)) {
    $safeLabel = 'manual'
}

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$recordDir = Join-Path $OutputRoot "$timestamp-$safeLabel"
New-Item -ItemType Directory -Force -Path $recordDir | Out-Null
$recordPath = Join-Path $recordDir 'record.json'

$traceScript = Join-Path $PSScriptRoot 'codex-cockpit-switch-trace.py'
$arguments = @(
    $traceScript,
    '--codex-home', $CodexHome,
    '--cockpit-home', $CockpitHome,
    '--label', $Label,
    '--out', $recordPath
)
if ($WatchSeconds -gt 0) {
    $arguments += @('--watch-seconds', ([string]::Format([Globalization.CultureInfo]::InvariantCulture, '{0}', $WatchSeconds)))
}

& python @arguments
if ($LASTEXITCODE -ne 0) {
    throw "codex-cockpit switch record capture failed with exit code $LASTEXITCODE"
}

$payload = Get-Content -LiteralPath $recordPath -Raw -Encoding UTF8 | ConvertFrom-Json
$after = $payload.after
$summary = [ordered]@{
    label = $Label
    record_path = $recordPath
    timestamp = $after.timestamp
    cockpit_current_account_id = $after.cockpit.current_account_id
    codex_launch_on_switch = $after.cockpit.launch_flags.codex_launch_on_switch
    codex_restart_specified_app_on_switch = $after.cockpit.launch_flags.codex_restart_specified_app_on_switch
    codex_specified_app_path = $after.cockpit.launch_flags.codex_specified_app_path
    cockpit_bind_account_id = $after.cockpit.default_instance.bindAccountId
    cockpit_follow_local_account = $after.cockpit.default_instance.followLocalAccount
    codex_forced_login_method = $after.codex.config.forced_login_method
    codex_model_provider = $after.codex.config.model_provider
    codex_openai_base_url = Get-JsonPropertyOrNull -Object $after.codex.config -Name 'openai_base_url'
    codex_auth_mode = $after.codex.auth.auth_mode
    codex_auth_has_api_key = $after.codex.auth.has_openai_api_key
    codex_auth_has_tokens = $after.codex.auth.has_tokens
    changed_files_within_watch = @($payload.changed_files | ForEach-Object { $_.file })
}

$summaryPath = Join-Path $recordDir 'summary.json'
$summary | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $summaryPath -Encoding UTF8

if ($Json) {
    $summary | ConvertTo-Json -Depth 5
}
else {
    Write-Host "Saved Codex/Cockpit switch record:"
    Write-Host "  label: $Label"
    Write-Host "  path : $recordPath"
    Write-Host "  account: $($summary.cockpit_current_account_id)"
    Write-Host "  forced_login_method: $($summary.codex_forced_login_method)"
    Write-Host "  auth_mode: $($summary.codex_auth_mode)"
    Write-Host "  model_provider: $($summary.codex_model_provider)"
    Write-Host "  openai_base_url: $($summary.codex_openai_base_url)"
    Write-Host "  cockpit launch_on_switch: $($summary.codex_launch_on_switch)"
    Write-Host "  cockpit bindAccountId: $($summary.cockpit_bind_account_id)"
}
