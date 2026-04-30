import datetime as dt
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _load_functional_effectiveness_script():
    script_path = ROOT / "scripts" / "verify-functional-effectiveness.py"
    spec = importlib.util.spec_from_file_location("verify_functional_effectiveness_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["verify_functional_effectiveness_script"] = module
    spec.loader.exec_module(module)
    return module


class FunctionalEffectivenessTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("verify_functional_effectiveness_script", None)

    def test_functional_effectiveness_succeeds_for_repo_evidence(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/verify-functional-effectiveness.py", "--as-of", "2026-04-27"],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["evidence_path"].endswith("20260427-autonomous-functional-verification.md"))
        self.assertEqual(payload["evidence_age_days"], 0)

    def test_functional_effectiveness_rejects_missing_effect_token(self) -> None:
        module = _load_functional_effectiveness_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            evidence_path = self._write_complete_evidence(repo_root)
            text = evidence_path.read_text(encoding="utf-8").replace("live_closure_ready", "not_ready")
            evidence_path.write_text(text, encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "attached_write_closure"):
                module.assert_functional_effectiveness(
                    repo_root=repo_root,
                    evidence_path=evidence_path,
                    as_of=dt.date(2026, 4, 27),
                )

    def test_functional_effectiveness_rejects_missing_claude_parity_evidence(self) -> None:
        module = _load_functional_effectiveness_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            evidence_path = self._write_complete_evidence(repo_root)
            text = evidence_path.read_text(encoding="utf-8").replace(
                "claude-code-native-attach-tier-parity.md",
                "missing-claude-parity.md",
            )
            evidence_path.write_text(text, encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "trial_and_adapter_surfaces"):
                module.assert_functional_effectiveness(
                    repo_root=repo_root,
                    evidence_path=evidence_path,
                    as_of=dt.date(2026, 4, 27),
                )

    def test_functional_effectiveness_rejects_stale_evidence(self) -> None:
        module = _load_functional_effectiveness_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            evidence_path = self._write_complete_evidence(repo_root, name="20250101-functional-verification.md")

            with self.assertRaisesRegex(ValueError, "stale"):
                module.assert_functional_effectiveness(
                    repo_root=repo_root,
                    evidence_path=evidence_path,
                    max_age_days=30,
                    as_of=dt.date(2026, 4, 27),
                )

    def test_verify_repo_contract_runs_functional_effectiveness_gate(self) -> None:
        completed = subprocess.run(
            [
                "pwsh",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                "scripts/verify-repo.ps1",
                "-Check",
                "Contract",
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("OK functional-effectiveness", completed.stdout)

    def _write_complete_evidence(
        self,
        repo_root: Path,
        *,
        name: str = "20260427-functional-verification.md",
    ) -> Path:
        evidence_path = repo_root / "docs" / "change-evidence" / name
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text(
            """
# 2026-04-27 Functional Verification

## Goal
- Verify autonomous functional effectiveness.

## Root Cause And Changes
- Root cause and changes are recorded.

## Verification
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/build-runtime.ps1` -> pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Runtime` -> pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check Contract` -> pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/doctor-runtime.ps1` -> pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/verify-repo.ps1 -Check All` -> pass.
- `python scripts/run-governed-task.py run --json` -> pass; task state `delivered`, verification refs include `build/test/contract/doctor`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/runtime-flow-preset.ps1 -AllTargets` -> pass; 5 targets, 0 failures, 0 changed fields.
- Temporary target attach/write smoke -> pass; wrote `docs/write-smoke.txt` and produced `live_closure_ready`.
- `python scripts/run-readonly-trial.py` -> pass.
- `python scripts/run-codex-adapter-trial.py` -> pass.
- `python scripts/run-claude-code-adapter-trial.py` -> pass.
- `python scripts/run-multi-repo-trial.py` -> pass; 2 repo profiles, 0 gate failures.
- `docs/change-evidence/20260427-claude-code-native-attach-tier-parity.md` -> referenced as the Claude parity evidence anchor.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/package-runtime.ps1` -> pass; provenance verification status `verified`.
- `python scripts/serve-operator-ui.py` -> pass.
- `python scripts/sync-agent-rules.py --scope All --fail-on-change` -> pass.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts/install-repo-hooks.ps1` -> pass; `core.hooksPath=.githooks`.
- `pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\\governance\\fast-check.ps1` -> pass.

## Rollback
- Revert this evidence file.
""".strip(),
            encoding="utf-8",
        )
        return evidence_path


if __name__ == "__main__":
    unittest.main()
