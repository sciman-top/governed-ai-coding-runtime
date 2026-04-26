# Dependency Baseline

## Current baseline
- Python code under `apps/`, `packages/`, `scripts/`, and `tests/` is currently `stdlib-only`.
- The allowed non-stdlib import roots are repository-local packages: `governed_ai_coding_runtime_contracts` and `lib`.
- Declared external Python dependencies: none.
- Host tools such as `python`, `pwsh`, `git`, and `codex` are operational prerequisites, not Python package dependencies.

## Machine verification
- Repo baseline command: `python scripts/verify-dependency-baseline.py`
- Target-repo baseline command: `python scripts/verify-dependency-baseline.py --target-repo-root <path> --require-target-repo-baseline`
- Machine-readable baseline: [dependency-baseline.json](./dependency-baseline.json)

## Host tooling baseline
- `host_tooling` is checked by the same verifier.
- Required tools currently include `python` and `pwsh`.
- Optional tools (for example `git`, `codex`) are reported but do not fail the baseline check when missing.

## Update rule
- If a new third-party Python module is required, do all of the following in one slice:
  - update [dependency-baseline.json](./dependency-baseline.json)
  - add explicit dependency and supply-chain evidence
  - introduce package manager metadata and lock strategy only when the repository is ready to make that dependency reproducible

## Rationale
- The repository currently prefers a `stdlib-only` baseline over premature package metadata.
- This keeps the supply-chain surface explicit while the repo is still in a docs-first / contracts-first stage.
