# Agent Rule Governance v2 Source Basis

- checked on: `2026-07-17`
- product question: what should remain when this repository only configures,
  audits, and improves OpenAI Codex and Anthropic Claude Code agent rules for
  explicitly registered target repositories?
- source priority: current official product documentation and first-party
  source > repository-local runtime evidence > fixed community source commits
- evidence labels: `official fact` means a behavior owned by OpenAI or
  Anthropic; `community inspiration` means a reusable structure, not a host
  contract
- non-goals: no provider, auth, credential, session, process, gateway, model
  invocation, or hosted-runtime operation

## Conclusion

The smallest defensible end state is a static agent-rule governance control
repository, not a parallel AI coding runtime.

Target repositories remain the source of truth for their project facts, real
commands, invariants, evidence paths, and rollback instructions. The control
repository owns only shared global rule sources, the cross-host contract,
explicit target registration, deterministic validation and projection logic,
native-host verification adapters, and aggregate evidence.

The preferred target-repository shape is:

```text
AGENTS.md       # host-neutral project contract and common body
CLAUDE.md       # @AGENTS.md plus only evidence-backed Claude-specific delta
```

This is intentionally asymmetric. Codex reads `AGENTS.md` natively. Claude
Code reads `CLAUDE.md`, and Anthropic explicitly documents importing an
existing `AGENTS.md` from a thin `CLAUDE.md`. A nested `AGENTS.md` therefore
also needs a corresponding Claude wrapper or an explicit host-aware
projection; a root wrapper does not make Claude Code discover unrelated
nested `AGENTS.md` files automatically.

## Official Facts: OpenAI Codex

