#!/usr/bin/env python3
"""Seal homework N's AI log at submission time.
Usage: tools/seal.py 4
Writes hw/hwN/seal.json {key, commitment, sealed_at, snapshot} and prints the LaTeX lines to paste
into the header of hw/hwN/hwN.tex. The snapshot is immutable; later log entries go to a 'latest'
blob encrypted with the same key (see publish.py). Re-running refuses unless --force."""
import datetime, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sealing
root = pathlib.Path(__file__).resolve().parent.parent
n = sys.argv[1].lstrip("hw"); force = "--force" in sys.argv
d = root / f"hw/hw{n}"; log = d / "ai_log.md"; out = d / "seal.json"
if not log.exists(): sys.exit(f"no {log}; nothing to seal")
if out.exists() and not force: sys.exit(f"{out} exists; use --force to re-seal (this changes the commitment!)")
text = log.read_text()
seal = {"hw": int(n), "key": sealing.new_key(), "commitment": sealing.commitment(text),
        "sealed_at": datetime.datetime.now().astimezone().isoformat(timespec="minutes"), "snapshot": text}
out.write_text(json.dumps(seal, indent=1))
url = f"https://algorithms.nymo.finance/hw{n}.html"
print(f"sealed {log} -> {out}\n\nPaste into hw{n}.tex header:\n")
print(f"\\aireport{{{url}}}{{{seal['key']}}}{{{seal['commitment']}}}")
