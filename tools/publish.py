#!/usr/bin/env python3
"""Build the transparency site into site/.
Public (plaintext): docs/ai_policy_public.md, per-HW status, seal date, commitment hash, session counts.
Encrypted (AES-256-GCM, key printed only in the submitted PDF): the per-HW log itself.
Reads ONLY docs/ai_policy_public.md, hw/*/STATUS, hw/*/ai_log.md, hw/*/seal.json. Never feedback, .tex, photos."""
import datetime, html, json, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import sealing
root = pathlib.Path(__file__).resolve().parent.parent
out = root / "site"; out.mkdir(exist_ok=True)

def md(text: str) -> str:
    res = []
    for b in text.split("\n\n"):
        lines = b.strip().splitlines()
        if not lines: continue
        if lines[0].startswith("|"):
            rows = [[html.escape(c.strip()) for c in l.strip("|").split("|")] for l in lines if not re.match(r"^\|[-| ]+\|$", l)]
            res.append("<table><tr>" + "".join(f"<th>{c}</th>" for c in rows[0]) + "</tr>" +
                       "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows[1:]) + "</table>")
        elif lines[0].startswith("#"):
            lvl = len(lines[0]) - len(lines[0].lstrip("#"))
            res.append(f"<h{lvl}>{html.escape(lines[0].lstrip('# '))}</h{lvl}>")
            if len(lines) > 1: res.append("<p>" + html.escape(" ".join(lines[1:])) + "</p>")
        elif re.match(r"^\d+\.", lines[0]):
            items, cur = [], ""
            for l in lines:
                if re.match(r"^\d+\.", l):
                    if cur: items.append(cur)
                    cur = re.sub(r"^\d+\.\s*", "", l)
                else: cur += " " + l.strip()
            items.append(cur)
            res.append("<ol>" + "".join(f"<li>{html.escape(i)}</li>" for i in items) + "</ol>")
        else:
            res.append("<p>" + html.escape(" ".join(l.strip() for l in lines)) + "</p>")
    return "\n".join(res)

CSS = ("body{max-width:760px;margin:3rem auto;padding:0 1rem;font:16px/1.55 Georgia,serif;color:#222}"
       "table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #ccc;padding:.3rem .5rem;text-align:left;vertical-align:top}"
       "th{background:#f4f4f4}code,tt{background:#f4f4f4;padding:0 .2rem;font-size:13px;word-break:break-all}"
       ".status{display:inline-block;padding:.1rem .5rem;border-radius:4px;background:#eee;font-size:13px}"
       "input{font:inherit;padding:.3rem;width:18rem}button{font:inherit;padding:.3rem .8rem}.err{color:#b00}.ok{color:#080}")

# Browser-side decryption: same KDF/cipher as tools/sealing.py.
JS = r"""
async function decrypt(blob, key) {
  const b = s => Uint8Array.from(atob(s), c => c.charCodeAt(0));
  const pw = new TextEncoder().encode(key.replace(/-/g,'').toUpperCase().trim());
  const base = await crypto.subtle.importKey('raw', pw, 'PBKDF2', false, ['deriveKey']);
  const k = await crypto.subtle.deriveKey({name:'PBKDF2', salt:b(blob.salt), iterations:blob.iter, hash:'SHA-256'},
             base, {name:'AES-GCM', length:256}, false, ['decrypt']);
  const pt = await crypto.subtle.decrypt({name:'AES-GCM', iv:b(blob.nonce)}, k, b(blob.ct));
  return new TextDecoder().decode(pt);
}
async function sha256(s) {
  const h = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
  return [...new Uint8Array(h)].map(x => x.toString(16).padStart(2,'0')).join('');
}
function render(mdText) {  // minimal: heading + pipe table + paragraphs
  const esc = s => s.replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
  let out = '', rows = [];
  const flush = () => { if (rows.length) { out += '<table>' + rows.map((r,i) => '<tr>' + r.map(c => (i?'<td>':'<th>') + esc(c) + (i?'</td>':'</th>')).join('') + '</tr>').join('') + '</table>'; rows = []; } };
  for (const line of mdText.split('\n')) {
    if (/^\|[-| ]+\|$/.test(line)) continue;
    if (line.startsWith('|')) { rows.push(line.replace(/^\||\|$/g,'').split('|').map(s => s.trim())); continue; }
    flush();
    if (line.startsWith('#')) out += '<h3>' + esc(line.replace(/^#+\s*/, '')) + '</h3>';
    else if (line.trim()) out += '<p>' + esc(line) + '</p>';
  }
  flush(); return out;
}
async function open_(id) {
  const key = document.getElementById('key').value, msg = document.getElementById('msg');
  const blob = BLOBS[id]; msg.className = ''; msg.textContent = 'decrypting…';
  try {
    const text = await decrypt(blob, key);
    const h = await sha256(text);
    const want = blob.commitment;
    msg.className = (want && h !== want) ? 'err' : 'ok';
    msg.textContent = want ? (h === want ? 'decrypted; SHA-256 matches the published commitment ' + want.slice(0,12) + '…' : 'decrypted, but SHA-256 ' + h.slice(0,12) + '… does NOT match the commitment ' + want.slice(0,12) + '…')
                           : 'decrypted (latest blob, no fixed commitment)';
    document.getElementById('report').innerHTML = render(text);
  } catch (e) { msg.className = 'err'; msg.textContent = 'wrong key (or corrupted blob)'; }
}
"""

def page(title, body, blobs=None):
    script = f"<script>const BLOBS={json.dumps(blobs or {})};{JS}</script>"
    return (f"<!doctype html><meta charset=utf-8><meta name=viewport content='width=device-width'><title>{html.escape(title)}</title>"
            f"<style>{CSS}</style>{body}{script}<p><small>Built {datetime.date.today()}. Full session transcripts available to the instructors on request.</small></p>")

policy = md((root / "docs/ai_policy_public.md").read_text())
rows = []
for d in sorted(root.glob("hw/hw*"), key=lambda p: int(p.name[2:])):
    n = d.name[2:]
    status = (d / "STATUS").read_text().strip() if (d / "STATUS").exists() else "unknown"
    log, sealf = d / "ai_log.md", d / "seal.json"
    blobs, parts = {}, [f"<p><a href=index.html>&larr; all homeworks</a></p><h1>Homework {n} <span class=status>{html.escape(status)}</span></h1>"]
    nlog = sum(1 for l in log.read_text().splitlines() if l.startswith("| 20")) if log.exists() else 0
    if sealf.exists():
        seal = json.loads(sealf.read_text())
        b = sealing.encrypt(seal["key"], seal["snapshot"]); b["iter"] = sealing.ITER; b["commitment"] = seal["commitment"]
        blobs["sealed"] = b
        parts.append(f"<p><b>Sealed</b> {html.escape(seal['sealed_at'])} (at submission). <b>Commitment</b> SHA-256: <tt>{seal['commitment']}</tt></p>")
        if log.exists() and log.read_text() != seal["snapshot"]:
            b2 = sealing.encrypt(seal["key"], log.read_text()); b2["iter"] = sealing.ITER; b2["commitment"] = None
            blobs["latest"] = b2
        parts.append("<p>Enter the key printed in the header of the submitted PDF.</p>"
                     "<p><input id=key placeholder='XXXXX-XXXXX-XXXXX-XXXXX' autocomplete=off> "
                     "<button onclick=\"open_('sealed')\">open sealed report</button> "
                     + ("<button onclick=\"open_('latest')\">open latest (incl. post-submission)</button>" if "latest" in blobs else "")
                     + "</p><p id=msg></p><div id=report></div>")
        sealed_str = "sealed " + seal["sealed_at"][:10]
    else:
        parts.append(f"<p>Not sealed yet. Sessions logged so far: {nlog}. The log is encrypted and published when the homework is submitted.</p>")
        sealed_str = "not sealed"
    (out / f"hw{n}.html").write_text(page(f"HW{n} AI log", "".join(parts), blobs))
    rows.append(f"<tr><td><a href=hw{n}.html>HW{n}</a></td><td>{html.escape(status)}</td><td>{nlog}</td><td>{sealed_str}</td>"
                f"<td><tt>{json.loads(sealf.read_text())['commitment'][:16] + '…' if sealf.exists() else ''}</tt></td></tr>")
index = policy + ("<h2>Homeworks</h2><table><tr><th>HW</th><th>status</th><th>AI sessions</th><th>seal</th><th>commitment</th></tr>"
                  + "".join(rows) + "</table>")
(out / "index.html").write_text(page("AI usage transparency — 601.433", index))
print(f"built site/ with {len(rows)} homework pages")
