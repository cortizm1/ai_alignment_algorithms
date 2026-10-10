"""Pure render functions for jhu.nymo.finance. Data in, FastHTML/MonsterUI components out. No I/O.

Look: black ink on paper, 1930s rubber-hose cartoon chrome (see docs/design_brief.md).
Everything visual is Python: SVG filters for film grain and halftone, SVG mascot, SVG stamps.
No JavaScript anywhere; the only interaction is one HTMX form post.
"""

from __future__ import annotations

from typing import Any

import markdown as md_lib
from fasthtml.common import (
    H1, H2, H3, A, Button, Details, Div, Form, Input, Label, Link, Meta, NotStr, P, Span, Style, Summary,
    Table, Tbody, Td, Th, Thead, Tr, ft_hx,
)
from fasthtml.svg import Circle, Defs, Ellipse, FeTurbulence, Filter, G, Line, Path, Pattern, Rect, Svg, Text
from monsterui.all import Theme

from web import config
from web.diagram import scheme_diagram

INK = "#111111"
PAPER = "#f2f2f2"

CSS = f"""
:root {{ --ink:{INK}; --paper:{PAPER}; --display:'Rye', serif; --condensed:'League Gothic', 'Oswald', sans-serif; --type:'Courier Prime', 'Courier New', monospace; }}
html, body {{ background: var(--paper) !important; color: var(--ink) !important; font-family: var(--type); }}
body {{ position: relative; }}
body::before {{ content:''; position: fixed; inset: 0; pointer-events: none; opacity: .07; filter: url(#grain); background: var(--ink); z-index: 0; mix-blend-mode: multiply; }}
.reel {{ position: relative; z-index: 1; max-width: 960px; margin: 0 auto; padding: 2rem 1.25rem 4rem; }}
.card {{ border: 4px solid var(--ink); border-radius: 18px; padding: 1.25rem 1.5rem; background: var(--paper); box-shadow: 8px 8px 0 var(--ink); }}
.title {{ font-family: var(--display); font-size: clamp(2.4rem, 7vw, 4.6rem); line-height: .95; letter-spacing: .01em; margin: 0; text-transform: uppercase; }}
.sub {{ font-family: var(--condensed); font-size: clamp(1.1rem, 3vw, 1.6rem); letter-spacing: .12em; text-transform: uppercase; margin: .4rem 0 0; }}
.meta {{ font-family: var(--condensed); letter-spacing: .14em; text-transform: uppercase; font-size: .85rem; }}
.rule {{ display:block; width: 100%; height: 14px; }}
.nav a {{ color: var(--ink); text-decoration: none; border-bottom: 3px solid var(--ink); font-family: var(--condensed); font-size: 1.15rem; letter-spacing: .12em; text-transform: uppercase; margin-right: 1.4rem; }}
.nav a:hover {{ background: var(--ink); color: var(--paper); }}
table.ledger {{ width: 100%; border-collapse: collapse; font-family: var(--type); font-size: .95rem; }}
table.ledger th {{ font-family: var(--condensed); letter-spacing: .12em; text-transform: uppercase; text-align: left; border-bottom: 4px solid var(--ink); padding: .5rem .4rem; font-weight: 400; font-size: 1.05rem; }}
table.ledger td {{ border-bottom: 2px solid var(--ink); padding: .55rem .4rem; vertical-align: top; }}
table.ledger a {{ color: var(--ink); font-weight: 700; }}
.badge {{ display:inline-block; border: 3px solid var(--ink); border-radius: 999px; padding: .05rem .6rem; font-family: var(--condensed); letter-spacing: .12em; text-transform: uppercase; font-size: .9rem; }}
.hex {{ font-family: var(--type); word-break: break-all; font-size: .8rem; background: repeating-linear-gradient(45deg, transparent 0 6px, rgba(17,17,17,.06) 6px 7px); padding: .5rem; border: 2px dashed var(--ink); }}
.static {{ font-family: var(--type); font-size: .62rem; line-height: 1.05; word-break: break-all; color: var(--ink); opacity: .55; max-height: 9rem; overflow: hidden; -webkit-mask-image: linear-gradient(#000 60%, transparent); mask-image: linear-gradient(#000 60%, transparent); }}
.btn {{ font-family: var(--condensed); letter-spacing: .14em; text-transform: uppercase; font-size: 1.1rem; background: var(--ink); color: var(--paper); border: 3px solid var(--ink); border-radius: 12px; padding: .5rem 1.2rem; cursor: pointer; box-shadow: 4px 4px 0 var(--paper), 4px 4px 0 3px var(--ink); }}
.btn:hover {{ background: var(--paper); color: var(--ink); }}
input.opening {{ width: 100%; font-family: var(--type); font-size: .95rem; border: 3px solid var(--ink); border-radius: 10px; padding: .6rem .8rem; background: var(--paper); color: var(--ink); }}
.memo {{ font-family: var(--type); line-height: 1.5; }}
.memo ol {{ list-style: decimal; padding-left: 1.6rem; }} .memo ol li {{ margin: .35rem 0; }} .memo p {{ margin: .6rem 0; }}
.memo h1, .memo h2, .memo h3 {{ font-family: var(--condensed); letter-spacing: .1em; text-transform: uppercase; }}
.memo table {{ border-collapse: collapse; width: 100%; font-size: .9rem; }}
.memo td, .memo th {{ border: 2px solid var(--ink); padding: .35rem .5rem; vertical-align: top; text-align: left; }}
.memo pre {{ white-space: pre-wrap; border-left: 4px solid var(--ink); padding-left: .8rem; font-size: .85rem; }}
details.transcript summary {{ cursor: pointer; font-family: var(--condensed); letter-spacing: .12em; text-transform: uppercase; font-size: 1.1rem; }}
.stamp {{ display:inline-block; transform: rotate(-6deg); margin: .5rem 0; }}
.footer {{ margin-top: 3rem; font-family: var(--condensed); letter-spacing: .14em; text-transform: uppercase; font-size: .8rem; text-align: center; }}
@keyframes blink {{ 0%, 92%, 100% {{ transform: scaleY(1); }} 96% {{ transform: scaleY(.08); }} }}
.eye {{ transform-origin: center; animation: blink 5.5s infinite; }}
"""


