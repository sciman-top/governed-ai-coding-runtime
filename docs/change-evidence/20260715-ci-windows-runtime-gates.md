# Windows Runtime Gate CI Repair

## Scope and cause

- `issue_id`: `control-verify-linux-windows-contract-20260715`
- `followup_issue_id`: `control-verify-clean-runner-host-state-20260715`
- baseline: `origin/main=4fd39cd0f3bf6fe8ac0b5f96b36206ea0d6589ef`; stacked governance base `9be5746a71999ee696cb48a285882f8bb7818329`
- write-set: `.github/workflows/verify.yml`; `scripts/host-feedback-summary.py`; provenance propagation in `scripts/select-next-work.py`, `scripts/evaluate-runtime-evolution.py`, `scripts/build-governance-hub-certification.py`, and `scripts/verify-evidence-recovery-posture.py`; focused runtime tests; `tests/fixtures/host-feedback/clean-windows-runner.json`; this evidence file. Gate-generated certification/repo-map/speed reports are not published in this slice.
- cause: both Verify jobs ran on `ubuntu-latest`, while the executed runtime contract explicitly checks the Windows process environment and uses executable `.cmd` fixtures. The Linux runner therefore produced nine inherited runtime test-file failures, including `PermissionError` for `fake-dotnet.cmd`.
- inherited proof: default-branch run `29394031470` at exact main SHA `4fd39cd0` and governance PR run `29403150644` at `9be5746a` both report `Completed 104 test files ... failures=9` with the same `.cmd` permission failure.
- change: move only `Repository integrity` and `Release preflight` to the supported `windows-latest` GitHub-hosted runner. The independent target-rule matrix remains on Ubuntu.
- hosted attempt 1: PR run `29404496213` proved both jobs selected Windows, then failed during checkout before tests because Git could not create the repository's deeply archived path (`Filename too long`).
- checkout repair: run `git config --global core.longpaths true` in each fresh job before `actions/checkout`; no repository content is excluded from verification.
- hosted attempt 2: PR run `29413222522` passed long-path checkout and all Windows-specific `.cmd`, doctor, guard, and operator paths. The remaining failures read `Path.home()`, Codex/Claude local status, and the Claude workload probe from a clean runner with no managed global copies or local host configuration. `test_runtime_evolution` also indexed a developer-residue `.runtime` artifact that is absent in a clean checkout.
- follow-up cause: the host-feedback boundary mixed deterministic repo assertions with live machine state, while selector/evolution/certification/recovery dynamically reloaded that module and bypassed local test mocks. The tests therefore encoded the developer machine as an undeclared prerequisite.
- deterministic repair: production continues to use live host state unless `GACR_HOST_FEEDBACK_FIXTURE` is explicitly set. CI points that variable to a strict repository-owned JSON fixture; paths outside `tests/fixtures/host-feedback`, malformed JSON, missing/extra keys, wrong types, and any acceptance scope other than `test_only_not_hosted` fail closed.
- claim boundary: fixture-derived output records `mode=test_fixture`, `acceptance_scope=test_only_not_hosted`, `hosted_acceptance=false`, fixture ref, and SHA-256. Selector/evolution/certification/recovery preserve that provenance; fixture success is never hosted/manual acceptance.

## pre_change_review

- `control_repo_manifest_and_rule_sources`: compared the 9.57 global sources, manifest, coordination contract, and verifier; this CI repair does not change any rule content or version.
- `user_level_deployed_rule_files`: confirmed the live Codex and Claude managed copies remain the already-published 9.57 hashes; this slice does not apply, downgrade, or rewrite user-level files.
- `repo_local_gate_scripts_and_ci`: compared `.github/workflows/verify.yml`, `scripts/verify-repo.ps1`, `scripts/doctor-runtime.ps1`, host-feedback and all dynamic consumers, the failing test modules, and exact-sha GitHub run logs. Attempt 1 proved the runner/long-path mismatch; attempt 2 isolated clean-runner host-state and residue coupling.
- `repo_local_repo_profile`: the repository remains Windows-first and its fixed gate order is unchanged; no repo profile, permission, credential, provider, or tool allowlist changes.
- `repo_local_readme_and_operator_docs`: production CLI behavior remains live-host by default and no operator command changes. The fixture is CI/test-only, so README/spec edits are not required; this evidence records its restricted activation and claim boundary.
- `current_official_tool_loading_docs`: agent loading semantics are unchanged. GitHub's current hosted-runner reference confirms `windows-latest` is a supported standard x64 workflow label.
- `drift-integration decision`: keep the governance commit and CI repair as separate commits/PRs; stack the repair on the 9.57 branch so normal hooks can validate against the already-published 9.57 managed copies without downgrading live state.

