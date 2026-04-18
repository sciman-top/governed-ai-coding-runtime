# Verification Runner

## Canonical Order
Full verification 按项目 gate 顺序执行：

1. `build`
2. `test`
3. `contract`
4. `doctor`

Quick verification 是缩短版 preflight，但仍保持已启用 gate 的顺序：

1. `test`
2. `contract`

## Live Commands
- `build`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1`
- `test`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime`
- `contract`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract`
- `doctor`: `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1`

## Escalation Conditions
- quick verification 失败后，交付前必须补 full verification 或 root-cause 证据
- contract/invariant 失败会阻断交付
- 缺失 required gate 也会阻断交付，除非有文档化的 `gate_na` 记录

## Evidence Artifact
verification output 必须附着到 change evidence 文件，并记录：

- mode: `quick` 或 `full`
- gate order
- per-gate result
- evidence link
- escalation conditions

## Related
- [English Version](./verification-runner.md)
