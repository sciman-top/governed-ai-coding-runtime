[CmdletBinding()]
param(
    [string[]] $Record,

    [string] $SnapshotRoot,

    [string] $Out,

    [switch] $Json
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
if ([string]::IsNullOrWhiteSpace($SnapshotRoot)) {
    $SnapshotRoot = Join-Path $repoRoot 'docs/change-evidence/codex-cockpit-snapshots'
}

if (-not $Record -or $Record.Count -eq 0) {
    if (-not (Test-Path -LiteralPath $SnapshotRoot -PathType Container)) {
        throw "No records were passed and snapshot root does not exist: $SnapshotRoot"
    }
    $Record = @(
        Get-ChildItem -LiteralPath $SnapshotRoot -Recurse -Filter 'record.json' |
            Sort-Object FullName |
            Select-Object -ExpandProperty FullName
    )
}
elseif ($Record.Count -eq 1 -and $Record[0].Contains(',')) {
    $Record = @($Record[0].Split(',') | ForEach-Object { $_.Trim() } | Where-Object { $_ })
}

if ($Record.Count -lt 2) {
    throw "At least two record JSON files are required for comparison."
}

$resolvedRecords = @($Record | ForEach-Object { (Resolve-Path -LiteralPath $_).Path })
$traceScript = Join-Path $PSScriptRoot 'codex-cockpit-switch-trace.py'

if ([string]::IsNullOrWhiteSpace($Out)) {
    $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $Out = Join-Path $SnapshotRoot "compare-$timestamp.json"
}

$arguments = @(
    $traceScript,
    '--compare'
) + $resolvedRecords + @(
    '--out', $Out
)

& python @arguments
if ($LASTEXITCODE -ne 0) {
    throw "codex-cockpit switch record comparison failed with exit code $LASTEXITCODE"
}

$comparison = Get-Content -LiteralPath $Out -Raw -Encoding UTF8 | ConvertFrom-Json

if ($Json) {
    $comparison | ConvertTo-Json -Depth 8
}
else {
    Write-Host "Saved Codex/Cockpit switch comparison:"
    Write-Host "  path: $Out"
    Write-Host "  records: $($comparison.record_count)"
    foreach ($transition in $comparison.transitions) {
        Write-Host ""
        Write-Host "From: $($transition.from_label) -> To: $($transition.to_label)"
        if ($transition.field_changes.Count -eq 0 -and $transition.file_changes.Count -eq 0) {
            Write-Host "  no semantic or tracked-file changes"
            continue
        }
        if ($transition.field_changes.Count -gt 0) {
            Write-Host "  field changes:"
            foreach ($change in $transition.field_changes) {
                Write-Host "    $($change.field): $($change.before) -> $($change.after)"
            }
        }
        if ($transition.file_changes.Count -gt 0) {
            Write-Host "  file changes:"
            foreach ($change in $transition.file_changes) {
                Write-Host "    $($change.file): $($change.before_mtime) -> $($change.after_mtime)"
            }
        }
    }
}