def headers() -> list[Any]:
    """Page headers: MonsterUI base theme, Google Fonts, our style block."""
    return [
        *Theme.zinc.headers(),
        Meta(name="viewport", content="width=device-width, initial-scale=1"),
        Meta(name="robots", content="noindex"),
        Link(rel="preconnect", href="https://fonts.googleapis.com"),
        Link(rel="stylesheet", href="https://fonts.googleapis.com/css2?family=Rye&family=League+Gothic&family=Courier+Prime:ital,wght@0,400;0,700;1,400&display=swap"),
        Style(CSS),
    ]


# ---- SVG furniture --------------------------------------------------------------


def grain_defs() -> Any:
    """Invisible SVG carrying the film-grain filter and the halftone pattern used by the page."""
    return Svg(
        Defs(
            Filter(FeTurbulence(type="fractalNoise", baseFrequency="0.9", numOctaves="2", stitchTiles="stitch"), id="grain"),
            Pattern(Circle(cx="3", cy="3", r="1.6", fill=INK), id="halftone", width="6", height="6", patternUnits="userSpaceOnUse"),
            Pattern(Circle(cx="4", cy="4", r="0.9", fill=INK), id="halftone-light", width="8", height="8", patternUnits="userSpaceOnUse"),
        ),
        width="0", height="0", style="position:absolute",
    )


def wobbly_rule() -> Any:
    """Hand-drawn horizontal rule."""
    return Svg(
        Path(d="M2 7 C 60 2, 120 12, 180 7 S 300 2, 360 7 S 480 12, 540 7 S 660 2, 720 7 S 840 12, 900 7 L 958 7",
             stroke=INK, stroke_width="4", fill="none", stroke_linecap="round"),
        viewBox="0 0 960 14", preserveAspectRatio="none", cls="rule",
    )


