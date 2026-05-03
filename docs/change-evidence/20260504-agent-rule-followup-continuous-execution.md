# Agent Rule Follow-up Continuous Execution

- date: 2026-05-04
- rule_ids: R1, R2, R4, R6, R8, E4
- risk: low
- current_landing: `scripts/classify-target-repo-worktree-changes.py`, `tests/runtime/test_target_repo_worktree_change_classification.py`, `docs/change-evidence/20260504-target-repo-worktree-change-classification.json`
- target_landing: deterministic post-sync worktree classification plus fresh host rule-load evidence
- rollback: revert this change set from git history; the script is read-only and does not mutate target repos

## Goal
Continue the v9.51 rule-family work by converting the remaining manual review observations into executable evidence:

- separate managed rule/profile/provenance changes from unrelated target-local worktree changes;
- run fresh Codex/Claude/Gemini sessions to verify the new rules are actually loaded;
- keep Codex native attach degradation and Gemini host warnings as host readiness evidence instead of treating them as repo-rule failures.

## Changes
- Added `scripts/classify-target-repo-worktree-changes.py`.
  - Inputs: target catalog, rule manifest, repo/code/runtime roots.
  - Output categories: `managed_rule_file`, `managed_repo_profile`, `managed_file_provenance`, `governance_local_state`, `control_repo_current_change`, `target_local_unrelated`.
  - The script is read-only. `--fail-on-unrelated` is opt-in for stricter pipelines.
  - `--output-path` writes a JSON report into evidence.
- Added `tests/runtime/test_target_repo_worktree_change_classification.py`.
  - Covers managed rule/profile/provenance classification.
  - Covers non-zero behavior for `--fail-on-unrelated`.
  - Covers `self-runtime` as control-repo current changes instead of target-local unrelated drift.
  - Covers `--output-path`.
- Wrote the current report to `docs/change-evidence/20260504-target-repo-worktree-change-classification.json`.

## Verification
- `python -m unittest tests.runtime.test_target_repo_worktree_change_classification`
  - result: pass, `Ran 4 tests`.
- `python -m unittest tests.runtime.test_target_repo_worktree_change_classification tests.runtime.test_agent_rule_sync tests.runtime.test_target_repo_governance_consistency`
  - result: pass, `Ran 41 tests`.
- `python scripts/classify-target-repo-worktree-changes.py --output-path docs/change-evidence/20260504-target-repo-worktree-change-classification.json`
  - result: `status=attention`, `target_count=6`, `failed_count=0`, `unrelated_change_count=2`.
  - managed-only targets: `classroomtoolkit`, `github-toolkit`, `self-runtime`, `skills-manager`, `vps-ssh-launcher`.
  - target-local unrelated target: `k12-question-graph`.
  - unrelated paths: `tools/run-gates.ps1`, `docs/evidence/g004-pgpass-installer-dry-run-report.json`.
- `python scripts/sync-agent-rules.py --scope All --fail-on-change`
  - result: pass, `entry_count=21`, `changed_count=0`, `blocked_count=0`.
- `python scripts/verify-target-repo-governance-consistency.py`
  - result: pass, `target_count=6`, `drift_count=0`.
- `python scripts/verify-pre-change-review.py`
  - result: pass, matched `docs/change-evidence/20260504-agent-rule-v951-k12-sync.md`.
- Hard gate order:
  - build: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` passed with `OK python-bytecode` and `OK python-import`.
  - test: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` passed `104 test files`, `failures=0`, plus `OK runtime-unittest`, `OK runtime-service-parity`, and `OK runtime-service-wrapper-drift-guard`.
  - contract/invariant: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` passed, including `target-repo-governance-consistency`, `agent-rule-sync`, `pre-change-review`, and `functional-effectiveness`.
  - hotspot: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` exited `0`; existing `WARN codex-capability-degraded` remains host readiness evidence.

## Fresh Rule Load Checks
- Codex:
  - command: `codex exec --cd D:\CODE\governed-ai-coding-runtime --sandbox read-only --ephemeral --output-last-message docs\change-evidence\20260504-codex-rule-load-check.txt "..."`
  - result: answered `v9.51` and `build -> test -> contract/invariant -> hotspot`.
  - deterministic support: `codex debug prompt-input "load check"` showed the model-visible prompt includes `AGENTS.md - Universal Agent Protocol v9.51` and the project `GlobalUser/AGENTS.md v9.51` rule body.
- Claude:
  - first attempt: `--max-budget-usd 0.05` failed with `error_max_budget_usd`; this was a verification parameter issue.
  - second attempt: `claude --print --output-format json --permission-mode plan --tools "" --no-session-persistence --max-budget-usd 0.25 "..."`
  - result: answered `v9.51` and `build -> test -> contract/invariant -> hotspot`.
- Gemini:
  - command: `gemini --approval-mode plan --output-format json --prompt "..."`
  - result: answered `v9.51` and `build -> test -> contract/invariant -> hotspot`.

## Host Readiness Notes
- Codex:
  - `codex status` still fails in this non-interactive context with `Error: stdin is not a terminal`.
  - `codex debug prompt-input` is useful as model-visible prompt evidence, but it does not prove the native attach status handshake required to clear `WARN codex-capability-degraded`.
  - Decision: keep `WARN codex-capability-degraded` as bounded host readiness evidence, not a rule-sync failure.
- Gemini:
  - `gemini` and `gemini skills list` report MCP issues and repeated skill conflict warnings where `C:\Users\sciman\.agents\skills\...` overrides duplicate `C:\Users\sciman\.gemini\skills\...` entries.
  - Gemini also reports `.pytest_cache` EPERM scan warnings.
  - Decision: record as host configuration hygiene items. Do not delete or rewrite user skill directories in this repo-rule task.

## Compatibility
- The new classifier does not change existing sync or consistency gates.
- It can be promoted later into an operator/reporting surface if repeated target-local drift causes review cost.
- Host warnings remain separated from repository correctness: rule loading is verified, while native attach and Gemini skill/MCP hygiene remain host readiness follow-ups.
