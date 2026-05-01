# 2026-05-01 GAP-138 Policy Tool Credential Audit Boundary

## Goal
Close `GAP-138` by turning tool/credential scope, repo-profile allowlists, and target-repo override limits into a fail-closed audit contract with a verifier-backed runtime report.

## Risk
- risk_tier: medium
- primary_risk: a governance runtime could silently widen tool or credential scope, or let target repos override policy boundaries without explicit audit evidence
- compatibility_boundary: this change adds schema/spec/architecture contracts, builder/verifier scripts, tests, and one generated report; it does not mutate user-level deployed rules, sync target repos, push, or merge

## Changes
- added [Policy Tool Credential Audit Schema](/D:/CODE/governed-ai-coding-runtime/schemas/jsonschema/policy-tool-credential-audit.schema.json)
- added [Policy Tool Credential Audit Spec](/D:/CODE/governed-ai-coding-runtime/docs/specs/policy-tool-credential-audit-spec.md)
- added [Policy Tool Credential Audit Boundary](/D:/CODE/governed-ai-coding-runtime/docs/architecture/policy-tool-credential-audit-boundary.json)
- added [Policy Tool Credential Audit Example](/D:/CODE/governed-ai-coding-runtime/schemas/examples/policy-tool-credential-audit/default-runtime.example.json)
- added [Policy Tool Credential Audit Builder](/D:/CODE/governed-ai-coding-runtime/scripts/build-policy-tool-credential-audit.py)
- added [Policy Tool Credential Audit Verifier](/D:/CODE/governed-ai-coding-runtime/scripts/verify-policy-tool-credential-audit.py)
- added [Policy Tool Credential Audit Tests](/D:/CODE/governed-ai-coding-runtime/tests/runtime/test_policy_tool_credential_audit.py)
- generated [Policy Tool Credential Audit Report](/D:/CODE/governed-ai-coding-runtime/docs/change-evidence/policy-tool-credential-audit-report.json)
- updated [Schema Catalog](/D:/CODE/governed-ai-coding-runtime/schemas/catalog/schema-catalog.yaml), [Schemas README](/D:/CODE/governed-ai-coding-runtime/schemas/README.md), [Schema Examples README](/D:/CODE/governed-ai-coding-runtime/schemas/examples/README.md), and [Architecture README](/D:/CODE/governed-ai-coding-runtime/docs/architecture/README.md) so the new contract is discoverable
- updated [scripts/verify-repo.ps1](/D:/CODE/governed-ai-coding-runtime/scripts/verify-repo.ps1) so `-Check Contract` requires the policy tool credential audit verifier

## Pre-Change Review
pre_change_review: required because this change updates `scripts/verify-repo.ps1`, adds a new governance boundary contract, and introduces a generated evidence artifact.

control_repo_manifest_and_rule_sources: checked against `rules/manifest.json`, `docs/backlog/issue-ready-backlog.md`, `docs/plans/governance-hub-reuse-and-controlled-evolution-plan.md`, `docs/specs/tool-contract-spec.md`, and `docs/architecture/control-pack-inheritance-matrix.json` before editing.

user_level_deployed_rule_files: not changed by this implementation; the audit remains repository-local and does not edit `~/.codex` or other deployed user rule copies.

target_repo_deployed_rule_files: not changed by this implementation; target repos are only represented as bounded override policy in the audit contract.

target_repo_gate_scripts_and_ci: checked for boundary impact by wiring the verifier into this control repo's contract gate rather than mutating downstream target-repo gates or CI.

target_repo_repo_profile: checked through `.governed-ai/repo-profile.json` as the source of the allowlisted local shell surface; no target repo profile was modified.

target_repo_readme_and_operator_docs: checked by updating status and schema discovery docs so the audit boundary is operator-visible instead of chat-only.

current_official_tool_loading_docs: checked at the boundary level through the existing host/source compatibility policy and host posture evidence; no tool-loading semantics were changed by this implementation.

drift-integration decision: integrate by adding a fail-closed audit boundary and verifier-backed report inside the control repo, while keeping deployed rule copies and target repo state unchanged until a later sync task explicitly needs them.

## Verification
```powershell
python scripts/build-policy-tool-credential-audit.py
```

Result: pass. Key output: `status=pass`, `audited_tool_count=4`, `unknown_tool_count=0`, `overbroad_credential_count=0`, `unsupported_override_count=0`.

```powershell
python scripts/verify-policy-tool-credential-audit.py
```

Result: pass. Key output: `status=pass`, `repo_profile_allowlist_count=1`, `override_surface_count=2`.

```powershell
python -m unittest tests.runtime.test_policy_tool_credential_audit
```

Result: pass. Key output: `Ran 2 tests`, `OK`.

## Outcome
- tool and credential scope is now declared, audited, and fail-closed instead of implied
- target-repo override rules are limited to `tighten_only` or `platform_limit_only`
- default browser-like external side-effect surfaces remain denied until a later bounded contract exists

## Rollback
- remove `schemas/jsonschema/policy-tool-credential-audit.schema.json`
- remove `docs/specs/policy-tool-credential-audit-spec.md`
- remove `docs/architecture/policy-tool-credential-audit-boundary.json`
- remove `schemas/examples/policy-tool-credential-audit/default-runtime.example.json`
- remove `scripts/build-policy-tool-credential-audit.py`, `scripts/verify-policy-tool-credential-audit.py`, and `tests/runtime/test_policy_tool_credential_audit.py`
- remove `docs/change-evidence/policy-tool-credential-audit-report.json`
- remove the `policy-tool-credential-audit` hook from `scripts/verify-repo.ps1`
