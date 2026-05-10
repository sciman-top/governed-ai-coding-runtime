import importlib.util
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "codex-cockpit-switch-trace.py"


def load_trace_module():
    spec = importlib.util.spec_from_file_location("codex_cockpit_switch_trace", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CodexCockpitSwitchTraceTests(unittest.TestCase):
    def test_snapshot_summarizes_switch_state_without_secret_values(self):
        trace = load_trace_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / ".codex"
            cockpit_home = root / ".antigravity_cockpit"
            (cockpit_home / "codex_accounts").mkdir(parents=True)
            codex_home.mkdir()

            (cockpit_home / "config.json").write_text(
                json.dumps(
                    {
                        "codex_launch_on_switch": True,
                        "codex_restart_specified_app_on_switch": True,
                        "codex_specified_app_path": "C:/tmp/codex.cmd",
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps({"currentAccountId": "codex_apikey_test"}),
                encoding="utf-8",
            )
            (cockpit_home / "codex_accounts" / "codex_apikey_test.json").write_text(
                json.dumps(
                    {
                        "id": "codex_apikey_test",
                        "mode": "api",
                        "OPENAI_API_KEY": "sk-should-not-leak",
                        "base_url": "http://35.213.82.91:8003/v1",
                    }
                ),
                encoding="utf-8",
            )
            (cockpit_home / "codex_instances.json").write_text(
                json.dumps({"defaultSettings": {"bindAccountId": "codex_apikey_test", "followLocalAccount": False}}),
                encoding="utf-8",
            )
            (cockpit_home / "codex_model_providers.json").write_text(
                json.dumps({"openai": {"name": "openai", "base_url": "https://api.openai.com/v1"}}),
                encoding="utf-8",
            )
            (codex_home / "config.toml").write_text(
                'forced_login_method = "api"\nmodel_provider = "openai"\n[model_providers.openai]\nbase_url = "http://35.213.82.91:8003/v1"\n',
                encoding="utf-8",
            )
            (codex_home / "auth.json").write_text(
                json.dumps(
                    {
                        "auth_mode": "apikey",
                        "OPENAI_API_KEY": "sk-also-should-not-leak",
                        "base_url": "http://35.213.82.91:8003/v1",
                    }
                ),
                encoding="utf-8",
            )

            with closing(sqlite3.connect(codex_home / "state_5.sqlite")) as conn:
                conn.execute("create table threads (id text primary key, model_provider text, cwd text)")
                conn.execute("insert into threads values ('a', 'openai', 'D:/CODE/governed-ai-coding-runtime')")
                conn.execute("insert into threads values ('b', 'openai', 'D:/CODE/k12-question-graph')")
                conn.commit()

            report = trace.snapshot(codex_home, cockpit_home)
            self.assertEqual(report["cockpit"]["current_account_id"], "codex_apikey_test")
            self.assertTrue(report["cockpit"]["launch_flags"]["codex_launch_on_switch"])
            self.assertEqual(report["codex"]["config"]["forced_login_method"], "api")
            self.assertTrue(report["codex"]["auth"]["has_openai_api_key"])
            self.assertEqual(report["codex"]["state_db"]["threads_by_model_provider"][0]["model_provider"], "openai")

            serialized = json.dumps(report, ensure_ascii=False)
            self.assertNotIn("sk-should-not-leak", serialized)
            self.assertNotIn("sk-also-should-not-leak", serialized)

    def test_compare_reports_surfaces_semantic_switch_changes(self):
        trace = load_trace_module()
        before = {
            "label": "before-restart",
            "after": {
                "timestamp": "2026-05-10T23:50:00",
                "files": {
                    "codex_auth": {"sha256": "aaa", "mtime_iso": "2026-05-10T23:50:00"},
                },
                "cockpit": {
                    "current_account_id": "codex_oauth",
                    "launch_flags": {"codex_launch_on_switch": False},
                    "default_instance": {"bindAccountId": None, "followLocalAccount": True},
                },
                "codex": {
                    "config": {
                        "model_provider": "openai",
                        "forced_login_method": "chatgpt",
                        "openai_base_url": "https://api.openai.com/v1",
                    },
                    "auth": {"auth_mode": "chatgpt", "has_openai_api_key": False, "has_tokens": True},
                    "state_db": {"threads_by_model_provider": [{"model_provider": "openai", "count": 10}]},
                },
            },
        }
        after = {
            "label": "api-reconnecting",
            "after": {
                "timestamp": "2026-05-10T23:55:00",
                "files": {
                    "codex_auth": {"sha256": "bbb", "mtime_iso": "2026-05-10T23:55:00"},
                },
                "cockpit": {
                    "current_account_id": "codex_api",
                    "launch_flags": {"codex_launch_on_switch": True},
                    "default_instance": {"bindAccountId": "codex_api", "followLocalAccount": False},
                },
                "codex": {
                    "config": {
                        "model_provider": "openai",
                        "forced_login_method": "api",
                        "openai_base_url": "http://35.213.82.91:8003/v1",
                    },
                    "auth": {"auth_mode": "apikey", "has_openai_api_key": True, "has_tokens": False},
                    "state_db": {"threads_by_model_provider": [{"model_provider": "openai", "count": 10}]},
                },
            },
        }

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            before_path = root / "before.json"
            after_path = root / "after.json"
            before_path.write_text(json.dumps(before), encoding="utf-8")
            after_path.write_text(json.dumps(after), encoding="utf-8")

            comparison = trace.compare_reports([before_path, after_path])

        fields = {item["field"]: item for item in comparison["transitions"][0]["field_changes"]}
        self.assertEqual(fields["cockpit.current_account_id"]["after"], "codex_api")
        self.assertEqual(fields["cockpit.codex_launch_on_switch"]["after"], True)
        self.assertEqual(fields["codex.config.forced_login_method"]["after"], "api")
        self.assertEqual(fields["codex.config.openai_base_url"]["after"], "http://35.213.82.91:8003/v1")
        self.assertEqual(comparison["transitions"][0]["file_changes"][0]["file"], "codex_auth")


if __name__ == "__main__":
    unittest.main()
