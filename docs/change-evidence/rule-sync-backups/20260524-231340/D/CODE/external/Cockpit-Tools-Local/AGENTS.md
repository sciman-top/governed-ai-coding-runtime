# Repository Guidelines

This guide extends `GlobalUser/AGENTS.md v9.52`. Treat runtime facts and source code as authoritative, then this file, then general contributor docs.

## Project Structure & Module Organization

Cockpit Tools Local is a Tauri 2 desktop app with a React 19/Vite frontend and Rust workspace backend.

- `src/`: React UI, hooks, types, utilities, styles, assets, and locales.
- `src-tauri/`: Tauri shell, commands, capabilities, icons, and platform integration.
- `crates/cockpit-core/`: shared Rust logic for accounts, providers, OAuth, quotas, config, and persistence.
- `crates/cockpit-cli/`: CLI entrypoint over the shared core.
- `scripts/`: version sync, locale checks, release preflight, checksums, and publishing helpers.
- `docs/`, `public/`, `Casks/`: documentation, static assets, donations, and Homebrew cask metadata.

Do not edit generated outputs such as `dist/`, `target/`, `target-test/`, `target-codex-verify/`, or `node_modules/`.

## Build, Test, and Development Commands

- `npm run dev`: start the Vite frontend server.
- `npm run tauri dev`: run the full desktop app in development mode.
- `npm run typecheck`: run strict TypeScript checks with no emit.
- `npm run build`: sync version, typecheck, and build the frontend.
- `cargo test --package cockpit-core`: run core Rust tests.
- `cargo run --package cockpit-cli -- <command>`: exercise CLI behavior.
- `npm run release:preflight`: run release readiness checks before tagging.

Run finite verification commands autonomously when needed, including `npm run typecheck`, `npm run build`, Cargo tests, and focused script checks. Do not treat every `npm run` as `confirmation_required`. Only if seeing the latest code live requires starting, restarting, or rerunning a long-running/session-impacting app or server flow, such as `npm run dev`, `npm run tauri dev`, `npm run tauri build`, or an equivalent command, state the exact command, why live verification requires it, expected impact such as ports/windows/single-instance wakeups/resource use/Codex or Cockpit continuity risk, and whether it is live verification or packaged build validation. Ask explicitly: `是否允许我现在执行 <command> 进行实时验证？` Do not run that live command until the user explicitly confirms in the current task; if the user already granted task-scoped permission for that exact command, mention that grant before running it.

For riskier changes, verify in order: build/typecheck, tests, contract or invariant checks, then hotspot/manual smoke.

## Coding Style & Naming Conventions

Use TypeScript strict mode, React functional components, hooks, and existing Zustand/i18next patterns. Keep components in PascalCase, hooks as `useXxx.ts`, utilities in camelCase, and CSS near the existing style layer. Rust follows idiomatic 2021 edition style; run `cargo fmt` before commits and keep modules snake_case.

## Testing Guidelines

Add focused Rust tests near changed core modules when behavior changes. For frontend changes, at minimum run `npm run typecheck` autonomously; use `npm run tauri dev` for UI or platform flows only when live desktop inspection is actually needed and the live `npm run` confirmation gate above is satisfied. Locale changes should use `npm run release:preflight` when feasible.

## Commit & Pull Request Guidelines

Recent history uses concise Conventional Commit style, for example `fix(codex): recover direct projection current account` and `docs: clarify Codex switching ownership`. Keep commits scoped. PRs should target `main`, describe behavior changes, list verification commands, link issues, and include screenshots for UI changes.

## Security & Configuration Tips

Never commit secrets, account tokens, OAuth state, generated provider data, or private machine paths. Treat `SECURITY.md`, Tauri capabilities, updater/signing files, and release scripts as high-impact; document verification and rollback evidence when changing them.

When maintaining Cockpit while Codex is in use, keep Codex continuity as a hard guardrail: first place Codex on a verified Direct API or Direct OAuth fallback and prove it with a real `codex exec` probe, then request current-task authorization before running `npm run tauri dev` or `npm run tauri build`. Before these build/dev flows, state the expected impact and whether the command is live verification or packaged build validation. Do not stop, restart, kill, or auto-launch Codex App or `codex` processes unless the user explicitly confirms the interruption. Replacing the release exe, changing auth/provider, overwriting live config, or otherwise interrupting active Codex/Cockpit sessions also requires explicit confirmation; after the build or dev switch, re-probe Codex connectivity.

For Cockpit API service failover live probes while the current Codex CLI session must remain connected, use the bypass probe path instead of editing the active CLI provider: `.\scripts\smoke-local-hardened-api.ps1 -Stage fallback_probe -StartEphemeralGateway -TemporaryFallbackConfig -AcknowledgeLiveUpstreamRisk -RunUpstreamSmoke -AssertCodexCliConfigUntouched -WriteReport`. This path backs up and restores Cockpit local access config, runs a temporary gateway, and verifies `~/.codex/config.toml` / `~/.codex/auth.json` hashes without reading or writing their contents. If Codex App must also stay connected, add `-AppSafeIsolatedProbe -AssertCodexAppProcessStable`; this runs the temporary gateway from an isolated data root and port instead of writing the live Cockpit API service config. For the stronger task-level acceptance that Codex continues a coding task after an account quota 429, use `-RunCodexExecSmoke` instead of a raw HTTP smoke so a separate temporary `CODEX_HOME` runs `codex exec --ephemeral` through the isolated gateway.

Live upstream quota probes are risk-sensitive. Default verification must use offline/static/cached evidence; do not batch-refresh OAuth accounts, poll cooldown recovery, run `wham/usage`, run `-RunUpstreamSmoke`, run `-RunCodexExecSmoke`, or drain a free account unless the current task explicitly requires live upstream acceptance and the command includes `-AcknowledgeLiveUpstreamRisk`. Fallback continuity probes must use the current manually configured API service account pool; scripts must not auto-select accounts or write a temporary two-account pool. Existing pool accounts and cached quota/reset timestamps must be checked before any live refresh. Raising drain volume above defaults or lowering drain interval below 20 seconds also requires `-AcknowledgeExpandedLiveUpstreamRisk` and a report explaining why cached/reset data is insufficient. Cooldown recovery must be inferred from stored reset times/health registry by default, not from repeated refresh polling.

For Codex API service routing, quota continuity, pool scheduling, sorting, or risk-reduction changes, consult `D:\CODE\external\_reference_gateway_sources` before broader community lookup. Official `openai-codex` source is the highest reference for Codex-facing turn metadata, `/v1/responses` stream terminal semantics, same-turn replay boundaries, `previous_response_id`, and local completed Responses behavior. Sub2API, CLIProxyAPI, LiteLLM, and New API are structure references only for schedulability, persistent cooldown, fill-first/session affinity, pre-call rate checks, retry caps, and redacted audit patterns. If these references are stale, update them with non-destructive `git fetch --prune` / `pull --ff-only` and update `docs/reference-gateway-best-practices.md` before using them as evidence.
