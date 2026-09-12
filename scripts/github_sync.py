#!/usr/bin/env python3
"""Refresh the profile dashboard cache from public GitHub data.

Designed for GitHub Actions. No token is stored in the repository.
GITHUB_TOKEN is used for GraphQL contribution data; REST endpoints remain
publicly readable.
"""
from __future__ import annotations
import json, os, sys
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"site"/"data"
DATA.mkdir(parents=True,exist_ok=True)
USER=os.getenv("GITHUB_USER","RifatNSU701")
TOKEN=os.getenv("GITHUB_TOKEN","")
S=requests.Session()
S.headers.update({"Accept":"application/vnd.github+json","User-Agent":"RifatNSU701-profile-dashboard"})
if TOKEN:S.headers["Authorization"]=f"Bearer {TOKEN}"

def get(url, **params):
    r=S.get(url,params=params,timeout=20); r.raise_for_status(); return r.json()

def write(name,obj):
    (DATA/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def main():
    user=get(f"https://api.github.com/users/{USER}")
    repos=get(f"https://api.github.com/users/{USER}/repos",per_page=100,sort="updated")
    events=get(f"https://api.github.com/users/{USER}/events/public",per_page=30)
    repos=[r for r in repos if not r.get("private")]
    primary={}
    for r in repos:
        lang=r.get("language")
        if lang: primary[lang]=primary.get(lang,0)+1
    payload={
        "source":"github-actions-rest","syncedAt":datetime.now(timezone.utc).isoformat(),
        "user":{"login":user.get("login"),"name":user.get("name"),"bio":user.get("bio"),"location":user.get("location"),"blog":user.get("blog"),"public_repos":user.get("public_repos"),"public_gists":user.get("public_gists"),"followers":user.get("followers"),"following":user.get("following"),"html_url":user.get("html_url"),"avatar_url":user.get("avatar_url")},
        "repos":[{"name":r.get("name"),"html_url":r.get("html_url"),"description":r.get("description"),"language":r.get("language"),"topics":r.get("topics",[]),"stargazers_count":r.get("stargazers_count",0),"forks_count":r.get("forks_count",0),"updated_at":r.get("updated_at"),"pushed_at":r.get("pushed_at"),"fork":r.get("fork",False)} for r in repos],
        "events":events,"languages":primary
    }
    write("github.json",payload)
    if not TOKEN:
        print("GITHUB_TOKEN unavailable; REST cache refreshed, contribution calendar skipped."); return
    query="""query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){contributionsCollection(from:$from,to:$to){contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""
    now=datetime.now(timezone.utc); start=now.replace(hour=0,minute=0,second=0,microsecond=0); from_dt=start.replace(year=start.year-1)
    body=S.post("https://api.github.com/graphql",json={"query":query,"variables":{"login":USER,"from":from_dt.isoformat().replace("+00:00","Z"),"to":start.isoformat().replace("+00:00","Z")}},timeout=30).json()
    if body.get("errors"): raise RuntimeError(body["errors"])
    cal=body["data"]["user"]["contributionsCollection"]["contributionCalendar"]; days=[d for w in cal["weeks"] for d in w["contributionDays"]]
    counts={d["date"]:d["contributionCount"] for d in days}; dates=sorted(counts); best=run=0
    for d in dates:
        if counts[d]>0: run+=1; best=max(best,run)
        else: run=0
    cur=0
    for d in reversed(dates):
        if counts[d]>0: cur+=1
        else: break
    write("contributions.json",{"source":"github-graphql","syncedAt":datetime.now(timezone.utc).isoformat(),"total":cal["totalContributions"],"currentStreak":cur,"longestStreak":best,"days":[{"date":d["date"],"count":d["contributionCount"]} for d in days]})
    print(f"Synced {len(repos)} repositories and {len(days)} contribution days.")

if __name__=="__main__":
    try: main()
    except Exception as exc: print(f"SYNC ERROR: {exc}",file=sys.stderr); sys.exit(1)
