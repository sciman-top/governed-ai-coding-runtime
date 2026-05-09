# 2026-05-09 Codex Cockpit provider interop

- rules: R1/R4/R6/R8, E4/E6
- risk: medium, user-local Codex config/auth/state are persisted but backed up before repair
- landing: `scripts/codex-interop-check.py`, `scripts/Start-CodexShared.ps1`, `scripts/Optimize-CodexLocal.ps1`, `tests/runtime/test_codex_shared_launcher.py`, `README.md`, `README.zh-CN.md`
- destination: Cockpit Tools owns Codex App/CLI ChatGPT auth and Codex API provider switching; CC Switch stays scoped to Claude CLI and non-Codex third-party API switching

## Commands

- `python -m unittest tests.runtime.test_codex_shared_launcher`
- `python -m py_compile scripts\codex-interop-check.py`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\Optimize-CodexLocal.ps1 -Apply`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\Start-CodexShared.ps1 -Surface exec -UseCockpitCurrentAccount -CockpitAccountId codex_apikey_c087074540859bbe2e78150e85dd7378 --json "Reply with OK only."`
- `codex-cockpit-exec -CockpitAccountId codex_apikey_8b8853f15e823dc53bd156163035bc78 --help`
- `codex-interop-repair`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\doctor-runtime.ps1`

## Evidence

- `Optimize-CodexLocal.ps1 -Apply` installed `codex-cockpit`, `codex-cockpit-exec`, `codex-cockpit-app`, and `codex-cockpit-app-restart`.
- The interop checker now treats `C:\Users\sciman\.antigravity_cockpit` as the Codex account/provider source and treats `C:\Users\sciman\.cc-switch\cc-switch.db` as a boundary check only.
- Local Codex config is normalized to `model_provider = "cockpit"` with `[model_providers.cockpit]`, `[profiles.shared-cockpit-api]`, and `[profiles.shared-cockpit-auth]`.
- Local Codex history metadata is normalized to the stable `cockpit` provider bucket; the live distribution after repair was `{ "cockpit": 1582 }`.
- The RightCode Cockpit API account was projected into `auth.json`, used `forced_login_method=api`, reached `https://right.codes/codex/v1`, and a real `codex exec --json` request returned final text `OK`.
- The Cockpit provider at `http://35.213.82.91:8003/v1` was checked through the installed `codex-cockpit-exec` wrapper; the wrapper selected `profile=shared-cockpit-api`, `forced_login_method=api`, and `model_provider=cockpit`.
- `codex-interop-repair` restored the current Cockpit OAuth account projection after API-account probes; post-repair status was `pass`.
- The checker records Codex App restart semantics: the App reads auth/provider state at process startup, so account/API switches need `codex-cockpit-app-restart` or an equivalent Cockpit restart-on-switch setting to refresh the already-open App.
- `cc-switch` Codex rows are no longer modified by this repair path; CC Switch remains available for Claude CLI, GLM, DeepSeek, and other non-Codex API switching.
- Targeted unit coverage passed: `tests.runtime.test_codex_shared_launcher` ran 4 tests with 0 failures.
- Build gate passed with `OK python-bytecode` and `OK python-import`.
- Runtime gate passed: 106 runtime/service test files, failures `0`.
- Contract gate passed, including schema, dependency baseline, target governance consistency, agent rule sync, and functional effectiveness checks.
- Doctor gate exited `0`; it retained the existing `WARN codex-capability-degraded` host capability warning.

## Backups

- `C:\Users\sciman\.codex\config-backups\config-20260509-144855.toml`
- `C:\Users\sciman\.codex\backups\auth.json.20260509_144856_cockpit_auth.bak`
- `C:\Users\sciman\.codex\backups\auth.json.20260509_145013_cockpit_auth.bak`
- `C:\Users\sciman\.codex\backups\state_5.sqlite.20260509_144235_provider_bucket.bak`

## Rollback

- Restore the listed `config.toml`, `auth.json`, and `state_5.sqlite` backups if the local projection or provider-bucket migration must be undone.
- Re-run `codex-interop-repair` after any Cockpit Tools account switch to re-project the current Cockpit account without changing CC Switch.
- Revert the git commit containing this file and related script changes to remove the managed Cockpit interop behavior from the control repo.
