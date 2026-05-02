# 2026-05-03 Repo Slimming Closeout

## Rule
- `R1`: current landing point is Task 8 lane closeout; target home is an honest end-state report for the bounded repo-slimming and coding-speed lane.
- `R4`: this closeout records measured improvements and remaining limits without overstating physical repository reduction that did not happen yet.
- `R8`: before/after metrics, commands, evidence posture, guardrails, compatibility, and rollback are recorded here.

## Basis
- `docs/plans/repo-slimming-and-speed-plan.md`
- Fresh inventory and routing evidence now exist for all eight tasks in the lane.
- The right closeout question is not only "did the repo get smaller on disk", but "did the default active work surface, operator entrypoints, timing visibility, and archive/retention controls become more bounded and more executable without weakening governance".

## Changes
- Closed the bounded lane through inventory, archive indexing, repo-map routing, README slimming, `runtime-flow-preset` responsibility split, gate-timing split, and operator UI screenshot retention.
- Added executable dry-run/archive tooling instead of moving history blindly:
  - `scripts/archive-change-evidence.py`
  - `scripts/prune-operator-ui-screenshots.py`
- Added focused tests for each new control surface:
  - `tests/runtime/test_archive_change_evidence.py`
  - `tests/runtime/test_repo_slimming_surface.py`
  - `tests/runtime/test_repo_map_context_artifact.py`
  - `tests/runtime/test_runtime_flow_preset.py`
  - `tests/runtime/test_operator_ui_evidence_retention.py`
- Kept current operator entrypoints and hard-gate semantics stable while making the default fast/readiness paths clearer and timed.

## Before And After

### Repository Surface
- Before baseline (`2026-05-02` inventory):
  - `visible_surface.file_count=1154`
  - `visible_surface.byte_count=16097152` (`15.35 MB`)
  - `text_surface.file_count=1123`
  - `text_surface.line_count=184362`
  - `docs/change-evidence.file_count=572`
  - `docs/change-evidence.byte_count=9455870` (`9.02 MB`)
- After closeout (`2026-05-03` inventory):
  - `visible_surface.file_count=1174`
  - `visible_surface.byte_count=16186900` (`15.44 MB`)
  - `text_surface.file_count=1143`
  - `text_surface.line_count=186696`
  - `docs/change-evidence.file_count=585`
  - `docs/change-evidence.byte_count=9516948` (`9.08 MB`)
- Honest interpretation:
  - Physical repository size did **not** shrink in this lane because the work added executable guards, focused tests, fresh closeout evidence, and manifest-backed dry-run controls without yet moving archive candidates.
  - The lane still improved the active working posture by making archive-heavy surfaces explicitly excluded or classified rather than relying on operator memory.

### Context Budget
- Before repo-map artifact:
  - `selected_file_count=31`
  - `estimated_token_cost=5988`
  - `max_tokens=6000`
- After repo-map routing closeout:
  - `selected_file_count=31`
  - `estimated_token_cost=5985`
  - `excluded_archive_candidate_count=231`
  - `required_file_override_count=0`
  - `decision=keep`
- Result:
  - Token budget stayed under the `6000` ceiling while archive-heavy screenshot, snapshot, backup, and raw-run surfaces became first-class exclusions instead of implicit discipline.

### Fast And Readiness Timing
- `.\run.ps1 fast` closeout run:
  - `build` passed
  - shared `RuntimeQuick` slice passed
  - `50` tests in `21.339s` for the quick gate on the latest closeout run
- Full runtime timing:
  - `docs/change-evidence/runtime-test-speed-latest.json`
  - `target_count=101`
  - `elapsed_seconds=188.40806289999819`
  - `failure_count=0`
- Slowest current runtime files:
  - `tests/runtime/test_attached_repo_e2e.py` `65.195s`
  - `tests/runtime/test_autonomous_next_work_selection.py` `64.679s`
  - `tests/runtime/test_runtime_flow_preset.py` `58.095s`
  - `tests/runtime/test_dependency_baseline.py` `50.637s`
  - `tests/runtime/test_runtime_evolution.py` `44.590s`

## Evidence Movement And Retention
- Evidence moved in this lane: none.
- Evidence that now stays current by explicit rule:
  - latest machine-readable refs in `docs/change-evidence/evidence-index.json`
  - root `operator-ui-current-*.png` screenshots
  - milestone screenshots named in the retention contract
- Evidence that is now explicitly archive-plannable but not yet moved:
  - historical snapshots
  - rule-sync backups
  - superseded target-repo raw run JSON
  - `16` operator UI screenshot archive candidates totaling `4226988` bytes
- Rollback posture:
  - every new surface is additive
  - archive/index tooling is dry-run-first
  - screenshot apply mode requires an archive manifest and rollback instructions
  - code/doc changes remain revertible through git history

## Guardrails That Now Exist
- Archive candidate groups are machine-readable via `docs/change-evidence/evidence-index.json`.
- Repo-map routing excludes archive-heavy surfaces by default and reports exclusion metrics.
- Root README and plan index no longer carry long completion history inline.
- `runtime-flow-preset.ps1` has a first extracted responsibility with focused regression coverage.
- `fast` now routes through the shared `RuntimeQuick` gate instead of a second handwritten test list.
- Full runtime timing now refreshes a stable latest artifact on successful runs.
- Operator UI screenshots now have an executable `latest / milestone / archive_candidate` contract with manifest-backed apply mode.

## Commands
- `python scripts/audit-repo-slimming-surface.py`
- `python scripts/prune-operator-ui-screenshots.py --dry-run --json`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File run.ps1 fast`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Verification
- `fast` passed and remained explicitly non-authoritative for delivery.
- `Docs` gate passed.
- `Contract` gate passed, including `agent-rule-sync`, `pre-change-review`, `repo-map-context-artifact`, and `functional-effectiveness`.
- `doctor-runtime` passed all hard checks; current output still includes `WARN codex-capability-degraded`, which remains a known host-capability boundary rather than a repo-slimming regression.

## Compatibility
- Hard-gate order remains `build -> test -> contract/invariant -> hotspot`.
- No rule-source or distributed-rule contract was weakened.
- No archive move was silently performed.
- The lane improved control surfaces and documentation truthfulness without claiming a physical archive cleanup that has not yet been applied.

## Rollback
- Revert the repo-slimming lane changes in git history if this optimization batch is rejected.
- Remove the lane-specific evidence files and helper scripts added by `Task 1` through `Task 8` only as part of a deliberate rollback, not piecemeal.
- If future archive moves are later applied, use the generated manifests to restore moved artifacts before reverting the policy surfaces.
