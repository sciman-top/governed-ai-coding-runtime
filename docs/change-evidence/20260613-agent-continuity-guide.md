# 20260613 Agent Continuity Guide

## Goal
- current landing: `D:\CODE\governed-ai-coding-runtime`
- target home:
  - `README.md`
  - `README.zh-CN.md`
  - `README.en.md`
  - `docs/product/agent-continuity.md`
  - `docs/product/agent-continuity.zh-CN.md`
  - `docs/README.md`
  - `docs/change-evidence/20260613-agent-continuity-guide.md`
  - `docs/change-evidence/README.md`
- verification path: add a discoverable operator-facing continuity guide that matches the implemented continuity contract, CLI, and Operator UI boundary

## What Changed
- Added an English continuity guide at `docs/product/agent-continuity.md`.
- Added a Chinese continuity guide at `docs/product/agent-continuity.zh-CN.md`.
- Linked both guides from `docs/README.md` under the operator-facing daily-use surface.
- Linked both guides from the root README set under the quickstart / read-next surface.
- Kept the guide boundary narrow:
  - continuity is classification-first and read-only by default
  - secret-like payloads fail closed
  - `Claude Desktop` remains `referenced_only`
  - no claim of merged native histories or copied credentials

## Source Basis
- code and contract:
  - `packages/contracts/src/governed_ai_coding_runtime_contracts/agent_continuity.py`
  - `scripts/agent-continuity.py`
- plan and queue truth:
  - `docs/plans/agent-continuity-and-shared-context-plan.md`
  - `docs/architecture/planning-status.json`
- existing operator-facing patterns:
  - `docs/product/host-feedback-loop.md`
  - `docs/product/codex-cli-app-integration-guide.md`
- tests proving the claimed surfaces:
  - `tests/runtime/test_agent_continuity.py`
  - `tests/service/test_operator_api.py`
  - `tests/runtime/test_operator_ui.py`

## Verification
- `python -m unittest tests.runtime.test_agent_continuity tests.service.test_operator_api tests.runtime.test_operator_ui.OperatorUiTests.test_operator_ui_interactive_mode_renders_actions_and_ref_buttons -v`
  - result: pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - result: pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check DocsLinks`
  - result: pass

## Risk
- risk_level: `low`
- reason: documentation and navigation only; no runtime, host-local, or target-repo behavior changed

## Rollback
- remove:
  - `docs/product/agent-continuity.md`
  - `docs/product/agent-continuity.zh-CN.md`
  - related links in `docs/README.md`
  - this evidence file and its entry in `docs/change-evidence/README.md`
- re-run Docs and DocsLinks verification after rollback
