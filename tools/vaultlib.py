"""Shared model of the vault as a typed graph.

Nodes are Markdown notes, typed by the `type` frontmatter key. Edges are wiki links.
An edge found in a frontmatter key takes that key as its label (`source`, `task`,
`repo`, `touched`, ...); an edge found in the body is labelled `mentions`.

Standard library only, so it runs anywhere Claude Code does.
"""
from __future__ import annotations

import os
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
GENERATED = {"index.md", "log.md"}          # rebuilt or appended by tools, not graph content
POINTER = Path.home() / ".claude/tools/vault_path"
ENV = "CLAUDE_GRAPH_VAULT"


def vault_path(arg: str | None = None) -> Path:
    """--vault flag, then $CLAUDE_GRAPH_VAULT, then the one-line pointer file."""
    if arg:
        return Path(arg).expanduser()
    if os.environ.get(ENV):
        return Path(os.environ[ENV]).expanduser()
    if POINTER.exists():
        return Path(POINTER.read_text().strip()).expanduser()
    raise SystemExit(f"No vault found: pass --vault, set ${ENV}, or write the vault path to {POINTER}")


def frontmatter(text: str) -> tuple[dict, str]:
    """Parse the small YAML subset the templates use: `key: value` and `key:` followed by `  - item` lines."""
    m = re.match(r"^---\n(.*?)\n---\n?", text, re.S)
    if not m:
        return {}, text
    fm: dict = {}
    key = None
    for line in m.group(1).splitlines():
        if line.startswith((" ", "\t")) and key is not None:
            item = line.strip()
            if item.startswith("- "):
                if not isinstance(fm[key], list):
                    fm[key] = []
                fm[key].append(item[2:].strip().strip('"'))
            continue
        k, sep, v = line.partition(":")
        if not sep:
            continue
        key = k.strip()
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            inner = v[1:-1].strip()
            fm[key] = [x.strip().strip('"') for x in re.split(r",(?![^\[]*\]\])", inner)] if inner else []
        else:
            fm[key] = v.strip('"')
    return fm, text[m.end():]


@dataclass
class Note:
    path: Path
    rel: str                      # vault-relative path without .md, as Obsidian links it
    fm: dict
    body: str

    @property
    def name(self) -> str:
        return self.path.stem

    @property
    def type(self) -> str | None:
        return self.fm.get("type")

    @property
    def project(self) -> str:
        return self.fm.get("project") or self.rel.split("/")[0]


@dataclass
class Graph:
    vault: Path
    notes: dict[Path, Note]
    edges: list[tuple[Path, Path, str]] = field(default_factory=list)   # (src, dst, label)
    broken: list[tuple[Path, str]] = field(default_factory=list)        # (src, target text)

    def inbound(self) -> dict[Path, int]:
        deg: dict[Path, int] = defaultdict(int)
        for _, dst, _ in self.edges:
            deg[dst] += 1
        return deg

    def outbound(self) -> dict[Path, int]:
        deg: dict[Path, int] = defaultdict(int)
        for src, _, _ in self.edges:
            deg[src] += 1
        return deg


def load(vault: Path) -> Graph:
    notes: dict[Path, Note] = {}
    for p in sorted(vault.rglob("*.md")):
        parts = p.relative_to(vault).parts
        if p.name in GENERATED and len(parts) == 1:
            continue
        if "_templates" in parts or any(x.startswith(".") for x in parts):
            continue
        fm, body = frontmatter(p.read_text(errors="replace"))
        notes[p] = Note(p, str(p.relative_to(vault))[:-3], fm, body)

    by_name: dict[str, list[Path]] = defaultdict(list)
    by_rel: dict[str, Path] = {}
    for p, n in notes.items():
        by_name[n.name].append(p)
        by_rel[n.rel] = p

    g = Graph(vault, notes)
    for p, n in notes.items():
        sources = [(k, v if isinstance(v, str) else " ".join(v)) for k, v in n.fm.items()]
        sources.append(("mentions", n.body))
        for label, text in sources:
            for raw in LINK.findall(text):
                t = raw.strip()
                if t.endswith(".base"):
                    continue
                targets = [by_rel[t]] if t in by_rel else by_name.get(t.split("/")[-1], [])
                if not targets:
                    g.broken.append((p, t))
                for q in targets:
                    if q != p:
                        g.edges.append((p, q, label))
    return g
