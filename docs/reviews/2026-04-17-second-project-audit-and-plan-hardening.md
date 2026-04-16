# 2026-04-17 Second Project Audit And Plan Hardening

## Goal
Re-audit the repository before runtime coding starts, verify that planning assets match the current docs-first/contracts-first baseline, and harden the contract surface needed for the first executable slice.

## Current Repo Facts
- The repository has one committed baseline and is currently on `main`.
- Active top-level implementation directories are still limited to `docs/`, `schemas/`, and `scripts/`.
- Runtime directories `apps/`, `packages/`, `infra/`, and `tests/` are still intentionally absent.
- Project-level rules route documentation, decisions, and review conclusions to `docs/`; machine-readable contracts to `schemas/`; and GitHub planning helpers to `scripts/`.

## Audit Findings
1. `ADR-0005` makes control packs a first-class concept, but the repo had no machine-readable `control-pack` contract. This left GAP-003 underspecified for the next implementation session.
2. PRD and roadmap input lists still emphasized the early contract subset and did not fully list the contract family that is now landed.
3. Backlog and issue-seeding text used "sample control pack" without distinguishing metadata examples from runtime-consumable packs.
4. Active markdown links, schema/catalog pairing, JSON schema parsing, PowerShell script parsing, and existing schema examples were healthy at audit time.

## Optimization Decisions
- Add a draft `Control Pack Spec` plus JSON Schema and a minimal metadata example.
- Keep the new control-pack contract additive; do not change existing schema semantics.
- Update PRD and roadmap source lists so implementation starts from the complete governance-kernel contract family.
- Clarify that the newly added control-pack example is metadata only, while a runtime-consumable sample pack remains future implementation work.
- Keep runtime code out of this pass.

## Updated Implementation Posture
- Next implementation should start with skeleton and verification entrypoints, not with additional planning-only expansion.
- GAP-003 should implement a runtime-consumable pack from the metadata contract and wire it into repo admission.
- The first runnable slice should still prioritize task intake, repo profile resolution, bounded read-only execution, evidence, and a CLI/scripted trial path.

## Residual Risks
- The new `control-pack` schema only validates metadata shape; cross-artifact references still need a future catalog/link validator.
- `scripts/github/create-roadmap-issues.ps1` still owns its issue body text directly instead of reading `docs/backlog/issue-seeds.yaml`.
- Build, test, and hotspot gates remain `gate_na` until runtime and verification entrypoints exist.

## Verification Intent
This review should be paired with a change-evidence file that records:
- Codex diagnostics
- active markdown link check
- schema JSON parse
- schema catalog pairing
- schema example validation
- PowerShell script parse
- roadmap/backlog/script drift checks
