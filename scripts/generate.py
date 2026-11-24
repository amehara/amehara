#!/usr/bin/env python3
"""Generates bento.svg from stats.json (see fetch_stats.py).

Usage: python scripts/generate.py            # reads ./stats.json, writes ./bento.svg
No third-party dependencies.
"""
import base64
import json
import os
from datetime import date
from xml.sax.saxutils import escape

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEMO = {
    "username": "amehara",
    "updated": date.today().isoformat(),
    "contributions": 312,
    "streak": 6,
    "last20": [0, 2, 1, 0, 0, 3, 4, 1, 0, 2, 5, 1, 0, 0, 2, 3, 1, 4, 2, 1],
    "lines": 48200,
    "repos": 9,
    "stars": 14,
    "followers": 21,
    "now": {"repo": "bento-readme", "message": "add daily stats workflow", "when": "today"},
}


def load_stats():
    p = os.path.join(ROOT, "stats.json")
    data = dict(DEMO)
    if os.path.exists(p):
        with open(p) as f:
            data.update(json.load(f))
    return data


def compact(n):
    n = int(n)
    if n < 1000:
        return str(n)
    if n < 100_000:
        return f"{n / 1000:.1f}".rstrip("0").rstrip(".") + "k"
    if n < 1_000_000:
        return f"{round(n / 1000)}k"
    return f"{n / 1_000_000:.1f}".rstrip("0").rstrip(".") + "m"


def wrap(s, width, lines):
    words, out, cur = s.split(), [], ""
    for w in words:
        if len(cur) + len(w) + (1 if cur else 0) <= width:
            cur = f"{cur} {w}".strip()
        else:
            out.append(cur)
            cur = w
    if cur:
        out.append(cur)
    if len(out) > lines:
        out = out[:lines]
        out[-1] = out[-1][: width - 1].rstrip() + "…"
    return out


W, H = 1200, 1180
COLS = [24, 316, 608, 900]
ROWS = [24, 272, 520, 768, 1016]
CW, RH = 276, 232
GRAY = "#a1a1a6"

with open(os.path.join(ROOT, "fonts", "sora-subset.woff2"), "rb") as f:
    FONT_B64 = base64.b64encode(f.read()).decode()

with open(os.path.join(ROOT, "fonts", "sora-outline-digits.woff2"), "rb") as f:
    OUTLINE_B64 = base64.b64encode(f.read()).decode()

FONT = "'Sora',-apple-system,'SF Pro Display','Helvetica Neue',Arial,sans-serif"

defs, body = [], []
_n = [0]


def uid(p):
    _n[0] += 1
    return f"{p}{_n[0]}"


def card(x, y, w, h, r=36, fill="#161618"):
    g = uid("g")
    defs.append(f'<linearGradient id="{g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".10"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"/>')
    body.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="url(#{g})"/>')
    body.append(f'<rect x="{x+.5}" y="{y+.5}" width="{w-1}" height="{h-1}" rx="{r}" fill="none" stroke="#fff" stroke-opacity=".12"/>')


