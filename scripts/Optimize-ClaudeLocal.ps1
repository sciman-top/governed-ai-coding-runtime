[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [switch] $Apply,
    [string] $Provider = 'bigmodel-glm',
    [switch] $InstallProviderSwitcher = $true
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$script = Join-Path $PSScriptRoot 'claude-provider.py'
$arguments = @($script, 'optimize', '--provider', $Provider)
if ($Apply) {
    $arguments += '--apply'
}
if (-not $InstallProviderSwitcher) {
    $arguments += '--no-install-switcher'
}

python @arguments
