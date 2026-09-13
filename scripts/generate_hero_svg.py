#!/usr/bin/env python3
"""
generate_hero_svg.py
Builds assets/hero.svg — an animated banner for the README hero section.
GitHub sanitizes <script> tags out of SVGs, but CSS animation defined in
a <style> block inside the SVG still runs in the browser when the SVG is
displayed as an <img>, so the glow / scanline / typing motion is real,
visible animation — not a static image pretending to move.

Pulls the repository count and star count from docs/data/stats.json when
available so the banner reflects real numbers; falls back to a neutral
tagline (no numbers) if the data hasn't been generated yet.
"""

import json
import os

BASE = os.path.dirname(__file__)
STATS_PATH = os.path.join(BASE, "..", "docs", "data", "stats.json")
OUT_PATH = os.path.join(BASE, "..", "assets", "hero.svg")

NAME = "RIFAT KHAN"
ROLE = "CYBERSECURITY · NETWORKING · LINUX · IoT SECURITY"

def load_tagline():
    try:
        with open(STATS_PATH) as f:
            data = json.load(f)
        if data.get("pending"):
            return "SECURITY ENGINEERING // SYSTEM STATUS: ONLINE"
        repos = data["totals"]["repositories"]
        stars = data["totals"]["stars"]
        return f"{repos} REPOSITORIES // {stars} STARS // STATUS: ONLINE"
    except Exception:
        return "SECURITY ENGINEERING // SYSTEM STATUS: ONLINE"


SVG_TEMPLATE = """<svg width="960" height="220" viewBox="0 0 960 220" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#05080B"/>
      <stop offset="100%" stop-color="#0A1620"/>
    </linearGradient>
    <linearGradient id="edge" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0%" stop-color="#2FD9E8" stop-opacity="0"/>
      <stop offset="50%" stop-color="#2FD9E8" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#2FD9E8" stop-opacity="0"/>
    </linearGradient>
    <pattern id="grid" width="28" height="28" patternUnits="userSpaceOnUse">
      <path d="M 28 0 L 0 0 0 28" fill="none" stroke="#12202A" stroke-width="1"/>
    </pattern>
    <style>
      .scan {{ animation: scan 4.5s linear infinite; }}
      @keyframes scan {{
        0% {{ transform: translateX(-960px); opacity: 0; }}
        10% {{ opacity: 1; }}
        90% {{ opacity: 1; }}
        100% {{ transform: translateX(960px); opacity: 0; }}
      }}
      .pulse {{ animation: pulse 2.2s ease-in-out infinite; transform-origin: center; }}
      @keyframes pulse {{
        0%, 100% {{ opacity: 0.5; r: 5; }}
        50% {{ opacity: 1; r: 7; }}
      }}
      .type {{
        font-family: 'Courier New', monospace;
        font-size: 15px;
        fill: #2FD9E8;
        letter-spacing: 2px;
        overflow: hidden;
        white-space: nowrap;
        animation: reveal 3s steps(60, end) 1 both, blink 1s step-end infinite;
      }}
      @keyframes reveal {{ from {{ clip-path: inset(0 100% 0 0); }} to {{ clip-path: inset(0 0 0 0); }} }}
      @keyframes blink {{ 50% {{ opacity: 0.55; }} }}
      .name {{ font-family: 'Segoe UI', Arial, sans-serif; font-weight: 700; fill: #E9F4F8; }}
      .role {{ font-family: 'Courier New', monospace; fill: #7C8A97; letter-spacing: 3px; }}
    </style>
  </defs>

  <rect width="960" height="220" fill="url(#bg)"/>
  <rect width="960" height="220" fill="url(#grid)"/>
  <rect y="0" width="960" height="3" fill="url(#edge)" class="scan"/>

  <circle cx="40" cy="40" r="6" fill="#3DDC84" class="pulse"/>
  <text x="58" y="45" class="role" font-size="12">SYSTEM ACTIVE</text>

  <text x="40" y="110" font-size="42" class="name">{name}</text>
  <text x="40" y="140" font-size="14" class="role">{role}</text>

  <text x="40" y="185" class="type">&gt; {tagline}_</text>

  <rect x="0.5" y="0.5" width="959" height="219" fill="none" stroke="#1B2733" stroke-width="1"/>
</svg>
"""


def main():
    tagline = load_tagline()
    svg = SVG_TEMPLATE.format(name=NAME, role=ROLE, tagline=tagline)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