## reference_required_review

- `changed_surface_paths`: `.github/workflows/verify.yml`; `scripts/host-feedback-summary.py`; `scripts/select-next-work.py`; `scripts/evaluate-runtime-evolution.py`; `scripts/build-governance-hub-certification.py`; `scripts/verify-evidence-recovery-posture.py`; focused runtime tests; `tests/fixtures/host-feedback/clean-windows-runner.json`; and this evidence file.
- `official_sources_reviewed`: [GitHub-hosted runners reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners).
- `primary_references_reviewed`: exact default-branch and governance-branch GitHub Actions logs, repository workflow YAML, fixed gate scripts, and failing runtime tests.
- `local_runtime_evidence_reviewed`: YAML parse assertions, focused Windows tests, clean-home reproduction, 44 host/selector/evolution/certification/recovery/doctor tests, 9/9 candidate target audit, source/deployed rule zero-drift, and normal pre-commit output.
- `source_decision`: align runner/contract and long-path behavior, then inject only deterministic host inputs through a strict test boundary. Do not install fake auth/provider state, weaken or skip gates, omit archived repository content, treat fixture output as hosted acceptance, or move the independent target-rule matrix.

## reference_basis_review

- `changed_surface_paths`: `.github/workflows/verify.yml` remains the only reference-basis guarded path in this slice; runtime fixture/provenance code is governed by repository tests and contract gates.
- `reference_basis_surface_ids`: `release-gate-and-ci-boundaries`; `host-and-adapter-boundaries`.
- `required_local_reference_ids_reviewed`: `anthropic-claude-code-action`, `anthropic-claude-code`, `github-copilot-cli`, `google-antigravity-cli`, `openai-agents-js`, `openai-agents-python`, and `openai-codex`. The six host/runtime repositories were rechecked at clean frozen heads `ca9f6045`, `9776ad4c`, `ee726c11`, `edd0a07b`, `c359c206`, and `1f0566d3`; the action reference remains the workflow-group basis already recorded by the catalog.
- `reference_adoption_decision`: retain the existing fail-closed gate sequence, normal review/check visibility, provider-neutral CI boundary, and explicit provenance across dynamically loaded host consumers. Adopt only Windows runner alignment and a repository-owned test-input boundary. `google-antigravity-cli` was reviewed only because the cross-host catalog requires it; Gemini behavior, rules, provider configuration, and acceptance remain explicitly outside this task. Do not import provider workflows, prompt policy, credential behavior, or a parallel gate system.

## Verification and publication boundary

