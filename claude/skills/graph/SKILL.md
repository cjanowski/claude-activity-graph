---
name: graph
description: Maintain the Obsidian activity graph (engineering vault): set up a new project folder, ingest a raw source, close a session, run the lint, pull GitHub activity, write the weekly rollup, analyse the graph, or move the vault. Use when the user mentions the graph, the vault, Obsidian, session notes, lessons, or asks to record or look up what they did.
---

# Activity graph

Vault path: the single line in `~/.claude/tools/vault_path` (or `$CLAUDE_GRAPH_VAULT`). Read `README.md` and `index.md` there before answering anything from the vault. Notes are nodes, wiki links are edges, `type` says what a note is. Templates are in `_templates/`. The always-on rule in `~/.claude/CLAUDE.md` says *when*; this skill says *how*.

## New project
1. `mkdir -p <vault>/<name>/{tasks,lessons,decisions}`; write `<name>/project.md` from `_templates/Project.md`: what it is, where the code and tracker live, which skill drives it, and its stages.
2. Add it to the Projects line in `README.md`.
3. If it already has a tracker or notes, migrate them: one task note per item with `status`, one lesson note per repeatable cause with a `source` link. Lessons that hold everywhere go to `shared/lessons/`.
4. If it has a GitHub repo, link `project.md` to `github/repos/<repo>.md`.
5. If the project has its own skill, point it at `<vault>/<name>/lessons/` by reading `~/.claude/tools/vault_path`, never by spelling out the path.

## Ingest a source
1. Save the source unchanged under `raw/<project>/YYYY-MM-DD-<slug>.md` (spec, review result, clipped article, pasted page). Never edit it afterwards.
2. Read it, then write or update the compiled notes it affects (lessons, decisions, references). Each links back to the raw file.
3. Append `## [YYYY-MM-DD] ingest | <title>` to `log.md`.
4. Run the lint.

## Close a session
1. Write or update `sessions/YYYY-MM-DD-<project>.md` from `_templates/Session.md`: Done, Decisions, Next, and `touched` links to every task, decision and lesson.
2. Update `status` on any task that changed stage. Add a Decision or Lesson note for anything repeatable.
3. Append `## [date] session | <one line>` to `log.md`.
4. Run `python3 ~/.claude/tools/vault_lint.py` and fix every problem it reports.

The Stop hook `~/.claude/hooks/session_note_check.py` enforces step 1 when the session edited files.

## Lint
`python3 ~/.claude/tools/vault_lint.py` rebuilds `index.md`, appends to `log.md`, and reports broken links, orphans (decision, reference and stub notes with no inbound link), lessons without `source`, tasks without `status`, and duplicate names. `--check` writes nothing and exits 1 on problems. `--fix-stubs` creates a stub note per broken link target.

## Analyse
`python3 ~/.claude/tools/vault_graph.py stats` prints hubs, components, edge types and the learning loop (tasks that taught a lesson, lessons applied outside their home project). `html -o graph.html` writes an interactive explorer. Use `stats` before a weekly rollup.

## GitHub
`python3 ~/.claude/tools/github_ingest.py --days 30`. Run it after any session that pushed, and weekly. Repo notes keep their `## Notes` section across reruns.

## Weekly rollup
In the first session of a week, read the past week's `sessions/` and `github/activity/` notes. Write `sessions/YYYY-Www-rollup.md` (type: rollup) with what moved, what stalled, lessons added, and next week's three priorities. Link every session note it summarises.

## Move the vault
1. Move the vault folder; open it in Obsidian; check that the graph view renders.
2. Change the one line in `~/.claude/tools/vault_path`. Nothing else spells out the path.
3. Run the lint (expect 0 problems) and the hook smoke test: `echo '{}' | python3 ~/.claude/hooks/session_note_check.py; echo $?` should print 0.
4. If the new home is a plain folder (not iCloud), `git init` the vault; version history is part of the pattern. Don't put a git repo inside an iCloud-synced folder.
5. Log the move in `log.md`.

## Answer a question from the vault
Read `index.md`, open the relevant notes, and answer with links. If the answer took real synthesis, file it as a reference or decision note.
