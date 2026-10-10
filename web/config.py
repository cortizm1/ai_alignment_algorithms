"""Central configuration for the transparency site. The only module that reads the environment."""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parent.parent

#: Public per-homework records (sealed ciphertext + commitment), JSON, one file per HW.
DATA_DIR: Path = Path(os.environ.get("JHU_DATA_DIR", REPO_ROOT / "data")).resolve()
#: Public policy statement (markdown).
POLICY_FILE: Path = Path(os.environ.get("JHU_POLICY_FILE", REPO_ROOT / "docs" / "ai_policy_public.md")).resolve()
PORT: int = int(os.environ.get("JHU_PORT", "8010"))
PUBLIC_URL: str = os.environ.get("JHU_PUBLIC_URL", "https://jhu.nymo.finance").rstrip("/")
#: Session-signing secret. The site keeps no sessions; this only stops FastHTML from writing .sesskey to disk.
SECRET_KEY: str = os.environ.get("JHU_SECRET_KEY") or os.urandom(32).hex()
COURSE: str = "601.433 / 601.633 Introduction to Algorithms · JHU · Fall 2026"
