# Windows Runtime Gate CI Repair

## Scope and cause

- `issue_id`: `control-verify-linux-windows-contract-20260715`
- baseline: `origin/main=4fd39cd0f3bf6fe8ac0b5f96b36206ea0d6589ef`; stacked governance base `9be5746a71999ee696cb48a285882f8bb7818329`
- write-set: `.github/workflows/verify.yml` plus this evidence file only
- cause: both Verify jobs ran on `ubuntu-latest`, while the executed runtime contract explicitly checks the Windows process environment and uses executable `.cmd` fixtures. The Linux runner therefore produced nine inherited runtime test-file failures, including `PermissionError` for `fake-dotnet.cmd`.
- inherited proof: default-branch run `29394031470` at exact main SHA `4fd39cd0` and governance PR run `29403150644` at `9be5746a` both report `Completed 104 test files ... failures=9` with the same `.cmd` permission failure.
- change: move only `Repository integrity` and `Release preflight` to the supported `windows-latest` GitHub-hosted runner. The independent target-rule matrix remains on Ubuntu.

## pre_change_review

- `control_repo_manifest_and_rule_sources`: compared the 9.57 global sources, manifest, coordination contract, and verifier; this CI repair does not change any rule content or version.
- `user_level_deployed_rule_files`: confirmed the live Codex and Claude managed copies remain the already-published 9.57 hashes; this slice does not apply, downgrade, or rewrite user-level files.
- `repo_local_gate_scripts_and_ci`: compared `.github/workflows/verify.yml`, `scripts/verify-repo.ps1`, `scripts/doctor-runtime.ps1`, the nine failing test modules, and both exact-sha GitHub run logs. The observed runner OS conflicts with the commands' Windows contract.
- `repo_local_repo_profile`: the repository remains Windows-first and its fixed gate order is unchanged; no repo profile, permission, credential, provider, or tool allowlist changes.
- `repo_local_readme_and_operator_docs`: no operator command or public workflow contract changes, so README/spec edits are not required; this evidence records the runner-only repair.
- `current_official_tool_loading_docs`: agent loading semantics are unchanged. GitHub's current hosted-runner reference confirms `windows-latest` is a supported standard x64 workflow label.
- `drift-integration decision`: keep the governance commit and CI repair as separate commits/PRs; stack the repair on the 9.57 branch so normal hooks can validate against the already-published 9.57 managed copies without downgrading live state.

## reference_required_review

- `changed_surface_paths`: `.github/workflows/verify.yml` and this evidence file.
- `official_sources_reviewed`: [GitHub-hosted runners reference](https://docs.github.com/en/actions/reference/runners/github-hosted-runners).
- `primary_references_reviewed`: exact default-branch and governance-branch GitHub Actions logs, repository workflow YAML, fixed gate scripts, and failing runtime tests.
- `local_runtime_evidence_reviewed`: YAML parse assertions, focused Windows tests, 9/9 candidate target audit, source/deployed rule zero-drift, and normal pre-commit output.
- `source_decision`: change only the two mismatched runner labels; do not weaken tests, skip hooks, alter scripts, or move the independent target-rule matrix.

## reference_basis_review

- `changed_surface_paths`: `.github/workflows/verify.yml` is the only reference-basis guarded path in this slice.
- `reference_basis_surface_ids`: `release-gate-and-ci-boundaries`.
- `required_local_reference_ids_reviewed`: `anthropic-claude-code-action`, `github-copilot-cli`, and `openai-codex` were reviewed from the repo-owned local reference shelf at the frozen catalog heads.
- `reference_adoption_decision`: retain the existing fail-closed gate sequence, normal review/check visibility, and provider-neutral CI boundary. Adopt only the runner/contract alignment evidenced by this repository's Windows-specific tests and GitHub's supported runner label; do not import provider workflows, prompt policy, credential behavior, or a parallel gate system.

## Verification and publication boundary

- `git diff --check`: pass.
- YAML assertion: `repo-integrity.runs-on=windows-latest` and `release-preflight.runs-on=windows-latest`.
- focused Windows tests: `test_preflight_ci_wiring`, `test_repo_hook_enforcement`, and `test_runtime_doctor`; 21 tests passed.
- target contract: frozen candidate workspace passed 9/9; `skills-manager` uses governance head `c5a58621` only and is not claimed default-branch effective.
- required hosted proof: both Windows Verify jobs must pass at the frozen repair head before merge. If either repeats the same root cause twice, keep the PR open and enter `clarify_required`.

## Compatibility, security, and rollback

- compatibility: no application, schema, rule, data, auth, provider, secret, MCP, account, VPS, hosted UI, or user-process state changes.
- security: default GitHub token/permissions and workflow steps are unchanged; only the runner OS label changes.
- rollback: revert the repair commit to restore the two Ubuntu labels. Do not revert the 9.57 governance commit or touch target repositories.
