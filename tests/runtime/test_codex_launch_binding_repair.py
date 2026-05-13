from __future__ import annotations

import importlib.util
import json
import tempfile
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


if __name__ == "__main__":
    unittest.main()
