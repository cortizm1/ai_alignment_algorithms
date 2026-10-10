#!/usr/bin/env python3
"""Refresh the PUBLIC records for unsealed homeworks (status + session count only).
Sealed records are written by tools/seal.py and left untouched here."""
import json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
data = ROOT / "data"; data.mkdir(exist_ok=True)
for d in sorted(ROOT.glob("hw/hw*"), key=lambda p: int(p.name[2:])):
    n = int(d.name[2:]); pub = data / f"hw{n}.json"
    if pub.exists() and json.loads(pub.read_text()).get("sealed"):
        continue
    log = d / "ai_log.md"
    sessions = sum(1 for l in log.read_text().splitlines() if l.startswith("| 20")) if log.exists() else 0
    status = (d / "STATUS").read_text().strip() if (d / "STATUS").exists() else "unknown"
    pub.write_text(json.dumps({"hw": n, "status": status, "sessions": sessions}, indent=1))
    print(f"{pub.name}: {status}, {sessions} sessions")
