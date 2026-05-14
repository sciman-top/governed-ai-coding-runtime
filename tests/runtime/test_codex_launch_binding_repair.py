from __future__ import annotations

import importlib.util
import json
import sqlite3
import tempfile
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "codex-interop-check.py"


def load_interop_module():
    spec = importlib.util.spec_from_file_location("codex_interop_check", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CodexLaunchBindingRepairTests(unittest.TestCase):
    def test_backup_file_does_not_overwrite_same_second_backup(self) -> None:
        interop = load_interop_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = Path(tmp_dir) / "config.toml"
            path.write_text("first\n", encoding="utf-8")

            first = interop._backup_file(path, suffix="unit")
            path.write_text("second\n", encoding="utf-8")
            second = interop._backup_file(path, suffix="unit")

            self.assertNotEqual(first, second)
            self.assertEqual("first\n", first.read_text(encoding="utf-8"))
            self.assertEqual("second\n", second.read_text(encoding="utf-8"))

    def test_repairs_default_launch_binding_without_touching_codex_auth_or_history(self) -> None:
        interop = load_interop_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            cockpit_home = root / ".antigravity_cockpit"
            codex_home = root / ".codex"
            cockpit_home.mkdir()
            codex_home.mkdir()
            instances_path = cockpit_home / "codex_instances.json"
            auth_path = codex_home / "auth.json"
            state_path = codex_home / "state_5.sqlite"
            auth_path.write_text('{"auth_mode":"chatgpt"}\n', encoding="utf-8")
            state_path.write_bytes(b"sqlite-placeholder")
            instances_path.write_text(
                json.dumps(
                    {
                        "instances": [],
                        "defaultSettings": {
                            "followLocalAccount": False,
                            "bindAccountId": "codex_old_oauth",
                            "launchMode": "app",
                            "lastPid": None,
                        },
                    },
                    ensure_ascii=False,
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )

            action = interop.repair_cockpit_instance_follow_current(cockpit_home=cockpit_home)

            self.assertEqual("changed", action["status"])
            self.assertTrue(Path(action["backup_path"]).exists())
            repaired = json.loads(instances_path.read_text(encoding="utf-8"))
            self.assertTrue(repaired["defaultSettings"]["followLocalAccount"])
            self.assertIsNone(repaired["defaultSettings"]["bindAccountId"])
            self.assertEqual('{"auth_mode":"chatgpt"}\n', auth_path.read_text(encoding="utf-8"))
            self.assertEqual(b"sqlite-placeholder", state_path.read_bytes())

    def test_explicit_oauth_projection_does_not_use_deprecated_generic_cli_flag(self) -> None:
        interop = load_interop_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            cockpit_home = root / ".antigravity_cockpit"
            codex_home = root / ".codex"
            account_dir = cockpit_home / "codex_accounts"
            account_dir.mkdir(parents=True)
            codex_home.mkdir()
            account_id = "codex_oauth"
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps(
                    {
                        "version": "1.0",
                        "current_account_id": account_id,
                        "accounts": [{"id": account_id, "email": "user@example.test"}],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (account_dir / f"{account_id}.json").write_text(
                json.dumps(
                    {
                        "id": account_id,
                        "email": "user@example.test",
                        "auth_mode": "oauth",
                        "tokens": {"access_token": "token"},
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (codex_home / "config.toml").write_text(
                'model_provider = "cmp_1778165666417_1"\nforced_login_method = "api"\n',
                encoding="utf-8",
            )
            (codex_home / "auth.json").write_text('{"auth_mode":"apikey"}\n', encoding="utf-8")

            action = interop.repair_current_cockpit_oauth_projection(
                codex_home=codex_home,
                cockpit_home=cockpit_home,
            )

            self.assertEqual("repair_current_cockpit_oauth_projection", action["id"])
            self.assertEqual("changed", action["status"])
            self.assertEqual("oauth", action["explicit_repair"])
            auth = json.loads((codex_home / "auth.json").read_text(encoding="utf-8"))
            config = (codex_home / "config.toml").read_text(encoding="utf-8")
            self.assertEqual("chatgpt", auth["auth_mode"])
            self.assertIn('model_provider = "openai"', config)
            self.assertIn('forced_login_method = "chatgpt"', config)
            backup_paths = [item["backup_path"] for item in action["backups"]]
            self.assertTrue(any("cockpit-oauth-projection" in path for path in backup_paths))

    def test_projection_rebuilds_malformed_toml_into_parseable_config(self) -> None:
        interop = load_interop_module()
        malformed = 'model_provider = "broken\n[model_providers.openai]\nbase_url = "bad"\n'

        repaired = interop._project_cockpit_chatgpt_config(
            malformed,
            api_profiles=[
                {
                    "provider_id": "cmp_relay",
                    "provider_name": "relay",
                    "base_url": "http://127.0.0.1:8003/v1",
                }
            ],
        )

        parsed = tomllib.loads(repaired)
        self.assertEqual("openai", parsed["model_provider"])
        self.assertEqual("chatgpt", parsed["forced_login_method"])
        self.assertIn("Existing config.toml was malformed", repaired)
        self.assertEqual(
            "http://127.0.0.1:8003/v1",
            parsed["model_providers"]["cmp_relay"]["base_url"],
        )
        self.assertFalse(parsed["model_providers"]["cmp_relay"]["requires_openai_auth"])
        self.assertFalse(parsed["model_providers"]["cmp_relay"]["supports_websockets"])

    def test_history_visibility_repair_strategy_points_to_explicit_projection(self) -> None:
        interop = load_interop_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            state_path = Path(tmp_dir) / "state_5.sqlite"

            connection = sqlite3.connect(state_path)
            try:
                connection.execute(
                    """
                    create table threads(
                      id text primary key,
                      archived integer,
                      model_provider text,
                      first_user_message text,
                      has_user_event integer,
                      thread_source text
                    )
                    """
                )
                connection.execute(
                    """
                    insert into threads(id, archived, model_provider, first_user_message, has_user_event, thread_source)
                    values('thread-1', 0, 'openai', 'hello', 0, null)
                    """
                )
                connection.execute(
                    """
                    insert into threads(id, archived, model_provider, first_user_message, has_user_event, thread_source)
                    values('thread-2', 0, 'cmp_relay', 'hello', 0, null)
                    """
                )
                connection.commit()
            finally:
                connection.close()

            oauth = interop._inspect_codex_history_visibility_metadata(
                state_path,
                expected_provider="openai",
            )
            api = interop._inspect_codex_history_visibility_metadata(
                state_path,
                expected_provider="cmp_relay",
            )

            self.assertEqual("fail", oauth["status"])
            self.assertEqual("repair_current_cockpit_oauth_projection", oauth["repair_strategy"])
            self.assertEqual("fail", api["status"])
            self.assertEqual("repair_current_cockpit_api_projection", api["repair_strategy"])

    def test_explicit_api_projection_repairs_follow_current_and_custom_provider_bucket(self) -> None:
        interop = load_interop_module()
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            cockpit_home = root / ".antigravity_cockpit"
            codex_home = root / ".codex"
            account_dir = cockpit_home / "codex_accounts"
            account_dir.mkdir(parents=True)
            codex_home.mkdir()
            account_id = "codex_api"
            provider_id = "cmp_provider"
            (cockpit_home / "codex_accounts.json").write_text(
                json.dumps(
                    {
                        "version": "1.0",
                        "current_account_id": account_id,
                        "accounts": [{"id": account_id, "email": "api@example.test"}],
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (account_dir / f"{account_id}.json").write_text(
                json.dumps(
                    {
                        "id": account_id,
                        "email": "api@example.test",
                        "auth_mode": "apikey",
                        "openai_api_key": "sk-test",
                        "api_provider_id": provider_id,
                        "api_provider_name": "relay",
                        "api_base_url": "http://127.0.0.1:8003/v1",
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (cockpit_home / "codex_instances.json").write_text(
                json.dumps(
                    {
                        "instances": [],
                        "defaultSettings": {
                            "followLocalAccount": False,
                            "bindAccountId": "old",
                            "launchMode": "app",
                        },
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            (codex_home / "config.toml").write_text(
                'model_provider = "openai"\nforced_login_method = "chatgpt"\n',
                encoding="utf-8",
            )
            (codex_home / "auth.json").write_text('{"auth_mode":"chatgpt"}\n', encoding="utf-8")

            action = interop.repair_current_cockpit_api_projection(
                codex_home=codex_home,
                cockpit_home=cockpit_home,
            )

            self.assertEqual("repair_current_cockpit_api_projection", action["id"])
            self.assertEqual("changed", action["status"])
            self.assertTrue(action["cockpit_instance_binding_changed"])
            self.assertEqual(provider_id, action["provider_id"])
            auth = json.loads((codex_home / "auth.json").read_text(encoding="utf-8"))
            instances = json.loads((cockpit_home / "codex_instances.json").read_text(encoding="utf-8"))
            config = (codex_home / "config.toml").read_text(encoding="utf-8")
            self.assertEqual("apikey", auth["auth_mode"])
            self.assertEqual(provider_id, auth["api_provider_id"])
            self.assertIn(f'model_provider = "{provider_id}"', config)
            self.assertIn('forced_login_method = "api"', config)
            self.assertTrue(instances["defaultSettings"]["followLocalAccount"])
            self.assertIsNone(instances["defaultSettings"]["bindAccountId"])


if __name__ == "__main__":
    unittest.main()
