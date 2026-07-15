# 20260715 Agent Rule Governance 9.56 Current-State Reverification

## Scope

- `verified_at`: `2026-07-15T13:00:22+08:00`
- `control_repo`: `D:\CODE\governed-ai-coding-runtime`
- `managed_global_copies`: `C:\Users\sciman\.codex\AGENTS.md`, `C:\Users\sciman\.claude\CLAUDE.md`
- `discovered_targets`: `ai-content-delivery-studio`, `classroom-answer-toolkit`, `ClassroomToolkit`, `github-toolkit`, `k12-question-graph`, `local-ai-dev-orchestrator`, `qq-codex-bot`, `skills-manager`, `vps-ssh-launcher`
- `excluded_direct_children`: `external`, `governed-ai-coding-runtime`, `physicist_chinese_poster_batch_tool`, `文档`
- `baseline`: all ten repository worktrees were clean before verification; three target `main` branches already contained local commits not present on `origin/main`.

Direct-child Git-root discovery still finds exactly the nine allowlisted targets. Excluded directories were not recursively searched or project-rule modified. Gemini remains outside the managed family. The primary release record remains [20260715 Agent Rule Governance 9.56](./20260715-agent-rule-governance-9.56.md); this file records current-state changes and fresh verification without rewriting that historical release record.

## Research

The full source matrix, fixed source commits, local schema probes, and `adopt / reject / defer` decisions remain in [OpenAI / Anthropic Agent Rule Governance Refresh](../research/2026-07-14-agent-rule-governance-refresh.md). This refresh rechecked the following drift-prone sources and local versions.

| source_url | accessed_at | applicable_product | applicable_version | local_observation | decision | reason | verification_method |
|---|---|---|---|---|---|---|---|
| `https://developers.openai.com/codex/codex-manual.md` | `2026-07-15` | Codex App / CLI / cloud | current manual; local CLI `0.144.1` | manual helper updated the verified local cache; `codex debug prompt-input` remains available | adopt | official manual plus local executable evidence | manual helper, `codex --version`, `codex --help`, ten fresh prompt-input probes |
| `https://help.openai.com/en/articles/20001275-chatgpt-work-and-codex` | `2026-07-15` | ChatGPT Work / Codex | current hosted surfaces | desktop local work and web/mobile cloud Work remain separate surfaces | adopt | prevents local-file evidence from being projected to hosted Work or cloud | official page review plus local/hosted evidence separation |
| `https://code.claude.com/docs/en/memory` | `2026-07-15` | Claude Code | current docs; local CLI `2.1.206` | `CLAUDE.md` imports remain model context, not enforcement; imported files still consume context | adopt | supports the one-line `@AGENTS.md` wrapper and hook separation | official page review, wrapper verifier, current doctor, existing same-day interactive `/context` evidence |
| `https://code.claude.com/docs/en/claude-code-on-the-web` | `2026-07-15` | Claude Code cloud | current cloud surface | cloud sessions clone committed repository state and do not inherit machine-local files | adopt | preserves hosted/manual acceptance boundary | official page review and remote/default-branch audit |

No new community mechanism was promoted in this refresh. Existing fixed-commit community references remain structural cross-checks only; host semantics still require official documentation or local executable evidence.

## Architecture

- `Global WHAT`: release `9.56` remains the cross-repository obligations, risk, evidence, N/A, dirty-worktree, and completion contract.
- `Project WHERE/HOW`: all nine root `AGENTS.md` files remain repository-owned contract `2.0`; all nine `CLAUDE.md` files remain exact one-line imports.
- `Platform DELTA`: local Codex and Claude loading/enforcement evidence remains separate from ChatGPT Work, Codex cloud, Claude Chat, and Claude Code cloud.
- `Deterministic Enforcement`: family/target verifiers, sync scripts, schema, repository gates, target workflows, and aggregate GitHub Actions remain the enforcement surfaces. Aggregate CI intentionally audits remote default branches.

## Changes

- No global rule, manifest, schema, verifier, target project rule, wrapper, host config, provider, auth, credential, MCP endpoint, or runtime process was changed.
- Added only this current-state verification ledger and its evidence-index link.
- Recognized an external state change since the primary release: `ClassroomToolkit` integrated the `9.56` task commit and dependency-governance repair into remote `main` at `d364d547002fffd2fa7f64199d9209feaf7ebb98`.
- Preserved existing local-ahead `main` histories in `k12-question-graph`, `local-ai-dev-orchestrator`, and `skills-manager`; this task did not push those pre-existing commits.

## Integration

