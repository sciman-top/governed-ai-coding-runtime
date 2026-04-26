# GAP-093 Through GAP-095 Closeout Evidence

## Goal
Close the optimized hybrid long-term planning baseline, implement the `GAP-094` execution containment contract slice, and land the `GAP-095` provenance floor for generated light packs.

## Scope
- `GAP-093`: validate that roadmap, implementation plan, backlog, issue seeds, plan index, and docs index agree on `GAP-093..102`.
- `GAP-094`: add a schema/spec/Python/test floor for execution containment profiles.
- `GAP-095`: add local provenance generation, validation, doctor visibility, and operator documentation for repo attachment light packs.

## Changed Files
- `README.md`
- `README.en.md`
- `README.zh-CN.md`
- `docs/README.md`
- `docs/backlog/issue-ready-backlog.md`
- `docs/plans/optimized-hybrid-final-state-long-term-implementation-plan.md`
- `docs/specs/tool-contract-spec.md`
- `docs/specs/provenance-and-attestation-spec.md`
- `docs/product/target-repo-attachment-flow.md`
- `docs/product/target-repo-attachment-flow.zh-CN.md`
- `docs/quickstart/use-with-existing-repo.md`
- `docs/quickstart/use-with-existing-repo.zh-CN.md`
- `schemas/jsonschema/tool-contract.schema.json`
- `schemas/jsonschema/provenance-and-attestation.schema.json`
- `schemas/examples/tool-contract/default-runtime.example.json`
- `schemas/examples/provenance-and-attestation/repo-light-pack.example.json`
- `schemas/examples/README.md`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/__init__.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/runtime_status.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/tool_runner.py`
- `scripts/attach-target-repo.py`
- `scripts/doctor-runtime.ps1`
- `tests/runtime/test_repo_attachment.py`
- `tests/runtime/test_runtime_doctor.py`
- `tests/runtime/test_tool_runner.py`

## Change Summary
- Marked `GAP-093` as complete after issue rendering and docs validation passed.
- Added `ContainmentProfile` contract primitives for executable tool families.
- Added fail-closed contained execution governance for missing profiles, unknown tool families, and mismatched tool-family profiles.
- Added containment registry validation for the required executable tool families: `file_write`, `shell`, `git`, `package_manager`, `browser_automation`, and `mcp_tool_bridge`.
- Extended `tool-contract.schema.json` and `tool-contract-spec.md` with containment profile fields.
- Added a schema-valid default runtime tool-contract example.
- Updated user-facing README status so `LTP-01..06` remain trigger-based rather than started work.
- Generated `.governed-ai/light-pack.provenance.json` beside newly generated light packs.
- Validated declared light-pack provenance by matching `subject_digest`, `output_digest`, and `target_repo_binding`.
- Surfaced `OK attachment-light-pack-provenance` and `WARN attachment-light-pack-provenance-unsupported` in doctor output.
- Added a repo-light-pack provenance schema example and bilingual operator docs for regeneration/rollback behavior.

## Verification
Commands already run:
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `python -m unittest tests.runtime.test_tool_runner`
- `python -m unittest tests.runtime.test_repo_attachment tests.runtime.test_runtime_doctor tests.runtime.test_runtime_status`
- `python -m compileall packages/contracts/src scripts/run-readonly-trial.py`
- `python -m compileall packages/contracts/src scripts/attach-target-repo.py`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`

Key output:
- issue rendering before closeout: `issue_seed_version=4.2`, `rendered_tasks=80`, `rendered_epics=14`, `completed_task_count=70`, `active_task_count=10`
- issue rendering after closeout: `issue_seed_version=4.2`, `rendered_tasks=80`, `rendered_issue_creation_tasks=8`, `rendered_epics=14`, `completed_task_count=72`, `active_task_count=8`
- issue rendering after `GAP-095`: `issue_seed_version=4.2`, `rendered_tasks=80`, `rendered_issue_creation_tasks=7`, `rendered_epics=14`, `completed_task_count=73`, `active_task_count=7`
- docs verification: `OK active-markdown-links`, `OK backlog-yaml-ids`, `OK claim-evidence-freshness`, `OK post-closeout-queue-sync`
- targeted runtime tests: `Ran 15 tests ... OK`
- attachment/provenance runtime tests: `Ran 38 tests ... OK`
- runtime gate before provenance: `Ran 417 tests ... OK (skipped=5)`, `Ran 10 tests ... OK`
- runtime gate after provenance: `Ran 418 tests ... OK (skipped=5)`, `Ran 10 tests ... OK`
- contract gate: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`, `OK dependency-baseline`, `OK target-repo-rollout-contract`, `OK target-repo-governance-consistency`, `OK target-repo-powershell-policy`, `OK agent-rule-sync`
- compile: `tool_runner.py` and contract package compile successfully
- `git diff --check`: no whitespace errors; Git reported CRLF normalization warnings for existing text files

## Residual Risks
- `GAP-094` now has a contract and validation floor. Broader runtime/UI presentation can be strengthened later if a new execution family becomes active.
- Browser and MCP execution families are declared but remain non-executable until scoped by a later trigger-backed task.

## Rollback
Use git to revert the changed files above. If containment profile validation blocks a future experimental tool, either add an explicit profile and waiver or keep the tool denied until its runtime boundary is designed.
