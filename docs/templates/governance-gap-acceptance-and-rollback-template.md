# Governance GAP Acceptance And Rollback Template

Use this template for governance-lane GAP closeout notes, implementation evidence, or review packets when a change affects plans, specs, policies, or rollout behavior.

## Goal
- What this GAP or change is intended to accomplish.

## Scope
- What is in scope.
- What is intentionally out of scope.

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Verification Commands
```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts
```

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract
```

Add or remove commands so they match the actual change.

## Evidence Links
- `docs/change-evidence/<date>-<slug>.md`
- Additional evidence refs, if any

## Compatibility Impact
- `compatible`
- `compatible_with_note`
- `migration_required`
- `blocked`

Explain which one applies and why.

## Rollback Trigger
- What observable condition means this change should be rolled back.

## Rollback Reference
- Git revert, document restore, schema rollback note, or explicit `rollback_not_applicable`.

## Waiver Needed?
- `no`
- `yes`, with:
  - waiver id
  - owner
  - approver
  - expires at
  - recovery plan

## Residual Risks
- Risk 1
- Risk 2

## Notes
- Any reviewer or operator notes that should remain with the change.
