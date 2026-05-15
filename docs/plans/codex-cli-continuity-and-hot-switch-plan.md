# Codex CLI Continuity And Hot-Switch Plan

## Status
- Created: 2026-05-15.
- Queue: owner-directed scoped spike, not a new heavy `GAP` mainline.
- Current state: CCHS-001 partial evidence, CCHS-002 read-only guard, CCHS-003 bounded multi-segment runner, and CCHS-004 code-level operator visibility are implemented. No local Codex auth, Cockpit Tools state, provider profile, App process, or proxy configuration is changed by this plan.
- Current local policy: Cockpit Tools automatic switching, Codex batch quota refresh, and Cockpit Codex API service stay disabled by default. Enable them only as an operator-directed temporary mode with fresh listener-scope and projection evidence.
- Preferred gateway architecture: Cockpit owns ChatGPT/OAuth subscription-account state; LiteLLM owns normal API keys, multi-provider routing, logging, budgets, and unified OpenAI-compatible gateway behavior; Cockpit API service may be registered behind LiteLLM as one opt-in upstream provider after local listener hardening.
- Scope boundary: prioritize Codex CLI continuity through short-lived or resumable CLI runs. Treat Codex App hot account switching as unsupported by the native App path until official evidence changes.

## Goal
Provide a low-interruption way to keep Codex CLI coding work moving when Cockpit Tools auto-switches accounts, without taking over Cockpit Tools account ownership and without requiring Codex App hot account reload.

The target operating model is:

```text
Cockpit Tools owns account library, quota refresh, account groups, and auto-switch.
Governed runtime owns task continuity, handoff, evidence, and restart/resume orchestration.
Codex CLI runs as a replaceable worker process that reads current auth/config at process start.
Codex App remains native and restart-required for account changes unless a later official hot reload exists.
```

## Evidence Baseline
- Official Codex CLI/App hot profile switching is not currently a stable user-facing capability. The upstream hot-reload issue describes restart-required current behavior and proposes config watcher plus IPC broadcast as future work: <https://github.com/openai/codex/issues/3860>.
- Codex auth is cached inside `AuthManager`; the source includes `reload()`, but ordinary guarded token refresh checks account identity and is not a public cross-account hot-switch contract: <https://github.com/openai/codex/blob/a5040d0b391ed5f22c162028040f2663d5e96fb4/codex-rs/login/src/auth/manager.rs>.
- Community `codex-auth` treats native Codex CLI/App account changes as requiring client restart, with no-restart behavior reserved for customized clients: <https://github.com/Loongphy/codex-auth>.
- Community no-restart account switching projects generally use a local API reverse proxy, so the routing layer switches accounts rather than the native App hot-reloading auth: <https://github.com/isxlan0/Codex_AccountSwitch>.

## Architecture Decisions
- Do not compete with Cockpit Tools for account switch decisions. Cockpit remains the source for current account, quota, account groups, and selected free-account scope.
- Do not force hot account switching inside one long-running native Codex CLI process. Prefer small execution segments, `codex exec`, `codex resume`, and governed handoff summaries.
- Do not enable Codex App restart-on-switch by default. App restart is a separate operator choice for "quota continuity over interruption" mode.
- Do not implement proxy mode as the first step. Proxy is an experimental later track because it changes provider routing, credential custody, streaming behavior, and error attribution.
- Do not treat Cockpit Tools' Codex API service at `127.0.0.1:2876/v1` as the default proxy implementation. It is an operator-owned local-access upstream, best placed behind a dedicated gateway such as LiteLLM, and must remain off until the running build is proven loopback-only or protected by a host firewall rule.
- Do not build a Cockpit-aware adapter until the operator needs account-label, group, quota, or routing decisions that cannot be expressed by treating Cockpit API service as a single OpenAI-compatible LiteLLM upstream.
- Treat Cockpit config writes as high-risk. Default tools should read and diagnose; any repair must be explicit, backed up, narrow, and field-level.

## Mode Matrix
| Mode | Purpose | Account handoff behavior | Interruption risk | First implementation target |
|---|---|---|---|---|
| `native_cli_segmented` | Continue CLI work across Cockpit account switches | New CLI segment reads current Cockpit/Codex auth state | Low | Yes |
| `native_cli_same_process` | Hot switch inside one live CLI process | Not reliable as a public contract | Medium | No |
| `native_app_restart_required` | App uses account after restart | Manual or explicitly enabled restart | Medium to high | Diagnostics only |
| `gateway_litellm_default` | Route normal API-key traffic through LiteLLM | LiteLLM owns API keys, provider routing, logging, budgets, and limits | Low to medium | Preferred long-term gateway |
| `gateway_litellm_with_cockpit_upstream` | Register Cockpit API service as one LiteLLM upstream | Cockpit owns current OAuth/subscription account; LiteLLM owns client-facing gateway | Medium | Preferred Cockpit integration shape after listener hardening |
| `cockpit_aware_adapter` | Route based on Cockpit account labels, groups, or quota metadata | Custom adapter reads Cockpit state and exposes finer routing controls | Medium to high | Only if single-upstream Cockpit API is insufficient |
| `proxy_experimental` | Route requests through a dedicated local account proxy | Proxy chooses account per request or failure | Medium to high | Later PoC only; Cockpit API service is not the default proxy |

## Task List

