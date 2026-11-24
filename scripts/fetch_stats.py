#!/usr/bin/env python3
"""Fetches real GitHub account data and writes stats.json.

Env:
  GH_USER        github username (or pass as first CLI argument)
  GITHUB_TOKEN   token provided automatically by GitHub Actions (public data only)
  STATS_TOKEN    optional personal access token (scopes: repo, read:user) to also
                 count private repos and private contributions

If any request fails, the previous value in stats.json is kept.
No third-party dependencies.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "stats.json")
API = "https://api.github.com"

USER = os.environ.get("GH_USER") or (sys.argv[1] if len(sys.argv) > 1 else None)
if not USER:
    sys.exit("set GH_USER or pass the username as an argument")
TOKEN = os.environ.get("STATS_TOKEN") or os.environ.get("GITHUB_TOKEN")
HAS_PAT = bool(os.environ.get("STATS_TOKEN"))


def call(path, body=None):
    url = path if path.startswith("http") else API + path
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "bento-readme"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read()
        return r.status, (json.loads(raw) if raw else None), r.headers


def safe(fn, default=None):
    try:
        return fn()
    except Exception as e:  # noqa: BLE001
        print("warn:", e, file=sys.stderr)
        return default


def graphql():
    q = """query($u:String!){user(login:$u){followers{totalCount}
      contributionsCollection{contributionCalendar{totalContributions
      weeks{contributionDays{date contributionCount}}}}}}"""
    _, res, _ = call("/graphql", {"query": q, "variables": {"u": USER}})
    return res["data"]["user"]


def repos():
    out, page = [], 1
    while True:
        path = (f"/user/repos?affiliation=owner&per_page=100&page={page}" if HAS_PAT
                else f"/users/{USER}/repos?type=owner&per_page=100&page={page}")
        _, chunk, _ = call(path)
        out += chunk
        if len(chunk) < 100:
            return [r for r in out if not r["fork"] and r["owner"]["login"].lower() == USER.lower()]
        page += 1


def my_additions(full_name):
    for _ in range(6):
        status, res, _ = call(f"/repos/{full_name}/stats/contributors")
        if status == 200 and res is not None:
            for c in res:
                if c["author"] and c["author"]["login"].lower() == USER.lower():
                    return sum(w["a"] for w in c["weeks"])
            return 0
        time.sleep(4)  # 202: github is computing the stats
    return 0


def last_push():
    _, events, _ = call(f"/users/{USER}/events/public?per_page=50")
    for e in events:
        if e["type"] == "PushEvent" and e["payload"].get("commits"):
            c = e["payload"]["commits"][-1]
            when = datetime.fromisoformat(e["created_at"].replace("Z", "+00:00"))
            days = (datetime.now(timezone.utc) - when).days
            ago = "today" if days == 0 else "yesterday" if days == 1 else f"{days}d ago"
            return {"repo": e["repo"]["name"].split("/")[-1],
                    "message": c["message"].splitlines()[0][:80], "when": ago}
    return None


prev = {}
if os.path.exists(OUT):
    with open(OUT) as f:
        prev = json.load(f)
stats = dict(prev)
stats["username"] = USER
stats["updated"] = date.today().isoformat()

u = safe(graphql)
if u:
    cal = u["contributionsCollection"]["contributionCalendar"]
    days = sorted((d for w in cal["weeks"] for d in w["contributionDays"]), key=lambda d: d["date"])
    days = [d for d in days if d["date"] <= date.today().isoformat()]
    counts = [d["contributionCount"] for d in days]
    streak, i = 0, len(counts) - 1
    if i >= 0 and counts[i] == 0:  # today may not have activity yet
        i -= 1
    while i >= 0 and counts[i] > 0:
        streak += 1
        i -= 1
    stats.update(contributions=cal["totalContributions"], streak=streak,
                 last20=counts[-20:], followers=u["followers"]["totalCount"])

rs = safe(repos)
if rs is not None:
    stats["repos"] = len(rs)
    stats["stars"] = sum(r["stargazers_count"] for r in rs)
    total = sum(safe(lambda r=r: my_additions(r["full_name"]), 0) for r in rs)
    stats["lines"] = max(total, prev.get("lines", 0))  # additions only grow

n = safe(last_push)
if n:
    stats["now"] = n

with open(OUT, "w") as f:
    json.dump(stats, f, indent=2)
print(json.dumps(stats, indent=2))
