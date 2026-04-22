# 20260422 Runtime Persistence Hardening And Scan Scope

## Goal
继续执行上一轮审查后的后续建议，优先落地两类低风险、高收益改动：

1. 把更多关键 JSON/Text 持久化路径切到统一原子写。
2. 给 process-bridge `run_launch_mode()` 增加可选扫描范围，避免默认对整个 `cwd` 做不必要快照。

同时评估依赖清单/锁文件是否适合在当前仓库状态下直接落地。

## Scope
- `packages/contracts/src/governed_ai_coding_runtime_contracts/artifact_store.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_governance.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/learning_efficiency_metrics.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `packages/agent-runtime/artifact_store.py`
- `scripts/session-bridge.py`
- `tests/runtime/test_learning_efficiency_metrics.py`
- `tests/runtime/test_session_bridge.py`
- `docs/change-evidence/20260422-runtime-persistence-hardening-and-scan-scope.md`

## Review Findings
1. Medium: artifact and metrics persistence still used direct overwrite
- `artifact_store.py`、`repo_attachment.py`、`learning_efficiency_metrics.py`、`attached_write_governance.py` 仍有关键 `write_text()` 覆盖写。
- 这些文件不是控制平面主状态，但一旦半写，仍会影响 evidence / handoff / context pack / metrics 可读性和恢复能力。

2. Medium: process-bridge still lacked bounded snapshot scope
- 上一轮已经把 `_file_snapshot()` 从内容哈希降为元数据签名，但 `run_launch_mode()` 仍默认总是扫描整个 `cwd`。
- 对于只关心特定子目录的 launch fallback，这仍然会引入额外固定成本。

3. Deferred: dependency manifest and lockfile
- 仓库当前没有正式包管理策略，且 [packages/README.md](D:/CODE/governed-ai-coding-runtime/packages/README.md:13) 明确要求“只有在有显式 dependency / supply-chain evidence 时才引入包管理元数据”。
- 当前运行时代码几乎全部基于标准库；如果现在硬补 `pyproject.toml` / lockfile，只会引入新的构建后端决策和伪锁文件风险。
- 因此本轮只完成评估，不自动落地依赖清单。

## Changes
1. Extended atomic write coverage
- `packages/contracts/.../artifact_store.py`
  - `write_text()` / `write_json()` 改为 `atomic_write_text(...)`
- `packages/contracts/.../repo_attachment.py`
  - `_write_json()` 改为原子写，覆盖 repo profile、light pack、context pack 写入
- `packages/contracts/.../learning_efficiency_metrics.py`
  - `persist_learning_efficiency_metrics(...)` 改为原子写
  - 同时校验 `task_id` / `run_id` 文件段，防止输出根目录被路径片段逃逸
- `packages/contracts/.../attached_write_governance.py`
  - 审批请求落盘改为原子写
  - 审批文件名增加 `approval_id` 文件段校验
- `packages/agent-runtime/artifact_store.py`
  - 服务层 artifact store 改为本地原子写 helper
  - 避免引入对 contracts 包内部 helper 的新耦合

2. Added optional process-bridge snapshot scope
- `packages/contracts/.../session_bridge.py`
  - `run_launch_mode(..., snapshot_scope=None)` 新增可选扫描范围参数
  - `_resolve_snapshot_scope(...)` 约束扫描范围必须留在 `cwd` 内
  - `_file_snapshot(...)` 现在支持目录或单文件快照，并允许相对 `cwd` 产出路径
- `scripts/session-bridge.py`
  - `launch` 命令新增 `--snapshot-scope`
- 默认行为保持兼容：未提供时仍以 `cwd` 为扫描根

3. Added regression tests
- `tests/runtime/test_learning_efficiency_metrics.py`
  - 新增 unsafe `task_id` 持久化拒绝测试
- `tests/runtime/test_session_bridge.py`
  - 新增 scope-limited snapshot 只报告受控目录变化
  - 新增 snapshot scope 越界拒绝测试

## Verification
### Focused regression tests
1. `python -m unittest tests.runtime.test_artifact_store tests.runtime.test_learning_efficiency_metrics tests.runtime.test_repo_attachment tests.runtime.test_attached_write_governance tests.runtime.test_session_bridge`
- result: pass
- key output:
  - `Ran 67 tests`
  - `OK`

2. Service-layer standalone import probe
- command: inline Python `importlib.util.spec_from_file_location(...)` load `packages/agent-runtime/artifact_store.py`
- result: pass
- key output:
  - `FilesystemArtifactStore`

### Gate order
1. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
2. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
3. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
4. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`
5. `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Docs`
- result: all pass
- key output:
  - build: `OK python-bytecode`, `OK python-import`
  - runtime: `Ran 310 tests`, `OK runtime-unittest`, `OK runtime-service-parity`, `OK runtime-service-wrapper-drift-guard`
  - contract: `OK schema-json-parse`, `OK schema-example-validation`, `OK schema-catalog-pairing`
  - hotspot/doctor: `OK runtime-status-surface`, `OK codex-capability-ready`, `OK adapter-posture-visible`
  - docs: `OK active-markdown-links`, `OK claim-drift-sentinel`, `OK claim-evidence-freshness`

## Risks
- `snapshot_scope` 是新增能力，但默认关闭，不影响既有调用链。
- 依赖清单/lockfile 本轮未自动引入，`E5` 仍维持现状；这是刻意保守，不是遗漏。

## Rollback
Revert:
- `packages/contracts/src/governed_ai_coding_runtime_contracts/artifact_store.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/attached_write_governance.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/learning_efficiency_metrics.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/repo_attachment.py`
- `packages/contracts/src/governed_ai_coding_runtime_contracts/session_bridge.py`
- `packages/agent-runtime/artifact_store.py`
- `scripts/session-bridge.py`
- `tests/runtime/test_learning_efficiency_metrics.py`
- `tests/runtime/test_session_bridge.py`
- `docs/change-evidence/20260422-runtime-persistence-hardening-and-scan-scope.md`
