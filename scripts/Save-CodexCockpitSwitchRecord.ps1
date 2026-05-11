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

function Resolve-DefaultSnapshotRoot {
    $currentRoot = (Get-Location).Path
    if (
        (Test-Path -LiteralPath (Join-Path $currentRoot 'docs/change-evidence') -PathType Container) -and
        (Test-Path -LiteralPath (Join-Path $currentRoot 'scripts') -PathType Container)
    ) {
        return Join-Path $currentRoot 'docs/change-evidence/codex-cockpit-snapshots'
    }

    $scriptRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
    if (Test-Path -LiteralPath (Join-Path $scriptRoot 'docs/change-evidence') -PathType Container) {
        return Join-Path $scriptRoot 'docs/change-evidence/codex-cockpit-snapshots'
    }

    return Join-Path $scriptRoot 'docs/change-evidence/codex-cockpit-snapshots'
}

if ([string]::IsNullOrWhiteSpace($OutputRoot)) {
    $OutputRoot = Resolve-DefaultSnapshotRoot
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
$codexConfig = Get-JsonPropertyOrNull -Object (Get-JsonPropertyOrNull -Object $after -Name 'codex') -Name 'config'
$codexModelProvider = Get-JsonPropertyOrNull -Object $codexConfig -Name 'model_provider'
$codexModelProviders = Get-JsonPropertyOrNull -Object $codexConfig -Name 'model_providers'
$codexActiveProviderInfo = Get-JsonPropertyOrNull -Object $codexModelProviders -Name $codexModelProvider
$codexProfiles = Get-JsonPropertyOrNull -Object $codexConfig -Name 'profiles'
$codexSharedCockpitApiProfile = Get-JsonPropertyOrNull -Object $codexProfiles -Name 'shared-cockpit-api'
$cockpit = Get-JsonPropertyOrNull -Object $after -Name 'cockpit'
$cockpitCurrentAccountSummary = Get-JsonPropertyOrNull -Object $cockpit -Name 'current_account_summary'
$summary = [ordered]@{
    label = $Label
    record_path = $recordPath
    timestamp = Get-JsonPropertyOrNull -Object $after -Name 'timestamp'
    cockpit_current_account_id = Get-JsonPropertyOrNull -Object $cockpit -Name 'current_account_id'
    cockpit_current_account_auth_mode = Get-JsonPropertyOrNull -Object $cockpitCurrentAccountSummary -Name 'auth_mode'
    cockpit_current_account_api_provider_id = Get-JsonPropertyOrNull -Object $cockpitCurrentAccountSummary -Name 'api_provider_id'
    cockpit_current_account_api_provider_name = Get-JsonPropertyOrNull -Object $cockpitCurrentAccountSummary -Name 'api_provider_name'
    cockpit_current_account_base_url = Get-JsonPropertyOrNull -Object $cockpitCurrentAccountSummary -Name 'base_url'
    codex_launch_on_switch = Get-JsonPropertyOrNull -Object (Get-JsonPropertyOrNull -Object $cockpit -Name 'launch_flags') -Name 'codex_launch_on_switch'
    codex_app_path = Get-JsonPropertyOrNull -Object (Get-JsonPropertyOrNull -Object $cockpit -Name 'launch_flags') -Name 'codex_app_path'
    codex_restart_specified_app_on_switch = Get-JsonPropertyOrNull -Object (Get-JsonPropertyOrNull -Object $cockpit -Name 'launch_flags') -Name 'codex_restart_specified_app_on_switch'
    codex_specified_app_path = Get-JsonPropertyOrNull -Object (Get-JsonPropertyOrNull -Object $cockpit -Name 'launch_flags') -Name 'codex_specified_app_path'
    antigravity_dual_switch_no_restart_enabled = Get-JsonPropertyOrNull -Object (Get-JsonPropertyOrNull -Object $cockpit -Name 'launch_flags') -Name 'antigravity_dual_switch_no_restart_enabled'
    cockpit_bind_account_id = Get-JsonPropertyOrNull -Object (Get-JsonPropertyOrNull -Object $cockpit -Name 'default_instance') -Name 'bindAccountId'
    cockpit_follow_local_account = Get-JsonPropertyOrNull -Object (Get-JsonPropertyOrNull -Object $cockpit -Name 'default_instance') -Name 'followLocalAccount'
    cockpit_launch_mode = Get-JsonPropertyOrNull -Object (Get-JsonPropertyOrNull -Object $cockpit -Name 'default_instance') -Name 'launchMode'
    codex_forced_login_method = Get-JsonPropertyOrNull -Object $codexConfig -Name 'forced_login_method'
    codex_model_provider = $codexModelProvider
    codex_openai_base_url = Get-JsonPropertyOrNull -Object $codexConfig -Name 'openai_base_url'
    codex_active_provider_requires_openai_auth = Get-JsonPropertyOrNull -Object $codexActiveProviderInfo -Name 'requires_openai_auth'
    codex_active_provider_supports_websockets = Get-JsonPropertyOrNull -Object $codexActiveProviderInfo -Name 'supports_websockets'
    codex_shared_cockpit_api_model_provider = Get-JsonPropertyOrNull -Object $codexSharedCockpitApiProfile -Name 'model_provider'
    codex_shared_cockpit_api_openai_base_url = Get-JsonPropertyOrNull -Object $codexSharedCockpitApiProfile -Name 'openai_base_url'
    codex_auth_mode = Get-JsonPropertyOrNull -Object (Get-JsonPropertyOrNull -Object (Get-JsonPropertyOrNull -Object $after -Name 'codex') -Name 'auth') -Name 'auth_mode'
    codex_auth_has_api_key = Get-JsonPropertyOrNull -Object (Get-JsonPropertyOrNull -Object (Get-JsonPropertyOrNull -Object $after -Name 'codex') -Name 'auth') -Name 'has_openai_api_key'
    codex_auth_has_tokens = Get-JsonPropertyOrNull -Object (Get-JsonPropertyOrNull -Object (Get-JsonPropertyOrNull -Object $after -Name 'codex') -Name 'auth') -Name 'has_tokens'
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
    Write-Host "  active_provider_requires_openai_auth: $($summary.codex_active_provider_requires_openai_auth)"
    Write-Host "  shared_cockpit_api_model_provider: $($summary.codex_shared_cockpit_api_model_provider)"
    Write-Host "  cockpit launch_on_switch: $($summary.codex_launch_on_switch)"
    Write-Host "  cockpit app_path: $($summary.codex_app_path)"
    Write-Host "  cockpit no_restart: $($summary.antigravity_dual_switch_no_restart_enabled)"
    Write-Host "  cockpit bindAccountId: $($summary.cockpit_bind_account_id)"
    Write-Host "  cockpit launchMode: $($summary.cockpit_launch_mode)"
}
