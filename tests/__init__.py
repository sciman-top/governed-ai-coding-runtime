from __future__ import annotations

import os
from pathlib import Path
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_TMP = REPO_ROOT / ".runtime" / "tmp"
RUNTIME_TMP.mkdir(parents=True, exist_ok=True)

os.environ["TMP"] = str(RUNTIME_TMP)
os.environ["TEMP"] = str(RUNTIME_TMP)
os.environ["TMPDIR"] = str(RUNTIME_TMP)
tempfile.tempdir = str(RUNTIME_TMP)
