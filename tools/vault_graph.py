#!/usr/bin/env python3
"""Analyse and export the vault as a typed graph.

  vault_graph.py [--vault PATH] stats                 counts, hubs, components, the learning loop
  vault_graph.py [--vault PATH] json    [-o FILE]     nodes + typed edges as JSON
  vault_graph.py [--vault PATH] mermaid [--project P] Mermaid flowchart (paste into a README or Obsidian)
  vault_graph.py [--vault PATH] html    [-o FILE]     self-contained force-directed explorer (d3)

Read-only: it never writes into the vault.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from vaultlib import Graph, load, vault_path  # noqa: E402

TYPE_ORDER = ["task", "lesson", "decision", "session", "project", "repo", "reference", "activity"]


def to_dict(g: Graph) -> dict:
    ids = {p: n.rel for p, n in g.notes.items()}
    inbound, outbound = g.inbound(), g.outbound()
    nodes = [{"id": n.rel, "name": n.name, "type": n.type or "other", "project": n.project,
              "status": n.fm.get("status"), "in": inbound[p], "out": outbound[p]}
             for p, n in g.notes.items()]
    seen = set()
    edges = []
    for s, d, label in g.edges:
        key = (ids[s], ids[d], label)
        if key not in seen:
            seen.add(key)
            edges.append({"source": ids[s], "target": ids[d], "label": label})
    return {"nodes": nodes, "edges": edges}


def components(g: Graph, skip_types=("index",)) -> list[set[Path]]:
    adj: dict[Path, set[Path]] = defaultdict(set)
    keep = {p for p, n in g.notes.items() if n.type not in skip_types}
    for s, d, _ in g.edges:
        if s in keep and d in keep:
            adj[s].add(d)
            adj[d].add(s)
    seen: set[Path] = set()
    comps = []
    for start in keep:
        if start in seen:
            continue
        comp, stack = set(), [start]
        while stack:
            x = stack.pop()
            if x in comp:
                continue
            comp.add(x)
            stack.extend(adj[x] - comp)
        seen |= comp
        comps.append(comp)
    return sorted(comps, key=len, reverse=True)


def stats(g: Graph) -> str:
    n, e = len(g.notes), len(g.edges)
    types = Counter(x.type or "other" for x in g.notes.values())
    labels = Counter(lbl for _, _, lbl in g.edges)
    inbound = g.inbound()
    comps = components(g)
    out = [f"{n} nodes, {e} edges, density {e / (n * (n - 1)) if n > 1 else 0:.4f}",
           f"{len(comps)} weakly connected components, largest {len(comps[0]) if comps else 0} nodes",
           "", "Nodes by type"]
    out += [f"  {t:<10} {c}" for t, c in types.most_common()]
    out += ["", "Edges by label (frontmatter key, or 'mentions' for body links)"]
    out += [f"  {lbl:<10} {c}" for lbl, c in labels.most_common()]

    hubs = sorted((p for p, x in g.notes.items() if x.type not in ("index",)), key=lambda p: -inbound[p])[:8]
    out += ["", "Hubs (most inbound links)"]
    out += [f"  {inbound[p]:>3}  {g.notes[p].rel}" for p in hubs if inbound[p]]

    # The learning loop: work (tasks) -> lessons (via source) -> reused in later work.
    lessons = [p for p, x in g.notes.items() if x.type == "lesson"]
    tasks = [p for p, x in g.notes.items() if x.type == "task"]
    taught = {d for s, d, lbl in g.edges if lbl == "source" and g.notes[s].type == "lesson"}
    auto = sum(1 for p in lessons if str(g.notes[p].fm.get("auto")).lower() == "true")
    reuse = defaultdict(set)
    for s, d, _ in g.edges:
        if g.notes[d].type == "lesson" and g.notes[s].type in ("task", "session", "decision", "lesson"):
            reuse[d].add(g.notes[s].project)
    cross = [p for p in lessons if len(reuse[p] - {g.notes[p].project}) >= 1]
    out += ["", "Learning loop",
            f"  lessons            {len(lessons)}  ({auto} enforced by a script, auto: true)",
            f"  tasks that taught  {len(taught & set(tasks))} of {len(tasks)}",
            f"  lessons applied outside their home project  {len(cross)}"]
    for p in sorted(cross, key=lambda p: g.notes[p].rel):
        out.append(f"    {g.notes[p].rel}  <- {', '.join(sorted(reuse[p] - {g.notes[p].project}))}")
    status = Counter(str(g.notes[p].fm.get("status")) for p in tasks)
    if status:
        out += ["", "Tasks by status"] + [f"  {s:<10} {c}" for s, c in status.most_common()]
    return "\n".join(out)


def mermaid(g: Graph, project: str | None) -> str:
    keep = {p for p, n in g.notes.items()
            if n.type not in ("index", "activity") and (project is None or n.project in (project, "shared"))}
    ids = {p: f"n{i}" for i, p in enumerate(sorted(keep))}
    lines = ["flowchart LR"]
    for p in sorted(keep):
        n = g.notes[p]
        lines.append(f'  {ids[p]}["{n.name}"]:::{n.type or "other"}')
    seen = set()
    for s, d, lbl in g.edges:
        if s in keep and d in keep and (s, d) not in seen:
            seen.add((s, d))
            lines.append(f"  {ids[s]} -->|{lbl}| {ids[d]}" if lbl != "mentions" else f"  {ids[s]} -.-> {ids[d]}")
    colors = dict(zip(TYPE_ORDER, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#7a7a75"]))
    for t, c in colors.items():
        lines.append(f"  classDef {t} fill:{c},stroke:{c},color:#fff")
    return "\n".join(lines)


def html(g: Graph) -> str:
    template = (Path(__file__).resolve().parent / "graph_template.html").read_text()
    return template.replace("/*DATA*/null", json.dumps(to_dict(g)))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vault")
    ap.add_argument("cmd", nargs="?", default="stats", choices=["stats", "json", "mermaid", "html"])
    ap.add_argument("-o", "--out")
    ap.add_argument("--project")
    a = ap.parse_args(argv)
    g = load(vault_path(a.vault))
    text = {"stats": lambda: stats(g), "json": lambda: json.dumps(to_dict(g), indent=1),
            "mermaid": lambda: mermaid(g, a.project), "html": lambda: html(g)}[a.cmd]()
    if a.out:
        Path(a.out).write_text(text + "\n")
        print(f"wrote {a.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
