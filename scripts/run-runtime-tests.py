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
DEFAULT_TIMING_HISTORY_PATH = ROOT / "docs" / "change-evidence" / "runtime-test-speed-latest.json"
DEFAULT_AUTO_WORKER_CAP = 8


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


def _load_timing_history(path: Path | None) -> dict[str, float]:
    if path is None or not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    history: dict[str, float] = {}
    for item in payload.get("slowest") or []:
        if not isinstance(item, dict):
            continue
        target = item.get("target") or {}
        if not isinstance(target, dict):
            continue
        raw_duration = item.get("duration_seconds")
        try:
            duration = float(raw_duration)
        except (TypeError, ValueError):
            continue
        module = str(target.get("module") or "").strip()
        path_value = str(target.get("path") or "").strip().replace("\\", "/")
        if module:
            history[module] = duration
        if path_value:
            history[path_value] = duration
    return history


def _prioritize_targets(targets: list[TestTarget], timing_history: dict[str, float]) -> list[TestTarget]:
    if not timing_history:
        return list(targets)

    def known_duration(target: TestTarget) -> float:
        relative_path = target.path.relative_to(ROOT).as_posix()
        return max(
            timing_history.get(target.module, 0.0),
            timing_history.get(relative_path, 0.0),
        )

    return sorted(
        targets,
        key=lambda target: (
            -known_duration(target),
            target.suite,
            target.path.relative_to(ROOT).as_posix(),
        ),
    )


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

    cap_value = os.environ.get("GOVERNED_RUNTIME_TEST_AUTO_WORKER_CAP", "").strip()
    if cap_value:
        try:
            worker_cap = int(cap_value)
        except ValueError as exc:
            raise ValueError("GOVERNED_RUNTIME_TEST_AUTO_WORKER_CAP must be an integer") from exc
        if worker_cap < 1:
            raise ValueError("GOVERNED_RUNTIME_TEST_AUTO_WORKER_CAP must be greater than zero")
    else:
        worker_cap = DEFAULT_AUTO_WORKER_CAP

    cpu_count = os.cpu_count() or 2
    return max(1, min(worker_cap, cpu_count, target_count))


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
    parser.add_argument(
        "--timing-history-json",
        default=str(DEFAULT_TIMING_HISTORY_PATH.relative_to(ROOT)),
        help="Optional prior timing summary used to start known slow test files first. Use an empty string to disable.",
    )
    args = parser.parse_args()

    suites = args.suite or [
        ("runtime", (ROOT / "tests" / "runtime").resolve()),
        ("service", (ROOT / "tests" / "service").resolve()),
    ]
    targets = _discover_targets(suites, args.pattern)
    history_path = None
    if args.timing_history_json.strip():
        history_path = Path(args.timing_history_json)
        if not history_path.is_absolute():
            history_path = ROOT / history_path
    timing_history = _load_timing_history(history_path)
    targets = _prioritize_targets(targets, timing_history)
    prioritized_target_count = sum(
        1
        for target in targets
        if target.module in timing_history or target.path.relative_to(ROOT).as_posix() in timing_history
    )
    workers = _resolve_worker_count(args.workers, len(targets))
    timeout_seconds = _resolve_timeout_seconds(args.timeout_seconds)

    print(f"Running {len(targets)} test files with {workers} workers; timeout={timeout_seconds}s")
    if history_path is not None:
        if prioritized_target_count:
            print(f"Prioritized {prioritized_target_count} known slow test files from {history_path.relative_to(ROOT)}")
        else:
            print(f"No prior timing matches from {history_path.relative_to(ROOT)}")
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
            "timing_history_path": str(history_path.relative_to(ROOT)) if history_path else None,
            "prioritized_target_count": prioritized_target_count,
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
