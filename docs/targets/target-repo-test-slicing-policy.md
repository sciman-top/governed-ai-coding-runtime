# Target Repo Test Slicing Policy

## Purpose
Keep daily target-repo feedback fast without weakening full/release verification.

## One-Click Memory
This policy is persisted through the target catalog and one-click governance baseline sync:

- Source of truth: `docs/targets/target-repos-catalog.json`.
- One-click coding-speed apply: `scripts/runtime-flow-preset.ps1 -AllTargets -ApplyCodingSpeedProfile`.
- Compatibility apply: `scripts/runtime-flow-preset.ps1 -AllTargets -ApplyGovernanceBaselineOnly`.
- Apply implementation: `scripts/apply-target-repo-governance.py`.
- Drift check: `scripts/verify-target-repo-governance-consistency.py`.
- Execution: `scripts/governance/fast-check.ps1` reads `quick_gate_commands`; `full-check.ps1` reads `full_gate_commands`.
- No-op speed guard: `scripts/runtime-flow-preset.ps1 -ApplyAllFeatures -AutoMilestoneGateMode` may skip the milestone gate only when auto mode selected `fast`, governance sync changed nothing, the target is a git repository, and `git status --porcelain` is empty.

The target catalog is also the source of truth for base gate facts (`build_command`, `test_command`, and
`contract_command`). One-click apply may fill missing target `repo-profile.json` gate groups from the catalog, but an
existing target gate difference is a blocking drift that must be reviewed and integrated before either side is updated.

## Optional Outer-AI Handoff
When an outer AI agent is available, it may recommend a target-specific slice by writing:

`<target-repo>/.governed-ai/quick-test-slice.recommendation.json`

When the file is missing, one-click apply writes an AI-readable prompt to:

`<target-repo>/.governed-ai/quick-test-slice.prompt.md`

The JSON output exposes:

- `governance_sync_outer_ai_action`: `prompt_written`, `prompt_available`, or `none`.
- `governance_sync_quick_test_prompt_path`: prompt path for the AI to read.
- `governance_sync_quick_test_slice_source`: `argument`, `argument_skip`, `recommendation_file`, `recommendation_file_skip`, or `none`.
- `governance_sync_outer_ai_instruction`: exact instruction the session AI should follow.

For all-target runs, the top-level JSON also exposes:

- `outer_ai_recommendation_action`: `read_prompt_and_write_recommendation` or `none`.
- `outer_ai_recommendation_tasks`: one task per target that needs a recommendation file.

One-click apply treats this file as data. It reads only the fields below and ignores any instruction-like prose:

```json
{
  "schema_version": "1.0",
  "status": "ready",
  "quick_test_command": "python -m unittest tests.test_fast",
  "quick_test_reason": "Focused daily regression slice.",
  "quick_test_timeout_seconds": 180
}
```

Behavior:

- If the target catalog already declares `quick_test_command`, the catalog value wins.
- If the target catalog declares `quick_test_skip_reason`, the catalog skip wins and no outer-AI prompt is emitted.
- If the recommendation file exists with `status=ready`, one-click apply uses it for `quick_gate_commands.test`.
- If the recommendation file is missing, one-click apply writes a prompt and exposes an outer-AI recommendation task.
- If the prompt file already exists with different content, one-click apply blocks instead of overwriting the target-local prompt.
- If the recommendation file exists with `status=skip`, one-click apply treats that as a completed AI decision and keeps deterministic derived gates.
- If the recommendation file is malformed, one-click apply fails closed so bad AI output cannot silently change gates.

## Catalog Fields
Targets may declare:

- `quick_test_command`: focused test slice for daily `fast` feedback.
- `quick_test_reason`: short justification for why the slice is representative.
- `quick_test_timeout_seconds`: optional timeout override for the focused test slice.
- `quick_test_skip_reason`: durable catalog reason to suppress repeated outer-AI slicing prompts when no safe slice is justified.

