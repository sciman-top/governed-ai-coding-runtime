from __future__ import annotations

import os
from pathlib import Path
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_TMP = REPO_ROOT / ".runtime" / "tmp"
RUNTIME_HOME = REPO_ROOT / ".runtime" / "home"
RUNTIME_TMP.mkdir(parents=True, exist_ok=True)
RUNTIME_HOME.mkdir(parents=True, exist_ok=True)

os.environ["TMP"] = str(RUNTIME_TMP)
os.environ["TEMP"] = str(RUNTIME_TMP)
os.environ["TMPDIR"] = str(RUNTIME_TMP)
os.environ["GOVERNED_RUNTIME_HOME"] = str(RUNTIME_HOME)
tempfile.tempdir = str(RUNTIME_TMP)
