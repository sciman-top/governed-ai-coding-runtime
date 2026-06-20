from __future__ import annotations

import os
import tempfile
import uuid
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_HOME = REPO_ROOT / ".runtime" / "home"
RUNTIME_HOME.mkdir(parents=True, exist_ok=True)

RUNTIME_TMP = Path(tempfile.gettempdir()) / f"codex-runtime-{uuid.uuid4().hex}"
RUNTIME_TMP.mkdir(parents=True, exist_ok=False)

def _safe_mkdtemp(suffix=None, prefix=None, dir=None):
    base_dir = Path(dir) if dir is not None else RUNTIME_TMP
    base_dir.mkdir(parents=True, exist_ok=True)
    resolved_prefix = "tmp" if prefix is None else prefix
    resolved_suffix = "" if suffix is None else suffix
    candidate = base_dir / f"{resolved_prefix}{uuid.uuid4().hex}{resolved_suffix}"
    candidate.mkdir(parents=False, exist_ok=False)
    return str(candidate)


class _SafeTemporaryDirectory:
    def __init__(self, suffix=None, prefix=None, dir=None, ignore_cleanup_errors=False, *, delete=True):
        self.name = _safe_mkdtemp(suffix=suffix, prefix=prefix, dir=dir)
        self._closed = False
        self._delete = delete

    def __enter__(self):
        return self.name

    def __exit__(self, exc_type, exc, tb):
        self.cleanup()
        return False

    def cleanup(self):
        if self._closed:
            return
        self._closed = True

    def __fspath__(self):
        return self.name

    def __str__(self):
        return self.name


tempfile.mkdtemp = _safe_mkdtemp
tempfile.TemporaryDirectory = _SafeTemporaryDirectory

os.environ["TMP"] = str(RUNTIME_TMP)
os.environ["TEMP"] = str(RUNTIME_TMP)
os.environ["TMPDIR"] = str(RUNTIME_TMP)
os.environ["GOVERNED_RUNTIME_HOME"] = str(RUNTIME_HOME)
tempfile.tempdir = str(RUNTIME_TMP)
