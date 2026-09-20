#!/usr/bin/env python3
"""Generate a premium, data-driven GitHub Intelligence SVG for README.md."""
import json
import os
import html
from datetime import datetime

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(ROOT, "docs", "data", "stats.json")
OUTPUT = os.path.join(ROOT, "assets", "github-intelligence.svg")

BG = "#081018"
TEXT = "#F2F6FA"
MUTED = "#91A4B7"
GRID = "#243541"
CYAN = "#2FD9E8"
BLUE = "#2F9BF4"
PURPLE = "#8B68F5"
GREEN = "#39C98A"
AMBER = "#FFB52E"
PINK = "#F06B78"

def esc(value):
    return html.escape(str(value), quote=True)

def short_repo(name, limit=25):
    return name if len(name) <= limit else name[:limit-1] + "…"

def main():
    with open(DATA, encoding="utf-8") as handle:
        data = json.load(handle)

    profile = data.get("profile", {})
    totals = data.get("totals", {})
    repos = sorted(data.get("repositories", []), key=lambda r: (r.get("stars") or 0), reverse=True)
    activity = data.get("recent_activity", [])
    contributions = data.get("contributions")
    generated = data.get("generated_at", "")
    try:
        generated_label = datetime.fromisoformat(generated.replace("Z", "+00:00")).strftime("%d %b %Y · %H:%M UTC")
    except ValueError:
        generated_label = "Live repository data"

    width, height = 1200, 980
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">GitHub Intelligence</title>',
        '<desc id="desc">Dynamically generated GitHub profile statistics, repository activity and contribution data.</desc>',
        '<defs>',
        '<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0A1118"/><stop offset="1" stop-color="#071017"/></linearGradient>',
        '<linearGradient id="cyanBar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#2FD9E8"/><stop offset="1" stop-color="#2F9BF4"/></linearGradient>',
        '</defs>',
        f'<rect x="10" y="10" width="1180" height="960" rx="18" fill="url(#bg)" stroke="{GRID}"/>',
        '<rect x="11" y="11" width="1178" height="958" rx="17" fill="none" stroke="#13212B"/>',
        '<g font-family="Inter,Segoe UI,Arial,sans-serif">',
        f'<text x="58" y="68" font-size="34" font-weight="700" fill="{TEXT}">GitHub <tspan fill="{CYAN}">Intelligence</tspan></text>',
        f'<text x="58" y="100" font-size="17" fill="{MUTED}">Live repository metrics, activity and contribution telemetry</text>',
        '<g transform="translate(1015 48)"><rect width="125" height="36" rx="18" fill="#071D1A" stroke="#126D61"/><circle cx="19" cy="18" r="6" fill="#31E6B4"/><text x="34" y="24" font-size="14" fill="#31E6B4">Live Data</text></g>',
        f'<text x="1140" y="106" text-anchor="end" font-size="12" fill="{MUTED}">Updated {esc(generated_label)}</text>',
    ]

    cards = [
        ("Repositories", totals.get("repositories"), CYAN),
        ("Stars", totals.get("stars"), AMBER),
        ("Forks", totals.get("forks"), PURPLE),
        ("Open Issues", totals.get("open_issues"), PINK),
        ("Pull Requests", totals.get("pull_requests"), GREEN),
        ("Followers", profile.get("followers"), BLUE),
    ]
    card_w, card_h, gap = 170, 104, 14
    start_x, start_y = 58, 132
    for i, (label, value, color) in enumerate(cards):
        x = start_x + i * (card_w + gap)
        shown = "—" if value is None else f"{value:,}"
        svg.extend([
            f'<rect x="{x}" y="{start_y}" width="{card_w}" height="{card_h}" rx="12" fill="#0B151D" stroke="{GRID}"/>',
            f'<rect x="{x}" y="{start_y}" width="4" height="{card_h}" rx="2" fill="{color}"/>',
            f'<text x="{x+18}" y="{start_y+34}" font-size="27" font-weight="700" fill="{TEXT}">{esc(shown)}</text>',
            f'<text x="{x+18}" y="{start_y+65}" font-size="13" fill="{MUTED}">{esc(label)}</text>',
        ])

    # Repository stars chart
    panel_x, panel_y, panel_w, panel_h = 58, 264, 540, 360
    svg.extend([
        f'<rect x="{panel_x}" y="{panel_y}" width="{panel_w}" height="{panel_h}" rx="14" fill="#0B151D" stroke="{GRID}"/>',
        f'<text x="{panel_x+24}" y="{panel_y+34}" font-size="19" font-weight="700" fill="{TEXT}">Repository Stars</text>',
        f'<text x="{panel_x+24}" y="{panel_y+58}" font-size="12" fill="{MUTED}">Top repositories by current star count</text>',
    ])
    star_repos = repos[:6]
    max_stars = max([r.get("stars") or 0 for r in star_repos] + [1])
    for i, repo in enumerate(star_repos):
        y = panel_y + 91 + i * 43
        stars = repo.get("stars") or 0
        bar_w = 330 * stars / max_stars if max_stars else 0
        svg.extend([
            f'<text x="{panel_x+24}" y="{y+5}" font-size="12" fill="{TEXT}">{esc(short_repo(repo.get("name","")))}</text>',
            f'<rect x="{panel_x+174}" y="{y-7}" width="330" height="14" rx="7" fill="#16242D"/>',
            f'<rect x="{panel_x+174}" y="{y-7}" width="{bar_w:.1f}" height="14" rx="7" fill="url(#cyanBar)"/>',
            f'<text x="{panel_x+515}" y="{y+5}" text-anchor="end" font-size="12" font-weight="700" fill="{CYAN}">{stars}</text>',
        ])

    # Activity timeline
    ax, ay, aw, ah = 620, 264, 522, 360
    svg.extend([
        f'<rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" rx="14" fill="#0B151D" stroke="{GRID}"/>',
        f'<text x="{ax+24}" y="{ay+34}" font-size="19" font-weight="700" fill="{TEXT}">Recent Public Activity</text>',
        f'<text x="{ax+24}" y="{ay+58}" font-size="12" fill="{MUTED}">Latest events returned by the GitHub API</text>',
    ])
    for i, event in enumerate(activity[:8]):
        y = ay + 91 + i * 31
        typ = str(event.get("type") or "Activity").replace("Event", "")
        repo_name = short_repo(event.get("repo") or "GitHub", 28)
        created = str(event.get("created_at") or "")
        date_label = created[:10] if len(created) >= 10 else ""
        color = [CYAN, BLUE, GREEN, PURPLE, AMBER, PINK][i % 6]
        svg.extend([
            f'<circle cx="{ax+27}" cy="{y-3}" r="5" fill="{color}"/>',
            f'<text x="{ax+42}" y="{y+1}" font-size="12" fill="{TEXT}">{esc(typ)}</text>',
            f'<text x="{ax+155}" y="{y+1}" font-size="11" fill="{MUTED}">{esc(repo_name)}</text>',
            f'<text x="{ax+488}" y="{y+1}" text-anchor="end" font-size="10" fill="{MUTED}">{esc(date_label)}</text>',
        ])

    # Contribution panel
    cx, cy, cw, ch = 58, 646, 1084, 250
    svg.extend([
        f'<rect x="{cx}" y="{cy}" width="{cw}" height="{ch}" rx="14" fill="#0B151D" stroke="{GRID}"/>',
        f'<text x="{cx+24}" y="{cy+35}" font-size="19" font-weight="700" fill="{TEXT}">Contribution Activity</text>',
    ])

    if contributions and contributions.get("days"):
        days = contributions["days"]
        total_contrib = contributions.get("total", 0)
        svg.append(f'<text x="{cx+24}" y="{cy+61}" font-size="12" fill="{MUTED}">{total_contrib:,} contributions in the available calendar</text>')
        recent = days[-364:]
        max_count = max([d.get("count", 0) for d in recent] + [1])
        grid_x, grid_y = cx + 24, cy + 82
        cell, gap = 11, 3
        for i, day in enumerate(recent):
            col = i // 7
            row = i % 7
            count = day.get("count", 0)
            intensity = count / max_count
            color = "#10202A" if count == 0 else (CYAN if intensity > .66 else "#23869A" if intensity > .33 else "#165466")
            x = grid_x + col * (cell + gap)
            y = grid_y + row * (cell + gap)
            if x + cell <= cx + cw - 25:
                svg.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{color}"/>')
    else:
        svg.extend([
            f'<text x="{cx+24}" y="{cy+70}" font-size="14" fill="{MUTED}">Contribution calendar data is not available to the workflow yet.</text>',
            f'<text x="{cx+24}" y="{cy+100}" font-size="12" fill="#6F8496">Configure the optional GH_PAT secret with read:user scope to enable the contribution heatmap.</text>',
            f'<rect x="{cx+24}" y="{cy+130}" width="330" height="42" rx="10" fill="#0A1820" stroke="{GRID}"/>',
            f'<text x="{cx+42}" y="{cy+156}" font-size="12" fill="{CYAN}">Contribution data: awaiting authorization</text>',
        ])

    svg.extend([
        f'<text x="58" y="928" font-size="12" font-style="italic" fill="{MUTED}">Live GitHub data · generated by Python · synchronized every 6 hours</text>',
        '</g></svg>',
    ])

    with open(OUTPUT, "w", encoding="utf-8") as handle:
        handle.write("\n".join(svg) + "\n")

if __name__ == "__main__":
    main()
