# 2026-05-09 Codex Cockpit App prelaunch repair

## Scope

- landing: `scripts/Start-CodexShared.ps1`, `scripts/codex-interop-check.py`, `tests/runtime/test_codex_shared_launcher.py`
- destination: Cockpit Tools Codex account/API switches should launch Codex App through one shared `C:\Users\sciman\.codex` history root and the stable `cockpit` provider bucket on the first launch after switching.
- risk: medium local host config mutation, limited to `C:\Users\sciman\.codex` and `C:\Users\sciman\.antigravity_cockpit` backups.

## Commands

- `python -m unittest tests.runtime.test_codex_shared_launcher`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File .\scripts\Optimize-CodexLocal.ps1 -Apply`
- `python .\scripts\codex-interop-check.py --codex-home "$HOME\.codex" --cc-switch-db "$HOME\.cc-switch\cc-switch.db" --cockpit-home "$HOME\.antigravity_cockpit"`
- `codex-cockpit-exec --help`

## Evidence

- Root cause reproduced after switching from API to OAuth: live check failed with `dominant_provider=openai`, `active_provider=openai`, `active_forced_login_method=api`, and current Cockpit account `auth_mode=oauth`.
- `Start-CodexShared.ps1` now uses `PositionalBinding = $false`, so `codex-cockpit-exec "prompt"` no longer binds the prompt as `Profile`.
- `Start-CodexShared.ps1` now runs pre-launch interop repair for `UseCockpitCurrentAccount`; App launch also stops existing `Codex` / `codex` App processes before repair and launch.
- `codex-interop-check.py --apply --migrate-provider-bucket` now repairs top-level `forced_login_method`, stable `model_provider = "cockpit"`, provider auth mode, `auth.json`, history provider buckets, and Cockpit restart-on-switch settings.
- Live apply repaired current OAuth state to `model_provider=cockpit`, `forced_login_method=chatgpt`, `[model_providers.cockpit].base_url=https://api.openai.com/v1`, `requires_openai_auth=true`, and `state_5.sqlite` distribution `{ "cockpit": 1588 }`.
- Live Cockpit config now has `codex_launch_on_switch=true`, `codex_restart_specified_app_on_switch=true`, and `codex_specified_app_path=C:\Users\sciman\.local\bin\codex-cockpit-app-restart.cmd`.
- Installed `codex-cockpit-exec --help` printed `interop_repair_status=pass`, selected `profile=shared-cockpit-auth`, and showed `model_provider=cockpit`.

## Backups

- `C:\Users\sciman\.codex\config-backups\config-20260509-160027.toml`
- `C:\Users\sciman\.codex\backups\config.toml.20260509_160027_cockpit_provider.bak`
- `C:\Users\sciman\.codex\backups\auth.json.20260509_160027_cockpit_auth.bak`
- `C:\Users\sciman\.codex\backups\state_5.sqlite.20260509_160027_provider_bucket.bak`
- `C:\Users\sciman\.codex\config-backups\config-20260509-160256.toml`

## Rollback

- Restore the listed `config.toml`, `auth.json`, and `state_5.sqlite` backups if local Codex/Cockpit projection must be undone.
- Restore `C:\Users\sciman\.antigravity_cockpit\config.json` from the latest Cockpit backup if restart-on-switch should be disabled.
- Revert this repo change from git history to remove pre-launch repair from managed launchers.
