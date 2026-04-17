# Compatibility Matrix

## Purpose
Define what `governed-ai-coding-runtime` should treat as required support, supported support, best-effort support, and deferred support.

## Support Levels
- `required`: must work for the MVP to be credible
- `supported`: intended to work and should be tested
- `best_effort`: allowed, but not a primary compatibility promise yet
- `deferred`: explicitly outside the current promise

## Runtime And Environment Matrix

| Axis | Required | Supported | Best effort | Deferred |
|---|---|---|---|---|
| Production host OS | Linux | - | - | Windows production hosting |
| Developer host OS | - | Windows, macOS, Linux | - | - |
| Isolated execution target | Linux container or Linux-like sandbox | repo-local isolated workspace | Windows-native execution sandboxes | broad native multi-OS sandbox parity |
| Version control | Git | GitHub-hosted repos | GitLab, Bitbucket via later adapters | non-Git SCM |
| Agent frontend | Codex CLI/App compatible adapter plus governed API/runtime integration | CLI-driven integrations, MCP adapters, app-server style adapters | IDE adapters, browser/UI automation, cloud-agent adapters | one-off chat wrappers as the main model |
| Shell model | POSIX shell in sandbox | PowerShell for local operator/admin flows | repo-specific shell variants through profiles | ad hoc shell guessing |
| Artifact storage | local dev storage, S3-compatible runtime storage | any S3-compatible provider | custom object backends | vendor-specific lock-in as a hard requirement |
| Verification execution | repo profile command runner | GitHub Actions-aligned workflows | other CI via adapter layer | CI-specific product logic hardcoded into kernel |
| Package ecosystems | repo-profile driven commands | Python, Node.js, Go, Rust common flows | Java, .NET, other ecosystems through profile definitions | hardwired one-language assumption |

## Design Rules For Compatibility

### 1. Compatibility belongs in repo profiles and adapters
The kernel should define stable semantics. Environment variance should be encoded in:
- repo profiles
- agent adapters
- tool adapters
- sandbox adapters
- delivery adapters

### 2. Do not hardcode one shell model into task semantics
Task lifecycle, approval semantics, and verification order must stay stable even if command execution differs by environment.

### 3. Prefer command contracts over vendor-specific integrations
The runtime should work from declared commands and policies first. Provider-specific integrations can optimize later.

### 4. Prefer capability contracts over product-name integrations
The kernel should not hardcode one agent product's session model, auth model, event stream, or UI behavior. Agent products should be described through declared capabilities:
- invocation mode
- authentication ownership
- workspace control
- structured event visibility
- mutation model
- continuation model
- evidence export model

Codex CLI/App is the first compatibility target because it matches the primary user workflow, not because the kernel is Codex-specific.

### 5. Linux-first production is acceptable
For this product category, Linux-first runtime support is pragmatic. Cross-platform developer support matters more than promising all OSes as first-class production targets.

## Agent Product Shape Compatibility

| Product shape | Early target | Compatibility approach |
|---|---|---|
| Codex CLI/App with user auth | required | Use existing user-owned auth, managed workspace/worktree, CLI/app-server/MCP entrypoints where available, and external evidence/gate collection. |
| Non-interactive CLI agent | supported | Invoke through process adapter, collect JSONL/log output, diff, commands, and final handoff. |
| MCP-capable agent or tool host | supported | Map tools/resources through MCP while keeping policy and evidence semantics in the governance kernel. |
| IDE plugin agent | best_effort | Integrate through repo profile, generated context, diff/gate capture, and optional bridge APIs. Do not require full IDE replacement. |
| Cloud coding agent | best_effort | Treat as external execution with imported artifacts, approval records, diffs, logs, and verification evidence. |
| Browser/UI-only agent | best_effort | Use observe-only or manual-handoff mode unless stable automation or event export exists. |
| Unknown future agent form | supported by contract if possible | Require a capability declaration and map into the adapter contract; degrade gracefully when capabilities are missing. |

## Governance Friction Compatibility

Compatibility is not only whether the runtime can call an agent. It is also whether the runtime avoids suppressing the agent's useful capability.

The default friction model should be:
- `observe_only` for unsupported or exploratory integrations
- `advisory` for low-risk coding paths where evidence and gates are enough
- `enforced` for medium/high-risk writes
- `strict` for production-adjacent, dependency, CI, release, secrets-adjacent, or broad-write operations

The runtime should reuse upstream sandbox, approval, and permission capabilities when they are strong enough, then add repository-specific evidence and gate enforcement around them.

## Common Systems Compatibility

### Expected early compatibility
- GitHub repositories
- local repositories with Git
- Python and Node-heavy repos
- Codex CLI/App driven local coding sessions
- command-line verification flows
- worktree or isolated workspace based execution

### Reasonable near-term expansion
- GitLab and Bitbucket adapters
- broader package manager coverage
- stronger Windows-native repo execution support
- richer CI adapters
- MCP and app-server style agent integrations
- IDE and cloud-agent adapters where product APIs are stable

### Explicitly not required in MVP
- universal IDE integration
- universal shell parity
- fully generic enterprise workflow compatibility
- cross-organization federation

## What Cross-Platform Means Here
For this project, cross-platform should mean:
- developers can operate the system from common OSes
- repositories with different toolchains can be governed through profiles
- the governance kernel does not assume one repository shape
- agent products can be integrated through declared capabilities rather than kernel rewrites

It should not mean:
- every tool runs identically on every OS
- every CI/vendor ecosystem gets first-class support in Phase 1
- native parity is guaranteed before the isolated runtime model is stable
- every AI coding product receives a deep integration before it exposes stable automation or evidence surfaces

## Recommended Compatibility Roadmap
1. Linux-first execution runtime
2. Windows/macOS/Linux operator compatibility
3. GitHub-first repository support
4. Codex CLI/App compatible first adapter
5. repo-profile abstraction for additional ecosystems
6. generic agent adapter contract
7. adapter-driven expansion to MCP, app-server, IDE, cloud, and future agent products

## Acceptance Test Questions
- Can a repository declare its command model without patching kernel code?
- Can risk, approval, evidence, and verification semantics stay unchanged across environments?
- Can the runtime reject unsupported platform combinations clearly rather than failing ambiguously?
- Can compatibility grow through adapters instead of rewriting the task model?
- Can Codex CLI/App remain user-authenticated while the runtime governs workspace, gates, evidence, and delivery?
- Can an unknown future agent product be admitted by capability declaration rather than product-specific kernel changes?
- Does governance add friction only where risk justifies it?
