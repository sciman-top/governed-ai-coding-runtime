from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]


class CodexCockpitPolicyContractTests(unittest.TestCase):
    def test_project_rules_make_cockpit_the_only_switch_owner(self) -> None:
        agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")

        required = [
            "Direct OAuth、Direct API 和 Cockpit API service 往返切换由 Cockpit Tools 完全负责",
            "不得提供 8770 页面动作",
            "repair/smoke/checker",
            "LiteLLM gateway 管理",
            "history bucket 写入",
            "Disable-CodexProjectInterop.ps1",
            "Test-CodexGuardAbsence.ps1",
            "不得写入当前 Codex auth/provider/history/Cockpit account state",
            "禁止恢复 `codex-interop-check.py`",
            "禁止恢复 `codex-interop-check.py`、`CodexProjectionSmoke`",
            "Manage-LiteLLMGateway.ps1",
            "codex-cockpit-switch-guard.py",
            "generic `--apply`",
            "--migrate-provider-bucket",
            "SQLite provider trigger",
            "后台 guard",
            "no-op launcher",
            "restart wrapper",
            "自动重启 Codex",
        ]
        for text in required:
            with self.subTest(text=text):
                self.assertIn(text, agents)

    def test_current_docs_state_the_same_retired_boundary(self) -> None:
        paths = [
            ROOT / "README.md",
            ROOT / "README.zh-CN.md",
            ROOT / "README.en.md",
        ]

        required = [
            "Cockpit Tools",
            "Disable-CodexProjectInterop.ps1",
            "Test-CodexGuardAbsence.ps1",
            "CodexProjectionSmoke",
            "CodexApiProjectionRepair",
            "CodexOauthProjectionRepair",
            "CodexLaunchBindingRepair",
            "Manage-LiteLLMGateway.ps1",
            "codex-mode-*",
            "--migrate-provider-bucket",
            "SQLite provider trigger",
            "no-op launcher",
            "restart wrapper",
        ]
        forbidden = [
            "python scripts\\codex-interop-check.py",
            ".\\run.ps1 codex-mode-new",
            "scripts\\Manage-LiteLLMGateway.ps1 -Action",
            "scripts\\Save-CodexCockpitSwitchRecord.ps1",
            "scripts\\Compare-CodexCockpitSwitchRecords.ps1",
            "codex-cockpit-switch-trace.py --watch-seconds",
            "Repair API projection",
            "Codex/Cockpit API Provider Repair",
            "LiteLLM / Cockpit Gateway",
        ]
        for path in paths:
            content = path.read_text(encoding="utf-8")
            for text in required:
                with self.subTest(path=path.name, text=text):
                    self.assertIn(text, content)
            for text in forbidden:
                with self.subTest(path=path.name, forbidden=text):
                    self.assertNotIn(text, content)

    def test_retired_runbooks_and_scripts_are_removed(self) -> None:
        removed_paths = [
            ROOT / "scripts" / "codex-interop-check.py",
            ROOT / "scripts" / "codex-cockpit-switch-guard.py",
            ROOT / "scripts" / "codex-cockpit-cli-preflight-repair.py",
            ROOT / "scripts" / "Install-CodexCockpitNoopLauncher.ps1",
            ROOT / "scripts" / "Manage-LiteLLMGateway.ps1",
            ROOT / "scripts" / "Save-CodexCockpitSwitchRecord.ps1",
            ROOT / "scripts" / "Compare-CodexCockpitSwitchRecords.ps1",
            ROOT / "scripts" / "codex-cockpit-switch-trace.py",
            ROOT / "scripts" / "codex-cockpit-switch-health.py",
            ROOT / "docs" / "runbooks" / "codex-cockpit-api-provider-repair.md",
            ROOT / "docs" / "runbooks" / "litellm-cockpit-gateway.md",
        ]
        for path in removed_paths:
            with self.subTest(path=path.relative_to(ROOT).as_posix()):
                self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
