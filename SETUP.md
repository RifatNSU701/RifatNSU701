# Setup — do this once after pushing these files

1. **Push everything to `RifatNSU701/RifatNSU701`**, keeping the folder structure as-is
   (`README.md`, `assets/`, `docs/`, `scripts/`, `.github/workflows/`).

2. **Turn on GitHub Pages**
   Repo → Settings → Pages → Source: "Deploy from a branch" → Branch: `main`, folder: `/docs` → Save.
   The dashboard will be live at `https://RifatNSU701.github.io/RifatNSU701/` a minute or two later.

3. **Run the sync workflow once manually**
   Repo → Actions → "Sync GitHub Intelligence Data" → Run workflow.
   This replaces the placeholder `docs/data/stats.json` with your real numbers and regenerates
   `assets/hero.svg` with a live repo/star count. After this, it also runs automatically every 6 hours.

4. **Optional — enable the contribution calendar**
   Create a classic personal access token with `read:user` scope at
   github.com/settings/tokens, then add it as a repository secret named `GH_PAT`
   (Settings → Secrets and variables → Actions → New repository secret).
   Without this, the dashboard simply omits that one chart instead of faking it.

5. **Add real projects when ready**
   The "Research & Currently Building" section in `docs/index.html` ships empty on purpose —
   drop your actual repos/projects in there yourself when you have ones you want to feature.

## Files at a glance

- Profile entry point → `README.md`
- Full interactive dashboard → `docs/index.html`, `docs/style.css`, `docs/script.js`
- Real GitHub data, auto-updated → `docs/data/stats.json`
- Data-fetching script → `scripts/fetch_stats.py`
- Animated banner generator → `scripts/generate_hero_svg.py`
- Automation → `.github/workflows/update-stats.yml`
