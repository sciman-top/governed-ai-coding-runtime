# Tests

Runtime tests will live here once implementation packages exist.

## Phase 0 Verification
The repository integrity checks are:
- schema JSON parsing
- schema example validation
- schema catalog pairing
- PowerShell script parsing
- active markdown link checks
- roadmap/backlog/script drift checks

These checks are executed by `scripts/verify-repo.ps1`.

## Phase 1 Runtime Tests
Runtime contract unit tests now live under `tests/runtime/`.

Run them through the repository verifier:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```
