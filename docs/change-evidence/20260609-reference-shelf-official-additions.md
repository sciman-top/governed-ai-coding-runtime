# 20260609 Reference Shelf Official Additions

## Goal
- Current landing point: the local AI coding runtime reference shelf already covered the main host families, MCP specs/SDKs, A2A, browser automation, and several mature community agents.
- Target home: add the two highest-value missing official references without broadening the shelf indiscriminately, and keep the local shelf plus the control-repo research docs in sync.

## Why These Additions
- `modelcontextprotocol/inspector`
  - fills the official MCP inspection/debugging gap for server and tool-surface validation
  - complements `mcp-specification`, `mcp-typescript-sdk`, `mcp-python-sdk`, and `github-mcp-server` without pretending to be the protocol source of truth
- `anthropics/claude-plugins-official`
  - fills the official Claude plugin-distribution and packaging reference gap
  - complements `anthropic-claude-code` and `anthropic-claude-code-action` without replacing the main Claude host/runtime semantics source

## Scope
- Updated local shelf files under `D:\CODE\external\ai-coding-runtime-references`:
  - `references.manifest.json`
  - `README.md`
  - `clone-results.json`
- Updated control-repo research docs:
  - `docs/research/external-reference-repo-tiering.md`
  - `docs/research/external-reference-repo-one-page-overview.md`
  - `docs/research/external-reference-repos-index.md`
  - `docs/change-evidence/README.md`
- Added local shelf entries:
  - `repos/mcp-inspector`
  - `repos/anthropic-claude-plugins-official`

## Source Confirmation
- GitHub repo search confirmed:
  - `modelcontextprotocol/inspector` as the official MCP inspector repo
  - `anthropics/claude-plugins-official` as the official Anthropic-managed Claude plugin directory
- The local shelf update then refreshed official/protocol repos through the existing script rather than hand-cloning one-off repositories.

## Changes
- Added `mcp-inspector` and `anthropic-claude-plugins-official` to the local shelf manifest as `Tier 2 / 保留` official references.
- Updated the local shelf README reading order and official-reference tables so both new repos appear in the human-facing reference guide.
- Updated `clone-results.json` so the local inventory no longer omits the two new repos.
- Updated the control-repo research docs so the project-internal reference index, tiering, and one-page overview match the actual shelf contents.
- Kept deletion posture unchanged: no immediate removals; `google-gemini-cli` stays as a `Legacy Bridge`.

## Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File D:\CODE\external\ai-coding-runtime-references\update-reference-repos.ps1 -OfficialOnly -WriteJson -WriteMarkdown -WriteManifest`
  - result: pass
  - key output: `repo_count: 19`, `changed_count: 2`, `failed_count: 0`
- `git -C D:\CODE\external\ai-coding-runtime-references\repos\mcp-inspector rev-parse --short HEAD`
  - result: pass
  - key output: `a523a0f`
- `git -C D:\CODE\external\ai-coding-runtime-references\repos\anthropic-claude-plugins-official rev-parse --short HEAD`
  - result: pass
  - key output: `379a00d`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Scripts`

## Risks
- `anthropic-claude-plugins-official` is newer and may evolve quickly, so it should remain a packaging/distribution reference rather than being over-promoted into host-semantics truth.
- `mcp-inspector` improves MCP validation coverage, but it still must not outrank the MCP spec or SDKs in protocol-boundary disputes.

## Rollback
- Remove the two new local-shelf entries from `references.manifest.json`, `README.md`, and `clone-results.json`.
- Remove the matching entries from the control-repo research docs.
- Re-run the official-only shelf refresh if you need the human-readable reports to match the rolled-back manifest.
