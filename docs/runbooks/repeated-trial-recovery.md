# Repeated Trial Recovery

## Trigger
A repeated trial requires recovery when a governed trial fails twice, produces contradictory evidence, or cannot be replayed from recorded commands.

## Recovery Paths
1. Rerun the last successful command from the evidence file.
2. If replay fails, rerun the canonical verifier:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All
```

3. Compare new output with the prior evidence.
4. If the failure repeats, stop automatic execution and create a recovery task with the failing command, expected behavior, actual behavior, and evidence link.

## Evidence
Store recovery notes in `docs/change-evidence/` and include replay commands in the delivery handoff.
