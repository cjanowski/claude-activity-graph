---
type: index
---

# Engineering graph

Nodes are notes. Edges are wiki links. A note's type is its `type` property, and its folder agrees.
Each project gets a folder with `project.md`, `tasks/`, `lessons/` and `decisions/`.
Lessons that hold across projects go in `shared/lessons/`; research worth keeping goes in `shared/reference/`.

Tables: [[Lessons.base]], [[Tasks.base]], [[Sessions.base]], [[Activity.base]], [[Repos.base]].

`github/` is machine-written by `github_ingest.py`: `repos/` one note per repository, `activity/` one note per day of commits and PRs. Add your own text under a repo note's `## Notes`; reruns keep it.

`raw/` holds sources exactly as they arrived. Compiled notes link back to them; nothing edits them.

Every session with real work ends with a note in `sessions/` linking what it touched. The rule that keeps this current lives in `~/.claude/CLAUDE.md`; the Stop hook enforces it.

Projects: [[rag-service/project|rag-service]] (retrieval service), [[inference-gateway/project|inference-gateway]] (LLM gateway)

Conventions
- A lesson links to the task that taught it in `source`.
- A task links to its repo in `repo` and lists the code areas it touched in `areas`.
- A decision links to the task or project it was made for in `task`.
- `auto: true` on a lesson means a script or CI check already enforces it.
- Claude Code reads and writes these files directly. Keep frontmatter keys as they are.
