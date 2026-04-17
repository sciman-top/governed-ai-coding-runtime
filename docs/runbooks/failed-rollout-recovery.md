# Failed Rollout Recovery

## Trigger
A rollout fails when a required gate fails, a control cannot be promoted, or verification output conflicts with expected state.

## Recovery Steps
1. Stop promotion and keep the control in its current state.
2. Capture the failing command, exit code, and key output in `docs/change-evidence/`.
3. Run the smallest relevant verifier first, then rerun the full verifier:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

4. If the full verifier still fails, keep the rollout blocked and open a recovery task.

## Rollback
Use git history for tracked changes. Use `docs/change-evidence/snapshots/` only when git history is unavailable or extra audit material is required.
