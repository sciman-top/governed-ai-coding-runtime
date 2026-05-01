# GAP-143 Evidence Recovery Posture Contract

## Goal
- Close the next low-risk governance gap after `GAP-142`: `refresh_evidence_first` must be backed by one machine-checkable recovery contract, not separate narrative checks.
- Keep new implementation and `LTP-01..06` work blocked while latest target-run evidence is fresh but still degraded to `process_bridge`.

## Risk
- Risk level: low.
- Change type: verification script, docs gate wiring, runtime test, backlog/seed/claim/evidence docs.
- Compatibility: no runtime execution semantics change; this only hardens the proof surface around existing selector and feedback outputs.

## Commands
- `python scripts/verify-evidence-recovery-posture.py --as-of 2026-05-01`
- `python -m unittest tests.runtime.test_evidence_recovery_posture tests.runtime.test_host_feedback_summary tests.runtime.test_autonomous_next_work_selection`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Key Output
- `verify-evidence-recovery-posture.py` returns `status=pass`.
- The selector still returns `next_action=refresh_evidence_first`, `evidence_state=stale`, and `ltp_decision=defer_all`.
- Host feedback reports `target_runs.status=attention`, `freshness_status=fresh`, and `degraded_latest_run_count=5`.
- Effect feedback keeps `decision=adjust` and preserves `target-repo-reuse-host-capability-gap`.
- The required recovery evidence rule is `fresh target run with codex_capability_status=ready and adapter_tier=native_attach`.

## Evidence
- `scripts/verify-evidence-recovery-posture.py` joins the selector, host-feedback target-run posture, and target-repo reuse effect report into one assertion.
- `scripts/verify-repo.ps1 -Check Docs` now runs `OK evidence-recovery-posture`.
- `tests/runtime/test_evidence_recovery_posture.py` verifies the live degraded recovery posture stays fail-closed.
- `docs/backlog/issue-ready-backlog.md` and `docs/backlog/issue-seeds.yaml` define `GAP-143`.
- `docs/product/claim-catalog.json` adds `CLM-012` so the recovery posture remains drift-checked.

## Pre-Change Review
- `pre_change_review`: this change touches `scripts/verify-repo.ps1`, so the sensitive gate wiring is recorded here before final closeout.
- `control_repo_manifest_and_rule_sources`: no `rules/manifest.json` or rule source files are changed; the recovery posture is a Docs gate addition, not a rule distribution change.
- `user_level_deployed_rule_files`: no user-level `AGENTS.md`, `CLAUDE.md`, or `GEMINI.md` deployed files are changed.
- `target_repo_deployed_rule_files`: no target-repo deployed rule files are changed.
- `target_repo_gate_scripts_and_ci`: target-repo gate scripts and CI are not changed; only this control repo's Docs gate now calls `verify-evidence-recovery-posture.py`.
- `target_repo_repo_profile`: no `.governed-ai/repo-profile.json` files are changed.
- `target_repo_readme_and_operator_docs`: README updates only reflect the new `GAP-143` completion state and do not change target-repo operator commands.
- `current_official_tool_loading_docs`: no Codex/Claude/Gemini loading model assumptions are changed.
- `drift-integration decision`: integrate the new recovery posture into the existing selector/host-feedback/effect-report chain instead of creating a separate LTP or host-replacement path.

## Rollback
- Revert the `GAP-143` script, test, gate wiring, backlog/seed, claim-catalog, roadmap, README, and this evidence file.
- After rollback, run `python scripts/select-next-work.py --as-of 2026-05-01` and `python scripts/host-feedback-summary.py --assert-minimum --max-target-runs 5` to confirm the previous `GAP-142` guard remains active.
