param(
  [ValidateSet("All", "Build", "Contract", "Doctor", "Docs", "Runtime", "Scripts")]
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

function Invoke-IssueSeedingRenderCheck {
  $output = & pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll
  if ($LASTEXITCODE -ne 0) {
    throw "Issue seeding render check failed"
  }

  $summary = $output | ConvertFrom-Json
  if ($summary.rendered_tasks -lt 1 -or $summary.rendered_epics -lt 1 -or -not $summary.rendered_initiative) {
    throw "Issue seeding render check returned incomplete summary"
  }

  Write-CheckOk "issue-seeding-render"
}

function Invoke-ActiveMarkdownLinkCheck {
  $files = @()
  $git = Get-Command git -ErrorAction SilentlyContinue
  if ($git -and (Test-Path ".git")) {
    $markdownPaths = & $git.Source -c core.quotepath=false ls-files --cached --others --exclude-standard -- "*.md"
    if ($LASTEXITCODE -ne 0) {
      throw "git ls-files failed while collecting active markdown files"
    }

    $files = @(
      $markdownPaths |
        Where-Object { $_ } |
        ForEach-Object { Get-Item -LiteralPath (Join-Path (Get-Location) $_) } |
        Where-Object { $_.FullName -notmatch '[\\/]+docs[\\/]+change-evidence[\\/]' }
    )
  }
  else {
    $files = @(
      Get-ChildItem -Recurse -File -Filter *.md | Where-Object {
        $_.FullName -notmatch '[\\/]+docs[\\/]+change-evidence[\\/]' -and
        $_.FullName -notmatch '[\\/]+\.git[\\/]' -and
        $_.FullName -notmatch '[\\/]+\.worktrees[\\/]' -and
        $_.FullName -notmatch '[\\/]+\.runtime[\\/]'
      }
    )
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
      $_.Extension -in @('.md', '.json', '.ps1') -and $_.FullName -notmatch '[\\/]+\.runtime[\\/]'
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

function Invoke-HostReplacementClaimBoundaryScan {
  $targetFiles = @(
    "README.md",
    "README.en.md",
    "README.zh-CN.md",
    "docs/quickstart/ai-coding-usage-guide.md",
    "docs/quickstart/ai-coding-usage-guide.zh-CN.md",
    "docs/product/codex-cli-app-integration-guide.md",
    "docs/product/codex-cli-app-integration-guide.zh-CN.md"
  ) | ForEach-Object { Join-Path (Get-Location) $_ } | Where-Object { Test-Path $_ }

  $riskPatterns = @(
    '(?i)\bfully\s+replaces?\b.*\bhost\b',
    '(?i)\breplaces?\b.*\bupstream\b.*\bcoding\b.*\bproducts?\b',
    '(?i)\bhost\s+replacement\s+shell\b',
    '完全替代.{0,20}宿主',
    '替代上游.{0,30}宿主'
  )

  $negationPatterns = @(
    '(?i)\b(not|does not|should not|is not|isn''t|not implemented|not yet|without)\b',
    '不应|不是|并非|未实现|尚未|还没有|不替代|不取代'
  )

  $violations = [System.Collections.Generic.List[string]]::new()
  foreach ($file in $targetFiles) {
    $lineNo = 0
    foreach ($line in (Get-Content $file)) {
      $lineNo += 1
      $hasRisk = $false
      foreach ($pattern in $riskPatterns) {
        if ($line -match $pattern) {
          $hasRisk = $true
          break
        }
      }

      if (-not $hasRisk) {
        continue
      }

      $hasNegation = $false
      foreach ($pattern in $negationPatterns) {
        if ($line -match $pattern) {
          $hasNegation = $true
          break
        }
      }

      if (-not $hasNegation) {
        $violations.Add(("{0}:{1}:{2}" -f $file, $lineNo, $line))
      }
    }
  }

  if ($violations.Count -gt 0) {
    $violations | ForEach-Object { Write-Error $_ }
    throw "Host-replacement over-claim lines found in operator-facing docs"
  }

  Write-CheckOk "host-replacement-claim-boundary"
}

function Invoke-GapEvidenceSloCheck {
  $backlogPath = Join-Path (Get-Location) "docs/backlog/issue-ready-backlog.md"
  $seedPath = Join-Path (Get-Location) "docs/backlog/issue-seeds.yaml"
  $evidenceRoot = Join-Path (Get-Location) "docs/change-evidence"
  if (-not (Test-Path $backlogPath)) {
    throw "Issue-ready backlog not found: $backlogPath"
  }
  if (-not (Test-Path $seedPath)) {
    throw "Issue seeds file not found: $seedPath"
  }
  if (-not (Test-Path $evidenceRoot)) {
    throw "Change evidence directory not found: $evidenceRoot"
  }

  $seedIds = @(
    Select-String -Path $seedPath -Pattern '^\s+- id: (GAP-\d+)' |
      ForEach-Object { $_.Matches[0].Groups[1].Value } |
      Where-Object { $_ -match '^GAP-0(6[9]|7\d)$' }
  )
  if ($seedIds.Count -lt 1) {
    throw "No post-closeout GAP ids found in issue seeds"
  }

  $targetGaps = New-Object System.Collections.Generic.HashSet[string]
  $inPostCloseout = $false
  foreach ($line in (Get-Content $backlogPath)) {
    if ($line -match '^## Post-Closeout Optimization Queue') {
      $inPostCloseout = $true
      continue
    }
    if ($inPostCloseout -and $line -match '^## ') {
      break
    }
    if ($inPostCloseout -and $line -match '^### (GAP-\d+) ') {
      $gapId = $Matches[1]
      if ($seedIds -contains $gapId) {
        [void]$targetGaps.Add($gapId)
      }
    }
  }
  if ($targetGaps.Count -lt 1) {
    throw "No post-closeout GAP sections found in backlog"
  }

  $completedGaps = New-Object System.Collections.Generic.HashSet[string]
  $currentGap = $null
  foreach ($line in (Get-Content $backlogPath)) {
    if ($line -match '^### (GAP-\d+) ') {
      $currentGap = $Matches[1]
      continue
    }
    if ($line -match '^### ') {
      $currentGap = $null
      continue
    }
    if ($null -ne $currentGap -and $line -match '^- Status:\s*(.+?)\s*$') {
      if ($Matches[1] -match '^complete\b') {
        [void]$completedGaps.Add($currentGap)
      }
    }
  }

  foreach ($gapId in @($targetGaps)) {
    if (-not $completedGaps.Contains($gapId)) {
      continue
    }

    $gapSlug = $gapId.ToLower()
    $matches = @(
      Get-ChildItem -Path $evidenceRoot -File | Where-Object {
      $_.Name.ToLower().Contains($gapSlug) -and $_.Name.ToLower().Contains("closeout")
      }
    )
    if (-not $matches -or $matches.Count -lt 1) {
      throw "Missing closeout evidence file for completed $gapId"
    }

    $content = Get-Content -Raw $matches[0].FullName
    foreach ($requiredHeader in @("## Verification", "## Rollback")) {
      if ($content -notmatch [regex]::Escape($requiredHeader)) {
        throw "$($matches[0].Name) missing required section: $requiredHeader"
      }
    }

    foreach ($requiredToken in @(
      "scripts/build-runtime.ps1",
      "verify-repo.ps1 -Check Runtime",
      "verify-repo.ps1 -Check Contract",
      "scripts/doctor-runtime.ps1"
    )) {
      if ($content -notmatch [regex]::Escape($requiredToken)) {
        throw "$($matches[0].Name) missing required verification token: $requiredToken"
      }
    }
  }

  Write-CheckOk "gap-evidence-slo"
}

function Invoke-PostCloseoutQueueSyncCheck {
  $seedPath = Join-Path (Get-Location) "docs/backlog/issue-seeds.yaml"
  if (-not (Test-Path $seedPath)) {
    throw "Issue seeds file not found: $seedPath"
  }

  $postCloseoutIds = @(
    Select-String -Path $seedPath -Pattern '^\s+- id: (GAP-\d+)' |
      ForEach-Object { $_.Matches[0].Groups[1].Value } |
      Where-Object { $_ -match '^GAP-0(6[9]|7\d)$' }
  )
  if ($postCloseoutIds.Count -lt 1) {
    throw "No post-closeout GAP ids found in issue seeds"
  }

  $sorted = @($postCloseoutIds | Sort-Object)
  $minGap = $sorted[0]
  $maxGap = $sorted[$sorted.Count - 1]

  $syncTargets = @(
    "docs/backlog/README.md",
    "docs/backlog/full-lifecycle-backlog-seeds.md",
    "docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md"
  ) | ForEach-Object { Join-Path (Get-Location) $_ }

  foreach ($target in $syncTargets) {
    if (-not (Test-Path $target)) {
      throw "Post-closeout sync target missing: $target"
    }
    $matches = @(
      Select-String -Path $target -Pattern ([regex]::Escape($minGap) + '.*' + [regex]::Escape($maxGap) + '.*complete') -CaseSensitive:$false
    )
    if ($matches.Count -lt 1) {
      throw "Post-closeout queue posture drift in $target; expected '$minGap through $maxGap' complete line"
    }
  }

  Write-CheckOk "post-closeout-queue-sync"
}

function Invoke-ClaimDriftSentinelCheck {
  $catalogPath = Join-Path (Get-Location) "docs/product/claim-catalog.json"
  if (-not (Test-Path $catalogPath)) {
    throw "Claim catalog not found: $catalogPath"
  }

  $catalog = Get-Content -Raw $catalogPath | ConvertFrom-Json
  if ($null -eq $catalog.claims -or @($catalog.claims).Count -lt 1) {
    throw "Claim catalog must contain at least one claim entry"
  }

  foreach ($claim in @($catalog.claims)) {
    foreach ($requiredField in @("claim_id", "claim_text", "proof_command", "evidence_link")) {
      if (-not $claim.PSObject.Properties.Name.Contains($requiredField)) {
        throw "Claim catalog entry missing required field: $requiredField"
      }
      $value = [string]$claim.$requiredField
      if ([string]::IsNullOrWhiteSpace($value)) {
        throw "Claim catalog field '$requiredField' must be non-empty"
      }
    }

    $evidencePath = Join-Path (Get-Location) ([string]$claim.evidence_link)
    if (-not (Test-Path $evidencePath)) {
      throw "Claim $($claim.claim_id) references missing evidence file: $($claim.evidence_link)"
    }

    if (-not $claim.PSObject.Properties.Name.Contains("source_refs") -or $null -eq $claim.source_refs -or @($claim.source_refs).Count -lt 1) {
      throw "Claim $($claim.claim_id) must include source_refs"
    }

    foreach ($sourceRef in @($claim.source_refs)) {
      if (-not $sourceRef.PSObject.Properties.Name.Contains("path") -or -not $sourceRef.PSObject.Properties.Name.Contains("contains")) {
        throw "Claim $($claim.claim_id) source_ref must include path and contains"
      }

      $sourcePath = Join-Path (Get-Location) ([string]$sourceRef.path)
      if (-not (Test-Path $sourcePath)) {
        throw "Claim $($claim.claim_id) source file missing: $($sourceRef.path)"
      }

      $needle = [string]$sourceRef.contains
      if ([string]::IsNullOrWhiteSpace($needle)) {
        throw "Claim $($claim.claim_id) source_ref contains must be non-empty"
      }

      $sourceContent = Get-Content -Raw $sourcePath
      if ($sourceContent -notmatch [regex]::Escape($needle)) {
        throw "Claim $($claim.claim_id) drift detected: source text not found in $($sourceRef.path)"
      }
    }
  }

  Write-CheckOk "claim-drift-sentinel"
}

function Invoke-ContractChecks {
  Invoke-SchemaJsonParse
  Invoke-SchemaExampleValidation
  Invoke-SchemaCatalogPairing
}

function Invoke-BuildChecks {
  & pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
  if ($LASTEXITCODE -ne 0) {
    throw "Runtime build checks failed"
  }

  Write-CheckOk "runtime-build"
}

function Invoke-DocsChecks {
  Invoke-ActiveMarkdownLinkCheck
  Invoke-BacklogYamlIdCheck
  Invoke-OldProjectNameScan
  Invoke-HostReplacementClaimBoundaryScan
  Invoke-GapEvidenceSloCheck
  Invoke-ClaimDriftSentinelCheck
  Invoke-PostCloseoutQueueSyncCheck
}

function Invoke-ScriptChecks {
  Invoke-PowerShellParse
  Invoke-IssueSeedingRenderCheck
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

  & $python.Source -m unittest tests.service.test_session_api tests.service.test_operator_api
  if ($LASTEXITCODE -ne 0) {
    throw "Service API parity tests failed"
  }

  Write-CheckOk "runtime-service-parity"
}

function Invoke-DoctorChecks {
  & pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
  if ($LASTEXITCODE -ne 0) {
    throw "Runtime doctor checks failed"
  }

  Write-CheckOk "runtime-doctor"
}

switch ($Check) {
  "Build" { Invoke-BuildChecks }
  "Contract" { Invoke-ContractChecks }
  "Doctor" { Invoke-DoctorChecks }
  "Docs" { Invoke-DocsChecks }
  "Runtime" { Invoke-RuntimeChecks }
  "Scripts" { Invoke-ScriptChecks }
  "All" {
    Invoke-BuildChecks
    Invoke-RuntimeChecks
    Invoke-ContractChecks
    Invoke-DoctorChecks
    Invoke-DocsChecks
    Invoke-ScriptChecks
  }
}