def mesh(x, y, w, h, r, base, blobs, blur=42, gloss=.28):
    c, f, g = uid("c"), uid("f"), uid("g")
    defs.append(f'<clipPath id="{c}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/></clipPath>')
    defs.append(f'<filter id="{f}" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="{blur}"/></filter>')
    defs.append(f'<linearGradient id="{g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="{gloss}"/><stop offset=".4" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    s = f'<g clip-path="url(#{c})"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{base}"/><g filter="url(#{f})">'
    for bx, by, br, col in blobs:
        s += f'<circle cx="{x+bx}" cy="{y+by}" r="{br}" fill="{col}"/>'
    s += f'</g><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{g})"/></g>'
    s += f'<rect x="{x+.5}" y="{y+.5}" width="{w-1}" height="{h-1}" rx="{r}" fill="none" stroke="#fff" stroke-opacity=".35"/>'
    body.append(s)


def text(x, y, s, size, fill="#fff", weight=800, ls=-0.03, extra=""):
    body.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" letter-spacing="{ls}em" {extra}>{escape(str(s))}</text>')


def label(x, y, s, fill=GRAY):
    text(x, y, s, 14, fill, 600, 0.02)


def grad(id_, stops, x2=1, y2=0):
    st = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    defs.append(f'<linearGradient id="{id_}" x1="0" y1="0" x2="{x2}" y2="{y2}">{st}</linearGradient>')


def build(d):
    grad("txtPink", [(0, "#ff2d92"), (.55, "#ff7a45"), (1, "#ffc400")])
    grad("txtBlue", [(0, "#64d2ff"), (.55, "#7d7aff"), (1, "#ff5fa8")])
    grad("seg", [(0, "#64d2ff"), (1, "#bf5af2")])

    # ---- 1. hero (2x2) ----
    x, y = COLS[0], ROWS[0]
    card(x, y, 568, 480, 44, "#111113")
    text(x + 36, y + 70, "amehara", 34, "#fff", 800, -0.03)
    text(x + 36, y + 102, "ui/ux designer · design engineer", 17, GRAY, 600, 0)
    text(x + 36, y + 148, "i design interfaces", 21, "#e5e5ea", 500, -0.01)
    text(x + 36, y + 176, "and ship them.", 21, "#e5e5ea", 500, -0.01)
    text(x + 32, y + 322, "design", 160, "#fff", 800, -0.05, 'textLength="504" lengthAdjust="spacingAndGlyphs"')
    text(x + 32, y + 450, "to code", 148, "url(#txtPink)", 800, -0.05, 'textLength="504" lengthAdjust="spacingAndGlyphs"')

    # ---- 2. years ----
    x, y = COLS[2], ROWS[0]
    mesh(x, y, CW, RH, 36, "#ff8a00", [(60, 40, 100, "#ffd60a"), (250, 200, 110, "#ff6a00"), (230, 20, 60, "#ffcc00")])
    text(x + 22, y + 150, "2+", 150, "#0b0b0c", 800, -0.06)
    text(x + 26, y + 196, "years designing", 19, "#0b0b0c", 700, -0.01)
    text(x + 26, y + 220, "and building", 19, "#0b0b0c", 700, -0.01)

    # ---- 3. tall: contributions (outlined) ----
    x, y = COLS[3], ROWS[0]
    mesh(x, y, CW, 480, 36, "#2a1066", [(40, 60, 120, "#5e5ce6"), (240, 190, 130, "#d6247f"), (60, 420, 150, "#ff5e3a"), (250, 450, 100, "#ff3b30")], 48)
    label(x + 26, y + 46, "github", "#fff")
    s = compact(d["contributions"])
    size = 270 if len(s) <= 3 else 215
    tl = min(250, len(s) * 124)
    body.append(f'<text x="{x+14}" y="{y+316}" font-family="SoraOutline,Sora,sans-serif" font-size="{size}" font-weight="200" fill="none" stroke="#fff" stroke-width="5" stroke-linejoin="round" letter-spacing="-0.05em" textLength="{tl}" lengthAdjust="spacingAndGlyphs">{escape(s)}</text>')
    text(x + 26, y + 414, "contributions", 30, "#fff", 800, -0.03)
    text(x + 28, y + 446, "in the last year", 18, "#fff", 600, 0)

    # ---- 4. streak ----
    x, y = COLS[2], ROWS[1]
    card(x, y, CW, RH)
    label(x + 24, y + 42, "current streak")
    st = str(d["streak"])
    text(x + 22, y + 128, st, 92, "#fff", 800, -0.05)
    text(x + 30 + max(1, len(st)) * 62, y + 128, "days", 24, GRAY, 700, -0.01)
    bw, gap = 8, 3.6
    last = ([0] * 20 + d["last20"])[-20:]
    for i, c in enumerate(last):
        bx = x + 24 + i * (bw + gap)
        fill = "url(#seg)" if c else "#3a3a3c"
        body.append(f'<rect x="{bx:.1f}" y="{y+154}" width="{bw}" height="38" rx="4" fill="{fill}"/>')
    label(x + 24, y + 218, "last 20 days")

    # ---- 5. now (pill): last commit ----
    x, y = COLS[0], ROWS[2]
    card(x, y, 568, RH, 116, "#111113")
    body.append(f'<circle class="pulse" cx="{x+60}" cy="{y+66}" r="6" fill="#30d158"/>')
    label(x + 76, y + 71, "now · last commit")
    lines = wrap(d["now"]["message"].lower(), 19, 2)
    for i, ln in enumerate(lines):
        text(x + 52, y + 118 + i * 34, ln, 26, "#fff", 700, -0.03)
    text(x + 52, y + 118 + len(lines) * 34 + 12, f'{d["now"]["repo"]} · {d["now"]["when"]}', 15, GRAY, 600, 0)
    cx, cy = x + 568 - 116, y + 116
    rg = uid("rg")
    defs.append(f'<radialGradient id="{rg}" cx=".3" cy=".25" r=".9"><stop offset="0" stop-color="#ffd60a"/><stop offset=".45" stop-color="#ff2d92"/><stop offset=".8" stop-color="#5e5ce6"/><stop offset="1" stop-color="#64d2ff"/></radialGradient>')
    body.append(f'<circle cx="{cx}" cy="{cy}" r="84" fill="url(#{rg})"/>')
    body.append(f'<circle cx="{cx}" cy="{cy}" r="83" fill="none" stroke="#fff" stroke-opacity=".5" stroke-width="2"/>')
    body.append(f'<path d="M{cx-14} {cy-26} L{cx-42} {cy} L{cx-14} {cy+26} M{cx+14} {cy-26} L{cx+42} {cy} L{cx+14} {cy+26} M{cx+8} {cy-34} L{cx-8} {cy+34}" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>')

    # ---- 6. on ----
    x, y = COLS[2], ROWS[2]
    mesh(x, y, CW, RH, 36, "#30d158", [(240, 40, 100, "#ffd60a"), (30, 220, 100, "#a8ff78"), (150, 120, 60, "#d4fc79")])
    body.append(f'<rect x="{x+24}" y="{y+24}" width="60" height="34" rx="17" fill="#000" fill-opacity=".88"/><circle cx="{x+67}" cy="{y+41}" r="13" fill="#fff"/>')
    text(x + 20, y + 166, "on", 124, "#0b0b0c", 800, -0.06)
    text(x + 24, y + 208, "available for projects", 17, "#0b0b0c", 700, -0.01)

    # ---- 7. stack ----
    x, y = COLS[3], ROWS[2]
    card(x, y, CW, RH)
    label(x + 24, y + 42, "stack")
    chips = [("typescript", "#3178c6"), ("java", "#f89820"), ("python", "#ffd43b"), ("figma", "#ff7262"), ("react", "#61dafb"), ("next.js", "#ffffff")]
    cxp, cyp = x + 24, y + 62
    for name, col in chips:
        cw_ = len(name) * 9.4 + 40
        if cxp + cw_ > x + CW - 14:
            cxp, cyp = x + 24, cyp + 50
        body.append(f'<rect x="{cxp:.1f}" y="{cyp}" width="{cw_:.1f}" height="38" rx="19" fill="#fff" fill-opacity=".12"/>')
        body.append(f'<circle cx="{cxp+20:.1f}" cy="{cyp+19}" r="6" fill="{col}"/>')
        text(cxp + 33, cyp + 24.5, name, 14, "#fff", 600, 0)
        cxp += cw_ + 8

    # ---- 8. lines of code + account ----
    x, y = COLS[0], ROWS[3]
    card(x, y, CW, RH, 36, "#111113")
    label(x + 24, y + 42, "lines of code written")
    s = compact(d["lines"])
    size = 88 if len(s) <= 4 else 74
    text(x + 22, y + 122, s, size, "url(#txtBlue)", 800, -0.05, f'textLength="{min(232, round(size*0.62*len(s)))}" lengthAdjust="spacingAndGlyphs"')
    body.append(f'<line x1="{x+24}" y1="{y+148}" x2="{x+CW-24}" y2="{y+148}" stroke="#fff" stroke-opacity=".14"/>')
    for i, (v, l) in enumerate([(d["repos"], "repos"), (d["stars"], "stars"), (d["followers"], "followers")]):
        cxn = x + 24 + i * 82
        text(cxn, y + 188, compact(v), 26, "#fff", 800, -0.03)
        label(cxn, y + 210, l)

    # ---- 9. cta ----
    x, y = COLS[1], ROWS[3]
    mesh(x, y, 568, RH, 116, "#d4fc79", [(60, 60, 110, "#30d158"), (300, 230, 120, "#ffd60a"), (520, 60, 90, "#64d2ff"), (200, 200, 70, "#fff")], 44)
    text(x + 56, y + 134, "let's talk", 58, "#0b0b0c", 800, -0.04, 'textLength="300" lengthAdjust="spacingAndGlyphs"')
    text(x + 58, y + 176, "something beautiful in mind?", 17, "#0b0b0c", 600, -0.01)
    cx, cy = x + 568 - 116, y + 116
    body.append(f'<circle cx="{cx}" cy="{cy}" r="64" fill="#fff"/>')
    body.append(f'<path d="M{cx-26} {cy} H{cx+24} M{cx+6} {cy-20} L{cx+26} {cy} L{cx+6} {cy+20}" fill="none" stroke="#0b0b0c" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>')

    # ---- 10. :3 ----
    x, y = COLS[3], ROWS[3]
    mesh(x, y, CW, RH, 36, "#5b1480", [(40, 40, 110, "#ff2dd4"), (250, 210, 110, "#ff2d55"), (230, 30, 70, "#bf5af2")])
    text(x + 26, y + 150, ":3", 140, "#fff", 800, -0.06)
    text(x + 28, y + 204, "made with love", 18, "#fff", 700, -0.01)

    # ---- 11. footer band (light gradient, black text = max contrast) ----
    x, y = COLS[0], ROWS[4]
    mesh(x, y, 1152, 140, 44, "#fff1f6", [(110, 30, 120, "#ffc2e0"), (430, 130, 110, "#b9c6ff"), (760, 20, 110, "#ffcf8a"), (1090, 120, 130, "#ff9ec4"), (620, 80, 70, "#fff3b0")], 46, gloss=.4)
    text(x + 40, y + 102, "made by hand.", 84, "#0b0b0c", 800, -0.05)
    text(x + 1152 - 40, y + 82, f'updated {d["updated"]}', 19, "#0b0b0c", 700, 0, 'text-anchor="end"')

    style = (
        "@font-face{font-family:'Sora';font-weight:100 800;src:url(data:font/woff2;base64," + FONT_B64 + ") format('woff2')}"
        "@font-face{font-family:'SoraOutline';font-weight:200;src:url(data:font/woff2;base64," + OUTLINE_B64 + ") format('woff2')}"
        "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}.pulse{animation:pulse 1.6s ease-in-out infinite}"
        "@media (prefers-reduced-motion:reduce){.pulse{animation:none}}"
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}" role="img" aria-label="bento grid about amehara: ui/ux designer and design engineer">
<title>amehara · ui/ux designer · design engineer</title>
<style>{style}</style>
<defs>{"".join(defs)}</defs>
<rect width="{W}" height="{H}" rx="48" fill="#000"/>
{"".join(body)}
</svg>'''


if __name__ == "__main__":
    out = os.path.join(ROOT, "bento.svg")
    with open(out, "w") as f:
        f.write(build(load_stats()))
    print("wrote", out)
