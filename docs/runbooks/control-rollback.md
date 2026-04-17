# Control Rollback

## Trigger
A control rollback is required when an `observe -> enforce` promotion creates unacceptable failures or blocks valid work.

## Rollback Behavior
1. Move the control back from `enforce` to `observe`.
2. Preserve the failed enforcement evidence in `docs/change-evidence/`.
3. Re-run the relevant verifier and record the result.
4. Create a follow-up task for the control defect before attempting promotion again.

## Verification
Use the full verifier after rollback:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```
