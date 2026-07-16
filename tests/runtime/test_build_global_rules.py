import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "build-global-rules.py"
SPEC = importlib.util.spec_from_file_location("build_global_rules_script", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"unable to load {SCRIPT}")
build_global_rules = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build_global_rules)


class BuildGlobalRulesTests(unittest.TestCase):
    def test_committed_outputs_match_canonical_sources(self) -> None:
        result = build_global_rules.build(
            root=ROOT,
            manifest_path=ROOT / "rules" / "global" / "source-manifest.json",
            write=False,
        )

        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["changed_count"], 0)
        self.assertEqual(
            {item["output"] for item in result["results"]},
            {"rules/global/codex/AGENTS.md", "rules/global/claude/CLAUDE.md"},
        )

    def test_write_is_atomic_and_check_detects_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "sources").mkdir()
            (root / "sources" / "shared.md").write_text(
                "## 1. Shared\n\n{{PLATFORM_SECTION}}\n", encoding="utf-8"
            )
            (root / "sources" / "preamble.md").write_text("# Rule\n", encoding="utf-8")
            (root / "sources" / "platform.md").write_text(
                "## B. Platform\n- fact\n", encoding="utf-8"
            )
            manifest = {
                "placeholder": "{{PLATFORM_SECTION}}",
                "shared": "sources/shared.md",
                "outputs": [
                    {
                        "id": "rule",
                        "preamble": "sources/preamble.md",
                        "platform": "sources/platform.md",
                        "output": "generated/RULE.md",
                    }
                ],
            }
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

            drift = build_global_rules.build(root=root, manifest_path=manifest_path, write=False)
            applied = build_global_rules.build(root=root, manifest_path=manifest_path, write=True)
            output_path = root / "generated" / "RULE.md"
            output_path.write_bytes(output_path.read_text(encoding="utf-8").replace("\n", "\r\n").encode("utf-8"))
            current = build_global_rules.build(root=root, manifest_path=manifest_path, write=False)

        self.assertEqual(drift["status"], "fail")
        self.assertEqual(applied["status"], "applied")
        self.assertEqual(current["status"], "pass")
        self.assertEqual(current["results"][0]["status"], "current")

    def test_manifest_rejects_paths_outside_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            manifest = {
                "placeholder": "{{PLATFORM_SECTION}}",
                "shared": "../shared.md",
                "outputs": [],
            }

            with self.assertRaisesRegex(ValueError, "repo-relative path required"):
                build_global_rules.render_outputs(root=root, manifest=manifest)


if __name__ == "__main__":
    unittest.main()
