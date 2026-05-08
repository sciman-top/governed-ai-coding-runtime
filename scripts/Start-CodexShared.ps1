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
