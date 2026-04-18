# 20260418 Full Repo Deep Audit And Planning Refresh

## Goal
- 对当前仓库做一次 post-Foundation 深度审查。
- 清理 active planning chain、automation seed 与目录导航中的明显漂移。
- 在不改写历史 evidence 的前提下，把当前 Full Runtime 起跑入口收紧到一致状态。

## Basis
- `README.md`
- `README.en.md`
- `README.zh-CN.md`
- `docs/README.md`
- `docs/product/positioning-roadmap-competitive-layers.zh-CN.md`
- `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/plans/full-runtime-implementation-plan.md`
- `docs/reviews/README.md`
- `docs/change-evidence/README.md`
- `scripts/github/create-roadmap-issues.ps1`
- `packages/README.md`
- `packages/contracts/README.md`
- `apps/README.md`
- `infra/README.md`
- `tests/README.md`
- `AGENTS.md`

## Active Rule Inputs
- project rule path: `D:\OneDrive\CODE\governed-ai-coding-runtime\AGENTS.md`
- global rule source: `GlobalUser/AGENTS.md v9.39` from the current session context

## Platform Diagnostics
| cmd | exit_code | key_output | timestamp |
|---|---:|---|---|
| `codex --version` | 0 | `codex-cli 0.121.0` | `2026-04-18T03:04:57.7825390+08:00` |
| `codex --help` | 0 | `Codex CLI` help rendered successfully | `2026-04-18T03:04:57.7825390+08:00` |
| `codex status` | 1 | `Error: stdin is not a terminal` | `2026-04-18T03:04:57.7825390+08:00` |

## Platform N/A
- `type`: `platform_na`
- `reason`: `codex status` requires an interactive terminal and failed with `stdin is not a terminal`.
- `alternative_verification`: used `codex --version`, `codex --help`, direct inspection of the active project rule path, and direct execution of repo gate commands.
- `evidence_link`: `docs/change-evidence/20260418-full-repo-deep-audit-and-planning-refresh.md`
- `expires_at`: `n/a`

## Files Changed
- `README.md`
- `README.en.md`
- `README.zh-CN.md`
- `docs/README.md`
- `docs/backlog/full-lifecycle-backlog-seeds.md`
- `docs/backlog/issue-seeds.yaml`
- `docs/reviews/README.md`
- `docs/reviews/2026-04-18-full-repo-deep-audit-and-planning-refresh.md`
- `docs/change-evidence/README.md`
- `docs/change-evidence/20260418-full-repo-deep-audit-and-planning-refresh.md`
- `packages/README.md`
- `packages/contracts/README.md`
- `apps/README.md`
- `infra/README.md`
- `tests/README.md`
- `scripts/github/create-roadmap-issues.ps1`
- `scripts/verify-repo.ps1`
- `tests/runtime/test_runtime_doctor.py`
- `tests/runtime/test_issue_seeding.py`
- `docs/backlog/README.md`

## Decision Summary
- Keep `Foundation` recorded as completed implementation history, but stop presenting it as the current execution queue.
- Treat `Full Runtime / GAP-024` as the only active next-step queue in active seeds and navigation docs.
- Keep `GAP-027` framed as a `Minimal Operator Surface` with CLI-first delivery; move richer UI expectations to `Public Usable Release`.
- Refresh top-level and directory-level docs so they describe the current contract/test/gate substrate honestly.
- Move the standalone Chinese positioning / roadmap / competitive-layer note into `docs/product/` and index it as product context.
- Preserve historical evidence files unchanged and isolate them through index wording rather than retroactive edits.
- Fix `verify-repo.ps1` so active Markdown link checks respect ignored files and worktree artifacts, then lock that behavior with a regression test.
- Reduce seeding drift by making `scripts/github/create-roadmap-issues.ps1` read task titles and seed metadata from `docs/backlog/issue-seeds.yaml`, plus a `-ValidateOnly` mode for non-GitHub verification.
- Eliminate the remaining task-body drift by rendering task issue bodies from `docs/backlog/issue-ready-backlog.md` instead of duplicating body templates inside the script.
- Eliminate the remaining initiative/epic template drift by rendering those bodies from `docs/roadmap/governed-ai-coding-runtime-full-lifecycle-plan.md` and centralizing epic definitions in one place.
- Promote the remaining parser coupling into an active script gate by adding `-ValidateOnly -RenderAll` and wiring it into `scripts/verify-repo.ps1 -Check Scripts`.

## Commands
1. `git status --short`
   - exit: `0`
   - result: clean worktree before edits
2. `git log --oneline -10`
   - exit: `0`
   - result: confirmed recent planning and Foundation-closeout commits
3. `rg --files`
   - exit: `0`
   - result: enumerated current repo inventory
