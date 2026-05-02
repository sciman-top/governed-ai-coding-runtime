# Tests

Runtime and service boundary tests live here. Use the repo verifier for the
canonical test entrypoint so Windows process-environment normalization runs
before Python imports modules that may touch `asyncio` or subprocess APIs.

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
Runtime contract unit tests live under `tests/runtime/`. Service boundary tests
live under `tests/service/` and are included in the Runtime gate.

Run them through the repository verifier:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

For inner-loop work on target-governance speed-profile behavior, use the
bounded quick slice first, then run the full Runtime gate before delivery:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check RuntimeQuick
```

Direct test commands when the host process environment is already healthy:

```powershell
python -m unittest discover -s tests/runtime -p "test_*.py"
python -m unittest discover -s tests/service -p "test_*.py"
```

Foundation build and doctor checks are available through:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Build
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Doctor
```

Public usable release smoke paths are available through:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/bootstrap-runtime.ps1
python scripts/serve-operator-ui.py
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/package-runtime.ps1
```

Maintenance visibility is also covered by runtime tests and doctor:

```powershell
python scripts/run-governed-task.py status --json
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```
