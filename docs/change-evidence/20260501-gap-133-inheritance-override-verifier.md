# 2026-05-01 GAP-133 Inheritance Override And Forbidden Override Verifier

## Goal
Close `GAP-133` by mechanizing which governance surfaces remain unified, which repo-profile fields are baseline-inherited, which repo-local override points stay bounded and typed, and which override surfaces are forbidden from appearing in repo profiles or emitted light packs.

## Risk
- risk_tier: medium
- primary_risk: target repos could silently weaken gate order, evidence, rollback, or approval semantics through untyped or undocumented override paths
- compatibility_boundary: this change adds an inheritance matrix, a verifier, and repo-profile schema typing, but does not auto-sync target repos, mutate host policy, push, or merge

## Changes
- added [Control Pack Inheritance Matrix Spec](/D:/CODE/governed-ai-coding-runtime/docs/specs/control-pack-inheritance-matrix-spec.md)
- added [Control Pack Inheritance Matrix Schema](/D:/CODE/governed-ai-coding-runtime/schemas/jsonschema/control-pack-inheritance-matrix.schema.json)
- added [Control Pack Inheritance Matrix Example](/D:/CODE/governed-ai-coding-runtime/schemas/examples/control-pack-inheritance-matrix/minimum-governance-kernel.example.json)
- added [Control Pack Inheritance Matrix Runtime Asset](/D:/CODE/governed-ai-coding-runtime/docs/architecture/control-pack-inheritance-matrix.json)
- added [Control Pack Inheritance Verifier](/D:/CODE/governed-ai-coding-runtime/scripts/verify-control-pack-inheritance.py)
- added [Control Pack Inheritance Tests](/D:/CODE/governed-ai-coding-runtime/tests/runtime/test_control_pack_inheritance.py)
- updated [Repo Profile Spec](/D:/CODE/governed-ai-coding-runtime/docs/specs/repo-profile-spec.md) and [Repo Profile Schema](/D:/CODE/governed-ai-coding-runtime/schemas/jsonschema/repo-profile.schema.json) so inherited interaction, rule-file, and Windows-process policies are explicit and typed
- wired [scripts/verify-repo.ps1](/D:/CODE/governed-ai-coding-runtime/scripts/verify-repo.ps1) `-Check Contract` to fail closed when inheritance, override, or forbidden-override drift is detected

## Pre-Change Review
pre_change_review: required because this change updates `scripts/verify-repo.ps1` and repo-profile governance contracts.

control_repo_manifest_and_rule_sources: checked against `docs/specs/repo-profile-spec.md`, `schemas/jsonschema/repo-profile.schema.json`, `docs/specs/control-pack-inheritance-matrix-spec.md`, and `schemas/catalog/schema-catalog.yaml` before editing.

user_level_deployed_rule_files: not changed by this implementation; `GAP-133` stays in repository contracts and local verification.

target_repo_deployed_rule_files: not changed by this implementation; target-repo sync remains disabled.

target_repo_gate_scripts_and_ci: checked indirectly by attaching the new verifier only to this control repo's `Contract` gate.

target_repo_repo_profile: checked against `.governed-ai/repo-profile.json` so inherited fields are typed and emitted without leaking forbidden overrides.

target_repo_readme_and_operator_docs: checked by updating repository status docs so `GAP-133` is not left as planned after the verifier is live.

current_official_tool_loading_docs: not changed by this implementation; the new matrix and verifier operate on repository-owned contracts only.

drift-integration decision: integrate by making the inheritance matrix, repo-profile schema, baseline overrides, control pack, and emitted light pack mutually checked so forbidden override drift fails closed before target-repo effect-harness work begins.

## Verification
```powershell
python scripts/verify-control-pack-inheritance.py
```

Result: pass. Key output: `status=pass`, `inherited_field_count=6`, `override_field_count=7`, `forbidden_override_count=5`, `errors=[]`.

```powershell
python -m unittest discover -s tests/runtime -p "test_control_pack_inheritance.py"
```

Result: pass. Key output: `Ran 4 tests`, `OK`.

```powershell
Get-Content -Raw 'schemas/examples/control-pack-inheritance-matrix/minimum-governance-kernel.example.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/control-pack-inheritance-matrix.schema.json'
```

Result: pass. Key output: `True`.

```powershell
Get-Content -Raw '.governed-ai/repo-profile.json' |
  Test-Json -SchemaFile 'schemas/jsonschema/repo-profile.schema.json'
```

Result: pass. Key output: `True`.

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

Result: pass. Key output includes `OK control-pack-inheritance`, `OK control-pack-execution`, `OK target-repo-rollout-contract`, `OK target-repo-governance-consistency`, `OK pre-change-review`, and `OK functional-effectiveness`.

## Rollback
- revert the inheritance matrix spec, schema, example, and runtime asset
- remove `scripts/verify-control-pack-inheritance.py` and `tests/runtime/test_control_pack_inheritance.py`
- remove the `control-pack-inheritance` hook from `scripts/verify-repo.ps1`
- revert repo-profile schema typing additions if the inheritance matrix is intentionally removed or redesigned
