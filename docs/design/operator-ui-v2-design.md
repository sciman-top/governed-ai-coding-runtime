# Operator UI V2 Workbench Design

## Goal
- Preserve the existing operator functions, target selection, dry-run, history, and bounded evidence preview.
- Make the first screen feel like an operations workbench rather than a static report.
- Keep controls compact and predictable while giving command output enough width for real logs.

## Layout
- Header: product title plus runtime root and persistence metadata.
- Left rail: action buttons and execution settings only.
- Main work area:
  - summary metrics at the top,
  - command output and execution history as the primary work surface,
  - maintenance policy and attachment state below,
  - task table at the bottom.

## Visual Rules
- Maximum workbench width: `1560px`, centered on wide screens.
- Control rail width: `260px-300px`.
- Command output must not live in the narrow rail; it needs a wide terminal-style panel.
- Cards use restrained borders, 6px radius, and a quiet teal accent for active health/readiness state.
- Mutating actions use red text/border and still require confirmation.
- Mobile layout collapses to one column with no horizontal overflow.

## Current Design Image
- High-fidelity screenshot: `docs/change-evidence/operator-ui-v2-workbench.png`
