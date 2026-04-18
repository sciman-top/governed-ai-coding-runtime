# Tests

Repository tests already live here.

## Current Verification Surface
The repository integrity checks are:
- schema JSON parsing
- schema example validation
- schema catalog pairing
- PowerShell script parsing
- active markdown link checks
- roadmap/backlog/script drift checks

These checks are executed by `scripts/verify-repo.ps1`.

## Runtime Contract Tests
Runtime contract unit tests live under `tests/runtime/`.

Run them through the repository verifier:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

Foundation build and doctor checks are available through:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Build
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Doctor
```

As of the current baseline, `tests/runtime/` covers the MVP governance-kernel slices plus the Foundation substrate work through `GAP-023`.
