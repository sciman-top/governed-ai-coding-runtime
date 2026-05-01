# 2026-05-01 GAP-132 Control Pack Execution Contract

## Goal
Close `GAP-132` by upgrading the repository control-pack contract from metadata-only references to an executable and verifiable control-pack shape with explicit kernel-versus-target ownership boundaries and a controlled materialization path into runtime-consumable pack assets.

## Risk
- risk_tier: medium
- primary_risk: a control pack could claim reusable governance coverage without any runnable or verifiable runtime references
- compatibility_boundary: this change upgrades the `control-pack` contract, its example, and the runtime-consumable pack asset, but does not auto-apply policy, sync target repos, push, or merge

## Changes
- updated [Control Pack Spec](/D:/CODE/governed-ai-coding-runtime/docs/specs/control-pack-spec.md) to require `field_ownership`, `execution_contract`, and `materialization`
- updated [Control Pack Schema](/D:/CODE/governed-ai-coding-runtime/schemas/jsonschema/control-pack.schema.json) with fail-closed executable-ref validation
- updated [Control Pack Example](/D:/CODE/governed-ai-coding-runtime/schemas/examples/control-pack/minimum-governance-kernel.example.json) to carry runnable and verifiable refs across `policy`, `gate`, `hook`, `eval`, `workflow`, `skill`, `knowledge`, `memory`, `evidence`, and `rollback`
- updated [Runtime-Consumable Control Pack](/D:/CODE/governed-ai-coding-runtime/schemas/control-packs/minimum-governance-kernel.control-pack.json) to match the new source template
- added [Control Pack Execution Verifier](/D:/CODE/governed-ai-coding-runtime/scripts/verify-control-pack-execution.py)
- added [Control Pack Materializer](/D:/CODE/governed-ai-coding-runtime/scripts/materialize-control-pack.py)
- added [Control Pack Execution Tests](/D:/CODE/governed-ai-coding-runtime/tests/runtime/test_control_pack_execution.py)
- wired [scripts/verify-repo.ps1](/D:/CODE/governed-ai-coding-runtime/scripts/verify-repo.ps1) `-Check Contract` to fail closed on invalid or metadata-only runtime control packs

## Pre-Change Review
pre_change_review: required because this change updates `scripts/verify-repo.ps1`, which is part of the self-repo hard gate.

control_repo_manifest_and_rule_sources: checked against `docs/specs/control-pack-spec.md`, `schemas/jsonschema/control-pack.schema.json`, `schemas/examples/control-pack/minimum-governance-kernel.example.json`, and `schemas/control-packs/minimum-governance-kernel.control-pack.json` before editing.

user_level_deployed_rule_files: not changed by this implementation; `GAP-132` stays inside repository control-pack contracts and local verification.

target_repo_deployed_rule_files: not changed by this implementation; target-repo sync remains disabled.

target_repo_gate_scripts_and_ci: not changed by this implementation; the new verifier is attached only to this control repo's `Contract` gate.

target_repo_repo_profile: not changed by this implementation; the new ownership fields only distinguish kernel-owned and target-supplied pack fields.

target_repo_readme_and_operator_docs: checked by updating repository status docs so `GAP-132` is not left as a planned item after the contract and verifier are live.

current_official_tool_loading_docs: not changed by this implementation; the materializer and verifier run locally and do not alter host loading behavior.

drift-integration decision: integrate by making the source template, generated pack asset, verifier, and materializer mutually checked, so metadata-only control packs fail closed before later inheritance and target-repo reuse work begins.

## Verification
```powershell
python scripts/verify-control-pack-execution.py
```

Result: pass. Key output: `status=pass`, `pack_count=1`, `runnable_refs=5`, `verifiable_refs=5`, `errors=[]`.

```powershell
python -m unittest discover -s tests/runtime -p "test_control_pack_execution.py"
```

Result: pass. Key output: `Ran 4 tests`, `OK`.

```powershell
python scripts/materialize-control-pack.py
```

Result: pass. Key output: `mode=dry_run`, `operation_count=1`, `mutation_allowed=false`, `written_files=[]`.

```powershell
Get-Content -Raw 'schemas/examples/control-pack/minimum-governance-kernel.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/control-pack.schema.json'
```

Result: pass. Key output: `True`.

```powershell
Get-Content -Raw 'schemas/control-packs/minimum-governance-kernel.control-pack.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/control-pack.schema.json'
```

Result: pass. Key output: `True`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/github/create-roadmap-issues.ps1 -ValidateOnly -RenderAll
```

Result: pass. Key output: `issue_seed_version=5.1`, `rendered_tasks=117`, `completed_task_count=107`, `active_task_count=10`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
```

Result: pass. Key output includes `OK capability-portfolio`, `OK current-source-compatibility`, `OK claim-drift-sentinel`, and `OK post-closeout-queue-sync`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

Result: pass. Key output includes `OK schema-example-validation`, `OK control-pack-execution`, `OK dependency-baseline`, `OK agent-rule-sync`, `OK pre-change-review`, and `OK functional-effectiveness`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1
```

Result: pass. Key output: `OK python-bytecode`, `OK python-import`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime
```

Result: pass. Key output: `Running 86 test files with 4 workers`, `Completed 86 test files in 128.596s; failures=0`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1
```

Result: pass with existing host warning. Key output includes `OK runtime-status-surface`, `OK adapter-posture-visible`, and `WARN codex-capability-degraded`.

## Rollback
- revert the updated `control-pack` spec, schema, example, and runtime pack asset
- remove `scripts/verify-control-pack-execution.py`, `scripts/materialize-control-pack.py`, and `tests/runtime/test_control_pack_execution.py`
- remove the `control-pack-execution` hook from `scripts/verify-repo.ps1` if later planning intentionally returns control packs to metadata-only status
