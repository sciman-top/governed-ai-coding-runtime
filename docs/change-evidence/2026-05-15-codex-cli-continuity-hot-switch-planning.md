# 2026-05-15 Codex CLI Continuity Hot-Switch Planning

## Change
- Added a scoped planning baseline for Codex CLI continuity across Cockpit Tools account switches.
- The plan records that native Codex App account changes still require restart in the current observed posture, while CLI segmented execution is the lower-risk first implementation target.

## Risk
- `risk`: low for documentation-only planning.
- `live_state_changed`: false.
- `codex_app_restarted`: false.
- `cockpit_config_changed`: false.
- `auth_or_provider_changed`: false.

## Evidence
- Current user-observed behavior: Cockpit Tools can switch accounts, but already-open Codex App continues to use the old account until App restart.
- Official issue evidence: `openai/codex#3860` describes dynamic profile switching and hot reload as requested behavior, with restart-required current behavior.
- Official source evidence: Codex `AuthManager` caches auth and exposes internal reload behavior, but no stable public cross-account hot-switch command is documented for the running App.
- Community evidence: `codex-auth` recommends client restart for native Codex CLI/App account switching; `Codex_AccountSwitch` uses API reverse proxy for no-restart switching.

## Verification
- `git diff --check`

## Rollback
- Revert `docs/plans/codex-cli-continuity-and-hot-switch-plan.md`.
- Revert the `docs/plans/README.md` index entry.
