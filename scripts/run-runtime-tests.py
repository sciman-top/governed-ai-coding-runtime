from __future__ import annotations

import argparse
import concurrent.futures
import os
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class TestTarget:
    suite: str
    module: str
    path: Path


@dataclass(frozen=True)
class TestResult:
    target: TestTarget
    exit_code: int
    duration_seconds: float
    stdout: str
    stderr: str


def _parse_suite(value: str) -> tuple[str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("suite must use NAME=PATH format")
    name, raw_path = value.split("=", 1)
    name = name.strip()
    if not name:
        raise argparse.ArgumentTypeError("suite name must not be empty")
    path = (ROOT / raw_path.strip()).resolve()
    return name, path


def _module_name_for(path: Path) -> str:
    relative = path.relative_to(ROOT).with_suffix("")
    return ".".join(relative.parts)


def _discover_targets(suites: list[tuple[str, Path]], pattern: str) -> list[TestTarget]:
    targets: list[TestTarget] = []
    for suite_name, suite_path in suites:
        if not suite_path.exists():
            raise FileNotFoundError(f"test suite path not found: {suite_path}")
        for path in sorted(suite_path.glob(pattern)):
            if path.is_file():
                targets.append(TestTarget(suite=suite_name, module=_module_name_for(path), path=path))
    if not targets:
        raise RuntimeError("no test files discovered")
    return targets


def _resolve_worker_count(requested: int, target_count: int) -> int:
    if requested > 0:
        return min(requested, target_count)

    env_value = os.environ.get("GOVERNED_RUNTIME_TEST_WORKERS", "").strip()
    if env_value:
        try:
            parsed = int(env_value)
        except ValueError as exc:
            raise ValueError("GOVERNED_RUNTIME_TEST_WORKERS must be an integer") from exc
        if parsed < 1:
            raise ValueError("GOVERNED_RUNTIME_TEST_WORKERS must be greater than zero")
        return min(parsed, target_count)

    cpu_count = os.cpu_count() or 2
    return max(1, min(4, cpu_count, target_count))


def _resolve_timeout_seconds(requested: int) -> int:
    if requested > 0:
        return requested

    env_value = os.environ.get("GOVERNED_RUNTIME_TEST_TIMEOUT_SECONDS", "").strip()
    if env_value:
        try:
            parsed = int(env_value)
        except ValueError as exc:
            raise ValueError("GOVERNED_RUNTIME_TEST_TIMEOUT_SECONDS must be an integer") from exc
        if parsed < 1:
            raise ValueError("GOVERNED_RUNTIME_TEST_TIMEOUT_SECONDS must be greater than zero")
        return parsed

    return 180


def _run_target(target: TestTarget, timeout_seconds: int) -> TestResult:
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            [sys.executable, "-m", "unittest", target.module],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=ROOT,
            env=env,
            timeout=timeout_seconds,
        )
    except subprocess.TimeoutExpired as exc:
        elapsed = time.perf_counter() - started
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode("utf-8", errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode("utf-8", errors="replace")
        timeout_message = f"Timed out after {timeout_seconds}s while running {target.module}"
        return TestResult(
            target=target,
            exit_code=124,
            duration_seconds=elapsed,
            stdout=str(stdout),
            stderr=(str(stderr).rstrip() + "\n" + timeout_message).strip(),
        )
    return TestResult(
        target=target,
        exit_code=completed.returncode,
        duration_seconds=time.perf_counter() - started,
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def _print_result(result: TestResult) -> None:
    status = "PASS" if result.exit_code == 0 else "FAIL"
    print(f"{status} {result.target.suite} {result.target.path.relative_to(ROOT)} {result.duration_seconds:.3f}s")
    if result.exit_code != 0:
        if result.stdout.strip():
            print("--- stdout ---")
            print(result.stdout.rstrip())
        if result.stderr.strip():
            print("--- stderr ---", file=sys.stderr)
            print(result.stderr.rstrip(), file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run runtime/service unittest files in parallel.")
    parser.add_argument(
        "--suite",
        action="append",
        type=_parse_suite,
        default=[],
        help="Test suite to run, in NAME=PATH format. Defaults to runtime=tests/runtime and service=tests/service.",
    )
    parser.add_argument("--pattern", default="test_*.py")
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=0,
        help="Per-test-file timeout. Defaults to GOVERNED_RUNTIME_TEST_TIMEOUT_SECONDS or 180.",
    )
    parser.add_argument(
        "--summary-json",
        default="",
        help="Optional path for a machine-readable timing summary.",
    )
    args = parser.parse_args()

    suites = args.suite or [
        ("runtime", (ROOT / "tests" / "runtime").resolve()),
        ("service", (ROOT / "tests" / "service").resolve()),
    ]
    targets = _discover_targets(suites, args.pattern)
    workers = _resolve_worker_count(args.workers, len(targets))
    timeout_seconds = _resolve_timeout_seconds(args.timeout_seconds)

    print(f"Running {len(targets)} test files with {workers} workers; timeout={timeout_seconds}s")
    started = time.perf_counter()
    results: list[TestResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_target = {executor.submit(_run_target, target, timeout_seconds): target for target in targets}
        for future in concurrent.futures.as_completed(future_to_target):
            result = future.result()
            results.append(result)
            _print_result(result)

    results.sort(key=lambda item: item.duration_seconds, reverse=True)
    failed = [result for result in results if result.exit_code != 0]
    elapsed = time.perf_counter() - started

    print("Slowest test files:")
    for result in results[:10]:
        print(f"  {result.target.path.relative_to(ROOT)} {result.duration_seconds:.3f}s")
    print(f"Completed {len(results)} test files in {elapsed:.3f}s; failures={len(failed)}")

    if args.summary_json:
        summary_path = Path(args.summary_json)
        if not summary_path.is_absolute():
            summary_path = ROOT / summary_path
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "target_count": len(results),
            "worker_count": workers,
            "timeout_seconds": timeout_seconds,
            "elapsed_seconds": elapsed,
            "failure_count": len(failed),
            "failures": [
                {
                    "suite": result.target.suite,
                    "module": result.target.module,
                    "path": str(result.target.path.relative_to(ROOT)),
                    "exit_code": result.exit_code,
                    "duration_seconds": result.duration_seconds,
                }
                for result in failed
            ],
            "slowest": [
                {
                    "target": {
                        "suite": result.target.suite,
                        "module": result.target.module,
                        "path": str(result.target.path.relative_to(ROOT)),
                    },
                    "exit_code": result.exit_code,
                    "duration_seconds": result.duration_seconds,
                }
                for result in results[:10]
            ],
        }
        summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
