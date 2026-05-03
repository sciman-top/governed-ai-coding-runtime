[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet('list', 'status', 'install', 'switch', 'delete', 'optimize')]
    [string] $Command = 'status',

    [Parameter(Position = 1)]
    [string] $Name,

    [switch] $DryRun,
    [switch] $Apply,
    [string] $Provider = 'bigmodel-glm'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script = Join-Path $PSScriptRoot 'claude-provider.py'
if (-not (Test-Path -LiteralPath $script)) {
    $repoScript = Join-Path (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path 'scripts\claude-provider.py'
    if (Test-Path -LiteralPath $repoScript) {
        $script = $repoScript
    }
}

$arguments = @($script, $Command)
switch ($Command) {
    'switch' {
        if ([string]::IsNullOrWhiteSpace($Name)) {
            throw 'Provider profile name is required for switch.'
        }
        $arguments += $Name
        if ($DryRun) { $arguments += '--dry-run' }
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
