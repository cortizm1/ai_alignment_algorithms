#!/usr/bin/env python3
"""Seal an arbitrary file as a reel (demo / non-homework). Usage: tools/seal_file.py N FILE [status]
Writes data/hwN.json (public) and prints the opening (secret). Text files are used as-is; PDFs are
converted to text with mutool. No transcript attachment."""
import datetime as dt, json, pathlib, subprocess, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT))
from transparency import crypto  # noqa: E402
n, src = sys.argv[1], pathlib.Path(sys.argv[2]); status = sys.argv[3] if len(sys.argv) > 3 else "demo"
if src.suffix.lower() == ".pdf":
    text = subprocess.run(["mutool", "draw", "-F", "txt", str(src)], check=True, capture_output=True, text=True).stdout
    report = f"# Demo reel: {src.name}\n\n```\n{text.strip()}\n```\n".encode()
else:
    report = src.read_bytes()
sealed, opening = crypto.seal(report)
now = dt.datetime.now().astimezone().isoformat(timespec="minutes")
(ROOT / "data").mkdir(exist_ok=True)
(ROOT / "data" / f"hw{n}.json").write_text(json.dumps({"hw": int(n), "status": status, "sessions": 0, "sealed_at": now,
    "sealed": crypto.encode_sealed(sealed), "source": src.name}, indent=1))
print(f"public record -> data/hw{n}.json  commitment={sealed.commitment.hex()}")
print(f"OPENING (secret, give to whoever may read): {crypto.encode_opening(opening)}")