def mascot(size: int = 150) -> Any:
    """Rubber-hose owl: pie-cut eyes, white gloves holding a pencil, halftone belly. Inline SVG."""
    return Svg(
        # body
        Ellipse(cx="100", cy="118", rx="58", ry="62", fill=PAPER, stroke=INK, stroke_width="6"),
        Ellipse(cx="100", cy="132", rx="34", ry="38", fill="url(#halftone-light)", stroke="none"),
        # ear tufts
        Path(d="M58 70 L48 30 L80 58 Z", fill=INK), Path(d="M142 70 L152 30 L120 58 Z", fill=INK),
        # eyes (pie-cut pupils)
        Circle(cx="78", cy="92", r="22", fill=PAPER, stroke=INK, stroke_width="6"),
        Circle(cx="122", cy="92", r="22", fill=PAPER, stroke=INK, stroke_width="6"),
        G(Path(d="M78 92 L78 78 A14 14 0 1 1 66 98 Z", fill=INK), cls="eye"),
        G(Path(d="M122 92 L122 78 A14 14 0 1 1 110 98 Z", fill=INK), cls="eye"),
        # beak
        Path(d="M92 112 L108 112 L100 126 Z", fill=INK),
        # noodle arms + gloves
        Path(d="M50 130 C 20 140, 20 170, 48 172", stroke=INK, stroke_width="7", fill="none", stroke_linecap="round"),
        Path(d="M150 130 C 180 140, 180 170, 152 172", stroke=INK, stroke_width="7", fill="none", stroke_linecap="round"),
        Ellipse(cx="48", cy="176", rx="14", ry="11", fill=PAPER, stroke=INK, stroke_width="5"),
        Ellipse(cx="152", cy="176", rx="14", ry="11", fill=PAPER, stroke=INK, stroke_width="5"),
        # pencil in the right glove
        G(Rect(x="140", y="150", width="10", height="48", fill=PAPER, stroke=INK, stroke_width="4", transform="rotate(-35 145 174)"),
          Path(d="M157 142 L163 150 L151 154 Z", fill=INK, transform="rotate(-35 145 174)")),
        # feet
        Path(d="M80 178 L70 194 M86 180 L84 196 M120 178 L130 194 M114 180 L116 196", stroke=INK, stroke_width="6", stroke_linecap="round"),
        viewBox="0 0 200 200", width=str(size), height=str(size), role="img", aria_label="Rubber-hose owl mascot holding a pencil",
    )


def stamp(text: str, ok: bool) -> Any:
    """Rotated rubber stamp: VERIFIED or DOES NOT OPEN."""
    return Div(
        Svg(
            Rect(x="4", y="4", width="312", height="72", rx="12", fill="none", stroke=INK, stroke_width="6", stroke_dasharray="0" if ok else "14 8"),
            Rect(x="14", y="14", width="292", height="52", rx="8", fill="none", stroke=INK, stroke_width="2"),
            Text(text, x="160", y="52", text_anchor="middle", font_family="'League Gothic', 'Oswald', sans-serif", font_size="34", letter_spacing="4", fill=INK),
            viewBox="0 0 320 80", width="320", height="80", opacity="0.92",
        ),
        cls="stamp",
    )


def intertitle(title: str, sub: str = "") -> Any:
    """Title card like a silent-film intertitle."""
    return Div(H1(title, cls="title"), P(sub, cls="sub") if sub else None, wobbly_rule())


# ---- page shell -----------------------------------------------------------------


def nav() -> Any:
    return Div(A("Home", href="/"), A("Policy", href="/policy"), cls="nav", style="margin-bottom:1.5rem")


def page(*content: Any) -> Any:
    return Div(grain_defs(), nav(), *content,
               P(f"A Nymo Production · {config.COURSE}", cls="footer"), cls="reel")


def error_card(message: str) -> Any:
    return Div(H3("Reel jammed"), P(message, cls="memo"), cls="card")


def md(text: str) -> Any:
    """Markdown -> components (python-markdown, server side)."""
    return Div(NotStr(md_lib.markdown(text, extensions=["tables", "fenced_code"])), cls="memo")


# ---- pages ----------------------------------------------------------------------


