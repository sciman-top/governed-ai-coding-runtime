from __future__ import annotations

import argparse
import concurrent.futures
import os
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


def _run_target(target: TestTarget) -> TestResult:
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    started = time.perf_counter()
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", target.module],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=ROOT,
        env=env,
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
    args = parser.parse_args()

    suites = args.suite or [
        ("runtime", (ROOT / "tests" / "runtime").resolve()),
        ("service", (ROOT / "tests" / "service").resolve()),
    ]
    targets = _discover_targets(suites, args.pattern)
    workers = _resolve_worker_count(args.workers, len(targets))

    print(f"Running {len(targets)} test files with {workers} workers")
    started = time.perf_counter()
    results: list[TestResult] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_target = {executor.submit(_run_target, target): target for target in targets}
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

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
