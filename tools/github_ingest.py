#!/usr/bin/env python3
"""Pull GitHub activity into the vault as graph notes.

  github_ingest.py [--vault PATH] [--user LOGIN] [--days 30]

Writes
  github/repos/<name>.md          one note per repo (type: repo)
  github/activity/YYYY-MM-DD.md   one note per day of commits and PRs (type: activity), linked to repo notes

Idempotent: reruns regenerate everything above a note's "## Notes" heading and keep
what you wrote below it. Needs the GitHub CLI logged in (`gh auth status`).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vaultlib import vault_path  # noqa: E402


def gh(*args: str) -> str | None:
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"gh {' '.join(args[:3])}... failed: {r.stderr.strip()[:200]}", file=sys.stderr)
        return None
    return r.stdout


def yaml_str(s: str | None) -> str:
    return '"' + (s or "").replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ") + '"'


def write_keeping_notes(path: Path, fm: str, body: str) -> None:
    """Regenerate the machine-owned part of a note; keep the human-owned `## Notes` tail."""
    notes = "\n## Notes\n"
    if path.exists():
        m = re.search(r"\n## Notes\n.*", path.read_text(), re.S)
        if m:
            notes = m.group(0)
    path.write_text(fm + "\n" + body.rstrip() + "\n" + notes)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vault")
    ap.add_argument("--user", default=os.environ.get("GITHUB_USER"))
    ap.add_argument("--days", type=int, default=30)
    a = ap.parse_args(argv)
    vault = vault_path(a.vault)
    user = a.user or (gh("api", "user", "--jq", ".login") or "").strip()
    if not user:
        raise SystemExit("No GitHub user: pass --user, set $GITHUB_USER, or `gh auth login`.")
    since = (date.today() - timedelta(days=a.days)).isoformat()
    (vault / "github/repos").mkdir(parents=True, exist_ok=True)
    (vault / "github/activity").mkdir(parents=True, exist_ok=True)

    out = gh("repo", "list", user, "--limit", "200", "--json",
             "name,isPrivate,pushedAt,createdAt,primaryLanguage,description,url,isFork,isArchived")
    repos = json.loads(out) if out else []
    for r in repos:
        fm = "\n".join([
            "---", "type: repo", "source: github",
            f"name: {r['name']}", f"owner: {user}",
            f"language: {yaml_str((r.get('primaryLanguage') or {}).get('name', ''))}",
            f"private: {str(r['isPrivate']).lower()}", f"fork: {str(r['isFork']).lower()}",
            f"archived: {str(r['isArchived']).lower()}",
            f"created: {r['createdAt'][:10]}", f"pushed: {r['pushedAt'][:10]}",
            f"url: {r['url']}", f"description: {yaml_str(r.get('description'))}", "---"])
        body = f"# {r['name']}\n\n{r.get('description') or ''}\n\n{r['url']}"
        write_keeping_notes(vault / f"github/repos/{r['name']}.md", fm, body)
    print(f"{len(repos)} repo notes")

    # Commit search sees private repos the token can read; capped at 500 results by design.
    commits, page = [], 1
    while True:
        out = gh("api", f"search/commits?q=author:{user}+author-date:>={since}&sort=author-date&order=desc&per_page=100&page={page}")
        items = json.loads(out).get("items", []) if out else []
        commits += items
        if len(items) < 100 or page >= 5:
            break
        page += 1
    out = gh("search", "prs", "--author", user, "--created", f">={since}", "--limit", "100",
             "--json", "title,url,repository,createdAt,state,number")
    prs = json.loads(out) if out else []

    by_day: dict[str, dict[str, list]] = defaultdict(lambda: {"commits": [], "prs": []})
    for c in commits:
        by_day[c["commit"]["author"]["date"][:10]]["commits"].append(c)
    for p in prs:
        by_day[p["createdAt"][:10]]["prs"].append(p)

    for d, acts in sorted(by_day.items()):
        touched = sorted({c["repository"]["name"] for c in acts["commits"]} | {p["repository"]["name"] for p in acts["prs"]})
        fm = "\n".join(["---", "type: activity", "source: github", f"date: {d}", f"user: {user}",
                        f"commits: {len(acts['commits'])}", f"prs: {len(acts['prs'])}",
                        "repos:"] + [f'  - "[[{r}]]"' for r in touched] + ["---"])
        lines = [f"# GitHub activity {d}", ""]
        if acts["commits"]:
            lines.append("## Commits")
            lines += [f"- [[{c['repository']['name']}]] `{c['sha'][:7]}` {c['commit']['message'].splitlines()[0]}"
                      for c in acts["commits"]]
            lines.append("")
        if acts["prs"]:
            lines.append("## Pull requests")
            lines += [f"- [[{p['repository']['name']}]] #{p['number']} {p['title']} ({p['state']}) {p['url']}"
                      for p in acts["prs"]]
            lines.append("")
        write_keeping_notes(vault / f"github/activity/{d}.md", fm, "\n".join(lines))
    print(f"{len(commits)} commits, {len(prs)} PRs since {since} -> {len(by_day)} activity notes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