- `git diff --check`: pass.
- YAML assertion: `repo-integrity.runs-on=windows-latest`, `release-preflight.runs-on=windows-latest`, and both jobs enable `core.longpaths` before checkout.
- focused Windows tests: `test_preflight_ci_wiring`, `test_repo_hook_enforcement`, and `test_runtime_doctor`; 21 tests passed.
- clean-home reproduction: before the fixture boundary, `test_host_dimension_keeps_config_attention_nonblocking` failed with `pass != attention` when `USERPROFILE/HOME/CODEX_HOME/CLAUDE_CONFIG_DIR` pointed to an empty runner home.
- focused deterministic regression: 44 tests across `test_host_feedback_summary`, `test_autonomous_next_work_selection`, `test_runtime_evolution`, `test_governance_hub_certification`, `test_evidence_recovery_posture`, and `test_runtime_doctor` passed with explicit fixture provenance.
- fixture guards: live status/probe loaders were asserted not called; external paths, missing/extra keys, exact-type violations, and non-test acceptance scopes all failed closed.
- fixture identity: `tests/fixtures/host-feedback/clean-windows-runner.json` SHA-256 is `3aaede254117445026d908719b902808b6b184fb89ef8e8ad9e463b051cf6624`.
- artifact isolation: runtime-evolution candidate wiring now uses an injected resolved ref in its unit test, while a separate temporary-repo test proves latest-artifact selection without developer `.runtime` residue.
- target contract: frozen candidate workspace passed 9/9; `skills-manager` uses governance head `c5a58621` only and is not claimed default-branch effective.
- fixed local gate attempt 1: build passed; Runtime completed 104 test files with `failures=0`; Contract passed through target-project rules and pre-change review, then correctly failed `reference-required` because this evidence did not literally mention guarded path `scripts/evaluate-runtime-evolution.py`; hotspot was not run after the ordered Contract failure.
- fixed local gate attempt 2: build passed; Runtime again completed 104 test files with `failures=0`; Contract passed `reference-required`, then correctly failed the independent `reference-basis` check because the new guarded host/adaptor surface and three additional required local reference IDs were not yet recorded. Hotspot was not run after the ordered Contract failure.
- fixed local gate attempt 3, ordered and complete: build exit `0` (`OK python-bytecode`, `OK python-import`); Runtime exit `0` (104 test files, 8 workers, `failures=0`); Contract exit `0` (schema, dependency, certification, family/sync, 9/9 candidate target rules, pre-change, reference-required, reference-basis, functional-effectiveness); hotspot exit `0` (all doctor checks `OK`, including Windows process environment, gate commands, hooks, Codex capability, and adapter posture).
- workflow `All` attempt 1: build and all 104 Runtime test files passed, then target audit correctly failed because the command defaulted to divergent original worktrees under `D:/CODE`, where eight local checkouts still reviewed 9.56. No code changed; the project contract requires the isolated candidate root for this dirty/divergent case.
- workflow `All` attempt 2: with `GACR_TARGET_PROJECT_RULE_WORKSPACE_ROOT=.worktrees/candidate-contract`, `verify-repo.ps1 -Check All` exited `0`; build, 104 Runtime files, 9/9 candidate target Contract, doctor, docs, planning, host-feedback, recovery, evolution, claim and PowerShell checks all passed.
- workflow release preflight: the same explicit fixture and candidate root produced exit `0`; build/test/contract/doctor all reported `pass`, and `auto_commit` was `skipped` with `reason=disabled_by_caller`.
- generated-report boundary: governance certification, repo-map context, and runtime-speed reports were restored after the gates to HEAD blobs `1793331a0d77c58cf849e2ca03d7f2ce0c03cfa2`, `0d850f845ff193f7f94cdc115b5a57f65f91ffd3`, and `3bd1993affab25e923087a53c8a93e84911bb556`; none belongs to this publication slice.
- post-gate evidence-only update: `gate_na`; `reason=only this evidence text was updated after the complete fixed gates, workflow All, and release preflight to record already-observed exit codes`; `alternative_verification=git diff --check plus direct reference-required/reference-basis verifiers and final staged-diff review`; `evidence_link=docs/change-evidence/20260715-ci-windows-runtime-gates.md`; `expires_at=the next executable/config/schema/test/fixture change`; `recovery_condition=rerun build -> test -> contract/invariant -> hotspot whenever that condition is met`.
- required hosted proof: both Windows Verify jobs must pass at the frozen repair head before merge. If either repeats the same root cause twice, keep the PR open and enter `clarify_required`.

## Compatibility, security, and rollback

- compatibility: no application, schema, rule, auth, provider, secret, MCP, account, VPS, hosted UI, or user-process state changes. Production without the fixture environment variable remains on the existing live-host path.
- security: default GitHub token/permissions are unchanged. The fixture contains no credentials, is constrained to a repository test directory, is exact-shape validated, and cannot assert hosted acceptance.
- rollback: revert the CI repair commits to restore the prior workflow and remove the fixture/provenance boundary. Do not revert the 9.57 governance commit or touch target repositories; after rollback, clean hosted runners will again be expected to fail for the recorded platform and host-state causes.