- Global source/deployed raw SHA-256 values match: Codex `D3C873F73A378136B43588EBB2DB2291077A16A5FB8CFA9264AF22B17232786B`; Claude `4A24410AFA9F39911C05E745397858C44EA90216DCF989C4D817A16775F30A7C`.
- Guarded sync dry-run returned `changed_count=0` and `blocked_count=0`; no redundant apply was performed because the prior protected apply was already effective.
- The existing rollback backup `docs/change-evidence/rule-sync-backups/20260715-003426/` was rechecked recursively: two files exist with SHA-256 `6B6D478CCD29BB5406F9B586C72AF9B34CE9DFF6BA25E629C6FE8B314C237E0F` (Codex 9.55) and `92348E2BFA1AB06528CFBAF8E86C10BE9DB5E37785C23CAFB6977BF1B9D6956D` (Claude 9.55).
- Gate-generated tracked reports in the control repository and K12, plus four generated K12/skills-manager reports, were compared with the clean baseline and removed or restored by exact path. Final repository content returned to the frozen baseline before this ledger was added.
- No broad cleanup, reset, branch deletion, worktree deletion, process restart, live VPS action, or hosted workspace mutation occurred.

## Verification

### Control And Rule Family

| command | exit | key result |
|---|---:|---|
| `python scripts/verify-agent-rule-family.py` | 0 | release `9.56`; common A/C/D hash matched |
| `python scripts/verify-target-project-rules.py --require-all` | 0 | 9 discovered, 9 passed, no missing or unlisted roots |
| `python scripts/sync-agent-rules.py --scope All --fail-on-change` | 0 | `changed_count=0`, `blocked_count=0` |
| `pwsh ... scripts/build-runtime.ps1` | 0 | Python bytecode/import passed |
| `pwsh ... scripts/verify-repo.ps1 -Check Runtime` | 0 | 104 test files, 8 workers, failures `0` |
| `pwsh ... scripts/verify-repo.ps1 -Check Contract` | 0 | schema, dependency, rule family, target audit, pre-change, reference, and effectiveness checks passed |
| `pwsh ... scripts/doctor-runtime.ps1` | 0 | runtime/path/gate/hook/status/capability checks passed |

### Fresh Local Loading

- Codex: ten new `codex debug prompt-input` processes covered the control repository and all nine targets. Every process returned `exit=0`, `items=5`, `global_956=true`, `project_contract=true`, `project_review_956=true`, and `cwd_seen=true`.
- Claude: `claude doctor` returned `exit=0`, version `2.1.206`, commit `edc8ebf7f852`, and no installation issue. Model-visible loading continues to rely on the unchanged same-day ten-repository interactive `/context` evidence in the primary release record; a non-interactive `claude -p` self-report was deliberately not substituted for `/context`.
- The Codex/Claude global and project files, hashes, wrappers, and CLI versions did not drift between the primary interactive proof and this refresh.
- These results prove local loading only. ChatGPT Work web/mobile, Codex cloud, Claude Chat, and Claude Code cloud remain onsite/manual acceptance pending.

### Target Gates

| repository | ordered verification | result |
|---|---|---|
| `ai-content-delivery-studio` | build; 461 tests; reference/format; release preflight | pass |
| `classroom-answer-toolkit` | build; 57 tests; 43 assets / 3 packs / 3 snapshots; toolchain | pass; cloud-backed lanes remain disabled without egress/secrets |
| `ClassroomToolkit` | build; 3544 tests; 29 contract tests; hotspot; standard quality profile | pass; dependency governance and vulnerability scan now pass |
| `github-toolkit` | compile; 189 tests; benchmark; Ruff; Mypy | pass; independent contract remains compliant `gate_na`; no GitHub write occurred |
| `k12-question-graph` | build; C002 dry-run; roadmap guard; structured parse | pass; `REAL005=not_closed`; process-impacting full gate and independent hotspot remain compliant `gate_na` |
| `local-ai-dev-orchestrator` | 307 tests; planning verifier; selector; preflight | pass; build/hotspot remain compliant `gate_na`; baseline is still candidate |
| `qq-codex-bot` | fast; 867 tests / 10 skipped; full verifier; local health | repository full gate pass; `all_checks_ok=false`, Docker daemon/local runtime absent, no VPS projection |
| `skills-manager` | build; 485 Unit; 12 E2E; doctor/dependency; full profile | pass |
| `vps-ssh-launcher` | compile; 93 pytest / 1 skipped / 20 subtests; 94 unittest / 1 skipped; offline full gate | pass; no real SSH integration |

## Git