4. `rg -n "governed-agent-platform|...|foundation-runtime-substrate" README.md README.zh-CN.md README.en.md docs scripts schemas packages tests AGENTS.md`
   - exit: `0`
   - result: identified active drift versus historical evidence copies
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
   - exit: `0`
   - result: `OK python-bytecode`, `OK python-import`
6. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
   - exit: `0`
   - result: `Ran 87 tests ... OK`
7. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
   - exit: `0`
   - result: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`
8. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
   - exit: `0`
   - result: live doctor prerequisites passed
9. `python -m unittest tests.runtime.test_runtime_doctor.RuntimeBuildAndDoctorScriptTests.test_verify_repo_docs_ignores_ignored_worktree_markdown`
   - exit: `1` before the fix
   - result: reproduced the verifier bug by showing `-Check Docs` failed when an ignored `.worktrees/` Markdown file contained a broken link
10. `python -m unittest tests.runtime.test_runtime_doctor`
   - exit: `0` after the fix
   - result: script regression coverage passed with the new ignored-worktree case
11. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
   - exit: `1` before the fix, `0` after the fix
   - result: all build/runtime/contract/doctor/docs/scripts checks now pass in one run
12. `git diff --check`
   - exit: `0`
   - result: no whitespace errors; only CRLF normalization warnings from Git
13. `python -m unittest tests.runtime.test_issue_seeding.IssueSeedingScriptTests.test_validate_only_reports_seed_summary_from_yaml`
   - exit: `1` before the fix, `0` after the fix
   - result: reproduced the missing validation entrypoint, then verified the script can now parse `issue-seeds.yaml` and report the active seed summary without calling GitHub
14. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly`
   - exit: `0`
   - result: emitted JSON summary from `issue-seeds.yaml` including `issue_seed_version`, `issue_count`, and the current `GAP-027` title
15. `python -m unittest tests.runtime.test_issue_seeding.IssueSeedingScriptTests.test_validate_only_can_render_task_body_from_backlog`
   - exit: `1` before the fix, `0` after the fix
   - result: reproduced that the script could not render a backlog-derived task body, then verified it now emits `GAP-027` body text from the active backlog section
16. `python -m unittest tests.runtime.test_issue_seeding.IssueSeedingScriptTests.test_validate_only_can_render_epic_body_from_lifecycle_plan tests.runtime.test_issue_seeding.IssueSeedingScriptTests.test_validate_only_can_render_initiative_body_from_lifecycle_plan`
   - exit: `1` before the fix, `0` after the fix
   - result: reproduced that initiative/epic validation either still reflected old template expectations or lacked roadmap-derived coverage, then verified both bodies render from the active lifecycle plan
17. `python -m unittest tests.runtime.test_issue_seeding.IssueSeedingScriptTests.test_verify_repo_scripts_runs_issue_seeding_render_check`
   - exit: `1` before the fix, `0` after the fix
   - result: reproduced that `verify-repo.ps1 -Check Scripts` did not enforce issue body rendering, then verified the scripts gate now emits `OK issue-seeding-render`
18. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
   - exit: `0`
   - result: rendered all `17` task bodies, `5` epic bodies, and the initiative body without calling GitHub

## Verification Result
- `build`: pass
- `test`: pass
- `contract/invariant`: pass
- `hotspot`: pass
- `docs`: pass
- `scripts`: pass
- `runtime regression test`: pass
- `issue seeding regression test`: pass

## Risks
- The GitHub seeding script no longer duplicates task titles, seed metadata, task bodies, epic bodies, or the initiative body. The remaining parser-level coupling is now an explicit scripts gate; backlog and roadmap structure drift should fail `verify-repo.ps1 -Check Scripts`.
- This cleanup only improves planning and navigation fidelity; it does not implement `GAP-024`.
- Historical evidence remains intentionally inconsistent with the active baseline and must continue to be excluded from active doc drift assumptions.
- `verify-repo.ps1` is now git-aware for Markdown enumeration; if this repo later needs to verify Markdown files outside git tracking, the fallback path or policy may need another explicit decision.

## Rollback
- Preferred rollback: `git restore --source=HEAD -- README.md README.en.md README.zh-CN.md docs/README.md docs/backlog/README.md docs/backlog/full-lifecycle-backlog-seeds.md docs/backlog/issue-seeds.yaml docs/reviews/README.md docs/reviews/2026-04-18-full-repo-deep-audit-and-planning-refresh.md docs/change-evidence/README.md docs/change-evidence/20260418-full-repo-deep-audit-and-planning-refresh.md packages/README.md packages/contracts/README.md apps/README.md infra/README.md tests/README.md scripts/github/create-roadmap-issues.ps1 scripts/verify-repo.ps1 tests/runtime/test_runtime_doctor.py tests/runtime/test_issue_seeding.py`
- If only the new audit artifacts need removal, restore just:
  - `docs/reviews/2026-04-18-full-repo-deep-audit-and-planning-refresh.md`
  - `docs/change-evidence/20260418-full-repo-deep-audit-and-planning-refresh.md`