def home_page(recs: list[dict[str, Any]]) -> Any:
    rows = [
        Tr(
            Td(A(f"Reel {r['hw']}", href=f"/hw/{r['hw']}")),
            Td(Span(r.get("status", "unknown"), cls="badge")),
            Td(str(r.get("sessions", 0))),
            Td(r.get("sealed_at", "")[:16].replace("T", " ") or "not yet"),
            Td(Span((r.get("sealed") or {}).get("commitment", "")[:16] + ("…" if r.get("sealed") else ""), cls="hex") if r.get("sealed") else ""),
        )
        for r in recs
    ]
    return page(
        Div(
            Div(
                Div(intertitle("AI-usage transparency", "Every homework, every session, on the record"), style="flex:1 1 60%"),
                Div(mascot(190), style="flex:0 0 auto;align-self:center"),
                style="display:flex;gap:1.5rem;flex-wrap:wrap;align-items:flex-start",
            ),
            P("I attempt every problem by hand. An AI tool may name gaps in a finished draft and type my pages "
              "into LaTeX word for word. It never solves. Each homework's session log and full transcript are "
              "sealed with a Pedersen commitment before the deadline and published encrypted. The opening is "
              "printed in the header of the submitted PDF, so the graders, and only they, can verify and read.", cls="memo"),
            P(A("Read the full policy and the cryptographic scheme →", href="/policy"), cls="meta"),
            cls="card",
        ),
        H2("The ledger", cls="sub", style="margin-top:2.5rem"),
        Table(Thead(Tr(Th("Reel"), Th("Status"), Th("AI sessions"), Th("Sealed"), Th("Commitment"))), Tbody(*rows), cls="ledger")
        if rows else P("No reels yet.", cls="memo"),
    )


def policy_page(markdown_text: str) -> Any:
    return page(
        intertitle("The policy", "What the tool may and may not do"),
        Div(md(markdown_text), cls="card"),
        H2("The scheme, as a map", cls="sub", style="margin-top:2.5rem"),
        Div(scheme_diagram(), cls="card", style="padding:.5rem"),
    )


def hw_page(rec: dict[str, Any]) -> Any:
    n = rec["hw"]
    sealed = rec.get("sealed")
    head = intertitle(f"Reel {n}", f"Homework {n} · {rec.get('status', 'unknown')}")
    if not sealed:
        body = Div(P(f"Not sealed yet. AI sessions logged so far: {rec.get('sessions', 0)}. "
                     "The log is sealed and published when the homework is submitted.", cls="memo"), cls="card")
        return page(head, body)
    body = Div(
        P(Span("Sealed", cls="meta"), " ", rec.get("sealed_at", "")[:16].replace("T", " "), cls="memo"),
        P(Span("Pedersen commitment (ristretto255)", cls="meta"), cls="memo"),
        Div(sealed["commitment"], cls="hex"),
        P(Span("Ciphertext (ChaCha20-Poly1305)", cls="meta"), cls="memo", style="margin-top:1rem"),
        Div(sealed["ciphertext"], cls="static"),
        Form(
            Label("Opening, from the header of the submitted PDF", cls="meta", **{"for": "opening"}),
            Input(id="opening", name="opening", cls="opening", placeholder="<64 hex>.<64 hex>", autocomplete="off", spellcheck="false"),
            Button("Open the vault", cls="btn", type="submit", style="margin-top:.8rem"),
            hx_post=f"/hw/{n}/open", hx_target="#verdict", hx_swap="innerHTML", style="margin-top:1.4rem",
        ),
        Div(id="verdict"),
        cls="card",
    )
    return page(head, body)


def verdict_partial(opened: Any) -> Any:
    """HTMX partial rendered into #verdict."""
    if not opened.ok:
        return Div(stamp("DOES NOT OPEN", ok=False), P(opened.message, cls="memo"))
    parts = [stamp("COMMITMENT VERIFIED", ok=True), P(opened.message, cls="memo"), wobbly_rule(), md(opened.report)]
    if opened.transcript:
        parts.append(Details(Summary("Full session transcript (redacted of credentials)"), md(opened.transcript), cls="transcript"))
    return Div(*parts)
