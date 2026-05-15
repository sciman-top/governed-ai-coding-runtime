# Codex CLI Continuity And Hot-Switch Plan

## Status
- Created: 2026-05-15.
- Queue: owner-directed scoped spike, not a new heavy `GAP` mainline.
- Current state: CCHS-001 partial evidence, CCHS-002 read-only guard, CCHS-003 bounded multi-segment runner, and CCHS-004 code-level operator visibility are implemented. No local Codex auth, Cockpit Tools state, provider profile, App process, or proxy configuration is changed by this plan.
- Current local policy: Cockpit Tools local API service is enabled only as an operator-directed LiteLLM upstream mode after fresh listener-scope and Windows Firewall posture evidence. Codex App is not restarted by this lane.
- Preferred gateway architecture: Cockpit owns ChatGPT/OAuth subscription-account state; LiteLLM owns normal API keys, multi-provider routing, logging, budgets, and unified OpenAI-compatible gateway behavior; Cockpit API service may be registered behind LiteLLM as one opt-in upstream provider after local listener hardening.
- Plan rebaseline: keep CCHS-001 through CCHS-004 as completed or partial native-boundary groundwork. CCHS-005A through CCHS-005F now provide a live `Codex -> LiteLLM -> Cockpit API service` lane; keep the old segmented-runner path as fallback, not the primary continuation route.
- Compatibility supplement: the new gateway lane must not retire the old direct Cockpit projection lane. Codex App/CLI must still support explicit OAuth/API roundtrip switching through `CodexOauthProjectionRepair` and `CodexApiProjectionRepair`; the operator-facing choice is `new_gateway_litellm` versus `old_direct_projection_api` / `old_direct_projection_oauth`.
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
- Do not bypass LiteLLM for Codex CLI gateway mode. Cockpit Tools' Codex API service at `127.0.0.1:2876/v1` is an operator-owned local-access upstream behind LiteLLM, not the client-facing default.
- Cockpit local access may bind `0.0.0.0`; it is usable only when Windows Firewall profile policy or an explicit rule constrains inbound access.
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
| `old_direct_projection_api` | Preserve the old explicit API roundtrip path for Codex App/CLI | `CodexApiProjectionRepair` projects the current Cockpit API account directly into Codex auth/config/provider/history | Medium | Supported compatibility mode |
| `old_direct_projection_oauth` | Preserve the old explicit OAuth roundtrip path for Codex App/CLI | `CodexOauthProjectionRepair` projects the current Cockpit OAuth account back to built-in `openai` auth/config/history | Medium | Supported compatibility mode |
| `new_gateway_litellm` | Use the new gateway lane | `Manage-LiteLLMGateway.ps1 -Action All` writes the reversible `litellm_gateway` profile and uses Cockpit API service behind LiteLLM | Medium | Preferred new opt-in mode |
| `cockpit_aware_adapter` | Route based on Cockpit account labels, groups, or quota metadata | Custom adapter reads Cockpit state and exposes finer routing controls | Medium to high | Only if single-upstream Cockpit API is insufficient |
| `proxy_experimental` | Route requests through a dedicated local account proxy | Proxy chooses account per request or failure | Medium to high | Later PoC only; Cockpit API service is not the default proxy |

## Task List

### Rebaseline Cleanup
- Keep CCHS-002, CCHS-003, and CCHS-004 because they already provide read-only switch health, bounded CLI segment continuity, and operator visibility.
- Do not delete the segmented runner. It remains the fallback when gateway mode is disabled or broken.
- Do not delete or deprecate the old direct OAuth/API projection roundtrip. It remains the compatibility lane for Codex App/CLI when the operator chooses direct Cockpit projection instead of LiteLLM gateway mode.
- Do not treat CCHS-003 live smoke as a blocker for the LiteLLM lane. Gateway mode should be validated through its own mock, local, and live smoke gates.
- Supersede the old single CCHS-005 coarse PoC with CCHS-005A through CCHS-005F below.

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

### CCHS-005A LiteLLM Gateway Runtime Baseline
**Purpose:** Establish a local LiteLLM runtime plan without touching Codex or Cockpit live state.

**Acceptance criteria:**
- [x] Choose local install shape: Python venv under `.runtime/litellm/venv`; do not install into arbitrary global Python by default.
- [x] Define LiteLLM config, log, PID, master key, and secret redaction boundaries under `.runtime/litellm/`.
- [x] Keep the default bind address loopback-only at `127.0.0.1:4000`.
- [x] Record install/start/stop/status/smoke/rollback commands in `docs/runbooks/litellm-cockpit-gateway.md`.

**Verification:**
- [x] `litellm --version` from the venv reports `LiteLLM: Current Version = 1.84.0`.
- [x] local config renders without printing upstream keys.
- [x] rollback is scoped to the PID file and managed Codex config block created by this lane.

**Dependencies:** CCHS-002.

