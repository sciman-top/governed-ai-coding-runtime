# 2026-05-06 Cockpit Tools Borrowing Matrix

## Scope

Review `jlcodes99/cockpit-tools` as a mechanism source for this control repo, not as a product blueprint to clone.

Reviewed sources on 2026-05-06:

- GitHub README: `https://github.com/jlcodes99/cockpit-tools/blob/main/README.en.md`
- GitHub releases: `https://github.com/jlcodes99/cockpit-tools/releases`

## Decision Summary

| Area | Cockpit Tools signal | Decision | Why |
| --- | --- | --- | --- |
| New account persistence | Strong Codex account import/export and managed-account lifecycle | adopt_now | This repo had a real gap: newly logged-in Codex accounts could appear as active but had no named snapshot entrypoint. |
| Broken account index repair | Release notes show repeated auto-repair / rebuild work for local account indexes | adopt_now | Matches this repo's "host fact first, repair local truth, then surface evidence" direction. |
| Quota / usage surfacing | Dashboard emphasizes remaining quota and reset windows | adopt_now | Already aligned with this repo's 8770 Codex panel; useful as a consistency target for other providers when an evidence-backed source exists. |
| Local API compatibility gateway | Cockpit Tools ships a broader Codex local API service and OpenAI-compatible shims | defer | Potentially useful later, but this repo is a governance sidecar, not a replacement execution host or general-purpose local gateway product. |
| Multi-platform account manager UX | Cockpit Tools spans many AI IDEs in one desktop-oriented dashboard | defer | Some UI patterns are useful, but copying the product scope would blur this repo's control-plane boundary. |
| Silent background mutation | Cockpit Tools optimizes for convenience and broad local account operations | do_not_adopt | This repo should keep local state mutation explicit, evidence-backed, and bounded by governance semantics. |
| Desktop packaging / distribution machinery | Homebrew/Cask, DMG, release automation, desktop app ergonomics | do_not_adopt | Out of scope for this repo's current objective. |

## Concrete Borrowing Targets

### 1. Adopt now

- `save current login as named snapshot`
  - Landed in this slice for Codex via `save-active` UI/API/CLI.
- `snapshot/index self-repair`
  - Next candidate: add a deterministic repair path when official app storage is ambiguous or when named snapshot drift is detectable but no clean target exists.
- `quota-source labeling`
  - Keep distinguishing `local snapshot`, `session jsonl`, and explicit online refresh sources in the UI.

### 2. Defer

- `provider-neutral quota contract`
  - Only add for Claude(GLM) or other providers if there is a stable, auditable local or official source.
- `local API gateway compatibility`
  - Revisit only if this repo explicitly chooses to govern a shared local gateway contract rather than only inspecting one.

### 3. Do not adopt

- `turn this repo into a universal account manager`
  - That would compete with the host tools and weaken the current "governance/control-plane" boundary.
- `silent auto-import or auto-write of account state`
  - This repo should keep account persistence explicit and operator-visible.

## Immediate Follow-on Candidates

1. Add `repair-active-snapshot-index` for Codex:
   - classify `missing_named_snapshot`, `drifted`, and `official_app_account=ambiguous`
   - offer explicit repair actions rather than only passive status text
2. Add a provider-usage capability matrix:
   - Codex: supported now
   - Claude(GLM): status only
   - others: `platform_na` until a real source exists
3. Keep the 8770 surface as the first integration target:
   - do not create a second parallel local account management UI

## Boundary Reminder

The useful lesson from Cockpit Tools is not "copy the whole product". The useful lesson is:

- make local account state explicit
- make repair actions operator-visible
- make quota sources labeled and refreshable
- keep every local mutation reversible

That is compatible with `governed-ai-coding-runtime` as a governance sidecar. Becoming a universal AI IDE desktop manager is not.
