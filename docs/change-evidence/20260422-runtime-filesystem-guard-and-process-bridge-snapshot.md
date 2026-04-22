# 20260422 Runtime Filesystem Guard And Process Bridge Snapshot

## Goal
对当前 runtime 代码做一次小步、根因优先的审查与修复，在不改变外部接口和数据结构的前提下，先收敛两个高收益问题：

1. 文件型状态存储缺少统一路径约束，`task_id` / `approval_id` 可以直接拼进文件路径。
2. process-bridge `run_launch_mode()` 在命令前后对整个工作目录逐文件读取内容并做 SHA-256，比对成本与仓库体积线性相关。

## Scope
- `packages/contracts/src/governed_ai_coding_runtime_contracts/file_guard.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/task_store.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_execution.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `tests/runtime/test_task_store.py`
- `tests/runtime/test_attached_write_execution.py`
- `tests/runtime/test_session_bridge.py`
- `docs/change-evidence/20260422-runtime-filesystem-guard-and-process-bridge-snapshot.md`

## Review Findings
1. High: file-backed state path escape
- `FileTaskStore._path_for()` 直接使用 `task_id` 组装 `<task_root>/<task_id>.json`。
- 审批记录路径同样直接使用 `approval_id` 组装 `approvals/<approval_id>.json`。
- 复现实验显示 `task_id="../escape"` 会把任务文件写到 task root 外部。
- 影响：
  - 破坏状态目录边界。
  - 在 Windows 上还会暴露非法文件名/保留设备名风险。
  - 一旦和 CLI / service wrapper 结合，会形成真实的文件越界读写面。

2. Medium: process-bridge launch snapshot is full-content scan
- `session_bridge.run_launch_mode()` 调用 `_file_snapshot()`，在执行前后各对整个 cwd 做一次 `rglob("*") + read_bytes() + sha256`。
- 这会把一次非常轻的命令放大成“扫描整个仓库两遍”的固定成本。
- 轻量基准（300 个 1 KiB 文件）在改动前耗时约 `252.38 ms`，改动后约 `14.19 ms`。

3. Medium: non-atomic state rewrites
- 任务记录和审批记录此前使用 `write_text()` 直接覆盖。
- 一旦进程中断，可能留下半写 JSON，随后影响 status/doctor/operator surface。

## Changes
1. Added shared file guard primitives
- 新增 `file_guard.py`：
  - `validate_file_component(...)`
  - `atomic_write_text(...)`
- 统一拦截路径分隔符、保留段、控制字符、Windows 非法字符和设备名。

2. Hardened task record persistence
- `task_store.py` 现在：
  - 在 `_path_for()` 上校验 `task_id`。
  - 在 `save()` 上改为原子写。

3. Hardened approval record persistence
- `attached_write_execution.py`：
  - `_approval_record_path()` 统一校验 `approval_id`。
  - 审批状态更新改为原子写。
- `session_bridge.py`：
  - 新增 `_approval_file_path()` 统一审批文件定位。
  - `write_status` / `approval_ref` / `approval_status` / `approval_session_identity` 等路径全部改走统一校验。
  - `_persist_tool_approval_request()` / `_persist_approval_session_identity()` 改为原子写。
  - 显式传入的 `approval_id` 会先校验再接受。

4. Reduced process-bridge snapshot overhead
- `_file_snapshot()` 从“读取整个文件内容求哈希”改为读取 `size + mtime_ns` 的轻量签名。
- 保留 `changed_files` / `deleted_files` 的外部语义不变。
- 额外增加删除文件、同尺寸改写两个回归测试，避免性能优化破坏可观测性。

## Verification
### Codex platform diagnostics
timestamp: `2026-04-22T19:39:24.5182614+08:00`

1. `codex --version`
- exit_code: `0`
- key_output: `codex-cli 0.122.0`

2. `codex --help`
- exit_code: `0`
- key_output: `Codex CLI` / command list rendered normally

3. `codex status`
- exit_code: `1`
- `platform_na`
- reason: `stdin is not a terminal`
- alternative_verification: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- evidence_link: `docs/change-evidence/20260422-runtime-filesystem-guard-and-process-bridge-snapshot.md`
- expires_at: `n/a`

### Reproduction / supporting checks
1. Unsafe task id escape reproduction before fix
- command: inline Python using `FileTaskStore.save(task_id="../escape")`
- result: reproduced
- key output:
  - `"saved_path": "...\\tasks\\..\\escape.json"`
  - `"under_root": false`

2. Unsafe task id blocked after fix
- command: inline Python using the same payload after the patch
- result: blocked
- key output:
  - `"blocked": true`
  - `"error": "task_id must not contain path separators"`

3. Launch snapshot micro-benchmark
- command: inline Python calling `session_bridge._file_snapshot()` on 300 files
- result:
  - before patch: `252.38 ms`
  - after patch: `14.19 ms`

4. Focused regression tests
- `python -m unittest tests.runtime.test_task_store tests.runtime.test_attached_write_execution tests.runtime.test_session_bridge`
- result: pass
- key output:
  - `Ran 44 tests`
  - `OK`

5. Docs consistency check
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- result: pass
- key output:
  - `OK active-markdown-links`
  - `OK claim-drift-sentinel`
  - `OK claim-evidence-freshness`

### Gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
- result: all pass
- key output:
  - build: `OK python-bytecode`, `OK python-import`
  - runtime: `Ran 307 tests`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`
  - contract: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`
  - hotspot/doctor: `OK runtime-status-surface`, `OK codex-capability-ready`, `OK adapter-posture-visible`

## Risks
- `_file_snapshot()` 现在依赖文件元数据而不是内容哈希，极端场景下如果文件内容变化且 `size` 与 `mtime_ns` 同时保持不变，`changed_files` 可能漏报。
- 这里的取舍是明确的：该快照只用于 process-bridge 变化提示，不作为安全边界或持久化真相来源；换来的收益是把每次 launch 的固定成本从“扫描内容”降到“读取元数据”。
- 当前没有统一改造所有 JSON/Text 写入点；这次只收敛 task/approval 这些直接影响控制面状态稳定性的关键路径。

## Rollback
Revert:
- `packages/contracts/src/governed_ai_coding_runtime_contracts/file_guard.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/task_store.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_execution.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `tests/runtime/test_task_store.py`
- `tests/runtime/test_attached_write_execution.py`
- `tests/runtime/test_session_bridge.py`
- `docs/change-evidence/20260422-runtime-filesystem-guard-and-process-bridge-snapshot.md`
