import importlib.util
import json
import subprocess
import sys
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


class CodexCockpitCliPreflightRepairTests(unittest.TestCase):
    def test_cli_fails_closed_as_deprecated(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(2, completed.returncode)
        payload = json.loads(completed.stdout)
        self.assertEqual("deprecated", payload["status"])
        self.assertEqual("codex_cockpit_cli_preflight_repair_deprecated", payload["actions"][0]["id"])
        self.assertIn("deprecated", completed.stderr)

    def test_print_env_does_not_emit_openai_api_key(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--print-env"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(2, completed.returncode)
        self.assertEqual("", completed.stdout)
        self.assertNotIn("OPENAI_API_KEY", completed.stdout)

    def test_repair_api_is_no_write_compatibility_shim(self) -> None:
        module = _load_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_home = root / "codex"
            cockpit_home = root / "cockpit"
            codex_home.mkdir()
            cockpit_home.mkdir()
            config_path = codex_home / "config.toml"
            auth_path = codex_home / "auth.json"
            config_path.write_text('forced_login_method = "chatgpt"\nmodel_provider = "openai"\n', encoding="utf-8")
            auth_path.write_text('{"tokens":{"access_token":"test"}}\n', encoding="utf-8")
            before_config = config_path.read_text(encoding="utf-8")
            before_auth = auth_path.read_text(encoding="utf-8")

            changes = module.repair(codex_home, cockpit_home, dry_run=False)

            self.assertEqual([], changes)
            self.assertEqual({}, module.wrapper_environment(codex_home))
            self.assertEqual(before_config, config_path.read_text(encoding="utf-8"))
            self.assertEqual(before_auth, auth_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
