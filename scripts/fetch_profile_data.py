#!/usr/bin/env python3
"""Fetch stats + latest blog posts -> assets/profile.json. Stdlib only.
Token: $STATS_TOKEN (PAT, optional) or $GITHUB_TOKEN. Works unauthenticated (rate-limited)."""
import json, os, urllib.request, xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = json.load(open(os.path.join(ROOT, "profile.config.json")))
TOKEN = os.environ.get("STATS_TOKEN") or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")


def get(url, raw=False):
    req = urllib.request.Request(url, headers={"User-Agent": "profile-generator"})
    if TOKEN and "api.github.com" in url:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    return data if raw else json.loads(data)


def stats():
    u = get(f"https://api.github.com/users/{CFG['login']}")
    stars, page = 0, 1
    while True:
        repos = get(f"https://api.github.com/users/{CFG['login']}/repos?per_page=100&page={page}")
        stars += sum(r["stargazers_count"] for r in repos if not r["fork"])
        if len(repos) < 100:
            break
        page += 1
    return {"repos": u["public_repos"], "followers": u["followers"], "stars": stars}


def posts():
    try:
        root = ET.fromstring(get(CFG["feed"], raw=True))
    except Exception:
        return []
    out = []
    for it in root.iter("item"):
        out.append({
            "title": it.findtext("title", ""),
            "url": it.findtext("link", ""),
            "date": " ".join((it.findtext("pubDate", "") or "").split(" ")[1:4]),
        })
        if len(out) >= CFG["posts"]["count"]:
            break
    return out


os.makedirs(os.path.join(ROOT, "assets"), exist_ok=True)
data = {"stats": stats(), "posts": posts()}
json.dump(data, open(os.path.join(ROOT, "assets", "profile.json"), "w"), indent=2)
print(data)
