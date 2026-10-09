# Design brief — algorithms.nymo.finance

Reference: hermes-agent.nousresearch.com (studied 2026-10-09). What makes it work, and what we keep:

| Hermes does | We do (black & white, 1930s rubber-hose cartoon) |
|---|---|
| One saturated field (#0000f2) + one paper tone (#f2f2f2), nothing else | Ink `#111111` on paper `#f2f2f2`, nothing else. Greys only as halftone dots, never flat fills |
| Tall compressed display face for the hero, mono/condensed small caps for labels | Display: a 1930s poster/woodcut face (Google: `Rye` or `Limelight`). Labels: condensed caps (`League Gothic`). Body/mono: typewriter (`Courier Prime`) — the "office memo" voice of a transparency report |
| Engraving-style single-color illustration with radiating lines | Rubber-hose character drawn as inline SVG: pie-cut eyes, white gloves, noodle limbs, thick 6px outlines, halftone shading via an SVG `<pattern>` of dots. One mascot: an owl or a pencil with gloves (algorithms + handwriting) |
| Hard-edged rectangular buttons, hairline rules, generous grid | Same geometry, but corners slightly rounded like cel-drawn shapes; hairline rules become hand-drawn wobbly SVG strokes |
| Film-still screenshot framed in the page | Title-card framing: iris-wipe circle masks (SVG `clipPath`), "A Nymo Production" intertitle header, film-grain via SVG `feTurbulence` filter on the page background |

## Tech constraints (binding, from the weus stack)
- FastHTML + MonsterUI only. No JavaScript files, no `<script>` beyond what FastHTML/HTMX injects.
- All interactivity through HTMX attributes (form POST for the opening, `hx_post` for the verify partial).
- Styling: MonsterUI theme as base (`Theme.slate` or `Theme.zinc`), overridden by one `Style()` block in the headers that sets fonts and the two colors as CSS variables. Google Fonts via one `Link()` in headers.
- Illustrations are Python functions returning `Svg(...)` component trees in `ui_components.py`. Pure render, no I/O.
- Halftone, grain, iris masks: SVG filters and patterns, all in Python.

## Pages
1. `/` — title card: "AI-Usage Transparency, 601.433", mascot, one-paragraph contract, table of homeworks (status, sealed date, commitment prefix, sessions). Intertitle style.
2. `/hw/{n}` — "Reel N": commitment (full hex, monospace), sealed-at, a single input for the opening token, button "Open the vault". Without a valid opening the page shows the encrypted blob as a halftone-scrambled block (the ciphertext hex rendered small, like film static).
3. `/hw/{n}/open` (POST) — HTMX partial: on success, the report rendered as a typewritten memo plus the transcript (collapsible `<details>`), and a stamped badge "COMMITMENT VERIFIED" / "DOES NOT OPEN" (SVG rubber-stamp, rotated). The server never stores the opening.
4. `/policy` — the public statement from `docs/ai_policy_public.md`.

## Tone
Serious content, playful frame. The report itself is plain typewriter text; the cartoon lives only in the chrome (header, mascot, stamps, iris wipes). Nothing animates except HTMX swaps and a CSS-only blink on the mascot's eyes.
