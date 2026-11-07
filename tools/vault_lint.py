#!/usr/bin/env python3
"""Lint the vault, rebuild index.md, append to log.md.

  vault_lint.py [--vault PATH] [--check] [--fix-stubs]

Checks: broken wiki links, orphan notes (decision, reference and stub notes with no
inbound link), missing frontmatter `type`, lessons without a `source` link, tasks
without `status`, duplicate note names.

Default mode rebuilds index.md (every note, one line, grouped by project and type)
and appends a lint line to log.md. --check writes nothing and exits 1 on any
problem (for CI). --fix-stubs creates a stub note for each broken link target.
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vaultlib import Graph, load, vault_path  # noqa: E402

ORPHAN_TYPES = ("decision", "reference", "stub", None)   # tasks/lessons/sessions are reached via index and Bases
FOLDER_QUALIFIED = ("README", "project")                  # same name in every project folder by convention


def problems(g: Graph) -> dict[str, list[str]]:
    out: dict[str, list[str]] = defaultdict(list)
    rel = {p: n.rel for p, n in g.notes.items()}
    for src, target in g.broken:
        out["broken link"].append(f"{rel[src]} -> [[{target}]]")
    inbound = g.inbound()
    by_name: dict[str, list[str]] = defaultdict(list)
    for p, n in g.notes.items():
        by_name[n.name].append(n.rel)
        if n.type is None:
            out["missing type"].append(n.rel)
        if n.type == "lesson" and "[[" not in str(n.fm.get("source", "")):
            out["lesson without source"].append(n.rel)
        if n.type == "task" and not n.fm.get("status"):
            out["task without status"].append(n.rel)
        if inbound[p] == 0 and n.type in ORPHAN_TYPES:
            out["orphan (no inbound link)"].append(n.rel)
    for name, rels in by_name.items():
        if len(rels) > 1 and name not in FOLDER_QUALIFIED:
            out["duplicate name"].append(f"{name}: {rels}")
    return out


def index(g: Graph) -> str:
    groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    for n in sorted(g.notes.values(), key=lambda n: n.rel):
        first = next((l.strip() for l in n.body.splitlines() if l.strip() and not l.startswith("#")), "")
        summary = n.fm.get("description") or first
        groups[(str(n.fm.get("project") or "-"), n.type or "-")].append(f"- [[{n.rel}|{n.name}]] {summary[:110]}")
    out = [f"# Index\n\nEvery note, one line. Rebuilt by `vault_lint.py` on {date.today()}. "
           "Read this first when answering a question from the vault.\n"]
    for (proj, typ), lines in sorted(groups.items()):
        out.append(f"\n## {proj} / {typ} ({len(lines)})\n")
        out += lines
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vault")
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 if any problem")
    ap.add_argument("--fix-stubs", action="store_true")
    a = ap.parse_args(argv)
    vault = vault_path(a.vault)
    g = load(vault)
    found = problems(g)
    total = sum(len(v) for v in found.values())

    print(f"{len(g.notes)} notes, {len(g.edges)} edges, {total} problems")
    for k, v in found.items():
        print(f"\n{k} ({len(v)})")
        for item in v[:25]:
            print(f"  {item}")
        if len(v) > 25:
            print(f"  ... {len(v) - 25} more")

    if a.check:
        return 1 if total else 0

    if a.fix_stubs:
        for src, target in g.broken:
            stub = vault / "stubs" / f"{target.split('/')[-1]}.md"
            stub.parent.mkdir(exist_ok=True)
            if not stub.exists():
                stub.write_text(f"---\ntype: stub\n---\n\nReferenced from [[{src.stem}]] but not yet written.\n")
    (vault / "index.md").write_text(index(g))
    with (vault / "log.md").open("a") as f:
        f.write(f"## [{date.today()}] lint | {len(g.notes)} notes, {total} problems: "
                + ", ".join(f"{k} {len(v)}" for k, v in found.items()) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
