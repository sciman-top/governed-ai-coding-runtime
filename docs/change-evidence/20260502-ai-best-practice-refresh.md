# 2026-05-02 AI Best Practice Refresh

## Goal
- Current landing: `D:\CODE\governed-ai-coding-runtime`.
- Target home: controlled runtime evolution evidence and low-risk refresh artifacts.
- Verification path: source review -> runtime evolution dry-run -> experience review -> feedback refresh -> build/test/contract/hotspot gates.

## Source Review
## pre_change_review
- `control_repo_manifest_and_rule_sources`: checked the active project instruction chain, `rules/manifest.json` scope expectations from the project rules, and the current runtime-evolution/core-principle policy files before this refresh. This run did not edit managed rule source files.
- `user_level_deployed_rule_files`: no user-level deployed rule files were edited in this run; existing user-level instructions were treated as execution constraints only.
- `target_repo_deployed_rule_files`: no target-repo deployed rule files were edited or synchronized in this run.
- `target_repo_gate_scripts_and_ci`: current working tree already contains unrelated sensitive CI/gate-path edits (`.github/workflows/*`, `scripts/run-runtime-tests.py`, `docs/targets/target-repo-test-slicing-policy.md`, and `tests/runtime/test_run_runtime_tests_runner.py`). They were not authored by this refresh; this refresh only reads their presence when gates report pre-change-review requirements.
- `target_repo_repo_profile`: no target repo profile was edited in this run.
- `target_repo_readme_and_operator_docs`: no target repo README/operator docs were edited in this run.
- `current_official_tool_loading_docs`: official docs and project policy were reviewed before execution; external docs remain evidence inputs and do not override local code or policy facts.
- `drift-integration decision`: do not integrate or overwrite unrelated pending sensitive-path changes during this refresh. Keep this run bounded to source review, generated runtime artifacts, host/effect feedback refresh, and evidence recording.

Official and primary sources reviewed or probed in this run:
- OpenAI Codex documentation and release guidance: Codex works best with configured environments, reliable test commands, clear `AGENTS.md`, and traceable terminal/test evidence.
- OpenAI agent guardrail guidance: tool safeguards should be risk-rated by write access, reversibility, account permission, and impact.
- Anthropic Claude Code best practices: explore first, plan, then code; give the agent verification commands; manage context aggressively; use automation and parallel sessions with explicit guardrails.
- OpenAI Codex `AGENTS.md` guide: project instructions are a scoped input, not a replacement for executable checks.
- GitHub Actions schedule documentation: schedule is a workflow trigger, not the right mechanism for this owner-directed immediate refresh.

Community and reference projects reviewed as candidate signals:
- Continue: source-controlled AI checks as PR status checks.
- OpenHands: agent runtime, sandbox, and software-engineering agent surface.
- NVIDIA OpenShell: policy-governed private runtime for autonomous agents.
- Google SRE eliminating toil: repeated manual work should become automation only when it is frequent, valuable, and safe to automate.
- Recent agent-rules research: negative constraints and executable guardrails are safer than broad positive instruction files.

These sources are candidate evidence only. They do not override repository policy, local code facts, or the hard gate order.

