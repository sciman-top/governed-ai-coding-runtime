# 2026-04-22 Auto Commit Policy For Target Repos

## Goal
- Add machine-readable and executable support for auto-committing pending changes at governed gate checkpoints/milestones, with Chinese commit messages.

## Basis
- User request: apply this runtime to target repositories and support automatic judgement + auto-commit at key nodes/milestones.
- Repo gate order contract remains unchanged: `build -> test -> contract/invariant -> hotspot`.

## Changes
- Added `auto_commit_policy` to repo-profile schema and spec:
  - `schemas/jsonschema/repo-profile.schema.json`
  - `docs/specs/repo-profile-spec.md`
- Added template sample for target repos:
  - `schemas/examples/repo-profile/target-repo-fast-full-template.example.json`
- Added default disabled policy into generated attachment profile:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
- Implemented post-gate auto-commit logic in governance gate runner:
  - `scripts/governance/gate-runner-common.ps1`
  - `scripts/governance/fast-check.ps1` (added `-MilestoneTag`)
  - `scripts/governance/full-check.ps1` (added `-MilestoneTag`)
- Added regression assertion for attachment CLI inferred profile:
  - `tests/runtime/test_repo_attachment.py`

## Commands
- `python -m unittest tests/runtime/test_repo_attachment.py tests/runtime/test_repo_profile.py tests/runtime/test_verification_runner.py`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/governance/fast-check.ps1 -RepoProfilePath schemas/examples/repo-profile/target-repo-fast-full-template.example.json -WorkingDirectory . -Json`
- Temporary repo simulation (manual script) to verify:
  - gate pass
  - dirty tree detection
  - `git add -A` + `git commit -m "<中文模板>"`
  - JSON summary includes `auto_commit.status=committed` and commit hash.

## Evidence
- Targeted Python tests passed (`39` tests).
- Simulation commit subject example:
  - `自动提交：tmp-autocommit fast 2026-04-22 21:34:27 +08:00 none`
- Governance summary now emits `auto_commit` block with:
  - `status`, `reason`, `commit_hash`, `commit_message`, `trigger`, `milestone_tag`.

## Rollback
- Revert changed files in one commit:
  - `git revert <this-commit>`
- Or restore only this feature area:
  - `git checkout -- scripts/governance/fast-check.ps1 scripts/governance/full-check.ps1 scripts/governance/gate-runner-common.ps1`
  - `git checkout -- schemas/jsonschema/repo-profile.schema.json docs/specs/repo-profile-spec.md schemas/examples/repo-profile/target-repo-fast-full-template.example.json`
  - `git checkout -- packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py tests/runtime/test_repo_attachment.py`
