from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "docs" / "change-evidence" / "policy-tool-credential-audit-report.json"


def main() -> int:
    try:
        result = inspect_policy_tool_credential_audit(repo_root=ROOT)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "pass" else 1


def inspect_policy_tool_credential_audit(*, repo_root: Path) -> dict:
    builder = _load_builder()
    result = builder(
        repo_root=repo_root,
        config_path=repo_root / "docs" / "architecture" / "policy-tool-credential-audit-boundary.json",
        repo_profile_path=repo_root / ".governed-ai" / "repo-profile.json",
        tool_contract_path=repo_root / "schemas" / "examples" / "tool-contract" / "default-runtime.example.json",
        output_path=OUTPUT_PATH,
    )
    failures: list[str] = []
    if result["unknown_tools"]:
        failures.append("unknown_tool_detected")
    if result["missing_policy_basis_refs"]:
        failures.append("missing_policy_basis")
    if result["overbroad_credential_refs"]:
        failures.append("overbroad_credential_scope")
    if result["unsupported_override_refs"]:
        failures.append("unsupported_override")
    if any(item["status"] != "pass" for item in result["audited_tools"]):
        failures.append("tool_entry_failure")
    if any(item["status"] != "pass" for item in result["override_audit"]):
        failures.append("override_entry_failure")
    if result["summary"]["audited_tool_count"] < 4:
        failures.append("insufficient_audited_tools")

    result["status"] = "fail" if failures else "pass"
    result["invalid_reasons"] = failures
    return result


def _load_builder():
    script_path = ROOT / "scripts" / "build-policy-tool-credential-audit.py"
    spec = importlib.util.spec_from_file_location("build_policy_tool_credential_audit_script", script_path)
    if spec is None or spec.loader is None:
        raise ValueError(f"unable to load module: {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_policy_tool_credential_audit


if __name__ == "__main__":
    raise SystemExit(main())
