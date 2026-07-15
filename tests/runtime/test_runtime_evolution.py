import datetime as dt
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]


def _load_runtime_evolution_script():
    script_path = ROOT / "scripts" / "evaluate-runtime-evolution.py"
    spec = importlib.util.spec_from_file_location("evaluate_runtime_evolution_script", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["evaluate_runtime_evolution_script"] = module
    spec.loader.exec_module(module)
    return module


class RuntimeEvolutionTests(unittest.TestCase):
    def tearDown(self) -> None:
        sys.modules.pop("evaluate_runtime_evolution_script", None)

    def test_repo_runtime_evolution_dry_run_succeeds(self) -> None:
        module = _load_runtime_evolution_script()
        fixture_path = ROOT / "tests" / "fixtures" / "host-feedback" / "clean-windows-runner.json"

        with mock.patch.dict(os.environ, {"GACR_HOST_FEEDBACK_FIXTURE": str(fixture_path)}):
            payload = module.assert_runtime_evolution_policy(
                repo_root=ROOT,
                policy_path=ROOT / "docs" / "architecture" / "runtime-evolution-policy.json",
                as_of=dt.date(2026, 6, 6),
            )

        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["policy_id"], "default-runtime-evolution-review")
        self.assertFalse(payload["mutation_allowed"])
        self.assertEqual(payload["mode"], "dry_run")
        self.assertFalse(payload["online_source_check"])
        self.assertGreaterEqual(payload["candidate_count"], 1)
        self.assertIn("evidence_snapshot", payload)
        self.assertEqual(payload["evidence_snapshot"]["current_source"]["status"], "pass")
        self.assertEqual(payload["evidence_snapshot"]["host_feedback"]["status"], "pass")
        self.assertEqual(payload["evidence_snapshot"]["host_feedback"]["input_mode"], "test_fixture")
        self.assertEqual(
            payload["evidence_snapshot"]["host_feedback"]["acceptance_scope"],
            "test_only_not_hosted",
        )
        self.assertFalse(payload["evidence_snapshot"]["host_feedback"]["hosted_acceptance"])
        self.assertTrue(any(item["retrieval_mode"] == "dry_run_catalog" for item in payload["source_records"]))
        self.assertTrue(any(item["source_type"] == "internal_ai_coding_experience" for item in payload["source_records"]))
        self.assertTrue(any(item["candidate_id"] == "EVOL-AI-EXPERIENCE" for item in payload["candidates"]))
        self.assertFalse(any(item["candidate_id"] == "EVOL-EFFECT-FEEDBACK" for item in payload["candidates"]))
        self.assertTrue(all(item["patch_plan"] for item in payload["candidates"]))

    def test_source_catalog_covers_required_ai_feature_sources(self) -> None:
        module = _load_runtime_evolution_script()
        policy = json.loads((ROOT / "docs/architecture/runtime-evolution-policy.json").read_text(encoding="utf-8"))
        catalog_by_id = {item["source_id"]: item for item in policy["source_catalog"]}

        self.assertIn("mcp-inspector", catalog_by_id)
        self.assertIn("anthropic-claude-plugins-official", catalog_by_id)
        self.assertLessEqual(module.REQUIRED_SOURCE_CATALOG_IDS, set(catalog_by_id))
        required_refs = [catalog_by_id[source_id]["source_ref"] for source_id in module.REQUIRED_SOURCE_CATALOG_IDS]
        for expected_host in (
            "openai.com",
            "developers.openai.com",
            "docs.anthropic.com",
            "github.com/anthropics/claude-plugins-official",
            "developers.googleblog.com",
            "github.com/google-antigravity",
            "github.com/modelcontextprotocol/inspector",
            "antigravity.google",
            "modelcontextprotocol.io",
            "docs.openhands.dev",
            "aider.chat",
            "swe-agent.com",
        ):
            self.assertTrue(
                any(expected_host in source_ref for source_ref in required_refs),
                f"missing required source host: {expected_host}",
            )

    def test_internal_ai_coding_experience_sources_are_local_checks(self) -> None:
        module = _load_runtime_evolution_script()
        original_probe = module._probe_online_source
        module._probe_online_source = lambda source_ref: {
            "status": "ok",
            "http_status": 200,
            "content_type": "stubbed",
        }
        self.addCleanup(setattr, module, "_probe_online_source", original_probe)

        result = module.inspect_runtime_evolution_policy(
            repo_root=ROOT,
            policy_path=ROOT / "docs" / "architecture" / "runtime-evolution-policy.json",
            as_of=dt.date(2026, 6, 6),
            online_source_check=True,
        )

        internal_sources = [
            item
            for item in result["source_records"]
            if item["source_type"] == "internal_ai_coding_experience"
            and not item["source_id"].startswith("policy-source-")
        ]
        self.assertTrue(internal_sources)
        self.assertTrue(all(item["retrieval_mode"] == "local_file_check" for item in internal_sources))
        self.assertTrue(all(item["local_ref_exists"] for item in internal_sources))
        self.assertTrue(all(item["online_probe"] is None for item in internal_sources))

    def test_runtime_evolution_marks_stale_after_30_days(self) -> None:
        module = _load_runtime_evolution_script()
        policy = json.loads(
            (ROOT / "docs" / "architecture" / "runtime-evolution-policy.json").read_text(encoding="utf-8")
        )
        reviewed_on = dt.date.fromisoformat(policy["reviewed_on"])
        stale_as_of = reviewed_on + dt.timedelta(days=int(policy["stale_after_days"]) + 1)

        result = module.inspect_runtime_evolution_policy(
            repo_root=ROOT,
            policy_path=ROOT / "docs" / "architecture" / "runtime-evolution-policy.json",
            as_of=stale_as_of,
        )

        self.assertTrue(result["stale"])
        self.assertTrue(any(item["candidate_id"] == "EVOL-REVIEW-FRESHNESS" for item in result["candidates"]))
        refresh = next(item for item in result["candidates"] if item["candidate_id"] == "EVOL-REVIEW-FRESHNESS")
        self.assertEqual(refresh["proposed_action"], "modify")

    def test_ai_coding_experience_candidate_uses_resolved_artifact_ref(self) -> None:
        module = _load_runtime_evolution_script()
        expected_ref = ".runtime/artifacts/ai-coding-experience/20260620-ai-coding-experience-review.json"

        with mock.patch.object(module, "_resolve_ai_coding_experience_artifact_ref", return_value=expected_ref):
            result = module.inspect_runtime_evolution_policy(
                repo_root=ROOT,
                policy_path=ROOT / "docs" / "architecture" / "runtime-evolution-policy.json",
                as_of=dt.date(2026, 6, 20),
            )

        candidate = next(item for item in result["candidates"] if item["candidate_id"] == "EVOL-AI-EXPERIENCE")
        self.assertEqual(
            candidate["source_ref"],
            expected_ref,
        )
        self.assertEqual(
            result["evidence_snapshot"]["ai_coding_experience"]["artifact_source_ref"],
            expected_ref,
        )

    def test_ai_coding_experience_artifact_resolver_uses_latest_available_ref(self) -> None:
        module = _load_runtime_evolution_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            artifact_root = repo_root / module.AI_CODING_EXPERIENCE_ARTIFACT_ROOT
            artifact_root.mkdir(parents=True)
            (artifact_root / "20260618-ai-coding-experience-review.json").write_text("{}", encoding="utf-8")
            latest = artifact_root / "20260619-ai-coding-experience-review.json"
            latest.write_text("{}", encoding="utf-8")

            resolved = module._resolve_ai_coding_experience_artifact_ref(
                repo_root=repo_root,
                as_of=dt.date(2026, 6, 20),
            )

        self.assertEqual(latest.relative_to(repo_root).as_posix(), resolved)

    def test_runtime_evolution_rejects_invalid_candidate_action(self) -> None:
        module = _load_runtime_evolution_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            self._copy_required_files(repo_root)
            policy = json.loads((repo_root / "docs/architecture/runtime-evolution-policy.json").read_text(encoding="utf-8"))
            policy["candidate_actions"] = ["unsupported"]
            policy_path = repo_root / "docs/architecture/runtime-evolution-policy.json"
            policy_path.write_text(json.dumps(policy), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "candidate action is invalid"):
                module.assert_runtime_evolution_policy(
                    repo_root=repo_root,
                    policy_path=policy_path,
                    as_of=dt.date(2026, 6, 6),
                )

    def test_runtime_evolution_rejects_missing_required_source_catalog_id(self) -> None:
        module = _load_runtime_evolution_script()

        with tempfile.TemporaryDirectory() as tmp_dir:
            repo_root = Path(tmp_dir)
            self._copy_required_files(repo_root)
            policy_path = repo_root / "docs/architecture/runtime-evolution-policy.json"
            policy = json.loads(policy_path.read_text(encoding="utf-8"))
            removed_source_id = sorted(module.REQUIRED_SOURCE_CATALOG_IDS)[0]
            policy["source_catalog"] = [
                item for item in policy["source_catalog"] if item["source_id"] != removed_source_id
            ]
            policy_path.write_text(json.dumps(policy), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "source_catalog missing required source ids"):
                module.assert_runtime_evolution_policy(
                    repo_root=repo_root,
                    policy_path=policy_path,
                    as_of=dt.date(2026, 6, 6),
                )

    def test_evolve_runtime_wrapper_writes_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            artifact_root = Path(tmp_dir) / "runtime-artifacts"
            evidence_root = Path(tmp_dir) / "change-evidence"
            completed = subprocess.run(
                [
                    "pwsh",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    "scripts/evolve-runtime.ps1",
                    "-AsOf",
                    "2026-06-06",
                    "-ArtifactRoot",
                    str(artifact_root),
                    "-EvidenceRoot",
                    str(evidence_root),
                    "-WriteArtifacts",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=ROOT,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertIn("json", payload["artifact_refs"])
            self.assertIn("sources", payload["artifact_refs"])
            self.assertIn("candidates", payload["artifact_refs"])
            self.assertTrue(Path(payload["artifact_refs"]["json"]).exists())
            self.assertTrue(Path(payload["artifact_refs"]["sources"]).exists())
            self.assertTrue(Path(payload["artifact_refs"]["candidates"]).exists())

    def test_write_artifacts_emits_reviewable_source_and_candidate_snapshots(self) -> None:
        module = _load_runtime_evolution_script()
        original_probe = module._probe_online_source
        module._probe_online_source = lambda source_ref: {
            "status": "ok",
            "http_status": 200,
            "content_type": "stubbed",
        }
        self.addCleanup(setattr, module, "_probe_online_source", original_probe)

        with tempfile.TemporaryDirectory() as tmp_dir:
            artifact_root = Path(tmp_dir) / "runtime-artifacts"
            evidence_root = Path(tmp_dir) / "change-evidence"
            payload = module.assert_runtime_evolution_policy(
                repo_root=ROOT,
                policy_path=ROOT / "docs" / "architecture" / "runtime-evolution-policy.json",
                as_of=dt.date(2026, 6, 6),
                write_artifacts=True,
                artifact_root=artifact_root,
                evidence_root=evidence_root,
                online_source_check=True,
            )

            source_artifact = json.loads(Path(payload["artifact_refs"]["sources"]).read_text(encoding="utf-8"))
            candidate_artifact = json.loads(Path(payload["artifact_refs"]["candidates"]).read_text(encoding="utf-8"))

        self.assertEqual(source_artifact["artifact_type"], "runtime_evolution_sources")
        self.assertTrue(source_artifact["online_source_check"])
        self.assertEqual(source_artifact["source_count"], payload["source_count"])
        self.assertTrue(
            any(
                record.get("online_probe", {}).get("status") == "ok"
                for record in source_artifact["source_records"]
            )
        )
        self.assertEqual(candidate_artifact["artifact_type"], "runtime_evolution_candidates")
        self.assertEqual(candidate_artifact["candidate_count"], payload["candidate_count"])
        self.assertIn("evidence_snapshot", candidate_artifact)

    def test_operator_evolution_review_supports_online_source_check_flag(self) -> None:
        operator = (ROOT / "scripts" / "operator.ps1").read_text(encoding="utf-8")

        self.assertIn("[switch]$OnlineSourceCheck", operator)
        self.assertIn('$arguments += "-OnlineSourceCheck"', operator)

        module = _load_runtime_evolution_script()
        original_probe = module._probe_online_source
        module._probe_online_source = lambda source_ref: {
            "status": "ok",
            "http_status": 200,
            "content_type": "stubbed",
        }
        self.addCleanup(setattr, module, "_probe_online_source", original_probe)
        payload = module.assert_runtime_evolution_policy(
            repo_root=ROOT,
            policy_path=ROOT / "docs" / "architecture" / "runtime-evolution-policy.json",
            as_of=dt.date(2026, 6, 6),
            online_source_check=True,
        )
        self.assertTrue(payload["online_source_check"])

    def test_verify_repo_docs_runs_runtime_evolution_gate(self) -> None:
        verifier = (ROOT / "scripts" / "verify-repo.ps1").read_text(encoding="utf-8")

        self.assertIn("function Invoke-DocsChecks", verifier)
        self.assertIn("Invoke-RuntimeEvolutionReviewChecks", verifier)
        self.assertIn('Write-CheckOk "runtime-evolution-review"', verifier)

    def _copy_required_files(self, repo_root: Path) -> None:
        for relative in [
            "docs/architecture/runtime-evolution-policy.json",
            "docs/plans/runtime-evolution-review-plan.md",
            "docs/change-evidence/20260501-runtime-evolution-planning.md",
            "scripts/build-runtime.ps1",
            "scripts/verify-repo.ps1",
            "scripts/doctor-runtime.ps1",
        ]:
            source = ROOT / relative
            target = repo_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
