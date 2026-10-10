"""Read-only access to the public per-homework records in DATA_DIR. No crypto here."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from web import config


def list_records(data_dir: Path = config.DATA_DIR) -> list[dict[str, Any]]:
    """All homework records, sorted by number. Missing dir -> empty list."""
    if not data_dir.exists():
        return []
    out = []
    for f in sorted(data_dir.glob("hw*.json"), key=lambda p: int(p.stem[2:])):
        rec = json.loads(f.read_text())
        rec.setdefault("hw", int(f.stem[2:]))
        out.append(rec)
    return out


def get_record(n: int, data_dir: Path = config.DATA_DIR) -> dict[str, Any] | None:
    """One homework record or None."""
    f = data_dir / f"hw{n}.json"
    return json.loads(f.read_text()) | {"hw": n} if f.exists() else None


def policy_markdown(path: Path = config.POLICY_FILE) -> str:
    """The public policy statement, markdown source."""
    return path.read_text() if path.exists() else "_Policy statement not published yet._"
