# 2026-05-12 Codex workdir system32 investigation

## Scope
- Rule ID: R1/R3/R8, local Codex launcher and trusted-project state.
- Risk: medium. Live host config and launcher shim were inspected and repaired; no Codex App or long-running Codex process was restarted or killed by this task.
- Current landing: `C:\Users\sciman\.codex\config.toml`, `C:\Users\sciman\.local\bin\codex.ps1`, and this control repo.
- Target home: keep live host state clean and make the repo cleanup path disable project-level top-level `codex` shims.

## Root cause
- Live config had a stale trusted project entry for `c:\windows\system32`. This made `system32` a known Codex project even though the active repo also had the correct trusted entry.
- The active `codex` command resolved first to `C:\Users\sciman\.local\bin\codex.ps1`, a local wrapper ahead of the official npm/App entries. The wrapper launched the native `codex.exe` through `System.Diagnostics.ProcessStartInfo` without explicitly setting `WorkingDirectory`, leaving cwd propagation dependent on process defaults.
- No repo `AGENTS.md` rule was found that forces this project to `C:\WINDOWS\system32`.

## Changes
- Live repair: removed `[projects.'c:\windows\system32']` from `C:\Users\sciman\.codex\config.toml`.
- Live repair: added `$psi.WorkingDirectory = (Get-Location).ProviderPath` to `C:\Users\sciman\.local\bin\codex.ps1`.
- Repo repair: `scripts/Disable-CodexProjectInterop.ps1 -DisableProjectShortcuts` now disables top-level `codex.cmd` and `codex.ps1` shims as well as the cockpit/shared/relay shortcuts.
- Repo test: `tests/runtime/test_codex_shared_launcher.py` covers the top-level shim cleanup in `Disable-CodexProjectInterop.ps1`.

## Verification
- `python -m unittest tests.runtime.test_codex_shared_launcher`
  - Result: `Ran 18 tests in 3.331s`, `OK`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - Result: `OK python-bytecode`, `OK python-import`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - Result: `Completed 112 test files in 166.320s; failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - Result: contract checks passed, including `OK dependency-baseline`, `OK target-repo-governance-consistency`, `OK agent-rule-sync`, and `OK functional-effectiveness`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - Result: exit code 0; checks passed with residual `WARN codex-capability-degraded`.
- `git diff --check`
  - Result: exit code 0; only CRLF working-copy warnings for existing Windows-managed files.
- `Select-String -Path C:\Users\sciman\.codex\config.toml -Pattern "^\[projects\.'c:\\windows\\system32'\]"`
  - Result: no match.
- `Select-String -Path C:\Users\sciman\.codex\config.toml -Pattern "^\[projects\.'d:\\code\\governed-ai-coding-runtime'\]"`
  - Result: `[projects.'d:\code\governed-ai-coding-runtime']`.
- `Select-String -Path C:\Users\sciman\.local\bin\codex.ps1 -Pattern "WorkingDirectory|ProcessStartInfo"`
  - Result: `ProcessStartInfo` and `$psi.WorkingDirectory = (Get-Location).ProviderPath` are present.
- `codex exec --profile shared-chatgpt --skip-git-repo-check --dangerously-bypass-approvals-and-sandbox "...Get-Location..."`
  - Result: Codex started and printed `workdir: D:\CODE\governed-ai-coding-runtime`.
  - Residual: execution then failed with `401 Unauthorized` against `https://api.openai.com/v1/responses`; this is an auth/provider issue, not a cwd regression.

## Rollback
- Restore the previous live wrapper by removing `$psi.WorkingDirectory = (Get-Location).ProviderPath` from `C:\Users\sciman\.local\bin\codex.ps1`.
- Re-add `[projects.'c:\windows\system32']` only if a real workflow intentionally uses that directory as a trusted Codex project.
- Revert this repo diff for `scripts/Disable-CodexProjectInterop.ps1`, `tests/runtime/test_codex_shared_launcher.py`, and this evidence file.
