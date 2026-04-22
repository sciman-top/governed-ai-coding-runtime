# 20260422 Active Targets Unified Batch Validation

## Goal
对当前 active preset target 集做同批次、同口径的统一验证，输出最新总表，避免继续混用 `summary-latest.json`、`summary-allowedscope.json`、`summary-github-vps.json` 这些历史批次文件。

## Scope
- `docs/change-evidence/target-repo-runs/summary-active-targets-latest.json`
- `docs/change-evidence/target-repo-runs/summary-active-targets-20260422191507.json`
- `docs/change-evidence/target-repo-runs/summary-active-targets-rows-20260422191507.json`
- `docs/change-evidence/target-repo-runs/*-2026042219*.json`
- `docs/change-evidence/20260422-active-targets-unified-batch-validation.md`
- `docs/change-evidence/README.md`

## Batch
- `batch_stamp`: `20260422191507`
- targets source: `docs/targets/target-repos-catalog.json`
- target set:
  - `classroomtoolkit`
  - `github-toolkit`
  - `self-runtime`
  - `skills-manager`
  - `vps-ssh-launcher`

## Summary
| target | onboard | daily | verify_test | verify_contract | binding_state | attachment_health |
|---|---|---|---|---|---|---|
| `classroomtoolkit` | `pass` | `pass` | `pass` | `pass` | `healthy` | `healthy` |
| `github-toolkit` | `pass` | `pass` | `pass` | `pass` | `healthy` | `healthy` |
| `self-runtime` | `pass` | `pass` | `pass` | `pass` | `healthy` | `healthy` |
| `skills-manager` | `pass` | `pass` | `pass` | `pass` | `healthy` | `healthy` |
| `vps-ssh-launcher` | `pass` | `pass` | `pass` | `pass` | `healthy` | `healthy` |

## Evidence Outputs
- latest pointer:
  - `docs/change-evidence/target-repo-runs/summary-active-targets-latest.json`
- batch snapshot:
  - `docs/change-evidence/target-repo-runs/summary-active-targets-20260422191507.json`
- per-run expanded rows:
  - `docs/change-evidence/target-repo-runs/summary-active-targets-rows-20260422191507.json`
- raw run files:
  - `docs/change-evidence/target-repo-runs/classroomtoolkit-onboard-20260422191507.json`
  - `docs/change-evidence/target-repo-runs/classroomtoolkit-daily-20260422191548.json`
  - `docs/change-evidence/target-repo-runs/github-toolkit-onboard-20260422191627.json`
  - `docs/change-evidence/target-repo-runs/github-toolkit-daily-20260422191633.json`
  - `docs/change-evidence/target-repo-runs/self-runtime-onboard-20260422191639.json`
  - `docs/change-evidence/target-repo-runs/self-runtime-daily-20260422191858.json`
  - `docs/change-evidence/target-repo-runs/skills-manager-onboard-20260422192111.json`
  - `docs/change-evidence/target-repo-runs/skills-manager-daily-20260422192117.json`
  - `docs/change-evidence/target-repo-runs/vps-ssh-launcher-onboard-20260422192122.json`
  - `docs/change-evidence/target-repo-runs/vps-ssh-launcher-daily-20260422192129.json`

## Verification
### Unified execution
1. dynamic catalog batch execution against all targets in `docs/targets/target-repos-catalog.json`
- result:
  - `10 / 10` flows returned `exit_code = 0`
  - all `overall_status = pass`
  - all `verify_test = pass`
  - all `verify_contract = pass`
  - all `binding_state = healthy`

2. `Get-Content docs/change-evidence/target-repo-runs/summary-active-targets-latest.json -Raw`
- result:
  - confirms 5-target same-batch summary
  - confirms `batch_stamp = 20260422191507`

### Final gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- result: `OK python-bytecode`, `OK python-import`

2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- result: runtime tests pass

3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- result: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`

4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- result: doctor pass including active gate-command visibility

5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- result: docs checks pass including active markdown links and claim drift sentinels

## Risks
- `summary-active-targets-latest.json` 是当前 active target 集的最新指针，不会覆盖历史批次 summary 的审计价值；历史 summary 仍然保留，调用方不能混用不同 summary 语义。
- 该 latest summary 仍是“显式登记 target 集”的结果，不代表自动发现所有 `D:\CODE\*` 仓。

## Rollback
Delete generated summary artifacts if this batch should be discarded:
- `docs/change-evidence/target-repo-runs/summary-active-targets-latest.json`
- `docs/change-evidence/target-repo-runs/summary-active-targets-20260422191507.json`
- `docs/change-evidence/target-repo-runs/summary-active-targets-rows-20260422191507.json`
- `docs/change-evidence/target-repo-runs/*-2026042219*.json`

Revert docs:
- `docs/change-evidence/20260422-active-targets-unified-batch-validation.md`
- `docs/change-evidence/README.md`
