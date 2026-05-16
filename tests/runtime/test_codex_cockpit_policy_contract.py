from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class CodexCockpitPolicyContractTests(unittest.TestCase):
    def test_project_rules_promote_cockpit_roundtrip_contract_to_hard_boundary(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

        required = [
            "Codex/Cockpit OAuth/API 往返",
            "history bucket",
            "最高优先级",
            "docs/runbooks/codex-cockpit-api-provider-repair.md",
            "CodexProjectionSmoke",
            "CodexApiProjectionRepair",
            "CodexOauthProjectionRepair",
            "CodexLaunchBindingRepair",
            "--migrate-provider-bucket",
            "SQLite provider trigger",
            "后台 guard",
            "custom no-WebSocket provider",
            "threads.model_provider",
            "[model_providers.openai]",
            "tests.runtime.test_codex_cockpit_policy_contract",
        ]
        for text in required:
            with self.subTest(text=text):
                self.assertIn(text, agents)

    def test_runbook_and_readmes_keep_the_same_forbidden_repair_boundary(self) -> None:
        paths = [
            ROOT / "docs" / "runbooks" / "codex-cockpit-api-provider-repair.md",
            ROOT / "README.md",
            ROOT / "README.zh-CN.md",
        ]

        required = [
            "CodexProjectionSmoke",
            "CodexApiProjectionRepair",
            "CodexOauthProjectionRepair",
            "CodexLaunchBindingRepair",
            "--apply",
            "--migrate-provider-bucket",
            "SQLite provider trigger",
            "后台 guard",
            "no-op launcher",
            "restart wrapper",
            "自动重启 Codex",
        ]
        for path in paths:
            content = path.read_text(encoding="utf-8")
            for text in required:
                with self.subTest(path=path.name, text=text):
                    self.assertIn(text, content)

    def test_english_readme_keeps_the_same_high_priority_boundary(self) -> None:
        content = (ROOT / "README.en.md").read_text(encoding="utf-8")

        required = [
            "Codex/Cockpit OAuth/API roundtrips",
            "highest-priority local interoperability contract",
            "CodexProjectionSmoke",
            "CodexApiProjectionRepair",
            "CodexOauthProjectionRepair",
            "CodexLaunchBindingRepair",
            "--apply",
            "--migrate-provider-bucket",
            "SQLite provider triggers",
            "background guards",
            "no-op launchers",
            "restart wrappers",
            "automatic Codex restarts",
        ]
        for text in required:
            with self.subTest(text=text):
                self.assertIn(text, content)

    def test_hot_switch_plan_keeps_cockpit_api_service_opt_in(self) -> None:
        plan = (ROOT / "docs" / "plans" / "codex-cli-continuity-and-hot-switch-plan.md").read_text(
            encoding="utf-8"
        )
        index = (ROOT / "docs" / "plans" / "README.md").read_text(encoding="utf-8")

        required_plan_text = [
            "Cockpit Tools local API service is enabled only as an operator-directed LiteLLM upstream mode",
            "Preferred gateway architecture: Cockpit owns ChatGPT/OAuth subscription-account state; LiteLLM owns normal API keys",
            "Plan rebaseline: keep CCHS-001 through CCHS-004 as completed or partial native-boundary groundwork",
            "CCHS-005A through CCHS-005F now provide a live `Codex -> LiteLLM -> Cockpit API service` lane",
            "Rebaseline Cleanup",
            "Do not delete the segmented runner. It remains the fallback when gateway mode is disabled or broken.",
            "Supersede the old single CCHS-005 coarse PoC with CCHS-005A through CCHS-005F",
            "Do not bypass LiteLLM for Codex CLI gateway mode",
            "operator-owned local-access upstream behind LiteLLM",
            "Cockpit API service is not the default proxy",
            "gateway_litellm_with_cockpit_upstream",
            "CCHS-005A LiteLLM Gateway Runtime Baseline",
            "CCHS-005B Cockpit API Upstream Hardening",
            "CCHS-005C LiteLLM Config With Cockpit Upstream",
            "CCHS-005D Codex Profile To LiteLLM Gateway",
            "CCHS-005E Cockpit Current-Account Follow Test",
            "CCHS-005G Cockpit Source Follow-Current Mode",
            "CCHS-005F Closeout, Operator Runbook, And Rollback",
            "CCHS-005H Operator Mode Switch",
            "direct_projection",
            "gateway_litellm",
            "Cockpit materializes the matching Codex App/CLI projection directly",
            "A Cockpit-aware adapter is deferred until account-label, group, quota, or routing semantics are required",
            "model alias `cockpit-current`",
            "Preserve history bucket expectations and do not reintroduce `[model_providers.openai]`",
            "verify listener scope and host firewall posture",
            "Gateway rollback: restore `config.toml` provider/base URL from backup, stop LiteLLM, disable Cockpit API service",
        ]
        for text in required_plan_text:
            with self.subTest(text=text):
                self.assertIn(text, plan)

        self.assertIn("prefer Cockpit follow-current single-account local access", index)
        self.assertIn("use `Codex -> LiteLLM -> Cockpit API service` as the preferred opt-in local profile", index)
        self.assertIn("LiteLLM owns the client-facing gateway", index)
        self.assertIn("Cockpit owns ChatGPT OAuth account switching", index)
        self.assertIn("without listener-scope and firewall evidence", index)


if __name__ == "__main__":
    unittest.main()
