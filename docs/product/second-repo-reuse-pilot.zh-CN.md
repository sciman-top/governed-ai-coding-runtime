# 第二仓复用试点

## Pilot Scope
second-repo pilot 使用已有 sample repo profiles：

- primary: `python-service-sample`
- second: `typescript-webapp-sample`

这个 pilot 不访问外部仓。它证明相同 kernel semantics 可以通过 repo-profile 值和更严格的 override 来接纳第二种 repo 形态。

## Kernel Reuse Rule
第二仓可以在以下方面不同：

- language
- build/test commands
- path policies
- eval suites
- reviewer handoff text

但它不能重定义：

- task lifecycle
- approval state machine
- canonical verification order

## Additional Adapter Shape
这个 pilot 同时声明了一个 generic non-interactive process CLI adapter。其 logs-only event visibility 被记录为 adapter compatibility gap，而不是分叉 governance-kernel semantics 的理由。

## Related
- [English Version](./second-repo-reuse-pilot.md)
