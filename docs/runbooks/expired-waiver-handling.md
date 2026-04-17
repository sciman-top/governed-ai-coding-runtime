# Expired Waiver Handling

## Trigger
A waiver is expired when its `expires_at` date has passed or its owner cannot provide current evidence.

## Recovery Steps
1. Mark the waiver as expired in the relevant evidence or waiver record.
2. Re-run the blocked gate or document why it remains `gate_na`.
3. If the waived condition still exists, create a new waiver with owner, expiration, recovery plan, and evidence link.

## Evidence
Record the decision, command output, and recovery path in `docs/change-evidence/`.
