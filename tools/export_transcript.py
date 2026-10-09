#!/usr/bin/env python3
"""Export Claude Code session transcripts for this project to redacted Markdown.

Usage: tools/export_transcript.py [--out DIR] [--since YYYY-MM-DD] [SESSION_ID ...]
Default: every session of this project -> hw/transcripts/<date>-<session>.md

Redaction: every value found in the secret files (api_token.txt, ~/.config/nymo/*.env,
.env, site/deploy.env) is replaced by [REDACTED]; plus generic long-token patterns.
The exporter refuses to write a file that still contains a known secret.
Transcripts are published ENCRYPTED only (same opening as the HW report), never in plaintext:
they contain problem text, Carlos's claims, and critique, all of which syllabus §4 forbids publishing."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROJECT_KEY = "-" + str(ROOT).strip("/").replace("/", "-").replace("_", "-")
SESS_DIR = pathlib.Path.home() / ".claude" / "projects" / PROJECT_KEY
SECRET_FILES = [ROOT / "api_token.txt", ROOT / ".env", ROOT / "site" / "deploy.env",
                *pathlib.Path.home().glob(".config/nymo/*.env")]
GENERIC_PATTERNS = [
    r"\b[A-Z0-9]{32}\b",                      # orangewebsite-style tokens
    r"\b(?:ghp|gho|ghu|ghs|github_pat)_[A-Za-z0-9_]{20,}\b",
    r"\bsk-[A-Za-z0-9_-]{20,}\b",
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----",
    r"\b[0-9a-f]{64}\.[0-9a-f]{64}\b",        # a transparency opening token, should never be in a transcript
]


def load_secrets() -> list[str]:
    vals: list[str] = []
    for f in SECRET_FILES:
        if not f.exists():
            continue
        for line in f.read_text().splitlines():
            v = line.split("=", 1)[-1].strip().strip("'\"")
            if len(v) >= 12:
                vals.append(v)
    return vals


def redact(text: str, secrets: list[str]) -> str:
    for s in secrets:
        text = text.replace(s, "[REDACTED]")
    for p in GENERIC_PATTERNS:
        text = re.sub(p, "[REDACTED]", text)
    return text


def block_to_md(b: dict) -> str:
    t = b.get("type")
    if t == "text":
        return b.get("text", "")
    if t == "thinking":
        return "<details><summary>thinking</summary>\n\n" + b.get("thinking", "") + "\n\n</details>"
    if t == "tool_use":
        return f"**tool call `{b.get('name')}`**\n\n```json\n{json.dumps(b.get('input', {}), indent=1, ensure_ascii=False)}\n```"
    if t == "tool_result":
        c = b.get("content")
        if isinstance(c, list):
            c = "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
        return f"**tool result**\n\n```\n{c}\n```"
    if t == "image":
        return "*(image)*"
    return f"*({t})*"


def export(path: pathlib.Path, secrets: list[str]) -> tuple[str, str]:
    lines, first_ts = [], None
    for raw in path.read_text().splitlines():
        try:
            o = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if o.get("type") not in ("user", "assistant"):
            continue
        ts = o.get("timestamp", "")
        first_ts = first_ts or ts
        m = o.get("message", {})
        content = m.get("content")
        if isinstance(content, str):
            body = content
        else:
            body = "\n\n".join(block_to_md(b) for b in content or [] if isinstance(b, dict))
        body = re.sub(r"<system-reminder>[\s\S]*?</system-reminder>", "", body).strip()
        if not body:
            continue
        who = "Carlos" if o["type"] == "user" else "Claude"
        lines.append(f"### {who} · {ts[:19].replace('T', ' ')}\n\n{body}\n")
    md = f"# Session {path.stem}\n\nProject: {ROOT.name} · exported {dt.date.today()} · redacted\n\n" + "\n".join(lines)
    md = redact(md, secrets)
    for s in secrets:
        if s in md:
            sys.exit(f"REFUSING to write: a known secret survived redaction in {path.name}")
    return (first_ts or "")[:10], md


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("sessions", nargs="*")
    ap.add_argument("--out", default=str(ROOT / "hw" / "transcripts"))
    ap.add_argument("--since", default="")
    a = ap.parse_args()
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    secrets = load_secrets()
    files = [SESS_DIR / f"{s}.jsonl" for s in a.sessions] if a.sessions else sorted(SESS_DIR.glob("*.jsonl"))
    for f in files:
        date, md = export(f, secrets)
        if a.since and date < a.since:
            continue
        dest = out / f"{date or 'undated'}-{f.stem[:8]}.md"
        dest.write_text(md)
        print(f"{dest.relative_to(ROOT)}  ({len(md)//1024} KB)")


if __name__ == "__main__":
    main()
