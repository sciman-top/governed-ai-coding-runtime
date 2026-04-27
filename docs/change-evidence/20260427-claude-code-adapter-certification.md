# 20260427 Claude Code Adapter Certification

## Goal
- Execute `GAP-117..119` after the managed Claude Code settings/hooks surface.
- Add a first-class `claude-code` adapter probe and conformance path.
- Certify Codex plus Claude Code as dual first-class entrypoints in governance result without claiming identical adapter tier.

## Changed Files
- `packages/contracts/src/governed_ai_coding_runtime_contracts/claude_code_adapter.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/adapter_conformance.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
- `scripts/run-claude-code-adapter-trial.py`
- `tests/runtime/test_claude_code_adapter.py`
- `tests/runtime/test_adapter_conformance.py`
- `docs/product/adapter-degrade-policy.md`
- `docs/product/claim-catalog.json`
- `docs/plans/claude-code-first-class-entrypoint-plan.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/README.md`
- `docs/backlog/README.md`
- `docs/roadmap/optimized-hybrid-final-state-long-term-roadmap.md`
- `docs/architecture/hybrid-final-state-master-outline.md`
- `docs/architecture/current-source-compatibility-policy.json`

## Decision
Codex and Claude Code are certified as dual first-class entrypoints in governance result.

Current evidence-backed adapter posture:
- Codex: `adapter_id=codex-cli`, `adapter_tier=native_attach`, `parity_status=supported`.
- Claude Code: `adapter_id=claude-code`, `adapter_tier=process_bridge`, `parity_status=degraded`, `unsupported_capabilities=["native_attach"]`.

This means Claude Code is first-class for rules, gates, evidence, rollback, risk, claim drift, and target sync. It does not mean Claude Code has Codex `native_attach` parity.

## Verification
- `python -m unittest tests.runtime.test_claude_code_adapter tests.runtime.test_adapter_conformance tests.runtime.test_adapter_registry`
  - status: pass
  - key_output: `Ran 20 tests`; `OK`
- `python scripts/run-claude-code-adapter-trial.py --repo-id governed-ai-coding-runtime --task-id task-gap-117-claude --binding-id binding-self-runtime --settings --hooks`
  - status: pass
  - key_output: `adapter_id=claude-code`, `adapter_tier=process_bridge`, `unsupported_capabilities=["native_attach","structured_events","structured_evidence_export","resume_id"]`
- `python scripts/run-claude-code-adapter-trial.py --repo-id governed-ai-coding-runtime --task-id task-gap-117-claude-live --binding-id binding-self-runtime --probe-live --probe-cwd D:\CODE\governed-ai-coding-runtime`
  - status: pass
  - key_output: `claude_cli_available=true`, `settings_available=true`, `hooks_available=true`, `adapter_tier=process_bridge`, `unsupported_capabilities=["native_attach"]`
- `python scripts/run-codex-adapter-trial.py --repo-id governed-ai-coding-runtime --task-id task-gap-119-codex --binding-id binding-self-runtime --probe-live --probe-cwd D:\CODE\governed-ai-coding-runtime`
  - status: pass
  - key_output: `adapter_id=codex-cli`, `adapter_tier=native_attach`, `unsupported_capabilities=[]`
- `python scripts/run-claude-code-adapter-trial.py --repo-id governed-ai-coding-runtime --task-id task-gap-119-claude --binding-id binding-self-runtime --probe-live --probe-cwd D:\CODE\governed-ai-coding-runtime`
  - status: pass
  - key_output: `adapter_id=claude-code`, `adapter_tier=process_bridge`, `unsupported_capabilities=["native_attach"]`
- inline conformance matrix over the Codex and Claude Code trial payloads
  - status: pass
  - key_output: Codex `parity_status=supported`, Claude Code `parity_status=degraded`, both `conformance_status=pass`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - status: pass
  - key_output: `OK current-source-compatibility`, `OK claim-drift-sentinel`, `OK post-closeout-queue-sync`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`
  - status: pass
  - key_output: `OK powershell-parse`, `OK issue-seeding-render`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
  - status: pass
  - key_output: `OK target-repo-governance-consistency`, `OK agent-rule-sync`, `OK functional-effectiveness`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
  - status: pass
  - key_output: `Running 74 test files`, `failures=0`, `OK runtime-doctor`, `OK post-closeout-queue-sync`

## Residual Risks
- Claude Code remains degraded for `native_attach`; this is explicit and evidence-bound.
- The certification does not start broader `LTP-04` multi-host infrastructure.
- Claude Code host behavior can drift, so current-source and claim-drift gates must keep this claim fresh.

## Rollback
Revert the `claude_code_adapter` module, trial script, conformance additions, tests, docs, claim catalog update, and evidence. If only the adapter probe is rolled back, keep `GAP-116` settings/hooks templates and downgrade Claude Code from certified first-class to managed-but-not-certified support.