### CCHS-005B Cockpit API Upstream Hardening
**Purpose:** Make Cockpit API service safe enough to place behind LiteLLM.

**Acceptance criteria:**
- [x] Cockpit Tools' Codex API service is treated as a temporary operator mode, not as the default proxy implementation.
- [x] If Cockpit API service is used, verify listener scope and host firewall posture before pointing Codex CLI/App at `http://127.0.0.1:2876/v1`.
- [x] If the running Cockpit build binds non-loopback, add or verify a Windows firewall rule limiting inbound access to the local host.
- [x] Verify `/v1/models` through the Cockpit API service with a masked key, and record single-current-account behavior.

**Verification:**
- [x] Superseded evidence recorded the former pool mode with `account_count=3`.
- [ ] Current production evidence records `enabled=true`, `account_count=1`, `follow_current_account=true`, listener addresses including `0.0.0.0`, `firewall_profile_default_block=true` or explicit block rule, and `safe_for_upstream=true`.
- [x] local `/v1/models` probe succeeds without printing the token.
- [x] LAN exposure is constrained by Windows Firewall profile policy `BlockInbound,AllowOutbound`.

**Dependencies:** CCHS-005A, Cockpit Tools local API service operator enablement.

### CCHS-005C LiteLLM Config With Cockpit Upstream
**Purpose:** Register Cockpit API service as one OpenAI-compatible LiteLLM upstream while keeping normal API-key providers separate.

**Acceptance criteria:**
- [x] LiteLLM is implemented as the opt-in client-facing gateway and registers Cockpit API service as `cockpit-current`.
- [x] A Cockpit-aware adapter is deferred until account-label, group, quota, or routing semantics are required beyond the single-upstream model.
- [x] Secrets are stored in local environment or `.runtime/litellm/secrets.env`, not committed config.
- [x] LiteLLM upstream model alias `cockpit-current` distinguishes the Cockpit upstream.
- [x] Cockpit upstream key is stored in a local secret file excluded from git, not in committed config.

**Verification:**
- [x] LiteLLM `/v1/models` includes `cockpit-current`.
- [x] LiteLLM `/v1/chat/completions` succeeds against the live Cockpit upstream before Codex use.
- [x] smoke output redacts secrets and the committed script/config do not contain raw API keys.

**Dependencies:** CCHS-005A, CCHS-005B.

### CCHS-005D Codex Profile To LiteLLM Gateway
**Purpose:** Point Codex to LiteLLM as the stable client-facing base URL, without restarting Codex App automatically.

**Acceptance criteria:**
- [x] Add a reversible Codex profile that uses non-built-in custom provider `model_providers.litellm_gateway`.
- [x] Preserve history bucket expectations and do not reintroduce `[model_providers.openai]`.
- [x] Do not alter the active Codex App process; new CLI/App sessions pick up the profile after operator-controlled start or restart.
- [x] Document rollback to direct OAuth/API projection.

**Verification:**
- [x] `codex --profile litellm-gateway debug models` can read the LiteLLM-backed profile.
- [x] `codex exec` smoke succeeds through LiteLLM.
- [x] `CodexProjectionSmoke` passes after saved Cockpit API provider projection and launch-binding repair.

**Dependencies:** CCHS-005C.

### CCHS-005E Cockpit Current-Account Follow Test
**Purpose:** Prove the desired behavior: Cockpit manual account switching updates the Cockpit API service to the current single OAuth account, while Codex keeps the same LiteLLM endpoint.

**Acceptance criteria:**
- [x] Start with Codex pointing to LiteLLM and LiteLLM routing model alias `cockpit-current` to Cockpit API service.
- [ ] Configure Cockpit local access with `accountIds=[current_account_id]`, `followCurrentAccount=true`, and `restrictFreeAccounts=true` unless `-AllowFreeAccount` is explicitly intended.
- [ ] A new Codex request through LiteLLM succeeds through the Cockpit current-account upstream without changing the Codex endpoint.
- [x] Existing long-running Codex App sessions are not claimed to hot-reload account identity unless directly observed.

**Verification:**
- [ ] Cockpit local access `account_count=1` and `follow_current_account=true` are recorded without secrets.
- [ ] LiteLLM request succeeds through `cockpit-current`.
- [ ] Codex final message smoke succeeds through `litellm-gateway`.

**Dependencies:** CCHS-005D.

### CCHS-005G Cockpit Source Follow-Current Mode
**Purpose:** Make manual Cockpit Codex account switching update the API service account set without Codex process injection or Codex App restart.

**Acceptance criteria:**
- [ ] Cockpit local access collection persists `followCurrentAccount`.
- [ ] Manual `switch_codex_account` calls update API service `accountIds` to the switched account when `followCurrentAccount=true`.
- [ ] The switch itself remains successful if local access follow-current sync fails; the failure is logged and does not corrupt Codex auth.
- [ ] Cockpit bind host remains unchanged; this task does not modify `0.0.0.0`.
- [ ] Governance script `PrepareCockpitUpstream` writes only the current OAuth account and refuses API-key/free accounts by default.

