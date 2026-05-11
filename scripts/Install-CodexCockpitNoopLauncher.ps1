param()

$ErrorActionPreference = 'Stop'

[pscustomobject]@{
    status = 'deprecated'
    reason = 'No-op Codex launchers are disabled. Cockpit Tools owns Codex App launch-on-switch; use Cockpit settings to enable or disable native launch.'
    changed = $false
} | ConvertTo-Json -Depth 4

exit 2
