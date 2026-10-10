#!/usr/bin/env python3
"""Seal an arbitrary file as a reel (demo / non-homework). Usage: tools/seal_file.py N FILE [status] [--public-opening]
--public-opening publishes the opening in the record (for a try-it-yourself reel).
The report is a short markdown note; the file itself is an encrypted attachment with its mime type
(PDFs render inline in the browser and can be downloaded after a successful opening).
Writes data/hwN.json (public) and prints the opening (secret)."""
import datetime as dt, hashlib, json, mimetypes, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent; sys.path.insert(0, str(ROOT))
from transparency import crypto  # noqa: E402
args = [a for a in sys.argv[1:] if not a.startswith("--")]; public_opening = "--public-opening" in sys.argv
n, src = args[0], pathlib.Path(args[1]); status = args[2] if len(args) > 2 else "demo"
mime = mimetypes.guess_type(src.name)[0] or "application/octet-stream"
raw = src.read_bytes()
report = f"# Reel {n}: {status}\n\nSealed file: `{src.name}` ({mime}, {len(raw):,} bytes, SHA3-256 {hashlib.sha3_256(raw).hexdigest()}).\n\nThis reel exists so that anyone can try opening a commitment end to end: the opening below is public on purpose.\n".encode()
sealed, opening = crypto.seal(report)
att = {"name": src.name, "mime": mime, "sha3": hashlib.sha3_256(raw).hexdigest(), **crypto.seal_attachment(raw, sealed.commitment, opening)}
now = dt.datetime.now().astimezone().isoformat(timespec="minutes")
(ROOT / "data").mkdir(exist_ok=True)
(ROOT / "data" / f"hw{n}.json").write_text(json.dumps({"hw": int(n), "status": status, "sessions": 0, "sealed_at": now,
    "sealed": crypto.encode_sealed(sealed), "attachments": [att],
    **({"public_opening": crypto.encode_opening(opening)} if public_opening else {})}, indent=1))
print(f"public record -> data/hw{n}.json  commitment={sealed.commitment.hex()}")
print(f"OPENING (secret, give to whoever may read): {crypto.encode_opening(opening)}")
