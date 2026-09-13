#!/usr/bin/env python3
"""
fetch_stats.py
Pulls real data from the GitHub API for a single account, computes
aggregate statistics and language distribution, and writes the result
to docs/data/stats.json for the dashboard to render.

No numbers in the output are invented. Anything that cannot be
retrieved is omitted or set to null rather than guessed.

Auth:
  GITHUB_TOKEN   - provided automatically by GitHub Actions. Enough for
                   REST calls (repos, languages, events, search).
  GH_PAT         - optional personal access token with `read:user` scope.
                   Only needed for the GraphQL contribution calendar,
                   since the automatic GITHUB_TOKEN cannot read another
                   user's contribution history. If absent, the
                   "contributions" field is simply left out.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

USERNAME = os.environ.get("PROFILE_USERNAME", "RifatNSU701")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
PAT = os.environ.get("GH_PAT", "")
API = "https://api.github.com"
OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "docs", "data", "stats.json")


def gh_get(path, token=TOKEN):
    url = f"{API}{path}"
    req = urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": USERNAME,
        **({"Authorization": f"Bearer {token}"} if token else {}),
    })
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 403 and attempt < 2:
                time.sleep(5)
                continue
            print(f"WARN: GET {path} failed: {e}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"WARN: GET {path} failed: {e}", file=sys.stderr)
            return None
    return None


def gh_graphql(query, variables, token=PAT):
    if not token:
        return None
    req = urllib.request.Request(
        f"{API}/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": USERNAME,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"WARN: GraphQL failed: {e}", file=sys.stderr)
        return None


def get_all_repos():
    repos, page = [], 1
    while True:
        batch = gh_get(f"/users/{USERNAME}/repos?per_page=100&page={page}&type=owner")
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def main():
    user = gh_get(f"/users/{USERNAME}")
    repos = get_all_repos()
    non_fork_repos = [r for r in repos if not r.get("fork")]

    lang_bytes = {}
    total_stars = total_forks = total_open_issues = 0
    repo_summaries = []

    for repo in non_fork_repos:
        total_stars += repo.get("stargazers_count", 0)
        total_forks += repo.get("forks_count", 0)
        total_open_issues += repo.get("open_issues_count", 0)

        langs = gh_get(f"/repos/{USERNAME}/{repo['name']}/languages")
        if langs:
            for lang, count in langs.items():
                lang_bytes[lang] = lang_bytes.get(lang, 0) + count

        repo_summaries.append({
            "name": repo["name"],
            "description": repo.get("description"),
            "stars": repo.get("stargazers_count", 0),
            "forks": repo.get("forks_count", 0),
            "language": repo.get("language"),
            "url": repo.get("html_url"),
            "updated_at": repo.get("updated_at"),
        })

    total_bytes = sum(lang_bytes.values()) or 1
    languages = sorted(
        [
            {"name": lang, "bytes": count, "percent": round(count / total_bytes * 100, 2)}
            for lang, count in lang_bytes.items()
        ],
        key=lambda x: x["bytes"],
        reverse=True,
    )

    pr_search = gh_get(f"/search/issues?q=author:{USERNAME}+type:pr")
    issue_search = gh_get(f"/search/issues?q=author:{USERNAME}+type:issue")

    events = gh_get(f"/users/{USERNAME}/events/public") or []
    recent_activity = [
        {
            "type": e.get("type"),
            "repo": e.get("repo", {}).get("name"),
            "created_at": e.get("created_at"),
        }
        for e in events[:10]
    ]

    contributions = None
    gql = gh_graphql(
        """
        query($login: String!) {
          user(login: $login) {
            contributionsCollection {
              contributionCalendar {
                totalContributions
                weeks {
                  contributionDays { date contributionCount }
                }
              }
            }
          }
        }
        """,
        {"login": USERNAME},
    )
    if gql and gql.get("data", {}).get("user"):
        cal = gql["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        contributions = {
            "total": cal["totalContributions"],
            "days": [
                {"date": d["date"], "count": d["contributionCount"]}
                for week in cal["weeks"]
                for d in week["contributionDays"]
            ],
        }

    data = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "profile": {
            "public_repos": user.get("public_repos") if user else len(non_fork_repos),
            "followers": user.get("followers") if user else None,
            "following": user.get("following") if user else None,
        },
        "totals": {
            "repositories": len(non_fork_repos),
            "stars": total_stars,
            "forks": total_forks,
            "open_issues": total_open_issues,
            "pull_requests": pr_search.get("total_count") if pr_search else None,
            "issues_opened": issue_search.get("total_count") if issue_search else None,
        },
        "languages": languages,
        "repositories": sorted(repo_summaries, key=lambda r: r["updated_at"] or "", reverse=True),
        "recent_activity": recent_activity,
        "contributions": contributions,
        "notes": (
            "contributions is null unless a GH_PAT secret with read:user scope "
            "is configured, since the default Actions token cannot read another "
            "account's contribution calendar."
        ),
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
