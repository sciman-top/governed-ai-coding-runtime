# 2026-05-03 Change Evidence Archive Apply

## Rule
- `R1`: current landing point is the first manifest-backed evidence archive apply; target home is `docs/change-evidence/archive/change-evidence/20260502T164309Z/`.
- `R4`: this is a medium-risk evidence movement already authorized by the user's continuous-execution instruction; active target-run evidence was restored after gate feedback showed it still belongs in the active surface.
- `R8`: commands, key output, compatibility, rollback, and manifest path are recorded here.

## Basis
- The previous repo-slimming lane left archive candidates classified but not physically moved.
- The active work surface was still dominated by historical snapshots, rule-sync backups, and historical UI screenshots.
- `target-repo-runs/*.json` is still consumed by host feedback and effect-report gates, so it is not part of this generic archive apply.

## pre_change_review
- `control_repo_manifest_and_rule_sources`: checked `rules/manifest.json` and the self-runtime managed sources under `rules/projects/governed-ai-coding-runtime/*`; self-runtime project entries now consistently declare `9.49` after the project rules were updated from `v9.47` to `v9.49`.
- `user_level_deployed_rule_files`: `python scripts/sync-agent-rules.py --scope All --fail-on-change` reported global user-level Codex/Claude/Gemini rule targets as `skipped_same_hash` with source and target version `9.49`.
- `target_repo_deployed_rule_files`: the same sync dry-run reported self-runtime deployed `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` as `skipped_same_hash`; other target repos remained at their existing `9.47` source/target hashes and were not changed by this slice.
- `target_repo_gate_scripts_and_ci`: this slice does not change target-repo gate scripts or CI; local verification remains the self-repo gate chain plus `scripts/sync-agent-rules.py --scope All --fail-on-change`.
- `target_repo_repo_profile`: no `.governed-ai/repo-profile.json` or target repo profile files were changed.
- `target_repo_readme_and_operator_docs`: root `README.md` and target repo operator docs were not changed; evidence docs were limited to `docs/change-evidence/README.md` and this closeout note.
- `current_official_tool_loading_docs`: no new external loading semantics were introduced; the project rule change only aligns the self-runtime project files with the already-loaded global `GlobalUser/AGENTS.md v9.49` contract.
- `drift-integration decision`: integrate the self-runtime version drift in the manifest-managed source files and deployed self-runtime copies, then confirm with the rule sync dry-run instead of accepting same-version content drift or manually patching only one side.

## Changes
- Added manifest-backed apply mode to [archive-change-evidence.py](/D:/CODE/governed-ai-coding-runtime/scripts/archive-change-evidence.py).
- Kept latest and milestone operator UI screenshots out of the generic archive candidate set.
- Moved historical snapshots, rule-sync backups, and historical operator UI screenshots under [archive/change-evidence](/D:/CODE/governed-ai-coding-runtime/docs/change-evidence/archive/change-evidence/20260502T164309Z).
- Wrote rollback manifest [20260502T164309Z.json](/D:/CODE/governed-ai-coding-runtime/docs/change-evidence/archive/change-evidence-manifests/20260502T164309Z.json).
- Restored `50` target-run JSON files after `Docs` gate proved they remain active host-feedback evidence.

## Commands
- `python -m unittest tests.runtime.test_archive_change_evidence tests.runtime.test_operator_ui_evidence_retention`
- `python scripts/archive-change-evidence.py --dry-run --json`
- `python scripts/archive-change-evidence.py --apply --json`
- `git add -A`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

## Key Output
- Pre-apply generic archive candidates after latest/milestone filtering:
  - `historical_snapshots`: `49` files, `0.28 MB`
  - `rule_sync_backups`: `115` files, `0.94 MB`
  - `target_repo_raw_runs`: `50` files, `1.43 MB`
  - `docs_operator_ui_screenshots`: `13` files, `3.71 MB`
- Initial apply moved `227` files.
- Target-run restore moved `50` files back to `docs/change-evidence/target-repo-runs/`.
- Effective generic archive movement: `177` historical files.
- Post-restore archive dry-run reports `0` remaining generic archive candidates.

## Compatibility
- `target-repo-runs/*.json` remains active because `scripts/host-feedback-summary.py` and `scripts/verify-target-repo-reuse-effect-report.py` read that location directly.
- Generic archive apply no longer includes target-run JSON; target-run pruning must use `scripts/prune-target-repo-runs.py`.
- Markdown link verification passed before host-feedback checks; the host-feedback failure was a scope signal, not a broken-link failure.

## Rollback
- Use [20260502T164309Z.json](/D:/CODE/governed-ai-coding-runtime/docs/change-evidence/archive/change-evidence-manifests/20260502T164309Z.json) to move each archived file back to its recorded `source`.
- Target-run JSON files were already restored to their original active locations.
- Revert this commit if the archive layout itself is rejected.
