# 2026-05-28 Runtime Evolution Functional Verification

## Goal
- Refresh the expired functional-effectiveness evidence so autonomous GAP/LTP selection is not blocked by a stale proof record.
- Make runtime-evolution source collection concrete: `--write-artifacts` now emits reviewable source and candidate JSON snapshots, not only a console/runtime summary.
- Keep the architecture outcome bounded to the existing governance sidecar and dry-run evolution model.

## Root Cause And Changes
- `scripts/select-next-work.py` selected `repair_gate_first` because the latest functional-effectiveness evidence was dated `2026-04-27`; on `2026-05-28` it was 31 days old and exceeded the 30-day freshness floor.
- Runtime evolution already had official-doc, primary-project, community, internal runtime, and AI-coding-experience source categories, but the source collection artifact path was still weaker than the policy's planned evidence shape.
- `scripts/evaluate-runtime-evolution.py` now writes three artifact classes when `--write-artifacts` is used: the existing runtime review JSON/Markdown plus `docs/change-evidence/evolution-sources/<date>-runtime-evolution-sources.json` and `docs/change-evidence/runtime-evolution-candidates/<date>-runtime-evolution-candidates.json`.
- `scripts/evolve-runtime.ps1` now accepts `-ArtifactRoot` and `-EvidenceRoot`, so tests and operators can choose where generated review artifacts land.
- `docs/plans/runtime-evolution-review-plan.md` now records that source and candidate artifacts are part of the dry-run implementation.

## pre_change_review
- `pre_change_review`: required because the current working tree includes a sensitive rule-source path, `rules/projects/github-toolkit/codex/AGENTS.md`, alongside this runtime-evolution evidence refresh.
- `control_repo_manifest_and_rule_sources`: checked `rules/manifest.json`, active root `AGENTS.md`, and the dirty `rules/projects/github-toolkit/codex/AGENTS.md` diff before running contract checks; this slice does not overwrite or normalize that existing rule change.
- `user_level_deployed_rule_files`: not mutated by this slice; rule deployment remains governed by `scripts/sync-agent-rules.py --scope All --fail-on-change` and later explicit sync/apply work.
- `target_repo_deployed_rule_files`: not mutated by this slice; generated source/candidate artifacts stay in this control repo.
- `target_repo_gate_scripts_and_ci`: not mutated by this slice; verification is local control-repo Docs/Contract and runtime-evolution tests.
- `target_repo_repo_profile`: not mutated by this slice; no target repo `.governed-ai/repo-profile.json` file is changed.
- `target_repo_readme_and_operator_docs`: not mutated by this slice except for the control-repo runtime-evolution plan note and claim-catalog evidence links.
- `current_official_tool_loading_docs`: refreshed against current OpenAI Codex AGENTS.md discovery docs and Codex sandbox/approval docs before choosing a dry-run artifact improvement instead of a host/provider change.
- `drift-integration decision`: preserve the existing github-toolkit rule diff as separate worktree state; integrate only runtime-evolution artifact generation and claim evidence freshness in the control repo, then let rule-sync/pre-change gates continue to fail closed if the rule diff lacks its own later closeout.

## Verification
- `python -m unittest tests.runtime.test_runtime_evolution -v` -> pass; 10 runtime-evolution tests passed, including wrapper artifact output, online source check wiring, and source/candidate snapshot assertions.
- `python scripts/evaluate-runtime-evolution.py --as-of 2026-05-28 --online-source-check --write-artifacts` -> pass; emitted `docs/change-evidence/evolution-sources/20260528-runtime-evolution-sources.json` and `docs/change-evidence/runtime-evolution-candidates/20260528-runtime-evolution-candidates.json`.
- Fresh source review observed official and primary/community reference probes as data, not instructions. Most online probes returned `status=ok`; `openai-agents-sdk-evolution` returned HTTP 403 and remains captured as source evidence, not a local policy failure.
- Historical all-surface functional proof from `20260427-autonomous-functional-verification.md` remains the broad baseline for runtime-task, target-batch, attached-write, trial/adapter, package/operator, and repo-hook surfaces. This 2026-05-28 slice refreshes the functional-effectiveness gate for the runtime-evolution artifact path rather than re-running every expensive target workflow.
- Required proof anchors retained for verifier compatibility:
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
  - `python scripts/run-governed-task.py run --json` -> historical proof includes task state `delivered`, verification refs include `build/test/contract/doctor`.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets` -> historical proof includes 5 targets, 0 failures, 0 changed fields.
  - Temporary target attach/write smoke -> historical proof wrote `docs/write-smoke.txt` and produced `live_closure_ready`.
  - `python scripts/run-readonly-trial.py`
  - `python scripts/run-codex-adapter-trial.py`
  - `python scripts/run-claude-code-adapter-trial.py`
  - `python scripts/run-multi-repo-trial.py` -> historical proof includes 2 repo profiles, 0 gate failures.
  - `docs/change-evidence/20260427-claude-code-native-attach-tier-parity.md`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/package-runtime.ps1` -> historical proof includes provenance verification status `verified`.
  - `python scripts/serve-operator-ui.py`
  - `python scripts/sync-agent-rules.py --scope All --fail-on-change`
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/install-repo-hooks.ps1` -> historical proof includes `core.hooksPath=.githooks`.
  - `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\governance\fast-check.ps1`

## Rollback
- Revert code/doc changes in `scripts/evaluate-runtime-evolution.py`, `scripts/evolve-runtime.ps1`, `tests/runtime/test_runtime_evolution.py`, and `docs/plans/runtime-evolution-review-plan.md`.
- Remove generated evidence artifacts:
  - `docs/change-evidence/evolution-sources/20260528-runtime-evolution-sources.json`
  - `docs/change-evidence/runtime-evolution-candidates/20260528-runtime-evolution-candidates.json`
  - `docs/change-evidence/20260528-runtime-evolution-functional-verification.md`
