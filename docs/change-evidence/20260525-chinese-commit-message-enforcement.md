# 2026-05-25 Chinese Commit Message Enforcement

## Summary
Added repository-local `commit-msg` hooks so ordinary commits in this control repo and managed target repos must use a Chinese-first subject by default. This closes the repeated gap where prose rules said commit messages should prefer Chinese, but `git commit -m "English subject"` could still succeed.

## Basis
- User observed that commit messages kept appearing in English despite repeated `AGENTS.md` guidance.
- `AGENTS.md` is context guidance, not a deterministic permission or Git enforcement system.
- Global rule sources were already upgraded to `v9.53` with Chinese-first commit and Chinese-comment guidance; deterministic enforcement was still needed for local commits.

## Pre-change Review
- `pre_change_review`: reviewed the control repo rule sources, managed-file baseline, target rollout contract, hook installer, and existing target repo hook state before editing.
- `control_repo_manifest_and_rule_sources`: `rules/manifest.json` and rule sources already synchronized at `v9.53`; this change adds deterministic hooks rather than more prose.
- `user_level_deployed_rule_files`: global Codex/Claude/Gemini files were already deployed and verified by rule sync dry-run.
- `target_repo_deployed_rule_files`: target `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` files were already deployed and verified by rule sync dry-run.
- `target_repo_gate_scripts_and_ci`: target repos lacked repo-local `commit-msg` enforcement, so the governance baseline now manages `.githooks/commit-msg` and `scripts/hooks/commit-msg.ps1`.
- `target_repo_repo_profile`: target repo catalog and baseline were used as the rollout boundary; no ad-hoc repo outside catalog was modified.
- `target_repo_readme_and_operator_docs`: no target README/operator workflow contract required English-only Git subjects; technical identifiers remain allowed inside Chinese-first subjects.
- `current_official_tool_loading_docs`: current Codex rule behavior treats `AGENTS.md` as context, not a Git hook or permission layer, so deterministic enforcement belongs in hooks/baseline.
- `drift-integration decision`: observed drift between rule prose and actual target Git enforcement was integrated into managed baseline/templates, then applied by the standard rollout command.

## Files Changed
- `.githooks/commit-msg`
- `.governed-ai/managed-files/.githooks/commit-msg.provenance.json`
- `.governed-ai/managed-files/scripts/hooks/commit-msg.ps1.provenance.json`
- `scripts/hooks/commit-msg.ps1`
- `scripts/install-repo-hooks.ps1`
- `scripts/doctor-runtime.ps1`
- `docs/targets/templates/git-hooks/commit-msg`
- `docs/targets/templates/git-hooks/commit-msg.ps1`
- `docs/targets/target-repo-governance-baseline.json`
- `docs/targets/target-repo-rollout-contract.json`
- `docs/change-evidence/governance-hub-certification-report.json`
- `docs/change-evidence/runtime-test-speed-latest.json`
- `tests/runtime/test_repo_hook_enforcement.py`
- `tests/runtime/test_runtime_doctor.py`
- `tests/runtime/test_target_repo_governance_consistency.py`
- `tests/runtime/test_target_repo_rollout_contract.py`

## Behavior
- Ordinary commit subjects must contain Chinese text.
- Generated Git subjects beginning with `Merge `, `Revert `, `fixup!`, or `squash!` are allowed.
- Exceptional English-only commits require explicit opt-out with `GOVERNED_ALLOW_NON_CHINESE_COMMIT=1`.

## Commands

### Rule sync drift check
```powershell
python scripts/sync-agent-rules.py --scope All --fail-on-change
```
Result: `status=pass`, `entry_count=24`, `changed_count=0`, `blocked_count=0`; all global and target-repo rule files are already synchronized at `9.53`.

