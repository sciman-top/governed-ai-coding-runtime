# Agent Rule Governance Documentation

This directory documents the active Codex + Claude rule-governance product.
Runtime-era documents are recoverable from `archive/runtime-v1-20260716` and
Git history; they are intentionally absent from the active tree.

## Start Here

- [Root overview](../README.md)
- [Chinese guide](../README.zh-CN.md)
- [English guide](../README.en.md)
- [Project contract](../AGENTS.md)

## Active Design And Operations

- [Agent Rule Governance v2 architecture](./architecture/agent-rule-governance-v2.md)
- [Rule release runbook](./runbooks/agent-rule-release.md)
- [Official and community source basis](./research/agent-rule-governance-v2-sources.md)

## Evidence

- [Pre-change review](./change-evidence/20260716-agent-rule-governance-v2-pre-change-review.md)
- [Current migration evidence](./change-evidence/20260717-agent-rule-governance-v2-current-state.md)

The current evidence distinguishes repository-side verification from mutable
target state, native host loading, and hosted acceptance. Historical existence
of a runtime artifact is not evidence that the capability remains active.

## Machine Contracts

- [Global projection manifest](../rules/manifest.json)
- [Global canonical source manifest](../rules/global/source-manifest.json)
- [Target coordination registry](../rules/target-project-rule-coordination.json)
- [Target coordination schema](../schemas/jsonschema/target-project-rule-coordination.schema.json)
- [Target CI template](../rules/templates/github/agent-rule-contract.yml)

## Verification

```powershell
python scripts/rulesctl.py verify
python scripts/rulesctl.py status
python scripts/rulesctl.py audit --state default
```

`verify` is repo-local by default. `status` and `audit` intentionally retain
external target failures instead of weakening the control-repository gate or
hiding fleet drift.
