param(
  [ValidateSet("All", "Contract", "Docs", "Runtime", "Scripts")]
  [string]$Check = "All"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-CheckOk {
  param([string]$Name)
  Write-Host "OK $Name"
}

function Invoke-SchemaJsonParse {
  Get-ChildItem schemas/jsonschema/*.json | Sort-Object Name | ForEach-Object {
    Get-Content -Raw $_.FullName | ConvertFrom-Json > $null
  }

  Write-CheckOk "schema-json-parse"
}

function Invoke-SchemaExampleValidation {
  $schemaMap = @{}
  Get-ChildItem schemas/jsonschema/*.json | ForEach-Object {
    $schemaMap[$_.BaseName -replace '\.schema$', ''] = $_.FullName
  }

  Get-ChildItem -Recurse -File schemas/examples -Filter *.json | Sort-Object FullName | ForEach-Object {
    $dir = Split-Path $_.DirectoryName -Leaf
    $schemaPath = $schemaMap[$dir]
    if (-not $schemaPath) {
      throw "No matching schema for example directory: $dir"
    }

    $ok = Test-Json -Json (Get-Content -Raw $_.FullName) -SchemaFile $schemaPath
    if (-not $ok) {
      throw "Example failed schema validation: $($_.FullName)"
    }
  }

  Write-CheckOk "schema-example-validation"
}

function Invoke-SchemaCatalogPairing {
  $catalog = Get-Content -Raw schemas/catalog/schema-catalog.yaml
  $paths = [regex]::Matches($catalog, '^\s+path:\s+(.+)$', 'Multiline') | ForEach-Object { $_.Groups[1].Value.Trim() }
  $specs = [regex]::Matches($catalog, '^\s+source_spec:\s+(.+)$', 'Multiline') | ForEach-Object { $_.Groups[1].Value.Trim() }

  foreach ($path in ($paths + $specs)) {
    if (-not (Test-Path $path)) {
      throw "Schema catalog references missing file: $path"
    }
  }

  $knownSchemas = $paths | ForEach-Object { Split-Path $_ -Leaf }
  $uncataloguedSchemas = Get-ChildItem schemas/jsonschema/*.json | Where-Object { $knownSchemas -notcontains $_.Name }
  if ($uncataloguedSchemas) {
    throw "Uncatalogued schema files: $($uncataloguedSchemas.Name -join ', ')"
  }

  $knownSpecs = $specs | ForEach-Object { Split-Path $_ -Leaf }
  $uncataloguedSpecs = Get-ChildItem docs/specs/*.md | Where-Object {
    $_.Name -ne 'README.md' -and $knownSpecs -notcontains $_.Name
  }
  if ($uncataloguedSpecs) {
    throw "Uncatalogued spec files: $($uncataloguedSpecs.Name -join ', ')"
  }

  Write-CheckOk "schema-catalog-pairing"
}

function Invoke-PowerShellParse {
  Get-ChildItem scripts -Recurse -File -Filter *.ps1 | Sort-Object FullName | ForEach-Object {
    $tokens = $null
    $errors = $null
    [void][System.Management.Automation.Language.Parser]::ParseFile($_.FullName, [ref]$tokens, [ref]$errors)
    if ($errors.Count -gt 0) {
      $errors | Format-List *
      throw "PowerShell parser errors found in $($_.FullName)"
    }
  }

  Write-CheckOk "powershell-parse"
}

function Invoke-ActiveMarkdownLinkCheck {
  $files = Get-ChildItem -Recurse -File -Filter *.md | Where-Object {
    $_.FullName -notmatch '[\\/]+docs[\\/]+change-evidence[\\/]'
  }

  $broken = [System.Collections.Generic.List[string]]::new()
  foreach ($file in $files) {
    $text = Get-Content -Raw $file.FullName
    $matches = [regex]::Matches($text, '\[[^\]]+\]\(([^)]+)\)')
    foreach ($match in $matches) {
      $target = $match.Groups[1].Value.Trim()
      if ($target -match '^(https?:|mailto:|#)') { continue }
      if ($target -match '^<.*>$') {
        $target = $target.Trim('<', '>')
      }

      $path = ($target -split '#')[0]
      if ([string]::IsNullOrWhiteSpace($path)) { continue }

      $resolved = Join-Path $file.DirectoryName $path
      if (-not (Test-Path $resolved)) {
        $broken.Add("$($file.FullName): $target")
      }
    }
  }

  if ($broken.Count -gt 0) {
    $broken | ForEach-Object { Write-Error $_ }
    throw "Broken active markdown links found"
  }

  Write-CheckOk "active-markdown-links"
}

function Invoke-BacklogYamlIdCheck {
  $idsBacklog = Select-String -Path docs/backlog/issue-ready-backlog.md -Pattern '^### (GAP-\d+) (.+)$' |
    ForEach-Object { $_.Matches[0].Groups[1].Value }
  $idsYaml = Select-String -Path docs/backlog/issue-seeds.yaml -Pattern '^\s+- id: (GAP-\d+)' |
    ForEach-Object { $_.Matches[0].Groups[1].Value }

  $missingInYaml = $idsBacklog | Where-Object { $idsYaml -notcontains $_ }
  $missingInBacklog = $idsYaml | Where-Object { $idsBacklog -notcontains $_ }

  if ($missingInYaml -or $missingInBacklog) {
    throw "Backlog/YAML ID drift found. Missing in YAML: $($missingInYaml -join ', '); missing in backlog: $($missingInBacklog -join ', ')"
  }

  Write-CheckOk "backlog-yaml-ids"
}

function Invoke-OldProjectNameScan {
  $oldSlug = @('governed', 'agent', 'platform') -join '-'
  $oldTitle = @('Governed', 'Agent', 'Platform') -join ' '
  $oldPlain = @('governed', 'agent', 'platform') -join ' '
  $pattern = "$([regex]::Escape($oldSlug))|$([regex]::Escape($oldTitle))|$([regex]::Escape($oldPlain))"

  $searchFiles = @(
    (Get-Item README.md),
    (Get-ChildItem docs, schemas, scripts -Recurse -File | Where-Object {
      $_.Extension -in @('.md', '.json', '.ps1')
    })
  )

  $matches = Select-String -Path ($searchFiles | ForEach-Object { $_.FullName }) -Pattern $pattern
  $unexpected = $matches | Where-Object {
    $_.Path -notmatch '[\\/]+docs[\\/]+change-evidence[\\/]' -and
    $_.Path -notmatch '[\\/]+docs[\\/]+adrs[\\/]0004-' -and
    -not ($_.Path -match 'README\.md$' -and $_.Line -match 'Historical evidence may still mention')
  }

  if ($unexpected) {
    $unexpected | ForEach-Object { Write-Error "$($_.Path):$($_.LineNumber):$($_.Line)" }
    throw "Unexpected old project name references found"
  }

  Write-CheckOk "old-project-name-historical-only"
}

function Invoke-ContractChecks {
  Invoke-SchemaJsonParse
  Invoke-SchemaExampleValidation
  Invoke-SchemaCatalogPairing
}

function Invoke-DocsChecks {
  Invoke-ActiveMarkdownLinkCheck
  Invoke-BacklogYamlIdCheck
  Invoke-OldProjectNameScan
}

function Invoke-ScriptChecks {
  Invoke-PowerShellParse
}

function Invoke-RuntimeChecks {
  $python = Get-Command python -ErrorAction SilentlyContinue
  if (-not $python) {
    $python = Get-Command python3 -ErrorAction SilentlyContinue
  }
  if (-not $python) {
    throw "Required command not found: python or python3"
  }

  & $python.Source -m unittest discover -s tests/runtime -p "test_*.py"
  if ($LASTEXITCODE -ne 0) {
    throw "Runtime unit tests failed"
  }

  Write-CheckOk "runtime-unittest"
}

switch ($Check) {
  "Contract" { Invoke-ContractChecks }
  "Docs" { Invoke-DocsChecks }
  "Runtime" { Invoke-RuntimeChecks }
  "Scripts" { Invoke-ScriptChecks }
  "All" {
    Invoke-RuntimeChecks
    Invoke-ContractChecks
    Invoke-DocsChecks
    Invoke-ScriptChecks
  }
}
