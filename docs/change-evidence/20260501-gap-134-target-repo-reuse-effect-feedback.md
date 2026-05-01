# 2026-05-01 GAP-134 Target Repo Reuse Effect Feedback Harness

## Goal
Close `GAP-134` by proving on one real target repo that inherited controls, allowed overrides, gate execution, and effect metrics can be summarized into an operator-facing effect report with explicit keep/adjust/retire signals.

## Risk
- risk_tier: medium
- primary_risk: target-repo reuse could look healthy in contract space while still lacking measurable effect feedback or clear follow-up candidates
- compatibility_boundary: this change adds an effect-report builder, a verifier, and one real evidence report; it does not auto-sync target repos, mutate host policy, push, or merge

## Changes
- added [Target Repo Reuse Effect Report Builder](/D:/CODE/governed-ai-coding-runtime/scripts/build-target-repo-reuse-effect-report.py)
- added [Target Repo Reuse Effect Report Verifier](/D:/CODE/governed-ai-coding-runtime/scripts/verify-target-repo-reuse-effect-report.py)
- added [Target Repo Reuse Effect Feedback Tests](/D:/CODE/governed-ai-coding-runtime/tests/runtime/test_target_repo_reuse_effect_feedback.py)
- generated [ClassroomToolkit Effect Report](/D:/CODE/governed-ai-coding-runtime/docs/change-evidence/target-repo-runs/effect-report-classroomtoolkit.json) from real target-repo run evidence
- wired [scripts/verify-repo.ps1](/D:/CODE/governed-ai-coding-runtime/scripts/verify-repo.ps1) `-Check Contract` to require a verifier-backed effect report

## Pre-Change Review
pre_change_review: required because this change updates `scripts/verify-repo.ps1` and adds a verifier-backed evidence requirement.

control_repo_manifest_and_rule_sources: checked against `docs/backlog/issue-ready-backlog.md`, `docs/plans/governance-hub-reuse-and-controlled-evolution-plan.md`, `scripts/verify-repo.ps1`, and `docs/change-evidence/target-repo-runs/*.json` before editing.

user_level_deployed_rule_files: not changed by this implementation; the harness stays inside repository verification and evidence.

target_repo_deployed_rule_files: not changed by this implementation; the effect report reads existing target-repo run evidence and does not mutate the target repo.

target_repo_gate_scripts_and_ci: checked indirectly through the captured run evidence because the report reads real `verify_attachment`, gate results, and policy-decision refs from target-repo runs.

target_repo_repo_profile: checked indirectly through the latest target run because the report records whether inherited entrypoint policy is present in the target attachment status.

target_repo_readme_and_operator_docs: checked by updating repository status docs so `GAP-134` is not left as planned after the report and verifier are live.

current_official_tool_loading_docs: not changed by this implementation; the harness analyzes local evidence and does not alter host loading semantics.

drift-integration decision: integrate by requiring one verifier-backed effect report in `docs/change-evidence/target-repo-runs/`, so historical failures and current host degradation are converted into explicit candidates instead of chat-only notes.

## Verification
```powershell
python scripts/build-target-repo-reuse-effect-report.py --target classroomtoolkit
```

Result: pass. Key output: `baseline_run_ref=classroomtoolkit-daily-20260420225453.json`, `after_run_ref=classroomtoolkit-daily-20260501004238.json`, `decision=adjust`, `backlog_candidates=2`.

```powershell
python -m unittest discover -s tests/runtime -p "test_target_repo_reuse_effect_feedback.py"
```

Result: pass. Key output: `Ran 2 tests`, `OK`.

```powershell
python scripts/verify-target-repo-reuse-effect-report.py
```

Result: pass. Key output: `target=classroomtoolkit`, `decision=adjust`, `backlog_candidate_count=2`, `errors=[]`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

Result: pass. Key output includes `OK target-repo-reuse-effect-feedback`, `OK target-repo-rollout-contract`, `OK target-repo-governance-consistency`, and `OK functional-effectiveness`.

## Operator Outcome
- baseline run: `classroomtoolkit-daily-20260420225453.json` had `overall_status=fail`, `adapter_tier=native_attach`, and no inherited `required_entrypoint_policy`
- after run: `classroomtoolkit-daily-20260501004238.json` has `overall_status=pass`, `adapter_tier=process_bridge`, inherited `required_entrypoint_policy`, and complete evidence refs
- decision: `adjust`
- backlog candidates:
  - `target-repo-reuse-host-capability-gap`
  - `target-repo-reuse-historical-problem-trace`

## Rollback
- remove `scripts/build-target-repo-reuse-effect-report.py`, `scripts/verify-target-repo-reuse-effect-report.py`, and `tests/runtime/test_target_repo_reuse_effect_feedback.py`
- remove `docs/change-evidence/target-repo-runs/effect-report-classroomtoolkit.json`
- remove the `target-repo-reuse-effect-feedback` hook from `scripts/verify-repo.ps1`
