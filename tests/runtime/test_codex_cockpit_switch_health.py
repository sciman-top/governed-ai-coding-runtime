import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "codex-cockpit-switch-health.py"


def load_health_module():
    spec = importlib.util.spec_from_file_location("codex_cockpit_switch_health", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CodexCockpitSwitchHealthTests(unittest.TestCase):
    def test_evaluate_reports_selected_scope_without_secret_values(self):
        health = load_health_module()
        with tempfile.TemporaryDirectory() as tmp:
            cockpit_home = Path(tmp)
            (cockpit_home / "logs").mkdir()
            (cockpit_home / "config.json").write_text(
                json.dumps(
                    {
                        "currentAccountId": "acct_free_001",
                        "codex_auto_switch_enabled": True,
                        "codex_auto_switch_strategy": "free",
                        "codex_auto_switch_free_only": True,
                        "codex_auto_refresh_minutes": 15,
                        "codex_auto_switch_threshold_total_percent": 100,
                        "codex_auto_switch_threshold_model_percent": 90,
                        "codex_auto_switch_selected_account_ids": ["acct_free_001", "acct_free_002"],
                        "codex_launch_on_switch": False,
                        "codex_restart_specified_app_on_switch": False,
                        "codex_app_path": "",
                        "codex_specified_app_path": "",
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps(
                    {
                        "currentAccountId": "acct_free_001",
                        "accounts": [
                            {
                                "id": "acct_free_001",
                                "plan_type": "free",
                                "private_note": "contact-should-not-print",
                                "opaque_credential": "credential-should-not-print",
                            },
                            {"id": "acct_free_002", "plan_type": "free"},
                            {"id": "acct_plus_001", "plan_type": "plus"},
                        ],
                    }
                ),
                encoding="utf-8",
            )

            report = health.evaluate(cockpit_home, "codex_app")

        self.assertEqual(report["auto_switch"]["codex_auto_refresh_minutes"], 15)
        self.assertEqual(report["auto_switch"]["codex_auto_switch_selected_count"], 2)
        self.assertEqual(report["selected_scope"]["selected_found_count"], 2)
        self.assertEqual(report["selected_scope"]["selected_missing_count"], 0)
        self.assertEqual(report["selected_scope"]["selected_plan_types"], ["free"])
        self.assertTrue(report["runtime_boundary"]["codex_app_restart_required_for_account_change"])
        self.assertIn("codex_app_requires_restart_or_native_hot_reload_for_account_change", report["warnings"])

        serialized = json.dumps(report, ensure_ascii=False)
        self.assertNotIn("contact-should-not-print", serialized)
        self.assertNotIn("credential-should-not-print", serialized)

    def test_evaluate_surfaces_missing_selection_and_recent_401(self):
        health = load_health_module()
        with tempfile.TemporaryDirectory() as tmp:
            cockpit_home = Path(tmp)
            (cockpit_home / "logs").mkdir()
            (cockpit_home / "config.json").write_text(
                json.dumps(
                    {
                        "codex_auto_switch_enabled": True,
                        "codex_auto_switch_selected_account_ids": ["acct_missing"],
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps({"accounts": [{"id": "acct_free_001", "planType": "free"}]}),
                encoding="utf-8",
            )
            (cockpit_home / "logs" / "app.log").write_text(
                "Codex quota API failed: 401 Unauthorized token_invalidated\n",
                encoding="utf-8",
            )

            report = health.evaluate(cockpit_home, "codex_cli")

        self.assertEqual(report["selected_scope"]["selected_found_count"], 0)
        self.assertEqual(report["selected_scope"]["selected_missing_count"], 1)
        self.assertEqual(report["recent_auth_errors"]["token_invalidated_count"], 1)
        self.assertIn("selected_accounts_missing", report["warnings"])
        self.assertIn("recent_token_invalidated_or_401_seen", report["warnings"])
        self.assertFalse(report["runtime_boundary"]["codex_app_restart_required_for_account_change"])
        self.assertTrue(report["runtime_boundary"]["codex_cli_new_process_reads_projected_auth"])


if __name__ == "__main__":
    unittest.main()
