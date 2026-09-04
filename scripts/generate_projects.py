import html
import json
import os
import urllib.request

OWNER = "RifatNSU701"
OUT = "assets/projects"
API = "https://api.github.com/users/{}/repos?per_page=100&type=owner&sort=updated".format(OWNER)

headers = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "RifatNSU701-profile",
}
if os.getenv("GITHUB_TOKEN"):
    headers["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]

req = urllib.request.Request(API, headers=headers)
with urllib.request.urlopen(req, timeout=30) as response:
    repos = json.load(response)

repos = [
    r for r in repos
    if not r.get("fork") and r.get("name") != OWNER and not r.get("archived") and not r.get("private")
]
repos.sort(key=lambda r: (r.get("stargazers_count", 0), r.get("forks_count", 0), r.get("updated_at", "")), reverse=True)
repos = repos[:6]

os.makedirs(OUT, exist_ok=True)

GREEN = "#22C55E"
CYAN = "#06B6D4"
BG = "#0D1117"
CARD = "#111827"
TEXT = "#E5E7EB"
MUTED = "#9CA3AF"
BORDER = "#273244"


def esc(value):
    return html.escape(str(value or ""), quote=True)


def truncate(value, n=92):
    value = " ".join(str(value or "").split())
    return value if len(value) <= n else value[: n - 1] + "…"


def card(repo, index):
    name = esc(repo["name"])
    desc = esc(truncate(repo.get("description"), 96) or "No description provided.")
    lang = esc(repo.get("language") or "Repository")
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    x = 0 if index % 2 == 0 else 425
    y = 0 if index < 2 else 170 if index < 4 else 340
    accent = GREEN if index % 2 == 0 else CYAN
    return f'''<a href="{esc(repo["html_url"])}"><rect x="{x+1}" y="{y+1}" width="418" height="158" rx="12" fill="{CARD}" stroke="{BORDER}"/><rect x="{x+1}" y="{y+1}" width="4" height="156" rx="2" fill="{accent}"/><text x="{x+24}" y="{y+36}" fill="{GREEN}" font-family="Arial, sans-serif" font-size="19" font-weight="700">{name}</text><rect x="{x+330}" y="{y+20}" width="64" height="26" rx="13" fill="{BG}" stroke="{BORDER}"/><text x="{x+362}" y="{y+38}" text-anchor="middle" fill="{MUTED}" font-family="Arial, sans-serif" font-size="11">{lang}</text><text x="{x+24}" y="{y+72}" fill="{MUTED}" font-family="Arial, sans-serif" font-size="13">{desc}</text><text x="{x+24}" y="{y+124}" fill="{TEXT}" font-family="Arial, sans-serif" font-size="12">★ {stars:,}</text><text x="{x+105}" y="{y+124}" fill="{TEXT}" font-family="Arial, sans-serif" font-size="12">⑂ {forks:,}</text><text x="{x+330}" y="{y+124}" fill="{CYAN}" font-family="Arial, sans-serif" font-size="12">VIEW ↗</text></a>'''

height = max(170, ((len(repos) + 1) // 2) * 170)
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="846" height="{height}" viewBox="0 0 846 {height}"><rect width="846" height="{height}" fill="transparent"/>''' + "".join(card(r, i) for i, r in enumerate(repos)) + "</svg>"

with open(os.path.join(OUT, "notable-projects.svg"), "w", encoding="utf-8") as f:
    f.write(svg)

with open(os.path.join(OUT, "projects.json"), "w", encoding="utf-8") as f:
    json.dump(
        [
            {
                k: r.get(k)
                for k in ("name", "html_url", "description", "language", "stargazers_count", "forks_count")
            }
            for r in repos
        ],
        f,
        indent=2,
    )