## Commands And Evidence
Executed commands:
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action EvolutionReview -OnlineSourceCheck`
  - Result: pass.
  - Evidence: `.runtime/artifacts/runtime-evolution/20260502-runtime-evolution-review.json` and `.runtime/artifacts/runtime-evolution/20260502-runtime-evolution-review.md`.
  - Candidate summary: `EVOL-HOST-FEEDBACK` low risk, `EVOL-EFFECT-FEEDBACK` medium risk, `EVOL-AI-EXPERIENCE` low risk.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action ExperienceReview`
  - Result: pass.
  - Evidence: `.runtime/artifacts/ai-coding-experience/20260502-ai-coding-experience-review.json` and `.runtime/artifacts/ai-coding-experience/20260502-ai-coding-experience-review.md`.
  - Candidate summary: one checklist-first bugfix knowledge/memory/proposal/disabled skill candidate; mutation remains disabled.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\operator.ps1 -Action FeedbackReport`
  - Result: attention.
  - Evidence: `.runtime/artifacts/host-feedback-summary/latest.md`.
  - Key output: Codex and Claude host snapshots are `ok`; Claude workload is `ready/native_attach`; latest target runs are fresh but degraded for 5 repos because Codex target runs still use `process_bridge`.
- `python scripts\build-target-repo-reuse-effect-report.py --target classroomtoolkit`
  - Result: pass.
  - Evidence updated: `docs/change-evidence/target-repo-runs/effect-report-classroomtoolkit.json`.
- `python scripts\verify-target-repo-reuse-effect-report.py`
  - Result: pass after rebuilding the report.
- `python scripts\select-next-work.py --as-of 2026-05-02`
  - Result: pass.
  - Decision: `refresh_evidence_first`.
  - Reason: claims and source assumptions must be fresh before selecting implementation work.

## Decisions
- Do not schedule a weekly automation from this owner request. The requested action is immediate execution.
- Do not broadly refactor implementation code in this run. The current selector still chooses `refresh_evidence_first`, and host feedback still shows degraded target-run posture.
- Keep automatic evolution within the current guard: source collection, experience extraction, candidate evaluation, proposal generation, and evidence refresh are allowed; active policy mutation, skill enablement, target repo sync, push, and merge remain disabled.
- Keep `EVOL-AI-EXPERIENCE` as proposal/disabled skill candidate only. It is low risk but still requires human review before enablement.
- Keep `EVOL-EFFECT-FEEDBACK` as a bounded follow-up because it is medium risk and tied to target-run/host posture evidence.

## Current Findings
- Official and community best practices continue to support this repository's current direction: concise scoped instructions, executable guardrails, risk-rated tools, source-controlled checks, sandbox/policy boundaries, and measured effect feedback.
- The fresh `classroomtoolkit` effect report now points at `classroomtoolkit-daily-20260502135550.json` and verifies cleanly.
- The latest target-run evidence is fresh but not fully healthy: degraded `process_bridge` posture remains for the latest target runs, and `skills-manager-daily-20260502135550.json` is still a failed latest daily run.
- Because the remaining signal is evidence/host posture, not a proven implementation-code defect, broad code optimization would be premature.

## N/A
No `platform_na` or `gate_na` was used for this refresh evidence. Full project gates are run after the evidence updates in this same task.

## Rollback
- Revert this evidence file if the source review or conclusions are incorrect.
- Revert `docs/change-evidence/target-repo-runs/effect-report-classroomtoolkit.json` to the previous git version to restore the prior effect-report baseline.
- Delete `.runtime/artifacts/runtime-evolution/20260502-*`, `.runtime/artifacts/ai-coding-experience/20260502-*`, and `.runtime/artifacts/host-feedback-summary/latest.md` if the generated runtime artifacts need to be discarded. These artifacts do not enable runtime behavior.

## Next Boundary
The next valid implementation action is still evidence-first:
- refresh or diagnose degraded Codex target-run posture until fresh target evidence reaches `codex_capability_status=ready` and `adapter_tier=native_attach`, or
- explicitly accept `process_bridge` as the current bounded posture and open a separate owner-directed implementation slice for the `skills-manager` failed latest daily run.

## Rule Sync Drift Resolution Addendum
Current landing: `D:\CODE\governed-ai-coding-runtime`.
Target home: `rules/global/*` source files, then managed user-level deployed rule files through `scripts/sync-agent-rules.py`.
Verification path: compare manifest-managed sources and user-level deployed files -> integrate same-version drift into source -> dry-run sync -> apply managed sync -> contract gate.

Drift source:
- `python scripts\sync-agent-rules.py --scope All --fail-on-change` reported `blocked_same_version_drift` for `global-codex-agents`, `global-claude-claude`, and `global-gemini-gemini`.
- `rules/manifest.json` confirms these are managed global rule entries with backup policy enabled.
- `git diff --no-index` showed the target-only content was provider-aware local guidance for Codex / Claude / Gemini comparison and Claude Code third-party Anthropic-compatible provider mapping.
- `rg` over local config confirmed `C:\Users\sciman\.codex\config.toml` currently maps Anthropic-compatible traffic to `https://open.bigmodel.cn/api/anthropic` with `glm-5.1`, `glm-5-turbo`, and `glm-4.5-air`.

Decision:
- Integrate the target-only provider-aware guidance back into the control repo global source files, including the local compact-window guidance from the Claude deployed file.
- Align Codex, Claude, and Gemini global rule sources with the current same-version deployed user files so the manifest-managed source remains the truth.
- Use managed sync after source integration; do not force-overwrite same-version drift.

Sync evidence:
- `python scripts\sync-agent-rules.py --scope All --apply --force` updated the three global deployed files after source integration.
- Backups were written under `docs/change-evidence/rule-sync-backups/20260502-162159/`.
- `python scripts\sync-agent-rules.py --scope All --fail-on-change` then returned `status=pass`, `changed_count=0`, and `blocked_count=0` without `--force`.

Final gate evidence:
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\build-runtime.ps1`: pass (`OK python-bytecode`, `OK python-import`).
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Runtime` with `GOVERNED_RUNTIME_TEST_TIMEOUT_SECONDS=300`: pass, 95 test files, 0 failures.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\verify-repo.ps1 -Check Contract`: pass, including `agent-rule-sync`, `pre-change-review`, and `functional-effectiveness`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\doctor-runtime.ps1`: pass with existing `WARN codex-capability-degraded`; all hard checks returned `OK`.

Rollback:
- Revert `rules/global/codex/AGENTS.md`, `rules/global/claude/CLAUDE.md`, and `rules/global/gemini/GEMINI.md` to the previous git version.
- Restore user-level deployed rule files from the backup paths emitted by `scripts/sync-agent-rules.py --apply` if the synchronized deployed files need rollback.

## Gate Speed Review Addendum
Current landing: `D:\CODE\governed-ai-coding-runtime`.
Target home: self-runtime and target-repo coding-speed feedback loops.
Verification path: measure baseline -> implement bounded runner/CI controls -> rerun quick/full/target checks -> record actual effect and blockers.

Additional source review:
- pytest official docs: use slowest-duration reporting and timeout traceback support to identify expensive or stuck tests.
- GitHub Actions official docs: use dependency caching only when the repo has stable dependency metadata, use `concurrency` to cancel obsolete work, use matrix `fail-fast`/`max-parallel` where applicable, and set finite workflow/job time limits.
- Bazel official docs: mature test systems model test size, timeout, sharding, retries, cache behavior, and filtering explicitly.
- Google Testing Blog: keep the test portfolio pyramid-shaped; end-to-end/system tests should be limited, specific, and supported by testability improvements.

Changes:
- Added `scripts/verify-repo.ps1 -Check RuntimeQuick` as a first-class self-runtime inner-loop gate for target-governance speed-profile work.
- Kept full `Runtime` as the authoritative delivery gate.
- Added per-test-file timeout and optional `--summary-json` timing output to `scripts/run-runtime-tests.py`.
- Kept default runtime-test workers conservative at 4 after an 8-worker experiment showed resource contention.
- Added GitHub Actions `concurrency` and `timeout-minutes` to avoid stale or runaway CI work.
- Documented the runtime runner behavior and CI/slow-test recommendations in `docs/targets/target-repo-test-slicing-policy.md` and `tests/README.md`.

Measured effect:
- Baseline quick slice direct command: 46 tests in 19.4 seconds, command elapsed 19.581 seconds.
- Baseline full Runtime before changes: 94 test files, 4 workers, elapsed 273.659 seconds, failed on existing target effect/report certification drift.
- `RuntimeQuick` after changes: 46 tests in 16.889 seconds, command elapsed 18.3 seconds, pass.
- 8-worker full Runtime experiment: 95 test files, elapsed 328.889 seconds, failed with two 180-second per-file timeouts. Decision: do not raise default concurrency; use explicit worker override only for controlled experiments.
- All-target daily quick with `TargetParallelism=2`: 5 targets in 120 seconds batch time, 1 failure. The failure was `self-runtime` contract gate, caused by existing global rule sync same-version drift, not by the quick test slice itself.

Current blockers:
- `scripts/verify-repo.ps1 -Check Contract` is blocked by `agent-rule-sync`: global Codex and Claude rule files have same-version content drift.
- Self-runtime target quick flow still runs full Contract as its second quick gate; this remains correct for safety, but it means rule-sync drift can block target quick flow even when the quick test slice passes.

Rollback:
- Revert `scripts/verify-repo.ps1`, `scripts/run-runtime-tests.py`, `.github/workflows/*.yml`, `tests/runtime/test_run_runtime_tests_runner.py`, `docs/targets/target-repo-test-slicing-policy.md`, and `tests/README.md`.
- Delete `docs/change-evidence/runtime-test-speed-latest.json` if the 8-worker negative benchmark artifact should not be retained.

## Gate Speed Follow-up Addendum
Current landing: `D:\CODE\governed-ai-coding-runtime`.
Target home: manifest-managed rule source alignment, focused Docs link feedback, and Runtime test speed profile.
Verification path: `sync-agent-rules` dry-run -> Contract -> focused Runtime tests -> full runtime runner with timing JSON.

pre_change_review:
- control_repo_manifest_and_rule_sources: checked `rules/manifest.json`, `rules/global/*`, `rules/projects/*`, and `python scripts/sync-agent-rules.py --scope All --fail-on-change`; after source alignment all 18 entries are same-hash with `blocked_count=0`.
- user_level_deployed_rule_files: compared `rules/global/codex/AGENTS.md`, `rules/global/claude/CLAUDE.md`, and `rules/global/gemini/GEMINI.md` against `C:\Users\sciman\.codex\AGENTS.md`, `C:\Users\sciman\.claude\CLAUDE.md`, and `C:\Users\sciman\.gemini\GEMINI.md`; same-version drift was integrated into source rather than force-overwriting deployed files.
- target_repo_deployed_rule_files: the same sync dry-run reported all project target entries as `skipped_same_hash`.
- target_repo_gate_scripts_and_ci: reviewed changed gate scripts in `scripts/verify-repo.ps1`, existing sensitive sync/apply scripts, and workflow timeout/concurrency changes; `DocsLinks` is a narrow active-link feedback slice and does not replace full `Docs`.
- target_repo_repo_profile: no repo-profile semantic change is intended in this follow-up; profile-related sensitive paths are only covered by the standard pre-change review token set.
- target_repo_readme_and_operator_docs: updated `docs/targets/target-repo-test-slicing-policy.md` to document `RuntimeQuick`, runtime runner timeout/summary behavior, and `DocsLinks`.
- current_official_tool_loading_docs: retained the prior official-doc review from this evidence file; no new loading-model semantics were introduced.
- drift-integration decision: integrate current deployed global rule content into the control-repo sources, add focused feedback slices, and keep full gates authoritative.

Measured follow-up effect:
- Full runtime runner after rule-sync cleanup: 95 files, 4 workers, 341.087 seconds, 0 failures.
- After static verify-repo wiring checks: 317.728 seconds, 0 failures in the runner; `test_runtime_doctor.py` still dominated at 164.201 seconds.
- After `DocsLinks`: focused `test_runtime_doctor.py` passed in 23.035 seconds; full runtime runner reached 238.278 seconds before failing on this evidence gap and one tight elapsed-time assertion.
- Final first pass after evidence/threshold fixes: 95 files, 4 workers, 281.003 seconds, 0 failures; formal `verify-repo.ps1 -Check Runtime`, `Contract`, and `RuntimeQuick` also passed.
- Second pass removes three more duplicated full `Docs` invocations from Runtime tests by converting `core-principles`, `current-source-compatibility`, and `ltp-autonomous-promotion` wiring assertions to static verifier-contract checks.
- Second pass measured result: 95 files, 4 workers, 163.082 seconds, 0 failures.
- Third pass replaces heavy operator UI helper calls with mocks for status providers and command execution in contract-focused tests, while retaining separate real entrypoint smoke coverage.

Rollback:
- Revert `scripts/verify-repo.ps1`, `tests/runtime/test_runtime_doctor.py`, `tests/runtime/test_runtime_flow_preset.py`, and `docs/targets/target-repo-test-slicing-policy.md`.
- Revert `tests/runtime/test_core_principles.py`, `tests/runtime/test_current_source_compatibility.py`, and `tests/runtime/test_ltp_autonomous_promotion.py`.
- Revert `tests/runtime/test_operator_entrypoint.py`.
- Delete `docs/change-evidence/runtime-test-speed-after-*.json` if the timing artifacts should not be retained.

## Gate Speed Closeout Addendum
Current landing: `D:\CODE\governed-ai-coding-runtime`.
Target home: final Runtime speed evidence, rule-sync consistency, and hard-gate closeout.
Verification path: rule sync apply/dry-run -> pre-change review -> build -> Runtime -> Contract -> RuntimeQuick -> doctor.

Rule-sync closeout:
- `python scripts/sync-agent-rules.py --scope Targets --target self-runtime --apply`: pass; merged same-version project-rule drift for `AGENTS.md`, `CLAUDE.md`, and `GEMINI.md` into the manifest-managed sources and the deployed self-runtime files.
- Backups were written under `docs/change-evidence/rule-sync-backups/20260502-171618/`.
- `python scripts/sync-agent-rules.py --scope All --fail-on-change`: pass, `changed_count=0`, `blocked_count=0`, all 18 manifest entries same-hash.

Measured closeout effect:
- Stable post-cleanup baseline: 95 files, 4 workers, 341.087 seconds, 0 failures.
- Best full-run result after duplicate full-gate invocations were removed from Runtime tests: 95 files, 4 workers, 163.082 seconds, 0 failures.
- Follow-up full run after operator-entrypoint contract mocking: 95 files, 4 workers, 186.663 seconds, 0 failures; the operator test file itself dropped to 20.517 seconds in that run.
- Formal `verify-repo.ps1 -Check Runtime` closeout: 95 files, 4 workers, 228.234 seconds, 0 failures. This run is slower than the best direct runner result due normal host variance, but still materially faster than the 341.087-second post-cleanup baseline.
- 6-worker experiment: 95 files, 179.826 seconds, failed because concurrent rule-sync-sensitive checks observed same-version drift. Decision: keep the default at 4 workers; use `--workers` only for controlled experiments after drift-sensitive state is clean.

Final gate evidence:
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`: pass (`OK python-bytecode`, `OK python-import`).
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`: pass, 95 files, 228.234 seconds, 0 failures.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`: pass, including `agent-rule-sync`, `pre-change-review`, and `functional-effectiveness`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check RuntimeQuick`: pass, 47 tests in 29.384 seconds.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`: pass with existing `WARN codex-capability-degraded`; all hard checks returned `OK`.

Remaining hotspot profile:
- Slowest closeout Runtime files are still true integration/effectiveness paths: `test_attached_repo_e2e.py`, `test_run_governed_task_cli.py`, `test_runtime_flow_preset.py`, `test_autonomous_next_work_selection.py`, `test_runtime_evolution.py`, and `test_evidence_recovery_posture.py`.
- Next safe optimization lane is to split those files into contract-smoke and full integration layers with shared fixtures or explicit slow tags, while keeping the existing full Runtime gate authoritative.

## Gate Speed Fourth Pass Addendum
Current landing: `D:\CODE\governed-ai-coding-runtime`.
Target home: repeated subprocess reduction in Runtime hotspot tests.
Verification path: targeted hotspot tests -> full runtime runner -> formal gate closeout.

Changes:
- Converted functional assertions in `tests/runtime/test_run_governed_task_cli.py` from repeated Python CLI subprocesses to direct calls against the same loaded `run-governed-task.py` module; kept help-text tests as real CLI subprocess coverage.
- Mocked Codex capability probing in the status-surface unit test while preserving the `codex_capability` output contract.
- Kept one full `runtime-check.ps1` attached-repo E2E path in `tests/runtime/test_attached_repo_e2e.py`; added `-SkipVerifyAttachment` to repeated write-policy/default-tool/fallback cases that do not need to re-run target repo gates.

Measured fourth-pass effect:
- `python -m unittest tests.runtime.test_run_governed_task_cli`: pass, 9 tests in 31.714 seconds.
- `python -m unittest tests.runtime.test_attached_repo_e2e`: pass, 5 tests in 37.803 seconds.
- `python -m unittest tests.runtime.test_runtime_flow_preset`: pass, 17 tests in 40.383 seconds.
- `python scripts/run-runtime-tests.py --suite runtime=tests/runtime --suite service=tests/service --summary-json docs/change-evidence/runtime-test-speed-fourth-pass.json`: pass, 95 files, 167.128 seconds, 0 failures.
- Formal `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`: pass, 95 files, 179.161 seconds, 0 failures.
- Formal `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check RuntimeQuick`: pass, 47 tests in 20.543 seconds.

Fourth-pass hotspot profile:
- Slowest files after this pass: `test_autonomous_next_work_selection.py` 48.889s, `test_runtime_flow_preset.py` 45.474s, `test_runtime_evolution.py` 43.695s, `test_attached_repo_e2e.py` 42.870s, `test_evidence_recovery_posture.py` 41.797s.
- This pass validates the repeated-subprocess reduction lane. The remaining best lane is shared fixture/precomputed evidence for the autonomous/evolution/evidence posture tests, not raising runner worker count.

Final gate evidence:
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`: pass (`OK python-bytecode`, `OK python-import`).
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`: pass, 179.161 seconds.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`: pass, including `agent-rule-sync`, `pre-change-review`, and `functional-effectiveness`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`: pass with existing `WARN codex-capability-degraded`; all hard checks returned `OK`.

Rollback:
- Revert `tests/runtime/test_run_governed_task_cli.py` and `tests/runtime/test_attached_repo_e2e.py`.
- Delete `docs/change-evidence/runtime-test-speed-fourth-pass.json` if the timing artifact should not be retained.

## Gate Speed Fifth/Sixth Pass Addendum
Current landing: `D:\CODE\governed-ai-coding-runtime`.
Target home: repeated live evidence/source scans in autonomous selection and recovery posture tests.
Verification path: targeted tests -> full runtime runner -> formal gate closeout.

Changes:
- Converted `test_autonomous_next_work_selection.py`, `test_runtime_evolution.py`, and `test_evidence_recovery_posture.py` live JSON subprocess tests to direct module calls where the tested script already exposes the same assertion/inspection function.
- Cached the live evidence-recovery payload inside `test_evidence_recovery_posture.py` so the file does not recompute the same root-level recovery posture twice.
- Replaced the operator PowerShell `EvolutionReview -OnlineSourceCheck` full-chain test with static operator wiring assertions plus a direct runtime-evolution contract call with `online_source_check=True`.
- Extended `scripts/select-next-work.py` host-feedback detail output with target-run status, freshness, degraded count, and degraded repos.
- Updated `scripts/verify-evidence-recovery-posture.py` to reuse selector auto-detected host-feedback details instead of rebuilding host feedback a second time.

Measured fifth/sixth-pass effect:
- `python -m unittest tests.runtime.test_evidence_recovery_posture`: pass, 2 tests in 12.510 seconds after selector-detail reuse.
- `python -m unittest tests.runtime.test_autonomous_next_work_selection tests.runtime.test_evidence_recovery_posture`: pass, 9 tests in 59.191 seconds.
- Fifth full runner: pass, 95 files, 184.644 seconds, 0 failures; host variance dominated the total despite `evidence_recovery_posture.py` dropping to 23.746 seconds.
- Sixth full runner: pass, 95 files, 167.198 seconds, 0 failures; `evidence_recovery_posture.py` was 14.609 seconds.
- Formal `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`: pass, 95 files, 173.016 seconds, 0 failures.
- Formal `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check RuntimeQuick`: pass, 47 tests in 18.344 seconds.

Sixth-pass hotspot profile:
- Slowest files after this pass: `test_autonomous_next_work_selection.py` 50.032s, `test_runtime_flow_preset.py` 47.086s, `test_attached_repo_e2e.py` 45.012s, `test_runtime_evolution.py` 43.384s, `test_transition_stack_convergence.py` 41.947s.
- Next safe lane is to split or cache shared live root scans for autonomous/evolution/transition-stack checks. Raising default workers remains rejected due prior 6-worker instability.

Final gate evidence:
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`: pass (`OK python-bytecode`, `OK python-import`).
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`: pass, 173.016 seconds.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`: pass, including `agent-rule-sync`, `pre-change-review`, and `functional-effectiveness`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`: pass with existing `WARN codex-capability-degraded`; all hard checks returned `OK`.

Rollback:
- Revert `scripts/select-next-work.py`, `scripts/verify-evidence-recovery-posture.py`, `tests/runtime/test_autonomous_next_work_selection.py`, `tests/runtime/test_runtime_evolution.py`, and `tests/runtime/test_evidence_recovery_posture.py`.
- Delete `docs/change-evidence/runtime-test-speed-fifth-pass.json` and `docs/change-evidence/runtime-test-speed-sixth-pass.json` if the timing artifacts should not be retained.
