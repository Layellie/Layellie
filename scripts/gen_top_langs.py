"""Generate a byte-based Top Languages card (tokyonight style) from the GitHub API.

Counts real code bytes (GitHub Linguist data) across all public, non-fork repos,
so every language in every repo is represented — not just each repo's primary one.
Requires GITHUB_TOKEN in the environment.
"""
import json
import os
import urllib.request

USER = "Layellie"
OUT = os.path.join(os.path.dirname(__file__), "..", "top-langs.svg")
TOKEN = os.environ["GITHUB_TOKEN"]

COLORS = {
    "C#": "#178600", "C++": "#f34b7d", "QML": "#44a51c", "JavaScript": "#f1e05a",
    "TypeScript": "#3178c6", "HTML": "#e34c26", "CSS": "#563d7c", "Dart": "#00B4AB",
    "Python": "#3572A5", "C": "#555555", "Java": "#b07219", "Kotlin": "#A97BFF",
    "Swift": "#F05138", "Rust": "#dea584", "Go": "#00ADD8",
}

def api(path):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json"},
    )
    with urllib.request.urlopen(req) as r:
        return json.load(r)

totals = {}
for repo in api(f"/users/{USER}/repos?per_page=100&type=owner"):
    if repo["fork"]:
        continue
    for lang, size in api(f"/repos/{USER}/{repo['name']}/languages").items():
        totals[lang] = totals.get(lang, 0) + size

top = sorted(totals.items(), key=lambda kv: -kv[1])[:8]
total = sum(v for _, v in top) or 1

W, PAD, BARH, ROWH = 340, 22, 8, 36
H = 70 + len(top) * ROWH
rows = []
y = 62
for lang, size in top:
    pct = size / total * 100
    color = COLORS.get(lang, "#9da0a8")
    barw = max(4, (W - 2 * PAD) * size / total)
    rows.append(f'''
  <text x="{PAD}" y="{y}" class="lang">{lang}</text>
  <text x="{W - PAD}" y="{y}" text-anchor="end" class="pct">{pct:.1f}%</text>
  <rect x="{PAD}" y="{y + 8}" width="{W - 2 * PAD}" height="{BARH}" rx="4" fill="#2a2e42"/>
  <rect x="{PAD}" y="{y + 8}" width="{barw:.1f}" height="{BARH}" rx="4" fill="{color}"/>''')
    y += ROWH

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <style>
    .title {{ font: 600 16px 'Segoe UI', Ubuntu, sans-serif; fill: #70a5fd; }}
    .lang  {{ font: 400 12px 'Segoe UI', Ubuntu, sans-serif; fill: #38bdae; }}
    .pct   {{ font: 400 12px 'Segoe UI', Ubuntu, sans-serif; fill: #b9c1d9; }}
  </style>
  <rect width="{W}" height="{H}" rx="5" fill="#1a1b27"/>
  <text x="{PAD}" y="34" class="title">Top Languages by Code Size</text>
  {''.join(rows)}
</svg>
'''
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote top-langs.svg:", ", ".join(f"{l} {s / total * 100:.1f}%" for l, s in top))
