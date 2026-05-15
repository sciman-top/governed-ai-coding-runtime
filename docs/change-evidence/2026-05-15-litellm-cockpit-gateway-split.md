# 2026-05-15 LiteLLM Cockpit Gateway Split

- rule_id: `local-codex-cockpit-auth-interop`
- risk: low documentation and contract-test hardening
- landing: `docs/plans/codex-cli-continuity-and-hot-switch-plan.md`, `docs/plans/README.md`, `tests/runtime/test_codex_cockpit_policy_contract.py`
- destination: record the preferred split where Cockpit owns ChatGPT/OAuth subscription accounts, LiteLLM owns the normal API-key/multi-provider gateway, and Cockpit API service is an opt-in LiteLLM upstream after listener hardening
- rollback: revert this evidence file plus the plan/index/test changes in the same commit

## Decision

The best architecture is not Cockpit API service versus LiteLLM. The preferred split is:

- Cockpit Tools manages ChatGPT OAuth subscription accounts, manual account switching, account groups, and quota facts.
- LiteLLM Proxy manages normal API keys, multi-provider routing, unified OpenAI-compatible gateway behavior, logging, budgets, and limits.
- Cockpit API service may be registered as one LiteLLM upstream provider after it is verified or constrained to local-only access.
- A custom Cockpit-aware adapter is deferred until the operator needs account-label, group, quota, or routing decisions beyond the single-upstream model.

## Evidence Basis

- Local Cockpit Tools source snapshot shows the API service displays `127.0.0.1` but binds with `CODEX_LOCAL_ACCESS_BIND_HOST = "0.0.0.0"`, so listener hardening remains required before use.
- LiteLLM documentation describes the proxy as an OpenAI-compatible gateway and supports routing through configured upstream providers.
- This update changes only planning and policy contracts; it does not install LiteLLM, enable Cockpit API service, alter Codex auth, or restart Codex.

## Verification

- `python -m unittest tests.runtime.test_codex_cockpit_policy_contract` -> pass
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` -> pass
- `git diff --check` -> pass
