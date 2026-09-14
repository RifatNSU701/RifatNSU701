#!/usr/bin/env python3
"""Generate a premium language analytics SVG from docs/data/stats.json."""

import json
import math
import os

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "docs", "data", "stats.json")
OUT = os.path.join(ROOT, "assets", "language-analytics.svg")

PALETTE = ["#2FD9E8", "#FFB84D", "#8B7CFF", "#54D17A", "#FF6B8A", "#7FD6FF", "#C58CFF", "#66E0C2"]
BG = "#05080B"
PANEL = "#0A1016"
GRID = "#1B2833"
TEXT = "#DCE6EE"
MUTED = "#7F929F"


def esc(value):
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def polar(cx, cy, r, angle):
    a = math.radians(angle - 90)
    return cx + r * math.cos(a), cy + r * math.sin(a)


def arc_path(cx, cy, r, start, end):
    x1, y1 = polar(cx, cy, r, start)
    x2, y2 = polar(cx, cy, r, end)
    large = 1 if end - start > 180 else 0
    return f"M {x1:.2f} {y1:.2f} A {r} {r} 0 {large} 1 {x2:.2f} {y2:.2f}"


def main():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)

    languages = data.get("languages", [])
    if not languages:
        return

    top = languages[:5]
    other_percent = max(0, 100 - sum(x["percent"] for x in top))
    donut = top + ([{"name": "Other", "percent": round(other_percent, 2)}] if other_percent > 0 else [])

    total = sum(x["percent"] for x in donut) or 1
    cx, cy, radius = 195, 205, 112
    start = 0
    donut_parts = []
    for i, item in enumerate(donut):
        sweep = item["percent"] / total * 360
        end = start + sweep
        color = PALETTE[i % len(PALETTE)]
        donut_parts.append(f'<path d="{arc_path(cx, cy, radius, start, end)}" stroke="{color}" stroke-width="30" fill="none" stroke-linecap="round"/>')
        start = end

    bars = []
    bar_x = 475
    bar_y = 86
    bar_w = 410
    row_h = 42
    max_pct = max(x["percent"] for x in languages) or 1
    for i, item in enumerate(languages):
        y = bar_y + i * row_h
        width = item["percent"] / max_pct * bar_w
        color = PALETTE[i % len(PALETTE)]
        bars.append(f'<text x="{bar_x}" y="{y + 7}" fill="{TEXT}" font-size="13" font-family="Inter,Segoe UI,sans-serif">{esc(item["name"])}</text>')
        bars.append(f'<rect x="{bar_x + 105}" y="{y - 7}" width="{bar_w}" height="10" rx="5" fill="{GRID}"/>')
        bars.append(f'<rect x="{bar_x + 105}" y="{y - 7}" width="{width:.1f}" height="10" rx="5" fill="{color}"/>')
        bars.append(f'<text x="{bar_x + 535}" y="{y + 7}" fill="{color}" font-size="12" text-anchor="end" font-family="Inter,Segoe UI,sans-serif">{item["percent"]:.2f}%</text>')

    legend = []
    ly = 346
    for i, item in enumerate(donut):
        x = 52 + (i % 3) * 118
        y = ly + (i // 3) * 24
        color = PALETTE[i % len(PALETTE)]
        legend.append(f'<circle cx="{x}" cy="{y - 4}" r="4" fill="{color}"/>')
        legend.append(f'<text x="{x + 10}" y="{y}" fill="{MUTED}" font-size="11" font-family="Inter,Segoe UI,sans-serif">{esc(item["name"])}</text>')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="620" viewBox="0 0 960 620" role="img" aria-label="GitHub language analytics">
<defs>
  <linearGradient id="panel" x1="0" x2="1"><stop offset="0" stop-color="#0A1016"/><stop offset="1" stop-color="#0D151D"/></linearGradient>
  <filter id="glow"><feGaussianBlur stdDeviation="3" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="960" height="620" rx="22" fill="{BG}"/>
<rect x="18" y="18" width="924" height="584" rx="18" fill="url(#panel)" stroke="#15222C"/>
<text x="48" y="58" fill="{TEXT}" font-size="19" font-weight="700" font-family="Inter,Segoe UI,sans-serif">LANGUAGE ANALYTICS</text>
<text x="48" y="80" fill="{MUTED}" font-size="11" font-family="Inter,Segoe UI,sans-serif">Repository code distribution · live data snapshot</text>
<line x1="48" y1="96" x2="912" y2="96" stroke="{GRID}"/>
<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{GRID}" stroke-width="30"/>
{''.join(donut_parts)}
<circle cx="{cx}" cy="{cy}" r="77" fill="{PANEL}"/>
<text x="{cx}" y="{cy - 2}" fill="{TEXT}" font-size="24" font-weight="700" text-anchor="middle" font-family="Inter,Segoe UI,sans-serif">{languages[0]['percent']:.1f}%</text>
<text x="{cx}" y="{cy + 19}" fill="{MUTED}" font-size="11" text-anchor="middle" font-family="Inter,Segoe UI,sans-serif">top language</text>
{''.join(legend)}
<text x="475" y="128" fill="{TEXT}" font-size="13" font-weight="600" font-family="Inter,Segoe UI,sans-serif">Language share</text>
{''.join(bars)}
<text x="48" y="575" fill="{MUTED}" font-size="10" font-family="Inter,Segoe UI,sans-serif">Generated automatically from GitHub repository language byte counts</text>
<text x="912" y="575" fill="{MUTED}" font-size="10" text-anchor="end" font-family="Inter,Segoe UI,sans-serif">RifatNSU701</text>
</svg>'''

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
