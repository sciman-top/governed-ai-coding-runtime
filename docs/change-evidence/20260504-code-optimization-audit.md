# 2026-05-04 Code Optimization Audit

## Goal
- Current landing: `D:\CODE\governed-ai-coding-runtime`.
- Target home: runtime contract, host-environment robustness, governed gate execution, operator UI modularity, and runtime test speed in `packages/contracts` and `tests/runtime`.
- Verification: `build -> Runtime -> Contract -> doctor` using the repository hard-gate order.

## Baseline
- `git status --short --branch`: clean `main...origin/main` before changes.
- `.\run.ps1 fast`: pass; `build` plus `RuntimeQuick`, 53 tests in about 23 seconds.
- `python scripts/select-next-work.py --repo-root .`: pass; `next_action=wait_for_host_capability_recovery`, `ltp_decision=defer_all`.
- `python scripts/verify-evidence-recovery-posture.py --repo-root . --as-of 2026-05-04`: pass; host capability remains a bounded defer, not a trigger for new LTP implementation.

## Findings
- `subprocess_guard.py` inherited `ComSpec` from the ambient environment or Codex `shell_environment_policy.set`. For Windows `shell=True` execution this made the shell executable part of mutable local state instead of canonical host state.
- Governed gate execution was duplicated across `session_bridge.py`, `multi_repo_trial.py`, and `run-governed-task.py`, including timeout lookup, subprocess invocation, and stdout/stderr merging.
- Main maintainability hotspots were large mixed-responsibility files: `operator_ui.py`, `session_bridge.py`, `runtime-flow-preset.ps1`, and their paired large tests. `operator_ui.py` has now been split into bounded renderer, text, style, and script modules; remaining hotspot work should continue in similarly bounded slices.
- Runtime test speed is improved but still concentrated in a small slow set. The latest full runtime gate completed in about 105 seconds across 105 test files, down from about 123 seconds before the test-speed slice. Remaining slowest files include `test_runtime_flow_preset.py`, `test_attached_repo_e2e.py`, `test_dependency_baseline.py`, and `test_transition_stack_convergence.py`.
- Repository slimming evidence still shows `docs/change-evidence` and operator UI screenshots as the largest visible surface. Archive/delete work remains forbidden by default unless a dedicated dry-run, backup, and rollback slice is opened.

## Changes
- Removed `ComSpec` from Codex shell-policy inherited safe keys.
- Canonicalized Windows `SystemRoot`, `WINDIR`, and `ComSpec` after environment merge.
- Added regression coverage proving that neither Codex shell policy nor existing process environment can redirect governed Windows shell execution away from `System32\cmd.exe`.
- Added `run_governed_gate_command()` as the shared gate execution helper in `subprocess_guard.py`.
- Replaced duplicate governed gate execution paths in `session_bridge.py`, `multi_repo_trial.py`, and `scripts/run-governed-task.py`.
- Added helper regression coverage for stdout/stderr merge behavior and `GOVERNED_GATE_TIMEOUT_SECONDS` timeout handling.
- Split `operator_ui.py` into `operator_ui_text.py`, `operator_ui_style.py`, `operator_ui_script.py`, and the remaining main renderer.
- Preserved exact HTML output for zh-CN static, en static, and zh-CN interactive representative snapshots when compared to the pre-split `HEAD` renderer.
- Synced operator UI stale-source detection in `serve-operator-ui.py` and `operator-ui-service.ps1` so changes to split UI modules trigger the same restart/stale-content protection.
- Added a translation key parity regression test for `zh-CN` and `en`.
- Narrowed `test_run_governed_task_cli` to a temporary fast repo profile and mocked Codex capability in the `run_task` path; the file now runs in about 3.5 seconds locally instead of about 35 seconds.
- Forced attached repo e2e subprocesses through the explicit missing-Codex fallback path, preserving fallback assertions while avoiding repeated real host probes.
- Changed `select-next-work.py` to skip the expensive auto-detection chain when `gate_state`, `source_state`, and `evidence_state` are all supplied explicitly.
- Added a regression test proving explicit selector inputs do not call `_auto_detect_runtime_inputs`.
- Added `scripts/verify-shell-risk-contract.py` as a deterministic `packages/` and `scripts/` scanner for unapproved Python `shell=True`, destructive PowerShell `Remove-Item` / `Move-Item`, and unbounded `Start-Process` usage.
- Added explicit shell-risk allowlist entries with expected counts and reasons for the currently governed exceptions.
- Wired `shell-risk-contract` into `scripts/verify-repo.ps1 -Check Contract`.
- Added regression coverage proving new unapproved shell/destructive-process patterns fail and bounded or allowlisted cases remain explicit.
- Refreshed the repo-slimming surface dry-run report with `python scripts/audit-repo-slimming-surface.py` from a clean worktree after the shell-risk contract commit.
- Kept repo-slimming as inventory-only in this optimization batch: no archive move and no delete operation was executed.

## pre_change_review
- `pre_change_review`: required because this slice modifies `scripts/verify-repo.ps1`, a self-repo hard-gate entrypoint.
- `control_repo_manifest_and_rule_sources`: no `rules/manifest.json` or managed rule source file is changed by this shell-risk slice; the change stays in the control repo gate and verifier surface.
- `user_level_deployed_rule_files`: not modified; this slice does not sync or edit user-level deployed rule files.
- `target_repo_deployed_rule_files`: not modified; this slice does not sync or edit target-repo deployed rule files.
- `target_repo_gate_scripts_and_ci`: not modified; the new check governs this control repository's `packages/` and `scripts/` source surface only.
- `target_repo_repo_profile`: not modified; no `.governed-ai/repo-profile.json` target profile changes are part of this slice.
- `target_repo_readme_and_operator_docs`: not modified; no target operator docs or README semantics are changed.
- `current_official_tool_loading_docs`: N/A for this change because no Codex/Claude/Gemini rule loading model, import behavior, or wrapper semantics are changed.
- `drift-integration decision`: integrate shell-risk enforcement as a deterministic self-repo `Contract` gate with explicit allowlist counts instead of leaving the review as a one-time static scan.

