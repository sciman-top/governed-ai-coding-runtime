# 20260607 Host-Family PRD Definition Refresh

## Goal
- Current landing point: authoritative product-definition documents still mixed historical completion language with newer host-family and capability-surface interpretation.
- Target home: refresh the current product-definition layer so PRD, README entrypoints, and strategy/interaction docs all describe the same best-end-state blueprint and current host posture.

## Why This Change Was Needed
- `docs/architecture/planning-status.json` already separates `certified baseline` from `current live posture`, but some current entrypoint docs still implied stronger live-host parity than the current posture allows.
- The repository already had a new host-family blueprint, but the PRD and top-level entrypoints had not fully promoted it into the formal product definition.
- The external reference set now makes the Google direction and migration bridge clearer: `Antigravity family` is the long-term Google direction, while `Gemini CLI` remains an active but lower-priority compatibility bridge.

## Official And First-Party Grounding
- OpenAI Codex glossary: `https://developers.openai.com/codex/glossary`
  - confirms Codex App, CLI, IDE extension, Cloud, app-server, automations, worktrees, connectors, approvals, MCP, and related control surfaces as official product vocabulary
- OpenAI MCP and Connectors guide: `https://developers.openai.com/api/docs/guides/tools-connectors-mcp`
  - confirms approval-required defaults, trusted-server posture, allowed-tool narrowing, and deferred loading as current official MCP integration guidance
- Anthropic Claude Code official repo README: `https://github.com/anthropics/claude-code`
  - current local clone states Claude Code is used in terminal, IDE, or GitHub
- Google Antigravity CLI official repo README: `https://github.com/google-antigravity/antigravity-cli`
  - current local clone states Antigravity CLI and Antigravity 2.0 share a core agent engine, shared settings, and session export/continuation behavior
- Google Gemini CLI official repo: `https://github.com/google-gemini/gemini-cli`
  - current local clone remains active and recent commit history includes an `Antigravity transition banner`, so the strongest accurate wording is migration-bridge, not unconditional removal

## Files Updated
- `docs/prd/governed-ai-coding-runtime-prd.md`
- `docs/product/interaction-model.md`
- `docs/strategy/positioning-and-competitive-layering.md`
- `docs/README.md`
- `docs/plans/README.md`
- `README.md`
- `README.en.md`
- `README.zh-CN.md`

## Change Summary
- Promoted the current best-end-state blueprint into the PRD as a formal product-definition section.
- Added explicit host-family posture to the PRD: `Codex family`, `Claude family`, `Antigravity family`, and `Gemini CLI` as a legacy bridge.
- Tightened adapter requirements so capability declaration is part of the formal product boundary.
- Corrected entrypoint wording that could be read as persistent `native_attach` parity even though the current live posture still shows Codex target runs as `process_bridge / degraded`.
- Added direct links from current entrypoint docs to the host-family capability blueprint and the reference-repo overview/tiering docs.

## Verification
- Docs gate:
  - command: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
  - result: pass
  - key output: `OK planning-status`, `OK core-principles`, `OK current-source-compatibility`, `OK claim-drift-sentinel`, `OK post-closeout-queue-sync`
- Full runtime hard gates: `gate_na`
  - reason: this slice only changes authoritative product-definition and navigation documents
  - alternative verification: docs gate plus focused source review of official docs and first-party reference repos
  - evidence_link: this file
  - expires_at: `2026-06-07`

## Risks
- The main risk is wording drift between current live posture and historical certification language.
- The mitigation is to keep `planning-status.json` as the single source of current posture and reduce stronger claims in other entrypoint docs.

## Rollback
- Revert this evidence file and the listed documentation files with git if a later review rejects the refreshed host-family definition or entrypoint wording.
