[CmdletBinding()]
param(
    [ValidateSet('cli', 'exec', 'app')]
    [string] $Surface = 'cli',

    [string] $Profile = 'shared-chatgpt',

    [string] $AuthProfile,

    [string] $ApiKeyEnv,

    [string] $BaseUrl = $env:OPENAI_BASE_URL,

    [string] $ModelProvider,

    [string] $CodexHome = (Join-Path $HOME '.codex'),

    [switch] $UseCcSwitchCurrentProvider,

    [string] $CcSwitchDbPath = (Join-Path $HOME '.cc-switch\cc-switch.db'),

    [string] $Workdir,

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $Prompt
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function ConvertTo-TomlString {
    param([string] $Value)
    return '"' + ($Value -replace '\\', '\\' -replace '"', '\"') + '"'
}

$resolvedHome = (Resolve-Path -LiteralPath $CodexHome).Path
$env:CODEX_HOME = $resolvedHome

if (-not [string]::IsNullOrWhiteSpace($AuthProfile)) {
    $switcher = Join-Path $resolvedHome 'scripts\Switch-CodexAccount.ps1'
    if (-not (Test-Path -LiteralPath $switcher -PathType Leaf)) {
        throw "Missing Codex account switcher: $switcher"
    }
    & $switcher switch $AuthProfile -CodexHome $resolvedHome -NoLoginStatus
}

if (-not [string]::IsNullOrWhiteSpace($ApiKeyEnv)) {
    $apiKey = [Environment]::GetEnvironmentVariable($ApiKeyEnv, 'Process')
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        $apiKey = [Environment]::GetEnvironmentVariable($ApiKeyEnv, 'User')
    }
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        $apiKey = [Environment]::GetEnvironmentVariable($ApiKeyEnv, 'Machine')
    }
    if ([string]::IsNullOrWhiteSpace($apiKey)) {
        throw "API key environment variable is not set: $ApiKeyEnv"
    }
    $env:OPENAI_API_KEY = $apiKey
}

if ($UseCcSwitchCurrentProvider) {
    if (-not (Test-Path -LiteralPath $CcSwitchDbPath -PathType Leaf)) {
        throw "CC Switch database not found: $CcSwitchDbPath"
    }
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        throw 'python command not found; cannot read CC Switch provider state.'
    }
    $providerJson = & $python.Source -c @'
import json, sqlite3, sys
db = sys.argv[1]
con = sqlite3.connect(db)
con.row_factory = sqlite3.Row
row = con.execute("select name, settings_config from providers where app_type='codex' and is_current=1 limit 1").fetchone()
con.close()
if not row:
    print("{}")
    raise SystemExit(0)
payload = json.loads(row["settings_config"] or "{}")
auth = payload.get("auth") if isinstance(payload, dict) else {}
print(json.dumps({"name": row["name"], "openai_api_key": auth.get("OPENAI_API_KEY") if isinstance(auth, dict) else None}))
'@ $CcSwitchDbPath
    $provider = $providerJson | ConvertFrom-Json
    if (-not [string]::IsNullOrWhiteSpace([string]$provider.openai_api_key)) {
        $env:OPENAI_API_KEY = [string]$provider.openai_api_key
    }
    if ([string]::IsNullOrWhiteSpace($Profile)) {
        $Profile = 'shared-current-provider'
    }
}

$codexArgs = @()
if (-not [string]::IsNullOrWhiteSpace($Profile)) {
    $codexArgs += @('--profile', $Profile)
}
if (-not [string]::IsNullOrWhiteSpace($BaseUrl)) {
    $codexArgs += @('-c', ('openai_base_url={0}' -f (ConvertTo-TomlString $BaseUrl)))
}
if (-not [string]::IsNullOrWhiteSpace($ModelProvider)) {
    $codexArgs += @('-c', ('model_provider={0}' -f (ConvertTo-TomlString $ModelProvider)))
}
if ($Surface -ne 'app' -and -not [string]::IsNullOrWhiteSpace($Workdir)) {
    $codexArgs += @('--cd', $Workdir)
}
if ($Surface -eq 'exec') {
    $codexArgs += 'exec'
}
elseif ($Surface -eq 'app') {
    $codexArgs += 'app'
    if (-not [string]::IsNullOrWhiteSpace($Workdir)) {
        $codexArgs += $Workdir
    }
}
if ($Surface -ne 'app' -and $Prompt) {
    $codexArgs += $Prompt
}

Write-Host ("CODEX_HOME={0}" -f $env:CODEX_HOME)
Write-Host ("profile={0}" -f $Profile)
if (-not [string]::IsNullOrWhiteSpace($ApiKeyEnv)) {
    Write-Host ("OPENAI_API_KEY sourced from {0}" -f $ApiKeyEnv)
}
if ($UseCcSwitchCurrentProvider) {
    Write-Host ("OPENAI_API_KEY sourced from current CC Switch provider")
}
if (-not [string]::IsNullOrWhiteSpace($BaseUrl)) {
    Write-Host ("openai_base_url={0}" -f $BaseUrl)
}
if (-not [string]::IsNullOrWhiteSpace($ModelProvider)) {
    Write-Host ("model_provider={0}" -f $ModelProvider)
}
if ($Surface -eq 'app' -and $Prompt) {
    Write-Warning 'Codex app accepts a workspace path, not an initial prompt; trailing prompt arguments were ignored.'
}

& codex @codexArgs
