import json
import subprocess
import sys
import tempfile
import unittest
import importlib
from dataclasses import fields
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_SRC = ROOT / "packages" / "contracts" / "src"
if str(CONTRACTS_SRC) not in sys.path:
    sys.path.insert(0, str(CONTRACTS_SRC))

from governed_ai_coding_runtime_contracts.agent_continuity import LocalAgentContinuityIndex, audit_agent_continuity


class AgentContinuityTests(unittest.TestCase):
    def test_audit_reports_codex_and_claude_without_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            codex_home = root / "codex"
            codex_home.mkdir()
            escaped_codex_home = str(codex_home).replace("\\", "\\\\")
            escaped_codex_log = str(codex_home / "log").replace("\\", "\\\\")
            (codex_home / "config.toml").write_text(
                "\n".join(
                    [
                        'model = "gpt-5.5"',
                        'model_provider = "openai"',
                        f'sqlite_home = "{escaped_codex_home}"',
                        f'log_dir = "{escaped_codex_log}"',
                        "[history]",
                        'persistence = "save-all"',
                        "[profiles.shared-chatgpt]",
                        'model = "gpt-5.5"',
                    ]
                ),
                encoding="utf-8",
            )
            (codex_home / "state_5.sqlite").write_bytes(b"")
            session_dir = codex_home / "sessions" / "2026" / "05" / "10"
            session_dir.mkdir(parents=True)
            (session_dir / "rollout.jsonl").write_text("{}", encoding="utf-8")
            launcher_dir = root / ".local" / "bin"
            launcher_dir.mkdir(parents=True)
            (launcher_dir / "codex-shared.cmd").write_text("@echo off", encoding="utf-8")

            claude_home = root / "claude"
            claude_home.mkdir()
            (claude_home / "settings.json").write_text(
                json.dumps({"env": {"ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic"}}),
                encoding="utf-8",
            )
            (claude_home / "provider-profiles.json").write_text(
                json.dumps({"active": "bigmodel-glm", "profiles": []}),
                encoding="utf-8",
            )
            projects_dir = claude_home / "projects" / "repo"
            projects_dir.mkdir(parents=True)
            (projects_dir / "session.jsonl").write_text("{}", encoding="utf-8")
            (claude_home / "history.jsonl").write_text("{}", encoding="utf-8")

            payload = audit_agent_continuity(
                repo_root=repo,
                codex_home=codex_home,
                claude_home=claude_home,
                now=datetime(2026, 5, 10, tzinfo=UTC),
            )

        self.assertEqual("ok", payload["status"])
        self.assertEqual(3, payload["record_count"])
        records = {record["record_id"]: record for record in payload["records"]}
        self.assertEqual("native_shared", records["codex-shared-home"]["continuity_class"])
        self.assertEqual("save-all", records["codex-shared-home"]["config_summary"]["history_persistence"])
        self.assertEqual(["shared-chatgpt"], records["codex-shared-home"]["config_summary"]["profile_names"])
        self.assertEqual("bigmodel-glm", records["claude-shared-home"]["provider_alias"])
        self.assertEqual(1, records["claude-shared-home"]["config_summary"]["projects_jsonl_count"])
        self.assertTrue(records["claude-desktop-boundary"]["platform_na"]["applies"])
        serialized = json.dumps(payload, ensure_ascii=False)
        self.assertNotIn("ANTHROPIC_AUTH_TOKEN", serialized)
        self.assertNotIn("api_key", serialized.lower())

    def test_missing_host_homes_emit_platform_na(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            payload = audit_agent_continuity(
                repo_root=repo,
                codex_home=root / "missing-codex",
                claude_home=root / "missing-claude",
                now=datetime(2026, 5, 10, tzinfo=UTC),
            )
        records = {record["record_id"]: record for record in payload["records"]}
        self.assertTrue(records["codex-continuity-missing"]["platform_na"]["applies"])
        self.assertTrue(records["claude-continuity-missing"]["platform_na"]["applies"])

    def test_cli_audit_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            codex_home = root / "codex"
            claude_home = root / "claude"
            codex_home.mkdir()
            claude_home.mkdir()
            script = ROOT / "scripts" / "agent-continuity.py"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "audit",
                    "--json",
                    "--repo-root",
                    str(repo),
                    "--codex-home",
                    str(codex_home),
                    "--claude-home",
                    str(claude_home),
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
        payload = json.loads(completed.stdout)
        self.assertEqual("ok", payload["status"])
        self.assertEqual(3, payload["record_count"])

    def test_python_contract_covers_schema_required_fields(self) -> None:
        module = importlib.import_module("governed_ai_coding_runtime_contracts.agent_continuity")
        schema = json.loads(
            (ROOT / "schemas" / "jsonschema" / "agent-continuity-record.schema.json").read_text(encoding="utf-8")
        )

        dataclass_fields = {field.name for field in fields(module.AgentContinuityRecord)}
        for required_field in schema["required"]:
            self.assertIn(required_field, dataclass_fields)

    def test_schema_accepts_auditor_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            codex_home = root / "codex"
            claude_home = root / "claude"
            codex_home.mkdir()
            claude_home.mkdir()
            payload = audit_agent_continuity(
                repo_root=repo,
                codex_home=codex_home,
                claude_home=claude_home,
                now=datetime(2026, 5, 10, tzinfo=UTC),
            )

        for record in payload["records"]:
            self.assertTrue(self._schema_accepts(record), record["record_id"])

    def test_agent_continuity_exports_from_package_root(self) -> None:
        package = importlib.import_module("governed_ai_coding_runtime_contracts")
        self.assertTrue(hasattr(package, "AgentContinuityRecord"))
        self.assertTrue(hasattr(package, "audit_agent_continuity"))
        self.assertTrue(hasattr(package, "LocalAgentContinuityIndex"))

    def test_continuity_index_writes_and_searches_classified_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            codex_home = root / "codex"
            claude_home = root / "claude"
            codex_home.mkdir()
            claude_home.mkdir()
            payload = audit_agent_continuity(
                repo_root=repo,
                codex_home=codex_home,
                claude_home=claude_home,
                now=datetime(2026, 5, 10, tzinfo=UTC),
            )
            index = LocalAgentContinuityIndex(root / "continuity-index")
            for record in payload["records"]:
                index.write_record(record)

            result = index.search(repo_id="repo", tool_family="codex")

        self.assertEqual("ok", result["status"])
        self.assertEqual(1, result["record_count"])
        self.assertEqual("codex-shared-home", result["records"][0]["record_id"])
        self.assertEqual("records/codex-shared-home.json", result["records"][0]["record_ref"])

    def test_continuity_index_rejects_secret_like_records(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            codex_home = root / "codex"
            claude_home = root / "claude"
            codex_home.mkdir()
            claude_home.mkdir()
            payload = audit_agent_continuity(
                repo_root=repo,
                codex_home=codex_home,
                claude_home=claude_home,
                now=datetime(2026, 5, 10, tzinfo=UTC),
            )
            record = dict(payload["records"][0])
            record["task_summary"] = "api_key=sk-testsecretvalue123456"

            with self.assertRaisesRegex(ValueError, "secret-like"):
                LocalAgentContinuityIndex(root / "continuity-index").write_record(record)

    def test_cli_write_record_and_search_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            repo.mkdir()
            codex_home = root / "codex"
            claude_home = root / "claude"
            codex_home.mkdir()
            claude_home.mkdir()
            payload = audit_agent_continuity(
                repo_root=repo,
                codex_home=codex_home,
                claude_home=claude_home,
                now=datetime(2026, 5, 10, tzinfo=UTC),
            )
            record_path = root / "record.json"
            record_path.write_text(json.dumps(payload["records"][0]), encoding="utf-8")
            index_root = root / "continuity-index"
            script = ROOT / "scripts" / "agent-continuity.py"

            write = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "write-record",
                    "--index-root",
                    str(index_root),
                    "--record-json",
                    str(record_path),
                    "--json",
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )
            search = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "search",
                    "--index-root",
                    str(index_root),
                    "--repo-id",
                    "repo",
                    "--json",
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

        self.assertEqual("written", json.loads(write.stdout)["status"])
        self.assertEqual(1, json.loads(search.stdout)["record_count"])

    def _schema_accepts(self, payload: dict) -> bool:
        schema_path = ROOT / "schemas" / "jsonschema" / "agent-continuity-record.schema.json"
        command = (
            "$json = [Console]::In.ReadToEnd(); "
            f"if (Test-Json -Json $json -SchemaFile '{schema_path}') "
            "{ Write-Output 'true' } else { Write-Output 'false' }"
        )
        completed = subprocess.run(
            ["pwsh", "-NoProfile", "-Command", command],
            input=json.dumps(payload),
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        return completed.stdout.strip().lower() == "true"


if __name__ == "__main__":
    unittest.main()
