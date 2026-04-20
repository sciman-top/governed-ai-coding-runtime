# 20260420 Github-Toolkit And Vps-Ssh-Launcher One-Click Validation

## Goal
Apply governed one-click runtime flows to `github-toolkit` and `vps-ssh-launcher`, then verify real effectiveness with deny/pass write probes.

## Targets
- `github-toolkit` -> `D:\OneDrive\CODE\github-toolkit`
- `vps-ssh-launcher` -> `D:\OneDrive\CODE\vps-ssh-launcher`

## Execution Entry
- `scripts/runtime-flow.ps1`

## Applied Steps
For each target:
1. `onboard` (explicit gate commands: `python --version` for build/test/contract)
2. `daily` deny probe: write to `.governed-ai/runtime-probe-<ts>.txt` (expected deny)
3. `daily` allowed probe: write to `docs/runtime-probe-<ts>.txt` (expected execute)

## Summary Results
- `github-toolkit`
  - onboard: `pass`, attachment: `healthy`
  - deny probe: `fail` with `write_execution_status=denied`
  - deny reason: `write path is outside allowed scopes: .governed-ai/runtime-probe-20260420230743.txt`
  - allowed probe: `pass`, verify: `{contract: pass, test: pass}`, write: `executed`
  - probe landed: `D:\OneDrive\CODE\github-toolkit\docs\runtime-probe-20260420230743.txt`
- `vps-ssh-launcher`
  - onboard: `pass`, attachment: `healthy`
  - deny probe: `fail` with `write_execution_status=denied`
  - deny reason: `write path is outside allowed scopes: .governed-ai/runtime-probe-20260420230759.txt`
  - allowed probe: `pass`, verify: `{contract: pass, test: pass}`, write: `executed`
  - probe landed: `D:\OneDrive\CODE\vps-ssh-launcher\docs\runtime-probe-20260420230759.txt`

## Machine Evidence
- run summary:
  - `docs/change-evidence/target-repo-runs/summary-github-vps.json`
- raw run outputs:
  - `docs/change-evidence/target-repo-runs/github-toolkit-onboard-20260420230743.json`
  - `docs/change-evidence/target-repo-runs/github-toolkit-daily-deny-20260420230743.json`
  - `docs/change-evidence/target-repo-runs/github-toolkit-daily-allow-20260420230743.json`
  - `docs/change-evidence/target-repo-runs/vps-ssh-launcher-onboard-20260420230759.json`
  - `docs/change-evidence/target-repo-runs/vps-ssh-launcher-daily-deny-20260420230759.json`
  - `docs/change-evidence/target-repo-runs/vps-ssh-launcher-daily-allow-20260420230759.json`
- allowed-probe handoff/replay refs:
  - github-toolkit handoff: `artifacts/task-github-toolkit-daily-allow-20260420230743/task-github-toolkit-daily-allow-20260420230743-write-f9c83fd7d8dc/handoff/write-flow.json`
  - github-toolkit replay: `artifacts/task-github-toolkit-daily-allow-20260420230743/task-github-toolkit-daily-allow-20260420230743-write-f9c83fd7d8dc/replay/write-flow.json`
  - vps-ssh-launcher handoff: `artifacts/task-vps-ssh-launcher-daily-allow-20260420230759/task-vps-ssh-launcher-daily-allow-20260420230759-write-14637518ed0f/handoff/write-flow.json`
  - vps-ssh-launcher replay: `artifacts/task-vps-ssh-launcher-daily-allow-20260420230759/task-vps-ssh-launcher-daily-allow-20260420230759-write-14637518ed0f/replay/write-flow.json`

## Conclusion
- One-click attach-first flow is effective on both requested target repos.
- Guardrails deny out-of-scope writes consistently.
- Allowed-scope writes execute successfully and produce replay/handoff evidence.

## Optional Cleanup
If probe files should be removed:
- `D:\OneDrive\CODE\github-toolkit\docs\runtime-probe-20260420230743.txt`
- `D:\OneDrive\CODE\vps-ssh-launcher\docs\runtime-probe-20260420230759.txt`