| repository | local state | remote governance state | default_branch_effective | hosted rule-contract state |
|---|---|---|---:|---|
| `governed-ai-coding-runtime` | `main=24f0b5f`, clean, equals `origin/main` before this ledger | `main=24f0b5f` | yes | fresh aggregate run `29390285293` failed on the three non-effective targets below |
| `ai-content-delivery-studio` | clean `main=3749054` | `main=3749054` | yes | success `29351469072` |
| `classroom-answer-toolkit` | clean `main=6486358` | `main=6486358` | yes | success `29351470237` |
| `ClassroomToolkit` | clean `main=d364d54` | `main=d364d54`, includes `cd49d47` | yes | success `29356760034`; aggregate job fresh success |
| `github-toolkit` | clean `main=811afc3` | `main=811afc3` | yes | success `29351467159` |
| `k12-question-graph` | clean `main=4821492`, ahead 4 | `main=46a4b31`; task `5c987ce` | no | task success `29351490041`; aggregate job fresh failure on default main |
| `local-ai-dev-orchestrator` | clean `main=2fd4f62`, ahead 11 | `main=29dea22`; task `c9f70f5` | no | task success `29351495377`; aggregate job fresh failure on default main |
| `qq-codex-bot` | clean `main=47c7d71` | `main=47c7d71` | yes | success `29351470041` |
| `skills-manager` | clean `main=adbb8fe`, ahead 9 | `main=ae8a860`; task `4addb13` | no | task workflow success at the rule-changing SHA; aggregate job fresh failure on default main |
| `vps-ssh-launcher` | clean `main=2a57512` | `main=2a57512` | yes | success `29351466033` |

The aggregate failure is not a verifier defect: its contract intentionally audits remote default branches. Pointing the aggregate workflow at task branches would conceal the required `default_branch_effective=false` state.

## Risks

- `platform_na`: ChatGPT Work web/mobile, Codex cloud, Claude Chat, and Claude Code cloud local-file loading. `alternative_verification=official surface docs plus local source/deployed hashes`; `evidence_link=this file and the primary research`; `expires_at=next authorized hosted acceptance window`; `recovery_condition=run an authorized fresh hosted workspace/session check`.
- K12 test/full `gate_na`: `reason=PostgreSQL and API process impact lacks authorization`; `alternative_verification=build + C002 dry-run + roadmap guard + structured parse + rule audit`; `evidence_link=D:\CODE\k12-question-graph\docs\evidence\20260715-agent-rule-governance-9.56.md`; `expires_at=next executable change`; `recovery_condition=obtain explicit process-impact authorization and run tools/run-gates.ps1`.
- K12 hotspot `gate_na`: no independent command; recovery is to add and execute one at the next executable hotspot change.
- QQ live acceptance: repository verification passes, but local Docker/runtime health and VPS projection are not accepted; recovery requires an authorized runtime/VPS window.
- Three task branches are pushed but not default-branch effective. Their local `main` histories contain pre-existing commits, so this task cannot safely push them as this task's write-set or merge task branches without additional authorization.

## Completion Boundary

- `fully completed`: **no**. Global rule optimization and protected sync are published, source/deployed copies remain zero-drift, the control contract and six target default branches are current, and all authorized local gates pass or use compliant N/A; the open items below still prevent overall completion.
- `repo-side completed`: all nine targets remain discovered, audited, rule-contract verified, and have published governance commits.
- `pushed but not default-branch effective`: `k12-question-graph`, `local-ai-dev-orchestrator`, `skills-manager`.
- `onsite/manual acceptance pending`: ChatGPT Work, Codex cloud, Claude Chat, Claude Code cloud, K12 process-impacting full gate, QQ local/VPS live health.
- `blocked`: overall `fully completed` claim is blocked by the three non-effective default branches and onsite/manual items; there is no remaining `ClassroomToolkit` dependency blocker.

Open items:

| item | next_action | responsible_party | authorization_needed | retest_condition |
|---|---|---|---|---|
| three non-effective default branches | review the pre-existing local-ahead histories, then explicitly authorize a merge/push strategy per repository | repository owner | merge task branches and/or push pre-existing main commits | remote `main` contains the governance SHA and aggregate job passes |
| hosted OpenAI/Anthropic surfaces | run fresh workspace/session checks on each hosted surface | workspace owner/admin | hosted account/session access | model-visible/project rule source is proven on that surface |
| K12 process full gate | run `tools/run-gates.ps1` in a controlled PostgreSQL/API window | K12 operator | process-impact authorization | full gate exits 0 without losing prior process state |
| QQ live health | restore/authorize local Docker or VPS runtime and run the live acceptance runbook | QQ/VPS operator | runtime/VPS authorization | `all_checks_ok=true` and real message-path acceptance is recorded |

No overall `fully completed` claim is made while these items remain open.

## Rollback

- Revert only this ledger and its index link if this refresh must be removed.
- Global rollback remains the verified `docs/change-evidence/rule-sync-backups/20260715-003426/` plus a guarded sync and zero-drift rerun.
- Target rollback remains per-repository task-SHA revert on the published ref; never reset or overwrite the preserved local-ahead histories.