## Verification
- `python -m unittest tests.runtime.test_subprocess_guard -v`: pass, 7 tests.
- `python -m unittest tests.runtime.test_subprocess_guard tests.runtime.test_tool_runner tests.runtime.test_session_bridge -v`: pass, 69 tests.
- `python -m unittest tests.runtime.test_subprocess_guard tests.runtime.test_multi_repo_trial tests.runtime.test_session_bridge tests.runtime.test_run_governed_task_cli -v`: pass, 70 tests.
- `python -m unittest tests.runtime.test_operator_ui tests.runtime.test_operator_entrypoint -v`: pass, 37 tests.
- `python -m unittest tests.runtime.test_run_governed_task_cli -v`: pass, 9 tests in about 3.5 seconds.
- `python -m unittest tests.runtime.test_attached_repo_e2e -v`: pass, 5 tests in about 34 seconds.
- `python -m unittest tests.runtime.test_autonomous_next_work_selection -v`: pass, 8 tests in about 19.5 seconds.
- `python -m unittest tests.runtime.test_run_governed_task_cli tests.runtime.test_attached_repo_e2e tests.runtime.test_autonomous_next_work_selection -v`: pass, 22 tests in about 53.4 seconds.
- `python -m unittest tests.runtime.test_shell_risk_contract -v`: pass, 6 tests.
- `python -m unittest tests.runtime.test_repo_slimming_surface -v`: pass, 2 tests.
- `python scripts/verify-shell-risk-contract.py --json`: pass, checked 150 files, finding_count=0, stale_allowlist_count=0.
- `python scripts/audit-repo-slimming-surface.py`: pass; refreshed `docs/change-evidence/repo-slimming-surface-audit.json`.
- Pre-split vs post-split HTML exact comparison: pass for `empty-zh-static`, `empty-en-static`, and `full-zh-interactive`.
- `python -m py_compile packages\contracts\src\governed_ai_coding_runtime_contracts\subprocess_guard.py packages\contracts\src\governed_ai_coding_runtime_contracts\session_bridge.py packages\contracts\src\governed_ai_coding_runtime_contracts\multi_repo_trial.py scripts\run-governed-task.py tests\runtime\test_subprocess_guard.py`: pass.
- `python -m py_compile packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_text.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_style.py packages\contracts\src\governed_ai_coding_runtime_contracts\operator_ui_script.py scripts\serve-operator-ui.py tests\runtime\test_operator_ui.py tests\runtime\test_operator_entrypoint.py`: pass.
- `python -m py_compile scripts\select-next-work.py tests\runtime\test_autonomous_next_work_selection.py tests\runtime\test_attached_repo_e2e.py tests\runtime\test_run_governed_task_cli.py`: pass.
- `python -m py_compile scripts\verify-shell-risk-contract.py tests\runtime\test_shell_risk_contract.py`: pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`: pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`: pass, 105 test files in about 104.8 seconds, failures=0.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`: pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`: pass with existing `codex-capability-degraded` warning.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`: pass.
- `git diff --check`: pass; Git emitted only existing LF-to-CRLF working-copy warnings for edited files.

## Rollback
- Before commit: `git restore packages/contracts/src/governed_ai_coding_runtime_contracts/subprocess_guard.py packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py packages/contracts/src/governed_ai_coding_runtime_contracts/multi_repo_trial.py packages/contracts/src/governed_ai_coding_runtime_contracts/operator_ui.py scripts/run-governed-task.py scripts/serve-operator-ui.py scripts/operator-ui-service.ps1 scripts/select-next-work.py scripts/verify-repo.ps1 tests/runtime/test_subprocess_guard.py tests/runtime/test_operator_ui.py tests/runtime/test_operator_entrypoint.py tests/runtime/test_run_governed_task_cli.py tests/runtime/test_attached_repo_e2e.py tests/runtime/test_autonomous_next_work_selection.py docs/change-evidence/20260504-code-optimization-audit.md docs/change-evidence/runtime-test-speed-latest.json`; then remove the new split modules `operator_ui_script.py`, `operator_ui_style.py`, `operator_ui_text.py`, `scripts/verify-shell-risk-contract.py`, and `tests/runtime/test_shell_risk_contract.py`.
- After commit: `git revert <commit-sha>`.
- Repo-slimming dry-run rollback: `git restore docs/change-evidence/repo-slimming-surface-audit.json docs/change-evidence/20260504-code-optimization-audit.md`.

## Repo-Slimming Dry-Run Closeout
- `docs/change-evidence/repo-slimming-surface-audit.json` now records `out_of_scope_dirty_worktree.entry_count=0`, so the inventory was generated from a clean post-shell-risk-commit baseline.
- Latest inventory: `visible_surface.file_count=1358`, `visible_surface.megabytes=21.3`, `text_surface.file_count=1317`, `text_surface.line_count=220927`.
- Main active weight remains `docs/change-evidence`: `file_count=752`, `megabytes=14.73`, `text_line_count=97059`.
- Safety fence remains enforced in evidence: `delete_mode=forbidden_by_default`, `archive_move_mode=forbidden_by_default`.
- Future physical cleanup remains a separate apply task and must start with candidate catalog, dry-run proof, backup, rollback evidence, and focused verification.

## Task List Closeout
- Total tasks: `6`.
- Completed tasks: `6`.
- Remaining tasks in this optimization batch: `0`.
