# 20260504 Host Readiness Fixes

## Scope
- Current landing: host-level Gemini readiness warnings found after the v9.51 rule sync.
- Target home: user-level Gemini/Codex/Claude host configuration remains compatible with the managed rule family; repo rules are unchanged.
- Verification: fresh Gemini `skills list`, `mcp list --debug`, and rule-load prompt checks.

## Changes
- Rebuilt `C:\Users\sciman\.gemini\skills` from a broad Junction to `D:\CODE\skills-manager\agent` into a real directory containing only the 8 Gemini-unique skills.
- Backed up the original Junction at `C:\Users\sciman\.gemini\skills.junction-backup-20260504-042203`.
- Moved the user-level `.agents` copy of `anthropics-skills-skills-skill-creator` to `C:\Users\sciman\.agents\skills.disabled-backup-20260504-042342` so Gemini no longer reports a built-in skill override.
- Added `.pytest_cache/` and `**/.pytest_cache/` to `C:\Users\sciman\.gemini\.geminiignore`.
- Disabled stale duplicate `C:\Users\sciman\.gemini\.mcp.json` by moving it to `C:\Users\sciman\.gemini\.mcp.json.disabled-backup-20260504-042621`; `settings.json` remains the active MCP source.
- Added `mcp.excluded = ["github"]` in `C:\Users\sciman\.gemini\settings.json` because no `GITHUB_PERSONAL_ACCESS_TOKEN`, `GITHUB_TOKEN`, or `GH_TOKEN` is present and `github` MCP was the only disconnected server.

## Verification
- `gemini skills list`: no skill conflict warnings and no built-in skill override warnings remain.
- `gemini mcp list --debug`: `context7`, `microsoft-learn`, `openaiDeveloperDocs`, and `playwright` are connected; `github` is explicitly blocked instead of disconnected.
- `gemini --approval-mode plan --output-format json --prompt ...`: returned `loaded-rule-version: 9.51` and fixed order `build -> test -> contract/invariant -> hotspot`.

## Remaining Platform N/A
- `D:\CODE\governed-ai-coding-runtime\.pytest_cache` is an unreadable generated cache directory. `Get-Acl`, `icacls`, `Remove-Item`, and `attrib` all fail with access denied; `takeown` reports the current user lacks administrative privileges.
- Gemini still logs `Skipping unreadable directory ... .pytest_cache` during memory discovery before ignore filtering prevents the scandir.
- Recovery condition: remove or repair ACL for this generated directory from an elevated shell, then rerun `gemini skills list`.

## Rollback
- Restore Gemini broad skill Junction: remove the new `C:\Users\sciman\.gemini\skills` directory and rename `skills.junction-backup-20260504-042203` back to `skills`.
- Restore user skill override: move `C:\Users\sciman\.agents\skills.disabled-backup-20260504-042342\anthropics-skills-skills-skill-creator` back under `C:\Users\sciman\.agents\skills`.
- Restore `.mcp.json`: move `C:\Users\sciman\.gemini\.mcp.json.disabled-backup-20260504-042621` back to `C:\Users\sciman\.gemini\.mcp.json`.
- Re-enable Gemini GitHub MCP after providing a valid token by removing `github` from `mcp.excluded`.
