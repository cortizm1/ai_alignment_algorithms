#!/usr/bin/env python3
"""Seal an arbitrary file as a reel (demo / non-homework). Usage: tools/seal_file.py N FILE [status]
The report is a short markdown note; the file itself is an encrypted attachment with its mime type
(PDFs render inline in the browser and can be downloaded after a successful opening).
Writes data/hwN.json (public) and prints the opening (secret)."""
import datetime as dt, json, mimetypes, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT))
from transparency import crypto  # noqa: E402
n, src = sys.argv[1], pathlib.Path(sys.argv[2]); status = sys.argv[3] if len(sys.argv) > 3 else "demo"
mime = mimetypes.guess_type(src.name)[0] or "application/octet-stream"
report = f"# Demo reel\n\nSealed file: `{src.name}` ({mime}, {src.stat().st_size} bytes).\n\nThis reel exists to let readers test the opening flow end to end.\n".encode()
sealed, opening = crypto.seal(report)
att = {"name": src.name, "mime": mime, **crypto.seal_attachment(src.read_bytes(), sealed.commitment, opening)}
now = dt.datetime.now().astimezone().isoformat(timespec="minutes")
(ROOT / "data").mkdir(exist_ok=True)
(ROOT / "data" / f"hw{n}.json").write_text(json.dumps({"hw": int(n), "status": status, "sessions": 0, "sealed_at": now,
    "sealed": crypto.encode_sealed(sealed), "attachments": [att]}, indent=1))
print(f"public record -> data/hw{n}.json  commitment={sealed.commitment.hex()}")
print(f"OPENING (secret, give to whoever may read): {crypto.encode_opening(opening)}")
