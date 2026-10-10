#!/usr/bin/env python3
"""Seal homework N at submission time (Pedersen commitment + ChaCha20-Poly1305).

Usage: tools/seal.py N [--force]
Inputs : hw/hwN/ai_log.md (the report), hw/transcripts/*.md (redacted transcripts, all sessions so far)
Writes : hw/hwN/seal.json  (SECRET: opening + snapshot; gitignored)
         data/hwN.json     (PUBLIC: commitment, ciphertexts, status, sealed_at; served by the site)
Prints : the \\aireport line for the LaTeX header. Then run tools/deploy_server.sh data BEFORE submitting."""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from transparency import crypto  # noqa: E402

n = sys.argv[1].lstrip("hw") if len(sys.argv) > 1 else sys.exit(__doc__)
force = "--force" in sys.argv
hwdir, data = ROOT / f"hw/hw{n}", ROOT / "data"
log, secret, public = hwdir / "ai_log.md", hwdir / "seal.json", data / f"hw{n}.json"
if not log.exists():
    sys.exit(f"no {log}; nothing to seal")
if secret.exists() and not force:
    sys.exit(f"{secret} exists; --force re-seals and CHANGES the commitment")

subprocess.run([sys.executable, "-I", str(ROOT / "tools/export_transcript.py")], check=True, capture_output=True)
transcripts = sorted((ROOT / "hw/transcripts").glob("*.md"))
transcript_md = "\n\n---\n\n".join(t.read_text() for t in transcripts)

report = log.read_bytes()
sealed, opening = crypto.seal(report)
attachment = crypto.seal_attachment(transcript_md.encode(), sealed.commitment, opening)
now = dt.datetime.now().astimezone().isoformat(timespec="minutes")
status = (hwdir / "STATUS").read_text().strip() if (hwdir / "STATUS").exists() else "unknown"
sessions = sum(1 for line in log.read_text().splitlines() if line.startswith("| 20"))

secret.write_text(json.dumps({"hw": int(n), "opening": crypto.encode_opening(opening), "sealed_at": now,
                              "commitment": sealed.commitment.hex(), "snapshot": report.decode()}, indent=1))
data.mkdir(exist_ok=True)
public.write_text(json.dumps({"hw": int(n), "status": status, "sessions": sessions, "sealed_at": now,
                              "sealed": crypto.encode_sealed(sealed), "transcript": attachment,
                              "transcript_sessions": [t.name for t in transcripts]}, indent=1))
url = f"https://jhu.nymo.finance/hw/{n}"
print(f"sealed -> {public} (public) and {secret} (secret)\n\nPaste into hw{n}.tex header, then rebuild:\n")
print(f"\\aireport{{{url}}}{{{crypto.encode_opening(opening)}}}{{{sealed.commitment.hex()}}}")
print("\nThen: tools/deploy_server.sh data   (publish the commitment BEFORE submitting on Gradescope)")