### CCHS-001 Native Boundary And Probe Evidence
**Purpose:** Prove the current boundary before implementing runner behavior.

**Acceptance criteria:**
- [ ] Capture a before/after Cockpit auto-switch trace showing Cockpit current account, Codex auth account, and Codex App displayed account without printing secrets.
- [ ] Demonstrate that a new `codex exec` process reads the current post-switch state, or record the exact failure mode.
- [ ] Demonstrate that already-open Codex App does not use the new account until restart, or record a counterexample.
- [ ] Store evidence under `docs/change-evidence/` with command, timestamp, key output, and rollback notes.

**Verification:**
- [ ] `python scripts/codex-cockpit-switch-trace.py --watch-seconds 45 --out docs/change-evidence/<date>-codex-cli-switch-trace.json`
- [ ] redacted live `codex exec` smoke against current account after Cockpit switch

**Dependencies:** Current Cockpit Tools installation and selected free-account scope.

### CCHS-002 Read-Only Cockpit/Codex Switch Health Guard
**Purpose:** Add a checker that prevents false confidence in auto-switch state.

**Acceptance criteria:**
- [x] Report `codex_auto_switch_enabled`, thresholds, refresh interval, selected account count, selected plan types, restart-on-switch flags, and recent `401 token_invalidated` count.
- [x] Report whether selected account ids still resolve in `codex_accounts.json`.
- [x] Report `app_restart_required_for_account_change` when the target surface is Codex App.
- [x] Never write Cockpit or Codex config in default mode.

**Verification:**
- [x] focused unit tests with fixture `config.json` and `codex_accounts.json`
- [x] `python -m unittest tests.runtime.test_codex_cockpit_switch_health`

**Dependencies:** CCHS-001.

### CCHS-003 Codex CLI Continuity Runner Spike
**Purpose:** Implement a bounded CLI runner that can continue after quota failure by starting a new CLI segment after Cockpit switches accounts.

**Acceptance criteria:**
- [x] Start a Codex CLI segment with task id, repo path, account alias, and evidence path.
- [x] Detect quota, 401, and account-limit failures without swallowing unrelated errors.
- [x] Wait for Cockpit current account to change or for quota health to recover.
- [x] Restart a new `codex exec` segment using a generated handoff summary after Cockpit account change is observed.
- [x] Record every segment with command, exit code, account alias, failure reason, resume action, and rollback reference.

**Verification:**
- [x] unit tests for failure classification and handoff generation
- [x] dry-run with mocked Codex command
- [x] wrapper dry-run through `scripts/Start-CodexContinuity.ps1`
- [ ] one live opt-in smoke after user approval

**Dependencies:** CCHS-002.

### CCHS-004 Operator Visibility
**Purpose:** Show the difference between Cockpit switch state, CLI next-run state, and App restart-required state.

**Acceptance criteria:**
- [x] 8770 Codex panel shows `native_cli_segmented` versus `native_app_restart_required`.
- [x] The panel distinguishes current Cockpit account from the already-open App account when known.
- [x] The panel provides no automatic restart action unless explicitly added as a separate operator-confirmed action.

**Verification:**
- [x] UI contract tests or snapshot tests for the new status labels
- [ ] live 8770 page verification after service refresh

**Dependencies:** CCHS-002.

### CCHS-005 Proxy Feasibility PoC
**Purpose:** Evaluate API proxy hot switching only after the native CLI segmented path is proven insufficient.

**Acceptance criteria:**
- [ ] Proxy binds only to `127.0.0.1` by default.
- [ ] Cockpit Tools' Codex API service is treated as a temporary operator mode, not as the default proxy implementation.
- [ ] If Cockpit API service is used, verify listener scope and host firewall posture before pointing Codex CLI/App at `http://127.0.0.1:2876/v1`.
- [ ] LiteLLM is the default client-facing gateway for normal API-key providers and can register Cockpit API service as a single opt-in OpenAI-compatible upstream.
- [ ] A Cockpit-aware adapter is deferred until account-label, group, quota, or routing semantics are required beyond the single-upstream model.
- [ ] Authorization headers, refresh tokens, and request bodies are redacted from logs.
- [ ] Streaming, compact/resume behavior, tool-call traffic, and error propagation are tested against mocks before live use.
- [ ] Cockpit remains either the account owner or the proxy owner is explicitly declared; both must not auto-switch independently.
- [ ] Proxy mode is opt-in and reversible without changing default Cockpit native switching.

**Verification:**
- [ ] mock OpenAI-compatible endpoint tests
- [ ] redaction tests
- [ ] explicit manual live smoke only after CCHS-001 through CCHS-004 pass

**Dependencies:** CCHS-003.

## Recommended Execution Order
1. Complete CCHS-001 and preserve evidence.
2. Implement CCHS-002 as read-only guard.
3. Build CCHS-003 against mocks before any live Codex run.
4. Add CCHS-004 only after the status vocabulary is stable.
5. Start CCHS-005 only if segmented CLI continuity cannot meet the workflow need.

## Rollback
- Planning-only rollback: revert this file and its plan-index entry.
- Checker rollback: remove the read-only checker and tests; no live state should need restoration.
- Runner rollback: disable the CLI runner entrypoint and fall back to manual `codex exec` / `codex resume`.
- Proxy rollback: restore `config.toml` provider/base URL from backup, stop the proxy process, and return to Cockpit native account switching.
