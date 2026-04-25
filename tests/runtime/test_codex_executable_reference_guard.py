import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RISKY_CODEX_EXE_TOKEN = "codex" + ".exe"
SCAN_ROOTS = ("apps", "docs", "packages", "schemas", "scripts", "tests")
SKIP_DIR_PARTS = {
    ".git",
    ".runtime",
    "__pycache__",
    "change-evidence",
}
ALLOWLISTED_FILES = {
    Path("packages/contracts/src/governed_ai_coding_runtime_contracts/codex_adapter.py"),
    Path("tests/runtime/test_codex_adapter.py"),
}
TEXT_SUFFIXES = {
    ".bat",
    ".cmd",
    ".cs",
    ".json",
    ".md",
    ".ps1",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
}


class CodexExecutableReferenceGuardTests(unittest.TestCase):
    def test_active_sources_do_not_hardcode_codex_exe(self) -> None:
        violations: list[str] = []
        for scan_root in SCAN_ROOTS:
            root = ROOT / scan_root
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if not path.is_file():
                    continue
                relative = path.relative_to(ROOT)
                if any(part in SKIP_DIR_PARTS for part in relative.parts):
                    continue
                if relative in ALLOWLISTED_FILES:
                    continue
                if path.suffix.lower() not in TEXT_SUFFIXES:
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
                for line_number, line in enumerate(text.splitlines(), start=1):
                    if RISKY_CODEX_EXE_TOKEN.lower() in line.lower():
                        violations.append(f"{relative}:{line_number}: {line.strip()}")

        self.assertEqual(
            violations,
            [],
            "Use codex/codex.cmd or configurable --codex-bin instead of hard-coded exact .exe names:\n"
            + "\n".join(violations),
        )


if __name__ == "__main__":
    unittest.main()
