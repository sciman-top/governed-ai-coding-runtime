# Claude Code First-Class Entrypoint Plan

## Status
- Created on 2026-04-27 as owner-directed bounded scope after the post-certification selector.
- Queue: `GAP-115..119`.
- Current intent: make Codex and Claude Code equally important first-class supported hosts in governance outcome.
- This is not automatic permission to start the full `LTP-04 multi-host-first-class` heavy package.

## Goal
Promote Claude Code from generic non-Codex compatibility to a first-class supported host alongside Codex.

First-class means:
- equal governance requirements for rules, gates, evidence, rollback, risk classification, and claim drift
- equal all-target rollout expectations where the host surface exists
- equal `native_attach` adapter tier when live host evidence proves session/resume identity, structured output, hook events, and managed settings/hooks
- explicit `platform_na` or degraded posture when a Claude Code capability is unavailable

First-class does not mean:
- pretending Claude Code has the same host API as Codex, or that `native_attach` remains available after host capability drift
- replacing runtime-owned approval, containment, verification, rollback, evidence, or claim drift with host-local settings
- starting A2A gateway, full multi-host orchestration, or other `LTP-04` heavy infrastructure by default

## Architecture Decisions
- `CLAUDE.md` remains the Claude Code context rule surface.
- Claude Code settings, permissions, and hooks are the enforceable host-control surfaces and must complement, not replace, runtime gates.
- Adapter parity is measured by governance-result linkage, not by identical host APIs.
- Codex and Claude Code now share the `native_attach` tier on current evidence. If a future host build loses required session/resume, structured-output, or hook surfaces, the adapter must explicitly degrade while preserving the same runtime-owned evidence chain.

## Task List

### GAP-115 Dual First-Class Host Scope Boundary
Define the claim boundary and update planning sources so Codex and Claude Code are described as dual first-class entrypoints.

Acceptance criteria:
- [x] docs use "Codex + Claude Code dual first-class entrypoint" consistently
- [x] first-class means equal governance result and current evidence-backed `native_attach` tier, not identical host APIs
- [x] the plan records why full `LTP-04` remains trigger-based

Verification:
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

Dependencies: `GAP-114`

### GAP-116 Claude Code Settings And Hooks Governance Template
Add a managed Claude Code settings/hooks template surface for target repos.

Acceptance criteria:
- [x] `CLAUDE.md` carries context rules and settings/hooks carry enforceable controls
- [x] unsupported settings or hooks fail closed or record `platform_na`
- [x] template sync avoids overwriting unrelated local Claude configuration

Verification:
- [x] targeted template validation tests
- [x] target-repo governance consistency check
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`

Dependencies: `GAP-115`

### GAP-117 Claude Code Adapter Probe And Conformance Parity
Add a Claude Code-specific adapter probe and conformance path.

Acceptance criteria:
- [x] `claude-code` probe reports capability tier, degrade reason, and unsupported capabilities
- [x] conformance tests prove identity, evidence, verification, handoff, and replay linkage
- [x] missing Claude CLI or hook support records degraded posture instead of silent parity

Verification:
- [x] `python -m unittest tests.runtime.test_adapter_conformance tests.runtime.test_adapter_registry`
- [x] representative runtime-flow evidence for `adapter_id=claude-code`

Dependencies: `GAP-116`

### GAP-118 All-Target Claude Code Rule And Config Sync
Apply and verify Claude Code first-class rule/config surfaces across all active target repos.

Acceptance criteria:
- [x] all target repos have synchronized `CLAUDE.md`
- [x] managed Claude Code settings/hooks surfaces are synchronized or explicitly `platform_na`
- [x] drift detection covers changed managed files without touching unrelated local files

Verification:
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/sync-agent-rules.ps1 -Scope All -FailOnChange`
- [x] `python scripts/verify-target-repo-governance-consistency.py`
- [x] all-target governance baseline sync dry run or apply run as needed

Dependencies: `GAP-116`, `GAP-117`

### GAP-119 Dual First-Class Host Certification
Certify the dual first-class entrypoint claim only after fresh Codex and Claude Code evidence exists.

Acceptance criteria:
- [x] Codex and Claude Code each pass the same governance-result acceptance chain
- [x] final evidence names adapter tiers, unsupported/degraded capabilities if any, target repos, commands, and rollback
- [x] claim catalog and adapter parity matrix are updated without overstating `native_attach`

Verification:
- [x] `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All`
- [x] representative Codex and Claude Code runtime-flow evidence
- [x] all-target rule/config sync and governance consistency checks

Dependencies: `GAP-117`, `GAP-118`

## Risks And Mitigations
| risk | impact | mitigation |
|---|---|---|
| `CLAUDE.md` is treated as enforcement | host rules become advisory only | use settings/hooks plus runtime gates for enforcement |
| host capabilities are overstated | false final-state claim | require adapter tier, degrade reason, and `platform_na` evidence |
| target repo local settings are overwritten | user-local drift or data loss | sync only managed template surfaces and keep backups |
| full `LTP-04` starts by accident | unnecessary platform width | keep this queue bounded to Claude Code first-class support |

## Checkpoints
- After `GAP-115`: docs and issue rendering agree on the claim boundary.
- After `GAP-117`: Claude Code has real probe/conformance evidence, with degraded posture only when required host surfaces are missing.
- After `GAP-119`: dual first-class certification is either evidence-backed or downgraded.

## Rollback
Revert the `GAP-115..119` planning, templates, adapter changes, sync surfaces, claim-catalog entry, and evidence. If rollback happens after partial implementation, downgrade Claude Code to generic non-Codex compatibility until fresh evidence exists.
