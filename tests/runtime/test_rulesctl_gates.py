import importlib.util
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "rulesctl.py"
SPEC = importlib.util.spec_from_file_location("rulesctl_script", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"unable to load {SCRIPT}")
rulesctl = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rulesctl)


class RulesCtlGateTests(unittest.TestCase):
    def test_build_gate_checks_only_retained_rule_toolchain(self) -> None:
        result = rulesctl.build_gate()

        self.assertEqual(result["status"], "pass", result)
        checked_paths = {item["path"] for item in result["checks"]}
        self.assertIn("scripts/rulesctl.py", checked_paths)
        self.assertIn("rules/manifest.json", checked_paths)
        self.assertNotIn("scripts/run-governed-task.py", checked_paths)

    def test_product_boundary_rejects_runtime_gemini_and_ui_paths(self) -> None:
        findings = rulesctl.product_boundary_findings(
            [
                "README.md",
                "rules/global/codex/AGENTS.md",
                "apps/operator-api/main.py",
                "rules/global/gemini/GEMINI.md",
                "operator-ui-current-runtime.png",
            ]
        )

        self.assertEqual(
            findings,
            [
                "apps/operator-api/main.py",
                "operator-ui-current-runtime.png",
                "rules/global/gemini/GEMINI.md",
            ],
        )

    def test_verify_runs_fixed_order_and_stops_after_failure(self) -> None:
        calls: list[str] = []

        def result(name: str, status: str = "pass") -> dict:
            calls.append(name)
            return {"status": status, "gate": name, "checks": []}

        args = mock.Mock()
        with (
            mock.patch.object(rulesctl, "build_gate", side_effect=lambda: result("build")),
            mock.patch.object(rulesctl, "test_gate", side_effect=lambda: result("test")),
            mock.patch.object(
                rulesctl,
                "_contract_gate_from_args",
                side_effect=lambda unused: result("contract", "fail"),
            ),
            mock.patch.object(rulesctl, "hotspot_gate", side_effect=lambda: result("hotspot")),
        ):
            verified = rulesctl.verify_gates(args)

        self.assertEqual(calls, ["build", "test", "contract"])
        self.assertEqual(verified["status"], "fail")
        self.assertEqual(verified["stopped_after"], "contract")

    def test_parser_exposes_complete_rule_governance_surface(self) -> None:
        parser = rulesctl.build_parser()

        for command in (
            "status",
            "build",
            "test",
            "contract",
            "hotspot",
            "verify",
            "audit",
            "sync",
            "matrix",
        ):
            parsed = parser.parse_args([command])
            self.assertEqual(parsed.command, command)

    def test_json_adapter_marks_successful_domain_payload_as_pass(self) -> None:
        with mock.patch.object(
            rulesctl,
            "_run_process",
            return_value={
                "status": "pass",
                "exit_code": 0,
                "command": [],
                "stdout": '{"include":[]}',
                "stderr": "",
            },
        ):
            payload = rulesctl._run_json_script("matrix.py", [])

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["include"], [])


if __name__ == "__main__":
    unittest.main()
