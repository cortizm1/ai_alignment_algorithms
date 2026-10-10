"""Inline-SVG mind map of the commitment scheme. Pure render, ink on paper, no JS."""

from __future__ import annotations

from typing import Any

from fasthtml.svg import Defs, G, Line, Marker, Path, Rect, Svg, Text

INK, PAPER = "#111111", "#f2f2f2"
MONO = "'Courier Prime','Courier New',monospace"
COND = "'League Gothic','Oswald',sans-serif"


def _box(x: int, y: int, w: int, h: int, title: str, lines: list[str], dashed: bool = False) -> Any:
    kids = [Rect(x=x, y=y, width=w, height=h, rx=12, fill=PAPER, stroke=INK, stroke_width=4,
                 stroke_dasharray="10 6" if dashed else "0"),
            Text(title, x=x + 12, y=y + 26, font_family=COND, font_size=20, letter_spacing=2, fill=INK)]
    for i, ln in enumerate(lines):
        kids.append(Text(ln, x=x + 12, y=y + 50 + i * 18, font_family=MONO, font_size=13, fill=INK))
    return G(*kids)


def _arrow(x1: int, y1: int, x2: int, y2: int, label: str = "", bend: int = 0, lx: int = 0, ly: int = 0) -> Any:
    d = f"M{x1} {y1} C {x1 + bend} {y1}, {x2 - bend} {y2}, {x2} {y2}" if bend else f"M{x1} {y1} L{x2} {y2}"
    kids = [Path(d=d, fill="none", stroke=INK, stroke_width=3, marker_end="url(#arrowhead)")]
    if label:
        x, y = (lx or (x1 + x2) // 2), (ly or (y1 + y2) // 2 - 8)
        kids.append(Rect(x=x - 4 - len(label) * 4, y=y - 14, width=len(label) * 8 + 8, height=18, fill=PAPER))
        kids.append(Text(label, x=x, y=y, font_family=COND, font_size=15, letter_spacing=1, fill=INK, text_anchor="middle"))
    return G(*kids)


def _lane(x: int, w: int, title: str) -> Any:
    return G(Rect(x=x, y=10, width=w, height=640, rx=16, fill="none", stroke=INK, stroke_width=2, stroke_dasharray="4 6"),
             Text(title, x=x + w // 2, y=38, font_family=COND, font_size=22, letter_spacing=3, fill=INK, text_anchor="middle"))


def scheme_diagram() -> Any:
    """Three lanes: sealing on Carlos's machine, what is published, what the grader does."""
    return Svg(
        Defs(Marker(Path(d="M0 0 L10 5 L0 10 Z", fill=INK), id="arrowhead", markerWidth="10", markerHeight="10",
                    refX="9", refY="5", orient="auto", markerUnits="userSpaceOnUse")),
        _lane(10, 330, "1 · SEAL (my machine, before deadline)"),
        _lane(355, 290, "2 · PUBLISH (site + git, anyone)"),
        _lane(660, 330, "3 · OPEN (grader, holds the PDF)"),
        # lane 1
        _box(30, 60, 290, 78, "INPUTS", ["R  = ai_log.md   (session report)", "T  = transcripts  (redacted)"]),
        _box(30, 160, 290, 96, "RANDOMNESS", ["r  <- random scalar   (blinding)", "k  <- random 256-bit key", "H  = hash_to_group(domain)"]),
        _box(30, 280, 290, 78, "HASH  (SHA3-256, sponge)", ["m  = SHA3-256(R)  mod q"]),
        _box(30, 380, 290, 78, "PEDERSEN COMMITMENT", ["C  = m*G + r*H     on ristretto255"]),
        _box(30, 480, 290, 96, "ENCRYPT  (ChaCha20-Poly1305)", ["ct   = Enc_k(R ; AD = C)", "ct_T = Enc_k(T ; AD = C)", "AD binds ciphertext to C"]),
        _arrow(175, 138, 175, 160), _arrow(175, 256, 175, 280), _arrow(175, 358, 175, 380), _arrow(175, 458, 175, 480),
        # lane 2
        _box(375, 200, 250, 118, "PUBLIC RECORD", ["C         (commitment)", "ct, ct_T  (ciphertexts)", "sealed_at (timestamp)", "git commit -> GitHub time"]),
        _box(375, 420, 250, 96, "PDF HEADER  (Gradescope)", ["opening = k . r   (hex)", "C          (for cross-check)", "URL of this reel"], dashed=True),
        _arrow(320, 419, 375, 259, "C", bend=30, lx=347, ly=330), _arrow(320, 528, 375, 270, "ct, ct_T", bend=30, lx=347, ly=410),
        _arrow(320, 208, 375, 468, "k, r", bend=40, lx=347, ly=200),
        # lane 3
        _box(680, 60, 290, 78, "PASTE OPENING", ["from the PDF header into /hw/N"]),
        _box(680, 160, 290, 96, "DECRYPT", ["R' = Dec_k(ct ; AD = C)", "T' = Dec_k(ct_T ; AD = C)", "Poly1305 tag fails => DOES NOT OPEN"]),
        _box(680, 280, 290, 78, "RECOMPUTE", ["m' = SHA3-256(R')  mod q"]),
        _box(680, 380, 290, 78, "CHECK", ["C  ==  m'*G + r*H   ?"]),
        _box(680, 480, 290, 96, "VERDICT", ["equal     => COMMITMENT VERIFIED", "not equal => DOES NOT OPEN", "server stores nothing"]),
        _arrow(825, 138, 825, 160), _arrow(825, 256, 825, 280), _arrow(825, 358, 825, 380), _arrow(825, 458, 825, 480),
        _arrow(625, 468, 680, 99, "opening", bend=40, lx=652, ly=160), _arrow(625, 259, 680, 208, "C, ct, ct_T", bend=30, lx=652, ly=330),
        # properties strip
        Rect(x=10, y=664, width=980, height=76, rx=12, fill=INK),
        Text("HIDING: r random, so C says nothing about R      BINDING: discrete log, so C opens to one R only",
             x=500, y=694, font_family=COND, font_size=17, letter_spacing=1, fill=PAPER, text_anchor="middle"),
        Text("CONFIDENTIAL: k lives only in the PDF      INTEGRITY: AEAD with AD = C, no swapping ciphertexts between reels",
             x=500, y=722, font_family=COND, font_size=17, letter_spacing=1, fill=PAPER, text_anchor="middle"),
        viewBox="0 0 1000 745", width="100%", role="img", aria_label="Diagram of the Pedersen commitment and ChaCha20 encryption scheme",
        style="max-width:1000px;display:block;margin:1rem auto",
    )