| Official fact | Source | Architectural meaning |
|---|---|---|
| Codex builds an instruction chain once per run. At global scope it uses the first non-empty `AGENTS.override.md` or `AGENTS.md`. At project scope it walks from the project root to the current working directory, taking at most one instruction file per directory in the order `AGENTS.override.md`, `AGENTS.md`, then configured fallback names. Files are concatenated root-to-current-directory. | [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | The Codex adapter must model the actual root-to-cwd chain, not just check a root file. Override and fallback names are host semantics, not generic Markdown semantics. |
| Codex skips empty instruction files and stops when the combined guidance reaches `project_doc_max_bytes`, 32 KiB by default. Fallback names are effective only when listed in `project_doc_fallback_filenames`. | [AGENTS.md discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [project instructions discovery](https://learn.chatgpt.com/docs/config-file/config-advanced#project-instructions-discovery) | Static validation needs a byte-budget calculation, empty-file handling, and the effective fallback list from current configuration. Splitting text without checking the native budget is not a valid optimization. |
| Project `.codex/config.toml`, project hooks, and project rules load only for trusted projects. Codex walks project config layers from the project root toward the working directory, with the closest value winning for ordinary scalar configuration. | [Advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced), [configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference#configtoml) | The control repository may audit repo-local Codex settings, but file presence alone does not prove that the client accepted or loaded them. Fresh verification must include trust and resolved-source evidence. |
| Project-local Codex config cannot override host-owned provider, auth, profile, notification, or telemetry keys. The official reference explicitly ignores keys including `model_provider`, `model_providers`, `openai_base_url`, profile selection, and `otel` when they occur in project config. | [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference#configtoml) | Provider and account routing do not belong in target-repository rule governance. The verifier should reject or report such keys rather than attempting to manage them. |
| Codex lifecycle hooks load from active config layers. Matching hooks from multiple sources all run; project hooks require project trust; non-managed command hooks require review of their current hash. | [Hooks](https://learn.chatgpt.com/docs/hooks) | Hooks are a deterministic enforcement or observability surface, separate from prose instructions. The control repository can validate hook references and trust requirements, but should not introduce a central hook daemon. |
| Enterprise requirements and managed defaults are separate from user/project guidance. Managed requirements can constrain permissions, sandboxing, hooks, command rules, MCP servers, and supported runtime behavior. | [Managed configuration](https://learn.chatgpt.com/docs/enterprise/managed-configuration) | `requirements.toml`, MDM, and other administrator policy are an enterprise deployment plane. Ordinary target-rule updates may produce reviewable advice, but must not deploy or mutate managed policy without explicit administrative scope. |
| Local Codex runs and Codex cloud runs execute in different environments with different controls. ChatGPT Work permissions, local Codex sandbox/approval settings, and cloud execution policy are not interchangeable. | [ChatGPT Work Admin FAQ](https://learn.chatgpt.com/docs/enterprise/work-admin-faq#how-are-runtime-and-network-boundaries-governed) | A local hash, local prompt-input probe, or local gate cannot prove that a hosted surface loaded or accepted the same rule. `host_loaded` and `hosted_accepted` must remain separate states. |

OpenAI documentation was obtained through the current Codex manual helper and
the official OpenAI documentation service. The manual reported its local cache
as current on the checked date. The public pages remain live documentation, so
version-sensitive fields still require a fresh release-time check.

## Official Facts: Anthropic Claude Code

| Official fact | Source | Architectural meaning |
|---|---|---|
| Claude Code reads `CLAUDE.md`, not `AGENTS.md`. Anthropic recommends a `CLAUDE.md` containing `@AGENTS.md` when a repository already uses `AGENTS.md`; on Windows, the import is preferred over a symlink. | [How Claude remembers your project](https://code.claude.com/docs/en/memory#agentsmd) | A one-line import wrapper is the native Claude adapter for the shared project body. Duplicating the full body in both files creates avoidable drift. |
| Claude Code walks upward from the working directory for `CLAUDE.md` and `CLAUDE.local.md`. All discovered files are concatenated into context rather than overriding each other. Subdirectory instruction files load lazily when Claude reads files in those directories. | [How CLAUDE.md files load](https://code.claude.com/docs/en/memory#how-claudemd-files-load) | Claude validation must detect contradictory global/project/nested instructions; it must not assume that a closer project file deterministically replaces broader content. Lazy-load acceptance needs a file read in the relevant subtree. |
| `CLAUDE.md` and auto memory are context, not enforced configuration. Anthropic directs users to `PreToolUse` hooks when an action must be blocked regardless of model behavior. | [CLAUDE.md vs auto memory](https://code.claude.com/docs/en/memory#claudemd-vs-auto-memory), [extension comparison](https://code.claude.com/docs/en/features-overview) | Security and release guarantees need permissions, hooks, scripts, or CI. A sentence in a prompt cannot be certified as deterministic enforcement. |
| Anthropic recommends keeping each `CLAUDE.md` under roughly 200 lines. Imported files still enter the context window, so imports organize content but do not make it free. Path-scoped rules and skills serve different loading needs. | [Write effective instructions](https://code.claude.com/docs/en/memory#write-effective-instructions), [Extend Claude Code](https://code.claude.com/docs/en/features-overview) | The control repository should measure always-on context and move only genuinely path-specific or on-demand material to the native surface. It should not use imports to hide an oversized rule body. |
| Claude settings use Managed, CLI, Local, Project, then User precedence for ordinary values. Shared project settings live in `.claude/settings.json`; personal project settings live in `.claude/settings.local.json`. Permission rules merge differently, and a deny from any scope cannot be cancelled by an allow from another scope. Project allow rules are subject to workspace trust. | [Claude Code settings](https://code.claude.com/docs/en/settings), [Configure permissions](https://code.claude.com/docs/en/permissions) | The Claude adapter must implement native scope, merge, deny, and trust semantics. A central last-writer-wins abstraction would be incorrect. |
| Claude extensions have distinct roles: `CLAUDE.md` is always-on context, `.claude/rules/` can be path-scoped, skills are on-demand knowledge/workflows, subagents isolate execution context, hooks automate lifecycle events, and plugins package extensions for distribution. | [Extend Claude Code](https://code.claude.com/docs/en/features-overview) | A product limited to two host rule families should not pre-emptively become a skills, MCP, subagent, plugin, or multi-agent platform. Add those surfaces only when a concrete target requirement cannot be represented by durable project guidance. |
| Command hooks execute with the current operating-system user's permissions. Anthropic requires input validation, quoting, traversal protection, and careful review; Windows command hooks can use `shell: "powershell"`. | [Hooks reference](https://code.claude.com/docs/en/hooks#security-considerations), [Windows PowerShell hooks](https://code.claude.com/docs/en/hooks#windows-powershell-tool) | Enforcement scripts should remain small, reviewed, and target-owned. The control repository should lint them and their configuration, not run a privileged background service. |
| Managed settings are delivered by the Claude admin service, MDM/registry, or system files and can lock permissions, sandboxing, MCP, plugin sources, hooks, login, and other organization policy. | [Set up Claude Code for your organization](https://code.claude.com/docs/en/admin-setup), [Claude Code settings](https://code.claude.com/docs/en/settings#settings-precedence) | Enterprise policy delivery is outside normal repository rule synchronization. The control repository must not write registry, system policy, or remote admin state as a side effect of a project-rule release. |
| Custom subagents have independent context, tools, and permissions and use their own managed/CLI/project/user/plugin precedence. | [Create custom subagents](https://code.claude.com/docs/en/sub-agents) | Subagents are a separate execution extension. They are not required to configure `AGENTS.md` and `CLAUDE.md`, so they remain out of the minimal product. |

Mutable details such as supported settings keys, native platform constraints,
and recursive import limits have changed across recent Claude Code releases.
This document deliberately does not turn a historical numeric limit into an
architectural invariant. Release evidence must record the current official
page, installed version, and fresh native probe.

## Community Inspiration, Not Host Contracts

The repositories below are primary sources for their own implementation. They
do not define Codex or Claude Code behavior.

### AGENTS.md open format

- fixed source: [`agentsmd/agents.md@d1ac7f0`](https://github.com/agentsmd/agents.md/tree/d1ac7f063d20e70015ed6732664049ae4ba9d74e)
- observed structure: plain Markdown described as a predictable "README for
  agents," with concrete setup, test, style, and contribution instructions and
  support for nested project guidance
- adopt: a host-neutral project body owned by the target repository; concrete
  commands and repository facts rather than generic behavioral prose
- reject as normative: any claim about Claude imports, Codex byte budgets,
  settings, permissions, hooks, trust, or hosted loading; those remain owned by
  the official host documentation

### Ruler

- fixed source: [`intellectronica/ruler@a012f90`](https://github.com/intellectronica/ruler/tree/a012f90962c5da34031980a6447f3bd2aed43795)
- observed structure: a central Markdown source, per-agent output adapters,
  nested discovery, dry-run, backups/revert, and CI drift checks
- adopt: explicit adapter boundaries, deterministic preview, reversible apply,
  and CI comparison between intended and projected state
- reject for this product: broad support for many agents, MCP propagation,
  skills, subagents, generated-file ownership, and experimental nested behavior
  as default scope. Target project contracts in this repository family remain
  reviewed, committed, and target-owned rather than disposable generated files

### agnix

- fixed source: [`agent-sh/agnix@e943b42`](https://github.com/agent-sh/agnix/tree/e943b423ebb965f44437ce4cb011157ac4d13df8)
- observed structure: evidence-tagged rule metadata, a reusable validation
  core, structured diagnostics, safe/unsafe fix distinctions, and CLI/CI
  integration across agent configuration formats
- adopt: stable rule IDs, source citations, severity, fix confidence, and
  machine-readable diagnostics for Codex/Claude rule audits
- reject for this product: copying its Rust workspace, LSP, MCP, WebAssembly,
  editor, and multi-host breadth. A pinned external check may supplement local
  validation, but it cannot replace native-host probes or repository contracts

## Minimal End-State Architecture

```text
governed-ai-coding-runtime/
├── rules/global/
│   ├── codex/AGENTS.md
│   └── claude/CLAUDE.md
├── rules/target-project-rule-coordination.json
├── schemas/                    # registry, report, and contract schemas
├── scripts/
│   ├── sync-agent-rules.*      # protected global-only projection
│   ├── verify-agent-rule-family.py
│   └── verify-target-project-rules.py
├── tests/                      # loader/adapter/drift fixtures
└── docs/
    ├── research/
    └── change-evidence/

target-repository/
├── AGENTS.md                   # project-owned source of truth
├── CLAUDE.md                   # thin @AGENTS.md adapter
└── native enforcement only when required
    ├── .codex/config.toml or hooks
    └── .claude/settings.json or hooks
```

The processing flow is:

1. Discover only explicit target Git roots and resolve the selected state:
   workspace, immutable Git revision, or configured default branch.
2. Read project-owned rules and real repository gates without moving, cleaning,
   or overwriting unrelated target worktrees.
3. Resolve Codex and Claude loading semantics independently.
4. Validate compatibility, instruction budget, wrapper shape, contradictions,
   native settings, enforcement references, evidence fields, and rollback.
5. Produce a deterministic candidate diff or target-repository PR; do not keep
   a second central copy of target-specific rule bodies.
6. Verify the committed target state, then run a fresh native-host loading
   probe when authorization and the host surface are available.
7. Report `workspace_effective`, `default_branch_effective`, `host_loaded`, and
   `hosted_accepted` separately. Aggregate status must not erase a target-level
   failure or N/A boundary.

### Technology Stack

The existing lightweight stack is sufficient:

- Markdown for human-reviewable instruction bodies
- JSON/TOML plus JSON Schema for registries, settings, and reports
- Python for deterministic discovery, parsing, validation, projection, and
  tests
- PowerShell wrappers for Windows operator entry points
- Git objects and GitHub Actions for immutable-state audit and CI drift gates

No source-backed requirement justifies a database, web UI, message broker,
long-running service, model-call layer, or rewrite to Node.js or Rust. Those
choices would add operations and migration cost without improving native rule
loading or target-repository truth.

## Product Boundary

This control repository should own:

- global Codex and Claude rule sources and protected synchronization
- the host-neutral project contract and platform-specific adapter rules
- explicit target registration and immutable-revision/workspace auditing
- deterministic lint, schema validation, conflict detection, context-budget
  checks, wrapper checks, drift reports, backups, and rollback metadata
- native fresh-process probe definitions and evidence state labels

It should not own or operate:

- OpenAI or Anthropic provider selection, base URLs, API keys, OAuth, account
  state, billing, or model routing
- Codex or Claude process start/stop/restart, session history, continuity, or
  background supervision
- an LLM gateway, proxy service, telemetry collector, or live runtime switcher
- task execution, multi-agent orchestration, subagent scheduling, or worktree
  coordination as a product runtime
- a general MCP server, plugin marketplace, skill catalog, or reusable-agent
  platform
- enterprise MDM, registry, `requirements.toml`, managed settings, or remote
  admin deployment without a separately authorized administrator workflow
- target repositories' business build/test implementations, CI ownership,
  release approval, or hosted acceptance

The control repository may verify that a project rule points to a real command
or enforcement mechanism. It must not replace that mechanism or describe a
static audit as live runtime acceptance.

## Adopt, Reject, and Defer

| Decision | Item | Reason |
|---|---|---|
| `adopt` | Target-owned `AGENTS.md` common body plus thin `CLAUDE.md` import | Matches both native instruction models while minimizing duplication. |
| `adopt` | Separate Codex and Claude load-order adapters | The hosts use materially different discovery, merge, trust, and enforcement semantics. |
| `adopt` | Deterministic dry-run, immutable-revision audit, atomic/reversible projection, and CI drift checks | These improve traceability without creating a runtime. |
| `adopt` | Guidance/enforcement distinction | Both vendors separate model context from permissions, hooks, sandboxing, and administrator policy. |
| `reject` | Central copies of every target repository's rule body | They create a second source of truth and flatten repository-specific facts. |
| `reject` | Prose as proof of safety enforcement | Instructions influence model behavior but do not create a deterministic boundary. |
| `reject` | Local source/deployed hashes as proof of cloud or hosted loading | Local and hosted surfaces have different runtime and policy boundaries. |
| `reject` | Provider/auth/session/runtime features inside rule governance | Official configuration boundaries place them outside project instruction ownership. |
| `defer` | Skills, plugins, MCP, subagents, and generalized agent packaging | Add only for a concrete, separately accepted product requirement. |
| `defer` | Enterprise managed-policy deployment | Requires administrator ownership, fleet/version validation, rollback, and explicit authorization. |

## Verification Contract

Repository-side completion for this product means all of the following have
fresh evidence:

1. The selected target set and state source are explicit.
2. Codex and Claude rule chains resolve without incompatible instructions.
3. Shared text is single-sourced; host deltas are minimal and labeled.
4. Rule budgets, encoding, wrappers, schemas, and referenced commands pass
   deterministic checks.
5. Enforcement claims resolve to permissions, hooks, sandbox, scripts, or CI,
   or carry a complete N/A/waiver record.
6. Protected global sync reports zero unexpected drift.
7. Target immutable-revision audit passes independently of dirty workspace
   observations.
8. Native local loading and hosted acceptance remain separate evidence states.

This proves the rule-governance repository and audited target state described
by the evidence. It does not prove that every local workspace is clean, every
hosted surface has loaded the files, or every target product has completed its
business roadmap.

## Source Index

### OpenAI official

- [Codex manual](https://developers.openai.com/codex/codex-manual.md)
- [Custom instructions with AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)
- [Advanced configuration](https://learn.chatgpt.com/docs/config-file/config-advanced)
- [Configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
- [Hooks](https://learn.chatgpt.com/docs/hooks)
- [Managed configuration](https://learn.chatgpt.com/docs/enterprise/managed-configuration)
- [ChatGPT Work Admin FAQ](https://learn.chatgpt.com/docs/enterprise/work-admin-faq)

### Anthropic official

- [How Claude remembers your project](https://code.claude.com/docs/en/memory)
- [Extend Claude Code](https://code.claude.com/docs/en/features-overview)
- [Claude Code settings](https://code.claude.com/docs/en/settings)
- [Configure permissions](https://code.claude.com/docs/en/permissions)
- [Hooks reference](https://code.claude.com/docs/en/hooks)
- [Set up Claude Code for your organization](https://code.claude.com/docs/en/admin-setup)
- [Create custom subagents](https://code.claude.com/docs/en/sub-agents)

### Community primary sources

- [`agentsmd/agents.md@d1ac7f0`](https://github.com/agentsmd/agents.md/tree/d1ac7f063d20e70015ed6732664049ae4ba9d74e)
- [`intellectronica/ruler@a012f90`](https://github.com/intellectronica/ruler/tree/a012f90962c5da34031980a6447f3bd2aed43795)
- [`agent-sh/agnix@e943b42`](https://github.com/agent-sh/agnix/tree/e943b423ebb965f44437ce4cb011157ac4d13df8)
