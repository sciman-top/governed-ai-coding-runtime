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