**Verification:**
- [ ] Cockpit Rust/TypeScript typecheck and build pass.
- [ ] Governed runtime contract tests assert follow-current single-account behavior.
- [ ] Live status shows `safe_for_upstream=true`, `account_count=1`, and `follow_current_account=true` before Codex/LiteLLM smoke.

**Dependencies:** CCHS-005B, CCHS-005E.

### CCHS-005F Closeout, Operator Runbook, And Rollback
**Purpose:** Make gateway mode repeatable, reversible, and visible to future agents.

**Acceptance criteria:**
- [x] Add a runbook with start/stop/status/smoke/rollback commands.
- [x] Add evidence showing local listener scope, LiteLLM upstream config shape, Codex profile shape, and the current Cockpit upstream block.
- [x] Update contract tests so future changes cannot collapse Cockpit and LiteLLM ownership boundaries.
- [x] Keep Cockpit-aware adapter explicitly deferred.
- [ ] Streaming, compact/resume behavior, tool-call traffic, and error propagation are tested against mocks before live use.
- [x] Cockpit remains the account owner; LiteLLM is only the client-facing gateway.
- [x] Proxy mode is opt-in and reversible without changing default direct OAuth projection.

**Verification:**
- [ ] mock OpenAI-compatible endpoint tests
- [ ] redaction tests
- [ ] explicit manual live smoke only after CCHS-001 through CCHS-004 pass
- [ ] `build -> Runtime -> Contract -> hotspot` or structured N/A evidence for any live-only step

**Dependencies:** CCHS-005E.

### CCHS-005H Operator Mode Switch
**Purpose:** Provide an explicit old/new choice switch without hiding the old App/CLI OAuth/API roundtrip behavior.

**Acceptance criteria:**
- [x] `scripts/operator.ps1 -Action CodexGatewayEnable` selects the new `Codex -> LiteLLM -> Cockpit API service` lane by calling `scripts/Manage-LiteLLMGateway.ps1 -Action All`.
- [x] `scripts/operator.ps1 -Action CodexGatewayRollback` removes the managed gateway shape by calling `scripts/Manage-LiteLLMGateway.ps1 -Action Rollback`.
- [x] Cockpit self-use builds persist the canonical choice in `codex_runtime_mode.json` with `mode=direct_projection|gateway_litellm`, `accountKind=oauth|api|unknown`, `currentAccountId`, and `updatedAt`.
- [x] `scripts/operator.ps1 -Action CodexModeSync` reads `codex_runtime_mode.json` and materializes the matching governed runtime state.
- [x] `CodexApiProjectionRepair` and `CodexOauthProjectionRepair` remain the old direct projection switches for API and OAuth respectively.
- [x] Root shortcuts expose the same choice: `.\run.ps1 codex-mode-new`, `.\run.ps1 codex-mode-old-api`, `.\run.ps1 codex-mode-old-oauth`, and `.\run.ps1 codex-mode-rollback`.
- [x] The switch does not restore generic `--apply`, provider-bucket migration, background guard, no-op launcher, restart wrapper, or automatic Codex restart behavior.

**Verification:**
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action CodexGatewayEnable -DryRun`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action CodexGatewayRollback -DryRun`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action CodexApiProjectionRepair -DryRun`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/operator.ps1 -Action CodexOauthProjectionRepair -DryRun`

**Dependencies:** CCHS-005D, direct projection repair runbook.

## Recommended Execution Order
1. Complete CCHS-001 and preserve evidence.
2. Implement CCHS-002 as read-only guard.
3. Build CCHS-003 against mocks before any live Codex run.
4. Add CCHS-004 only after the status vocabulary is stable.
5. Execute CCHS-005A through CCHS-005F as the active gateway lane for `Codex -> LiteLLM -> Cockpit API service`.
6. Keep CCHS-005H available as the old/new operator switch: new gateway mode is preferred for local gateway work, while old direct API/OAuth projection remains supported for Codex App/CLI roundtrips.
7. Build a Cockpit-aware adapter only if the single Cockpit upstream model cannot satisfy account-label, group, quota, or routing requirements.

## Rollback
- Planning-only rollback: revert this file and its plan-index entry.
- Checker rollback: remove the read-only checker and tests; no live state should need restoration.
- Runner rollback: disable the CLI runner entrypoint and fall back to manual `codex exec` / `codex resume`.
- Gateway rollback: restore `config.toml` provider/base URL from backup, stop LiteLLM, disable Cockpit API service, remove any temporary firewall rule only if it was created by this lane, and return to Cockpit native account switching.
- Mode-switch rollback: run `scripts/operator.ps1 -Action CodexGatewayRollback`, then choose the old direct path explicitly with `CodexApiProjectionRepair` or `CodexOauthProjectionRepair` according to the current Cockpit account type.
