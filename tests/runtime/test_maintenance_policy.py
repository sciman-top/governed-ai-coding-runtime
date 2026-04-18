import sys
import tempfile
import unittest
from pathlib import Path
import importlib

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))


class MaintenancePolicyTests(unittest.TestCase):
    def test_load_maintenance_policy_status_reports_missing_docs(self) -> None:
        maintenance_policy = importlib.import_module("governed_ai_coding_runtime_contracts.maintenance_policy")

        with tempfile.TemporaryDirectory() as tmp_dir:
            status = maintenance_policy.load_maintenance_policy_status(Path(tmp_dir))

            self.assertEqual(status.stage, "missing")
            self.assertIsNone(status.compatibility_policy_ref)
            self.assertIsNone(status.retirement_policy_ref)

    def test_load_maintenance_policy_status_reports_completed_surface(self) -> None:
        maintenance_policy = importlib.import_module("governed_ai_coding_runtime_contracts.maintenance_policy")

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            docs_product = repo_root / "docs" / "product"
            docs_product.mkdir(parents=True, exist_ok=True)
            (docs_product / "runtime-compatibility-and-upgrade-policy.md").write_text("# policy\n", encoding="utf-8")
            (docs_product / "maintenance-deprecation-and-retirement-policy.md").write_text("# policy\n", encoding="utf-8")

            status = maintenance_policy.load_maintenance_policy_status(repo_root)

            self.assertEqual(status.stage, "completed")
            self.assertEqual(
                status.upgrade_policy_ref,
                "docs/product/runtime-compatibility-and-upgrade-policy.md",
            )
            self.assertEqual(
                status.triage_policy_ref,
                "docs/product/maintenance-deprecation-and-retirement-policy.md",
            )


if __name__ == "__main__":
    unittest.main()