### Hook installation check
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/install-repo-hooks.ps1
git config --get core.hooksPath
```
Result: `OK git core.hooksPath=.githooks`, then `.githooks`.

### Hook tests
```powershell
python -m unittest tests.runtime.test_repo_hook_enforcement
```
Result before doctor coverage expansion: `Ran 8 tests ... OK`.

### Focused regression checks
```powershell
python -m unittest tests.runtime.test_repo_hook_enforcement tests.runtime.test_runtime_doctor tests.runtime.test_target_repo_governance_consistency tests.runtime.test_target_repo_rollout_contract
```
Result: `Ran 63 tests ... OK`.

### Target rollout
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json -FailFast
```
Result: `target_count=7`, `failure_count=0`. The six external target repos received `.githooks/commit-msg` and `scripts/hooks/commit-msg.ps1`; this control repo already had equivalent files.

### Target hooksPath normalization
```powershell
git -C <target> config core.hooksPath .githooks
```
Result: `ClassroomToolkit`, `skills-manager`, `github-toolkit`, `k12-question-graph`, `vps-ssh-launcher`, and `external/Cockpit-Tools-Local` now report `core.hooksPath=.githooks`.

### Target hook behavior probe
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File <target>/scripts/hooks/commit-msg.ps1 -CommitMessagePath <english-message>
pwsh -NoProfile -ExecutionPolicy Bypass -File <target>/scripts/hooks/commit-msg.ps1 -CommitMessagePath <chinese-message>
```
Result for all six external target repos: English-only subject `fix sync drift` returned exit code `1`; Chinese subject `修复中文提交约束` returned exit code `0`.

### Target governance consistency
```powershell
python scripts/verify-target-repo-rollout-contract.py
python scripts/verify-target-repo-governance-consistency.py
```
Result: rollout contract `status=pass`; governance consistency `status=pass`, `drift_count=0`.

### Pre-change review retry
```powershell
python scripts/verify-pre-change-review.py
```
Result: `status=pass`, `matched_evidence=docs/change-evidence/20260525-chinese-commit-message-enforcement.md`.

### Full hard gates
```powershell
git diff --check
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```
Result: whitespace check passed with line-ending warnings only; build passed; Runtime passed with `111` test files and `failures=0`; Contract passed including `agent-rule-sync`, `pre-change-review`, and `functional-effectiveness`; Doctor exited `0` and now reports `OK repo-hook-commit-msg` and `OK repo-hook-commit-msg-script`. Existing `WARN codex-capability-degraded` remains non-blocking for this hook rollout.

## Gate Status
| gate | status | reason | alternative_verification | evidence_link | expires_at |
|---|---|---|---|---|---|
| build | `active` | `scripts/build-runtime.ps1` passed | `git diff --check` | `docs/change-evidence/20260525-chinese-commit-message-enforcement.md` | `n/a` |
| test | `active` | `verify-repo.ps1 -Check Runtime` passed with `111` test files and `failures=0` | focused 63-test regression slice | `docs/change-evidence/20260525-chinese-commit-message-enforcement.md` | `n/a` |
| contract/invariant | `active` | `verify-repo.ps1 -Check Contract` passed, including `agent-rule-sync`, `pre-change-review`, and target governance consistency | rule sync dry-run and hook behavior probe | `docs/change-evidence/20260525-chinese-commit-message-enforcement.md` | `n/a` |
| hotspot | `active` | `doctor-runtime.ps1` exited 0 and checks both pre-commit and commit-msg hooks; existing `codex-capability-degraded` warning is non-blocking for this change | target hook behavior probe | `docs/change-evidence/20260525-chinese-commit-message-enforcement.md` | `n/a` |

## Rollback
Remove `.githooks/commit-msg`, `scripts/hooks/commit-msg.ps1`, the two target templates, baseline/rollout-contract entries, doctor checks, and related tests; rerun `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/install-repo-hooks.ps1`, `python scripts/verify-target-repo-governance-consistency.py`, and the hook tests. For local target repos only, rollback `core.hooksPath` with `git -C <target> config --unset core.hooksPath` or restore its previous value.
