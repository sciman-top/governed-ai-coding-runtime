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
            "Cockpit Tools automatic switching, Codex batch quota refresh, and Cockpit Codex API service stay disabled by default",
            "Do not treat Cockpit Tools' Codex API service at `127.0.0.1:2876/v1` as the default proxy implementation",
            "Cockpit API service is not the default proxy",
            "verify listener scope and host firewall posture",
        ]
        for text in required_plan_text:
            with self.subTest(text=text):
                self.assertIn(text, plan)

        self.assertIn("treat Cockpit's `127.0.0.1:2876/v1` Codex API service as the default proxy", index)
        self.assertIn("without listener-scope and firewall evidence", index)


if __name__ == "__main__":
    unittest.main()
