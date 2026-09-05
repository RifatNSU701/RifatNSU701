import json
import os
import urllib.request
from datetime import date, timedelta
from pathlib import Path

OWNER = "RifatNSU701"
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "profile"
OUT.mkdir(parents=True, exist_ok=True)
TOKEN = os.environ.get("GITHUB_TOKEN")


def gql(query, variables=None):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json", "User-Agent": "RifatNSU701-profile"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        payload = json.load(response)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]


QUERY = """
query($login:String!, $from:DateTime!, $to:DateTime!) {
  user(login:$login) {
    name
    followers { totalCount }
    repositories(first:100, ownerAffiliations:OWNER, privacy:PUBLIC) {
      totalCount
      nodes {
        stargazerCount
        forkCount
        primaryLanguage { name color }
        languages(first:20, orderBy:{field:SIZE, direction:DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection(from:$from, to:$to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { date contributionCount color }
        }
      }
    }
  }
}
"""


def esc(value):
    return (str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def text(x, y, value, size=16, fill="#E6EDF3", weight=400, anchor="start"):
    return f'<text x="{x}" y="{y}" fill="{fill}" font-family="Inter,Segoe UI,Arial,sans-serif" font-size="{size}px" font-weight="{weight}" text-anchor="{anchor}">{esc(value)}</text>'


def card(x, y, w, h, label, value, accent="#22C55E", icon=""):
    return f'''<g><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="18" fill="#0B1117" stroke="#26313B"/>
    <circle cx="{x+28}" cy="{y+30}" r="10" fill="{accent}" opacity=".18"/>
    <circle cx="{x+28}" cy="{y+30}" r="4" fill="{accent}"/>
    {text(x+48,y+37,icon,13,"#8B949E",600)}
    {text(x+24,y+80,value,30,"#F0F6FC",700)}
    {text(x+24,y+108,label.upper(),11,"#8B949E",600)}
    </g>'''


def shell(width, height, body, title=None):
    title_part = text(34, 38, title, 17, "#F0F6FC", 700) if title else ""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<defs>
 <linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="#22C55E"/><stop offset="1" stop-color="#06B6D4"/></linearGradient>
 <filter id="glow"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
 <linearGradient id="grid" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#0B1117"/><stop offset="1" stop-color="#0D141B"/></linearGradient>
</defs>
<rect width="100%" height="100%" rx="20" fill="#070B10"/>
<rect x="1" y="1" width="calc(100% - 2px)" height="calc(100% - 2px)" rx="20" fill="url(#grid)" stroke="#26313B"/>
{title_part}{body}
</svg>'''


def main():
    today = date.today()
    end = today + timedelta(days=1)
    start = end - timedelta(days=365)
    data = gql(QUERY, {"login": OWNER, "from": f"{start.isoformat()}T00:00:00Z", "to": f"{end.isoformat()}T00:00:00Z"})["user"]

    repos = data["repositories"]
    followers = data["followers"]["totalCount"]
    repo_nodes = repos["nodes"]
    stars = sum(r["stargazerCount"] for r in repo_nodes)
    forks = sum(r["forkCount"] for r in repo_nodes)
    calendar = data["contributionsCollection"]["contributionCalendar"]
    total_contrib = calendar["totalContributions"]
    days = [d for w in calendar["weeks"] for d in w["contributionDays"]]

    # Language aggregation by byte-size across owned public repositories.
    langs = {}
    for repo in repo_nodes:
        for edge in repo.get("languages", {}).get("edges", []):
            name = edge["node"]["name"]
            langs.setdefault(name, {"size": 0, "color": edge["node"].get("color") or "#8B949E"})
            langs[name]["size"] += edge["size"]
    top_langs = sorted(langs.items(), key=lambda item: item[1]["size"], reverse=True)[:8]
    lang_total = sum(v["size"] for _, v in top_langs) or 1

    # Overview.
    body = (
        card(24, 58, 276, 128, "Public repositories", str(repos["totalCount"]), "#22C55E", "REPOSITORIES")
        + card(312, 58, 276, 128, "Stars received", f"{stars:,}", "#F59E0B", "STARS")
        + card(600, 58, 276, 128, "Followers", f"{followers:,}", "#06B6D4", "FOLLOWERS")
        + card(888, 58, 288, 128, "Contributions · 12 months", f"{total_contrib:,}", "#8B5CF6", "ACTIVITY")
    )
    (OUT / "overview.dark.svg").write_text(shell(1200, 210, body), encoding="utf-8")

    # Contribution heatmap, large and readable.
    weeks = calendar["weeks"]
    cell = 15
    gap = 5
    left = 42
    top = 62
    heat = [text(28, 36, f"{total_contrib:,} contributions in the last 12 months", 17, "#F0F6FC", 700)]
    heat.append(text(28, 54, "GitHub contribution calendar · live data", 11, "#8B949E", 400))
    for wi, week in enumerate(weeks):
        x = left + wi * (cell + gap)
        for di, d in enumerate(week["contributionDays"]):
            y = top + di * (cell + gap)
            count = d["contributionCount"]
            opacity = min(1.0, 0.18 + (count / max(1, max(day["contributionCount"] for day in days))) * 0.82)
            fill = "#22C55E" if count else "#111820"
            heat.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="4" fill="{fill}" opacity="{opacity:.2f}" stroke="#18232C"/>')
    heat.append(text(42, 204, "Less", 10, "#6E7681", 400))
    for i, a in enumerate([0.2, 0.45, 0.7, 1.0]):
        heat.append(f'<rect x="{75+i*22}" y="194" width="14" height="14" rx="4" fill="#22C55E" opacity="{a}"/>')
    heat.append(text(172, 204, "More", 10, "#6E7681", 400))
    (OUT / "contributions.dark.svg").write_text(shell(1200, 225, "".join(heat)), encoding="utf-8")

    # Premium language donut + ranked bars.
    cx, cy, radius = 190, 220, 112
    circumference = 2 * 3.1415926535 * radius
    donut = [text(30, 38, "Language distribution", 17, "#F0F6FC", 700), text(30, 57, "Across public repositories · live repository data", 11, "#8B949E", 400)]
    offset = 0
    colors = [v["color"] for _, v in top_langs]
    for idx, (name, info) in enumerate(top_langs):
        share = info["size"] / lang_total
        dash = share * circumference
        color = colors[idx] or "#8B949E"
        donut.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{color}" stroke-width="28" stroke-dasharray="{dash:.2f} {circumference-dash:.2f}" stroke-dashoffset="{-offset:.2f}" transform="rotate(-90 {cx} {cy})"/>')
        offset += dash
    donut += [f'<circle cx="{cx}" cy="{cy}" r="76" fill="#070B10"/>', text(cx, cy-4, str(len(top_langs)), 28, "#F0F6FC", 700, "middle"), text(cx, cy+20, "LANGUAGES", 10, "#8B949E", 600, "middle")]
    for i, (name, info) in enumerate(top_langs):
        y = 82 + i * 40
        share = info["size"] / lang_total * 100
        color = info["color"] or "#8B949E"
        donut.append(f'<circle cx="355" cy="{y-5}" r="6" fill="{color}"/>')
        donut.append(text(372, y, name, 13, "#D0D7DE", 600))
        donut.append(text(1125, y, f"{share:.1f}%", 12, "#8B949E", 600, "end"))
        donut.append(f'<rect x="500" y="{y+7}" width="625" height="6" rx="3" fill="#18232C"/>')
        donut.append(f'<rect x="500" y="{y+7}" width="{625*share/100:.1f}" height="6" rx="3" fill="{color}" opacity=".9"/>')
    (OUT / "languages.dark.svg").write_text(shell(1200, 430, "".join(donut)), encoding="utf-8")

    # Contribution rhythm by month, derived from the same live contribution calendar.
    monthly = {}
    for d in days:
        month = d["date"][:7]
        monthly[month] = monthly.get(month, 0) + d["contributionCount"]
    month_keys = sorted(monthly)[-12:]
    vals = [monthly[m] for m in month_keys]
    maxv = max(vals or [1])
    plot_x, plot_y, plot_w, plot_h = 78, 90, 1040, 250
    rhythm = [text(30, 38, "Contribution rhythm", 17, "#F0F6FC", 700), text(30, 57, "Monthly contribution volume · rolling 12 months", 11, "#8B949E", 400)]
    for gy in range(5):
        y = plot_y + gy * (plot_h / 4)
        rhythm.append(f'<line x1="{plot_x}" y1="{y}" x2="{plot_x+plot_w}" y2="{y}" stroke="#1B2730"/>')
    points = []
    for i, value in enumerate(vals):
        x = plot_x + i * (plot_w / max(1, len(vals)-1))
        y = plot_y + plot_h - (value / maxv) * plot_h
        points.append((x, y, value))
    if points:
        path = "M " + " L ".join(f"{x:.1f} {y:.1f}" for x, y, _ in points)
        area = path + f" L {points[-1][0]:.1f} {plot_y+plot_h} L {points[0][0]:.1f} {plot_y+plot_h} Z"
        rhythm.append(f'<path d="{area}" fill="url(#g)" opacity=".08"/>')
        rhythm.append(f'<path d="{path}" fill="none" stroke="url(#g)" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)"/>')
        for i, (x, y, value) in enumerate(points):
            rhythm.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#22C55E" stroke="#070B10" stroke-width="3"/>')
            rhythm.append(text(x, y-12, f"{value:,}", 10, "#C9D1D9", 600, "middle"))
            label = month_keys[i][5:7] + "/" + month_keys[i][2:4]
            rhythm.append(text(x, plot_y+plot_h+30, label, 10, "#8B949E", 600, "middle"))
    rhythm.append(text(78, 385, f"Total: {total_contrib:,} · Stars: {stars:,} · Forks: {forks:,}", 11, "#6E7681", 500))
    (OUT / "rhythm.dark.svg").write_text(shell(1200, 420, "".join(rhythm)), encoding="utf-8")


if __name__ == "__main__":
    main()
