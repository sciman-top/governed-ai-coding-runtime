# Codex/Cockpit Doc Boundary Refresh

- rule_id: `LocalCodexCockpit`
- risk_level: `low`
- change: refreshed active README/quickstart wording after retiring governed Codex/Cockpit switch, repair, gateway, and guard code.
- commands:
  - `rg -n "codex-interop-check|CodexProjectionSmoke|CodexApiProjectionRepair|CodexOauthProjectionRepair|CodexLaunchBindingRepair|Manage-LiteLLMGateway|codex-mode-|LiteLLM|8770|repair|guard" README.md docs --glob "!docs/change-evidence/**"`
- key_output:
  - `docs/README.md` still referenced `scripts/codex-interop-check.py` and explicit Cockpit API projection repair in active guidance.
  - `docs/quickstart/ai-coding-usage-guide.zh-CN.md` still said this repository provided read-only diagnostics and explicit API projection repair.
- compatibility:
  - docs-only boundary clarification; no runtime behavior changes.
  - Cockpit Tools remains the owner for Direct OAuth, Direct API, and Cockpit API service roundtrip switching.
- rollback:
  - revert this documentation commit with git if the ownership boundary changes again.
