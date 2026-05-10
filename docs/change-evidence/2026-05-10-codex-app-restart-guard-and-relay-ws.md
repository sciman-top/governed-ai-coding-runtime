# Codex App Restart Guard And Relay WebSocket Evidence

- date: 2026-05-10
- rule: R4/R8
- risk: medium, because restore scripts overwrite local Codex/Cockpit auth and state files when invoked by the operator
- destination: make Codex App restart testing recoverable without restarting or killing the running App from automation

## Current Facts

- `codex-cockpit --help` reported `interop_repair_status=pass`, `profile=shared-cockpit-auth`, `forced_login_method=chatgpt`, `provider_base_url=https://api.openai.com/v1`, `model_provider=openai`.
- `codex login status` reported `Logged in using ChatGPT`.
- The repair path does not invoke `codex app`, `codex-cockpit-app-restart`, `Stop-Process`, or the restore script. A later process snapshot showed Codex App/app-server running normally with root PID `25960` and app-server PID `29588`, both started at `2026-05-10T21:48:32/33`; that restart was not triggered by the repair commands recorded here.
- Cockpit provider storage still contains provider `35.213.82.91` at `http://35.213.82.91:8003/v1`.
- The current durable shared-history rule is built-in `model_provider = "openai"` plus top-level `openai_base_url` for API relay routing. Defining `[model_providers.openai]` is forbidden because Codex reserves built-in provider IDs.
- Live `C:\Users\sciman\.codex\config.toml` was checked and does not define `[model_providers.openai]`.

## Relay Probe

Command summary, with API keys redacted from output:

```powershell
GET  http://35.213.82.91:8003/v1/models
POST http://35.213.82.91:8003/v1/responses
WS   ws://35.213.82.91:8003/v1/responses
```

Key output:

```text
MODELS_OK count=77 first=gemini-3.1-flash-image-landscape
RESPONSES_HTTP_OK text=HTTP_RESPONSES_OK
RESPONSES_WS_FAIL The server returned status code '404' when status code '101' was expected.
```

Interpretation:

- The remote relay is not offline.
- HTTP Responses API works.
- The missing capability is the WebSocket upgrade route for `/v1/responses`.
- Client-side `model_providers.<id>.supports_websockets = false` can suppress the warning only for a custom provider bucket. It is not currently applied to the built-in `openai` bucket because Codex reserves built-in provider IDs and `openai_base_url` is the only built-in provider base URL override.

## Restart Guard

Added scripts:

- `scripts/Backup-CodexAppRestartState.ps1`
- `scripts/Restore-CodexAppRestartState.ps1`

Backup command:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Backup-CodexAppRestartState.ps1 -Json
```

Created backups during this repair window:

```text
C:\Users\sciman\.codex\backups\codex-app-restart-guard\20260510-214035
C:\Users\sciman\.codex\backups\codex-app-restart-guard\20260510-215541
```

The backup includes:

- `C:\Users\sciman\.codex\config.toml`
- `C:\Users\sciman\.codex\auth.json`
- `C:\Users\sciman\.codex\state_5.sqlite`
- `C:\Users\sciman\.codex\state_5.sqlite-wal`
- `C:\Users\sciman\.codex\state_5.sqlite-shm`
- Cockpit Codex account/provider index files
- Cockpit `codex_accounts` directory
- process snapshot

Restore protection check:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\Restore-CodexAppRestartState.ps1 -Latest
```

Expected key output while Codex App is running:

```text
Codex App/app-server is still running (...). Close it first, then rerun this restore command.
```

## Operator Recovery

If a manual Codex App restart fails and no Codex App/app-server process is running, restore the latest restart guard backup with:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File D:\CODE\governed-ai-coding-runtime\scripts\Restore-CodexAppRestartState.ps1 -Latest
```

The restore script first creates a pre-restore backup under:

```text
C:\Users\sciman\.codex\backups\codex-app-restart-guard\restore-preimage-<timestamp>
```

## Provider Guard And Switch Probes

Code guard added:

- `scripts/codex-interop-check.py` fails closed with `codex_builtin_provider_overrides_absent` if `config.toml` defines any reserved built-in provider table such as `[model_providers.openai]`, `[model_providers."openai"]`, `[model_providers.ollama]`, or `[model_providers.lmstudio]`.
- The repair path removes legacy relay provider tables and built-in provider override tables, then uses `model_provider = "openai"` and top-level `openai_base_url` for Cockpit API relay projection.
- Regression coverage in `tests/runtime/test_codex_shared_launcher.py` starts from an illegal `[model_providers.openai]` fixture, verifies dry-run failure, applies repair, and verifies the table is removed.

Live switch/probe summary, without restarting Codex App:

```text
API account: codex_apikey_8b8853f15e823dc53bd156163035bc78
API base URL: http://35.213.82.91:8003/v1
API probe targets: governed-ai-coding-runtime, ClassroomToolkit, github-toolkit, k12-question-graph, skills-manager, vps-ssh-launcher
API result: all 6 codex exec probes passed

OAuth account: codex_d5918a432f646d7a4f7070307400cc61
OAuth email: sciman.phys@gmail.com
OAuth probe targets: governed-ai-coding-runtime, ClassroomToolkit, github-toolkit, k12-question-graph, skills-manager, vps-ssh-launcher
OAuth result: all 6 codex exec probes passed

Restored current Cockpit account: codex_f9c21376dc05ab18f5d70f4e61b66a34
Restored current email: agi.phys@gmail.com
Restored login status: Logged in using ChatGPT
```

History visibility probe after restore:

```text
codex-history-view-diagnose: status=pass
non-archived App-source rows loaded: 342
default page limit: 50
visible targets: governed-ai-coding-runtime, ClassroomToolkit, github-toolkit, k12-question-graph, skills-manager, vps-ssh-launcher
```

## Verification

```text
python -m unittest tests.runtime.test_codex_shared_launcher
Ran 12 tests in 2.588s, OK

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1
OK python-bytecode
OK python-import

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime
Completed 109 test files in 125.930s; failures=0
OK runtime-unittest
OK runtime-service-parity
OK runtime-service-wrapper-drift-guard

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Contract
OK schema-json-parse
OK schema-example-validation
OK agent-rule-sync
OK pre-change-review
OK functional-effectiveness

pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\doctor-runtime.ps1
OK hard checks; residual WARN codex-capability-degraded is the existing native attach/status-handshake warning.

python scripts\codex-interop-check.py --quick-launch ...
status=pass
codex_builtin_provider_overrides_absent=pass
codex_thread_provider_distribution=openai:1636
codex_auth_matches_cockpit_current_account=pass
```

## Rollback

- Delete the two added scripts if the restart guard entrypoint is no longer wanted.
- Use git history to revert this evidence file.
- Existing live Codex/Cockpit config was not restored or overwritten during this change.