The full test command remains `test_command`. One-click apply must use `quick_test_command` only for `quick_gate_commands.test`; it must not replace `test_commands` or `full_gate_commands.test`.
`quick_test_command` and `quick_test_skip_reason` are mutually exclusive.

## Safe Slice Criteria
A `quick_test_command` is allowed when it satisfies all criteria:

- It covers the code path or governance mechanism most likely to change during daily work.
- It is deterministic and does not require external network or live devices.
- It is materially faster than the full `test_command`.
- The target still has a full test command in `test_command`.
- The target full gate still executes `build + test + contract/invariant`.

If these criteria are not met for a known target, declare `quick_test_skip_reason`; otherwise leave both fields absent so an outer AI can review the target.

## Recommended Patterns
- Python/unittest: select modules or individual test cases with `python -m unittest package.test_module.TestClass.test_case`.
- pytest: use explicit markers such as `-m "not slow"` or a maintained fast marker set.
- .NET: use `dotnet test --filter ...` for stable categories or traits.
- Node/Jest/Vitest: use affected/smoke scripts such as `npm run test:fast` when maintained by the target repo.
- Monorepo tools: use affected-task selection only when the dependency graph and fallback-to-full behavior are reliable.
- CI: cancel obsolete runs with workflow/job `concurrency`, set job/step timeouts, and only cache dependency manager state when the repo has stable lockfiles or dependency metadata.
- Slow-test profiling: keep the top slow tests visible in local output; for pytest targets prefer `--durations`, and for framework-agnostic target gates persist machine-readable timing summaries when available.

## Invariants
- `quick_test_command` is a daily feedback optimization, not a release gate.
- Full Runtime/target full gates remain authoritative for completion and release claims.
- Every generated or hand-written quick/full gate command should have a finite timeout unless the repo explicitly records a timeout N/A reason.
- One-click apply preserves hand-tuned `quick_gate_commands` unless they match a previously derived baseline group.
- Generated speed groups with `satisfies_gate_ids` are refreshable; stale generated groups must not preserve obsolete catalog commands.
- Consistency verification must fail on catalog/profile drift.
- Clean milestone gate skip is a no-op optimization, not a gate waiver. It is disabled for `full` milestone gates, release candidates, onboard flows, high-risk/write execution paths, and any target with pending git changes or baseline sync changes.
- Operators can force the no-op skip with `-SkipCleanMilestoneGate` or turn off auto clean skipping with `-DisableCleanMilestoneGateSkip`.
- JSON evidence must expose `clean_milestone_gate_skip_enabled`, `clean_milestone_gate_skip_source`, `milestone_gate_skipped`, and `milestone_gate_skip_reason` when `ApplyAllFeatures` or baseline+milestone mode is used.

## Self-Runtime Current Slice
`self-runtime` currently uses a focused Runtime slice covering:

- governance gate runner behavior;
- target governance consistency;
- the runtime-flow-preset baseline bootstrap case for slicing propagation;
- rollout contract checks;
- speed KPI export checks.

The full `self-runtime` test command remains `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`.
The first-class local entrypoint for that focused slice is `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check RuntimeQuick`.

`scripts/run-runtime-tests.py` is the self-runtime test-file runner. It defaults to up to 4 workers, applies a per-test-file timeout of 180 seconds unless `GOVERNED_RUNTIME_TEST_TIMEOUT_SECONDS` or `--timeout-seconds` overrides it, prints the slowest files, and can persist timing metadata with `--summary-json`.

`pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check DocsLinks` is a file-level feedback slice for active markdown link behavior. It exists for focused Runtime tests and does not replace the full `Docs` gate.

## Rollback
Remove `quick_test_command` and optional companion fields from the target catalog entry, or remove `.governed-ai/quick-test-slice.recommendation.json`, then run:

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\runtime-flow-preset.ps1 -AllTargets -ApplyCodingSpeedProfile -Json
python scripts\verify-target-repo-governance-consistency.py
```
