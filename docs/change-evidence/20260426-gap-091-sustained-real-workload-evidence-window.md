# 20260426 GAP-091 Sustained Real-Workload Evidence Window

## Goal
Close `GAP-091` by running the existing all-target runtime evidence window, classifying failures by long-term trigger family, and recording remediation without starting any `LTP-01..05` implementation package.

## Evidence Window
| run | command | exit_code | key_output | classification |
|---|---|---:|---|---|
| initial all-target daily | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -FlowMode daily -Json` | `1` | `target_count=5`; `failure_count=2`; failed targets: `classroomtoolkit`, `skills-manager`; passed targets: `github-toolkit`, `self-runtime`, `vps-ssh-launcher` | target gate command shell-compatibility drift |
| target profile remediation | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target classroomtoolkit -FlowMode onboard -Overwrite -Json` | `0` | `overall_status=pass`; `results test=pass, contract=pass`; `problem_trace.has_problem=false`; `failure_signature=none` | remediation proof |
| target profile remediation | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -Target skills-manager -FlowMode onboard -Overwrite -Json` | `0` | `overall_status=pass`; `results test=pass, contract=pass`; `problem_trace.has_problem=false`; `failure_signature=none` | remediation proof |
| final all-target daily | `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -FlowMode daily -Json` | `0` | `target_count=5`; `failure_count=0`; all targets pass | sustained window green |

## Failure Classification
The initial two failures emitted:

```text
'.' is not recognized as an internal or external command, operable program or batch file.
```

Root cause:
- `classroomtoolkit` target gate commands used dot-sourcing syntax without an explicit `pwsh -Command` wrapper in a batch-driven execution path.
- `skills-manager` target gate commands used relative PowerShell script invocation without explicit `pwsh -File` wrapping.

Remediation:
- `docs/targets/target-repos-catalog.json` now stores shell-explicit gate commands for the affected targets.
- `D:\CODE\ClassroomToolkit\.governed-ai\quick-test-slice.recommendation.json` was synced to the same explicit `pwsh -Command` form.
- Target `onboard -Overwrite` regenerated the runtime profiles and proved both affected targets pass their `test` and `contract` slices.

## LTP Trigger Classification
| package id | classification | reason |
|---|---|---|
| `LTP-01 orchestration-depth` | `watch` | The runtime flow coordinated five attached targets after target profile repair; no repeated pause/resume/compensation/retry graph failure was observed. |
| `LTP-02 policy-runtime-separation` | `not_triggered` | The failure was command-shell compatibility drift, not policy cardinality or audit burden. |
| `LTP-03 data-plane-scaling` | `watch` | No event, replay, query, or retention pressure surfaced in the all-target daily window; keep watching future target-run volume. |
| `LTP-04 multi-host-first-class` | `watch` | The issue was target command portability inside existing Codex/local execution paths, not evidence that a new first-class host adapter must start now. |
| `LTP-05 operations-hardening` | `not_triggered` | After profile repair, all five targets passed; operational failure is not the current main blocker. |

## Acceptance Mapping
- `representative real-workload evidence exists`: satisfied by the all-target daily window over five configured targets.
- `runtime failures are separated from target-repo business gate failures`: satisfied by classifying the initial failure as target gate command shell-compatibility drift and proving remediation through target onboard.
- `no LTP is marked triggered without command evidence and rollback notes`: satisfied; no LTP is marked `triggered`.

## Rollback
- Revert the catalog command updates in `docs/targets/target-repos-catalog.json`.
- Revert the generated target profile changes in `D:\CODE\ClassroomToolkit\.governed-ai\*` and `D:\CODE\skills-manager\.governed-ai\*` if this evidence window is rolled back.
- Re-run the final all-target daily command above after rollback to confirm whether the original shell-compatibility failure returns.
