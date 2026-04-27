# 20260427 Claude Code Native Attach Tier Parity

## Goal
- Follow up the initial Claude Code first-class certification by making the adapter tier equal where current evidence supports it.
- Promote Claude Code from `process_bridge` fallback posture to `native_attach` when live probe proves session/resume identity, structured output, hook events, and managed settings/hooks.
- Preserve the boundary that Codex and Claude Code host APIs are different and future host drift must degrade explicitly.

## Current-Source Basis
- Claude Code CLI reference: `https://code.claude.com/docs/en/cli-reference`
  - used capability inputs: `--resume`, `--session-id`, `--output-format`, `--include-hook-events`
- Claude Code hooks: `https://code.claude.com/docs/en/hooks`
  - used capability input: host hook lifecycle evidence
- Claude Code settings: `https://code.claude.com/docs/en/settings`
  - used capability input: managed project settings and permissions

## Changed Files
- `.claude/hooks/governed-pre-tool-use.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/claude_code_adapter.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_registry.py`
- `scripts/run-claude-code-adapter-trial.py`
- `tests/runtime/test_claude_code_adapter.py`
- `tests/runtime/test_adapter_registry.py`
- `docs/targets/templates/claude-code/governed-pre-tool-use.py`
- `docs/targets/target-repos-catalog.json`
- `docs/product/adapter-degrade-policy.md`
- `docs/product/adapter-conformance-parity-matrix.md`
- `docs/product/runtime-compatibility-and-upgrade-policy.md`
- `docs/product/claim-catalog.json`
- `docs/architecture/current-source-compatibility-policy.json`
- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/roadmap/optimized-hybrid-final-state-long-term-roadmap.md`
- `docs/plans/claude-code-first-class-entrypoint-plan.md`
- `docs/plans/optimized-hybrid-final-state-long-term-implementation-plan.md`
- `docs/plans/README.md`
- `docs/backlog/README.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/README.md`
- `docs/change-evidence/README.md`
- `rules/projects/github-toolkit/codex/AGENTS.md`
- `rules/projects/github-toolkit/claude/CLAUDE.md`
- `rules/projects/github-toolkit/gemini/GEMINI.md`

## Decision
Codex and Claude Code now have equal adapter tier on the current branch and current local host evidence:

| host | adapter_id | adapter_tier | parity_status | unsupported_capabilities |
|---|---|---|---|---|
| Codex CLI/App | `codex-cli` | `native_attach` | `supported` | `[]` |
| Claude Code | `claude-code` | `native_attach` | `supported` | `[]` |

Claude Code `native_attach` is defined by runtime-visible session/resume identity, structured stream output with hook lifecycle visibility, managed settings/hooks, and same-contract verification. It is not a claim that Claude Code exposes the same host API as Codex.

## Verification
- `claude --version`
  - status: pass
  - key_output: `2.1.114 (Claude Code)`
- `claude --help`
  - status: pass
  - key_output: includes `--resume`, `--session-id`, `--output-format`, `--include-hook-events`
- `python -m unittest tests.runtime.test_claude_code_adapter tests.runtime.test_adapter_registry tests.runtime.test_adapter_conformance`
  - status: pass
  - key_output: `Ran 24 tests`; `OK`
- `python scripts/run-claude-code-adapter-trial.py --repo-id governed-ai-coding-runtime --task-id task-gap-native-claude --binding-id binding-self-runtime --probe-live --probe-cwd D:\CODE\governed-ai-coding-runtime`
  - status: pass
  - key_output: `adapter_id=claude-code`, `adapter_tier=native_attach`, `flow_kind=live_attach`, `unsupported_capabilities=[]`, `session_id_available=true`, `structured_events_available=true`
- `python scripts/run-codex-adapter-trial.py --repo-id governed-ai-coding-runtime --task-id task-gap-native-codex --binding-id binding-self-runtime --probe-live --probe-cwd D:\CODE\governed-ai-coding-runtime`
  - status: pass
  - key_output: `adapter_id=codex-cli`, `adapter_tier=native_attach`, `flow_kind=live_attach`, `unsupported_capabilities=[]`
- inline conformance matrix over the live Codex and Claude Code trial payloads
  - status: pass
  - key_output: Codex `parity_status=supported`, Claude Code `parity_status=supported`, both `conformance_status=pass`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly -Json -GovernanceSyncTimeoutSeconds 120`
  - status: pass
  - key_output: `failure_count=0`
- `D:\CODE\github-toolkit`: `python -m py_compile gh_utils.py list-forks.py sync-forks.py test_toolkit.py test_support.py scripts/benchmark_hotpaths.py .claude/hooks/governed-pre-tool-use.py`
  - status: pass
  - key_output: no compile errors
- `D:\CODE\github-toolkit`: `python -m unittest test_toolkit.py`
  - status: pass
  - key_output: `Ran 137 tests`; `OK`
- `D:\CODE\github-toolkit`: `git diff --check`
  - status: pass
  - key_output: no whitespace errors
- `D:\CODE\github-toolkit`: `git commit -m "同步 GitHub Toolkit 治理画像 build 命令"`
  - status: pass
  - key_output: `18645a2`
- `python scripts/verify-target-repo-governance-consistency.py`
  - status: pass
  - key_output: `status=pass`, `target_count=5`, `drift_count=0`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -FailOnChange -Json`
  - status: pass
  - key_output: `status=pass`, `blocked_count=0`, `changed_count=0`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
  - status: pass
  - key_output: `OK python-bytecode`, `OK python-import`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
  - status: pass
  - key_output: `Running 74 test files with 4 workers`, `Completed 74 test files`, `failures=0`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - status: pass
  - key_output: `OK schema-json-parse`, `OK target-repo-governance-consistency`, `OK agent-rule-sync`, `OK functional-effectiveness`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
  - status: pass
  - key_output: `OK adapter-posture-visible`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
  - status: pass
  - key_output: `OK runtime-build`, `OK runtime-unittest`, `OK dependency-baseline`, `OK runtime-doctor`, `OK current-source-compatibility`, `OK powershell-parse`

## Residual Risks
- Claude Code `native_attach` depends on the current host CLI surface. A future Claude Code build that removes or changes `--resume`, `--session-id`, `--output-format=stream-json`, or `--include-hook-events` must degrade explicitly.
- Managed `.claude/settings.json` and `.claude/hooks/governed-pre-tool-use.py` remain required for this repo's Claude Code native attach posture.
- This does not start full `LTP-04` multi-host orchestration, A2A gateway, or host API unification.

## Rollback
Revert the Claude Code native attach predicate, CLI trial flag additions, registry contract update, tests, docs, claim catalog, compatibility policy, and this evidence file. If only the local Claude CLI loses the required surface, keep the code and let live probe downgrade Claude Code to `process_bridge` with `claude_native_attach_capability_incomplete`.
