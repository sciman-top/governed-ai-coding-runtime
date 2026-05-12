import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "codex-cockpit-cli-preflight-repair.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("codex_cockpit_cli_preflight_repair", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _top_level_value(config: str, key: str) -> str | None:
    top = config.split("\n[", 1)[0]
    prefix = f'{key} = "'
    for line in top.splitlines():
        if line.startswith(prefix) and line.endswith('"'):
            return line[len(prefix) : -1]
    return None


class CodexCockpitCliPreflightRepairTests(unittest.TestCase):
    def test_api_account_projects_custom_provider_and_history_bucket(self) -> None:
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / "codex"
            cockpit_home = root / "cockpit"
            api_account_id = "codex_apikey_test"
            provider_id = "cmp_test_1"

            _write_json(
                cockpit_home / "codex_accounts.json",
                {
                    "version": "1.0",
                    "accounts": [{"id": api_account_id, "email": "api-key-test"}],
                    "current_account_id": api_account_id,
                },
            )
            _write_json(
                cockpit_home / "codex_accounts" / f"{api_account_id}.json",
                {
                    "id": api_account_id,
                    "auth_mode": "apikey",
                    "openai_api_key": "sk-test-not-real",
                    "api_base_url": "http://127.0.0.1:18080/v1",
                    "api_provider_mode": "custom",
                    "api_provider_id": provider_id,
                    "api_provider_name": "Local Relay",
                },
            )
            _write_json(
                cockpit_home / "codex_model_providers.json",
                [
                    {
                        "id": provider_id,
                        "name": "Local Relay",
                        "baseUrl": "http://127.0.0.1:18080/v1",
                    }
                ],
            )
            _write_json(
                cockpit_home / "codex_instances.json",
                {
                    "instances": [],
                    "defaultSettings": {
                        "bindAccountId": api_account_id,
                        "extraArgs": "",
                        "workingDir": None,
                        "launchMode": "app",
                        "followLocalAccount": False,
                        "lastPid": None,
                    },
                },
            )
            codex_home.mkdir(parents=True)
            (codex_home / "config.toml").write_text(
                'forced_login_method = "chatgpt"\nmodel_provider = "openai"\n',
                encoding="utf-8",
            )
            connection = sqlite3.connect(codex_home / "state_5.sqlite")
            try:
                connection.execute("CREATE TABLE threads (id TEXT PRIMARY KEY, model_provider TEXT NOT NULL)")
                connection.executemany(
                    "INSERT INTO threads (id, model_provider) VALUES (?, ?)",
                    [("thread-1", "openai"), ("thread-2", "codex_local_access")],
                )
                connection.commit()
            finally:
                connection.close()

            changes = module.repair(codex_home, cockpit_home, dry_run=False)

            self.assertIn("auth.json", changes)
            self.assertIn("config.toml", changes)
            self.assertIn("state_5.sqlite:2", changes)
            config = (codex_home / "config.toml").read_text(encoding="utf-8")
            self.assertEqual(_top_level_value(config, "forced_login_method"), "api")
            self.assertEqual(_top_level_value(config, "model_provider"), provider_id)
            self.assertIsNone(_top_level_value(config, "openai_base_url"))
            self.assertNotIn("[model_providers.openai]", config)
            self.assertIn(f"[model_providers.{provider_id}]", config)
            self.assertIn("requires_openai_auth = true", config)
            self.assertIn("supports_websockets = false", config)
            self.assertNotIn("env_key", config)

            auth = json.loads((codex_home / "auth.json").read_text(encoding="utf-8"))
            self.assertEqual(auth.get("auth_mode"), "apikey")
            self.assertTrue(auth.get("OPENAI_API_KEY"))
            self.assertEqual(auth.get("api_base_url"), "http://127.0.0.1:18080/v1")
            self.assertEqual(auth.get("base_url"), "http://127.0.0.1:18080/v1")
            self.assertEqual(auth.get("OPENAI_BASE_URL"), "http://127.0.0.1:18080/v1")

            instances = json.loads((cockpit_home / "codex_instances.json").read_text(encoding="utf-8"))
            settings = instances["defaultSettings"]
            self.assertIsNone(settings["bindAccountId"])
            self.assertIs(settings["followLocalAccount"], True)

            connection = sqlite3.connect(codex_home / "state_5.sqlite")
            try:
                buckets = connection.execute(
                    "SELECT model_provider, COUNT(*) FROM threads GROUP BY model_provider"
                ).fetchall()
            finally:
                connection.close()
            self.assertEqual(buckets, [(provider_id, 2)])


if __name__ == "__main__":
    unittest.main()
