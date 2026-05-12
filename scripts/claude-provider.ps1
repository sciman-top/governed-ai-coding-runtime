[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('list', 'status', 'continuity', 'install', 'switch', 'delete', 'optimize')]
    [string] $Command = 'status',

    [Parameter(Position = 1)]
    [string] $Name,

    [Alias('dry-run')]
    [switch] $DryRun,
    [switch] $Apply,
    [string] $Provider = 'bigmodel-glm',
    [Alias('cc-switch-db')]
    [string] $CcSwitchDb
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) {
    $PSNativeCommandUseErrorActionPreference = $false
}

$script = Join-Path $PSScriptRoot 'claude-provider.py'
if (-not (Test-Path -LiteralPath $script)) {
    $repoScript = Join-Path (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path 'scripts\claude-provider.py'
    if (Test-Path -LiteralPath $repoScript) {
        $script = $repoScript
    }
}

$arguments = @($script, $Command)
switch ($Command) {
    'status' {
        if (-not [string]::IsNullOrWhiteSpace($CcSwitchDb)) {
            $arguments += @('--cc-switch-db', $CcSwitchDb)
        }
    }
    'switch' {
        if ([string]::IsNullOrWhiteSpace($Name)) {
            throw 'Provider profile name is required for switch.'
        }
        $arguments += $Name
        if ($DryRun) { $arguments += '--dry-run' }
        if (-not [string]::IsNullOrWhiteSpace($CcSwitchDb)) {
            $arguments += @('--cc-switch-db', $CcSwitchDb)
        }
    }
    'delete' {
        if ([string]::IsNullOrWhiteSpace($Name)) {
            throw 'Provider profile name is required for delete.'
        }
        $arguments += $Name
        if ($DryRun) { $arguments += '--dry-run' }
    }
    'optimize' {
        $arguments += @('--provider', $Provider)
        if ($Apply) { $arguments += '--apply' }
    }
}

python @arguments
exit $LASTEXITCODE
