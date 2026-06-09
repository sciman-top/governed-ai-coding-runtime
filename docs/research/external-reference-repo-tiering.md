# External Reference Repo Tiering

## Purpose
- Give the local `D:\CODE\external` reference set a stable priority model instead of one flat list.
- Answer two recurring maintenance questions:
  - which repos are `must-read` for current architecture and host-direction work?
  - which repos should be kept only as legacy bridge, supplemental guide, or low-priority observation material?

## Scope Boundary
- The canonical general-purpose AI coding runtime reference set is `D:\CODE\external\ai-coding-runtime-references`.
- Other sibling directories under `D:\CODE\external` such as `Cockpit-Tools-Local-references`, `k12-question-graph-references`, and `ai-content-delivery-studio-references` are project-specific side collections, not the main runtime reference baseline.
- This document ranks reference value; it does not make any external repo a source of truth over local contracts, tests, gates, evidence, or repo rules.

## Tier Model
- `Tier 1 / Must Read`
  - direct official or protocol source for current host-family strategy, adapter boundaries, or controlled runtime evolution
- `Tier 2 / Keep`
  - still useful and worth staying local, but not required reading for every architecture or planning pass
- `Tier 3 / Legacy Bridge`
  - keep locally because the repository still has real compatibility debt or migration needs, but do not treat as long-term direction
- `Tier 4 / Observe`
  - useful for periodic comparison, onboarding, or idea mining; lowest priority if disk, maintenance, or review attention must be reduced

## Tier 1 / Must Read
| Repo | Why it stays in Tier 1 |
| --- | --- |
| `openai-codex` | Core host-family source for Codex AGENTS/config/sandbox/approval semantics. |
| `openai-agents-python` | Official Python agent-runtime source for handoffs, guardrails, sessions, tracing, and sandbox-agent structure. |
| `openai-agents-js` | Official JS/TS agent-runtime source for multi-agent workflows, tools, and realtime/voice surfaces. |
| `anthropic-claude-code` | Official main host repo for Claude terminal/IDE/GitHub surfaces and plugin/runtime boundary. |
| `google-antigravity-cli` | Current Google host-family primary direction. |
| `mcp-specification` | Protocol boundary source for MCP semantics and security vocabulary. |
| `mcp-typescript-sdk` | TS MCP implementation boundary reference. |
| `mcp-python-sdk` | Python MCP implementation boundary reference. |
| `github-mcp-server` | First-party real MCP server boundary against an external production platform. |
| `a2aproject-A2A` | Official A2A protocol boundary for agent-to-agent interoperability. |
| `github-copilot-cli` | First-party competing host-family CLI surface for cross-host comparison. |
| `microsoft-playwright-cli` | First-party token-efficient browser automation CLI/skills reference for coding-agent workflows. |
| `microsoft-playwright-mcp` | First-party browser MCP reference for rich introspection and persistent browser context loops. |

## Tier 2 / Keep
| Repo | Why it stays local |
| --- | --- |
| `mcp-servers` | Official example server bundle; useful but secondary to spec + SDKs. |
| `mcp-inspector` | Official MCP testing/inspection tool; very useful for server/tool-surface debugging, but still secondary to spec + SDKs for protocol truth. |
| `anthropic-claude-code-action` | First-party CI/action surface; important, but narrower than the main `claude-code` host repo. |
| `anthropic-claude-plugins-official` | Official plugin directory with real packaging/MCP/skills combinations; useful for governed plugin-distribution boundaries, but narrower than the main host repo. |
| `openhands` | Strong execution-host and sandbox vocabulary reference. |
| `aider` | Best-in-class repo map and edit-loop ergonomics reference. |
| `swe-agent` | Useful repair-loop and benchmark-aware closure reference. |
| `continue` | Good source-controlled checks and IDE/CLI cooperation reference. |
| `opencode` | Useful terminal UX/provider/session abstraction reference. |
| `goose` | Useful extension and desktop/CLI packaging reference. |
| `hermes-agent` | Valuable skills/memory/self-improvement reference, but not a main host. |
| `langgraph` | Useful durable state and interrupt/resume orchestration reference. |
| `semantic-kernel` | Useful enterprise SDK and plugin/planner structure reference. |

## Tier 3 / Legacy Bridge
| Repo | Why it should not be deleted yet |
| --- | --- |
| `google-gemini-cli` | The repository still has real `GEMINI.md` compatibility and Google-host migration semantics to maintain, so this stays as a migration/enterprise bridge reference. |

## Tier 4 / Observe
| Repo | Why it is lower priority |
| --- | --- |
| `anthropic-claude-code-monitoring-guide` | Helpful official ROI/telemetry guide, but it is an operational measurement supplement, not a host/runtime semantics source. |
| `microsoft-ai-agents-for-beginners` | Useful teaching-grade examples, but lowest direct value for this repo's current host/runtime architecture decisions. |

## Deletion Recommendation
- Immediate deletion: `none`
- Reason:
  - all current clones are shallow, read-only, and relatively low-cost to keep
  - current repository still benefits from broad host-family comparison while the architecture is actively evolving
  - the better near-term move is `downgrade by tier`, not destructive cleanup

## First Archive Candidates If You Want To Slim Down Later
1. `microsoft-ai-agents-for-beginners`
2. `anthropic-claude-code-monitoring-guide`
3. one of `goose` / `opencode` if browser/desktop packaging comparisons stop producing new insights

## Practical Rule
- Before adding another external repo, require at least one of:
  - first-party host or protocol source
  - mechanism gap not already covered by an existing local reference
  - repeated design question that current Tier 1 and Tier 2 repos cannot answer
- Before deleting an external repo, confirm it is not the only local reference for:
  - a current host family
  - a current migration bridge
  - a protocol boundary
  - a repeated mechanism question with live design impact
