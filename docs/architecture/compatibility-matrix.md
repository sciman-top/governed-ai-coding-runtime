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
| Agent frontend | governed API / runtime integration | CLI-driven integrations | IDE adapters | one-off chat wrappers as the main model |
| Shell model | POSIX shell in sandbox | PowerShell for local operator/admin flows | repo-specific shell variants through profiles | ad hoc shell guessing |
| Artifact storage | local dev storage, S3-compatible runtime storage | any S3-compatible provider | custom object backends | vendor-specific lock-in as a hard requirement |
| Verification execution | repo profile command runner | GitHub Actions-aligned workflows | other CI via adapter layer | CI-specific product logic hardcoded into kernel |
| Package ecosystems | repo-profile driven commands | Python, Node.js, Go, Rust common flows | Java, .NET, other ecosystems through profile definitions | hardwired one-language assumption |

## Design Rules For Compatibility

### 1. Compatibility belongs in repo profiles and adapters
The kernel should define stable semantics. Environment variance should be encoded in:
- repo profiles
- tool adapters
- sandbox adapters
- delivery adapters

### 2. Do not hardcode one shell model into task semantics
Task lifecycle, approval semantics, and verification order must stay stable even if command execution differs by environment.

### 3. Prefer command contracts over vendor-specific integrations
The runtime should work from declared commands and policies first. Provider-specific integrations can optimize later.

### 4. Linux-first production is acceptable
For this product category, Linux-first runtime support is pragmatic. Cross-platform developer support matters more than promising all OSes as first-class production targets.

## Common Systems Compatibility

### Expected early compatibility
- GitHub repositories
- local repositories with Git
- Python and Node-heavy repos
- command-line verification flows
- worktree or isolated workspace based execution

### Reasonable near-term expansion
- GitLab and Bitbucket adapters
- broader package manager coverage
- stronger Windows-native repo execution support
- richer CI adapters

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

It should not mean:
- every tool runs identically on every OS
- every CI/vendor ecosystem gets first-class support in Phase 1
- native parity is guaranteed before the isolated runtime model is stable

## Recommended Compatibility Roadmap
1. Linux-first execution runtime
2. Windows/macOS/Linux operator compatibility
3. GitHub-first repository support
4. repo-profile abstraction for additional ecosystems
5. adapter-driven expansion to more hosts and providers

## Acceptance Test Questions
- Can a repository declare its command model without patching kernel code?
- Can risk, approval, evidence, and verification semantics stay unchanged across environments?
- Can the runtime reject unsupported platform combinations clearly rather than failing ambiguously?
- Can compatibility grow through adapters instead of rewriting the task model?
