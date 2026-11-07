# Design notes

Longer-form reasoning behind the README's design section, including what didn't work.

## What the graph is for

Two readers, two access patterns.

- **The agent** reads narrowly and often: `index.md` to find notes, then the project's `project.md` and the lessons for the stage it's about to work on. It writes at state transitions (task status, a decision, a lesson, session close). It never browses the graph view.
- **I** read broadly and rarely: the graph view to see where work clusters, Bases tables to scan open tasks and judgment-only lessons, the weekly rollup to see what stalled.

Most choices below follow from serving both readers with one set of files.

## Typed edges without a schema language

I considered a separate edge file (`edges.jsonl`) or Dataview-style inline fields (`taught-by:: [[x]]`). Both make edges explicit, but both are things Obsidian's graph view and Bases don't understand natively, and the agent would have to maintain two representations.

Instead an edge's type is the frontmatter key it sits in. `vaultlib.load()` walks each note's frontmatter, collects links per key, and labels the edge with the key. Body links get `mentions`. This gives me:

- typed edges in `vault_graph.py` (`source`, `touched`, `task`, `repo`, `repos`, `mentions`);
- Bases columns for free, since the same keys are properties;
- one place to add an edge type: a template.

The limit is that an edge can't have properties of its own (a weight, a date). So far a date on the source note has been enough.

## Lint as the compiler

The lint is what makes "the templates are the schema" true. It checks:

| Check | Why it's an error |
|---|---|
| broken link | an edge to nowhere; usually a rename the agent didn't propagate |
| lesson without `source` | a rule with no evidence can't be re-evaluated |
| task without `status` | invisible to the open-tasks Base |
| orphan decision/reference/stub | written and never connected, so no one will find it |
| duplicate name | name-based link resolution becomes ambiguous |
| missing `type` | the note isn't a node of any kind |

Tasks, lessons and sessions are exempt from the orphan check on purpose. They're reached through the index and Bases, and a fresh lesson legitimately has no inbound links until something applies it.

`--check` mode writes nothing and exits non-zero, so the example vault is linted in CI the same way I'd lint a schema.

## The Stop hook

The rule says "write a session note at the end of real work". On long sessions that's exactly the instruction that falls out of attention. So the hook reads the transcript at Stop, counts file-writing tool calls outside the vault and `~/.claude`, and if there are at least three and no session note from today, exits 2. Claude Code shows stderr to the model, which writes the note and stops again.

Details that matter:

- `stop_hook_active` short-circuits the second stop, so the hook can never loop.
- Bash commands count as edits only if they look like writes (`sed -i`, `>`, `mv`, `git commit`, ...) and name a path outside the ignored areas. Otherwise vault bookkeeping would trigger it.
- `CLAUDE_SKIP_SESSION_NOTE=1` turns it off for throwaway sessions.

It's a heuristic. A session that only ran commands with relative paths can slip through; I'd rather miss a note than nag on every exploratory session.

## Machine-written vs human-written

`github/` is regenerated on every ingest. Two rules make that safe:

1. Everything above `## Notes` belongs to the tool and is overwritten.
2. Everything from `## Notes` down belongs to me and is carried over.

`index.md` is entirely machine-owned, and `log.md` is append-only. The agent may write anywhere else.

## Things I'd change

- **Name-based link resolution** is Obsidian's default, and the vault follows it. It forces globally unique filenames for everything except `README` and `project`. A larger vault would want path-qualified links everywhere and a lint check to enforce them.
- **The frontmatter parser** handles the YAML subset the templates use, so the tools stay dependency-free. If templates ever need nested maps, I'll switch to PyYAML rather than grow the parser.
- **Lesson decay.** Nothing marks a lesson stale. A `last_applied` date written whenever a session `touched` a lesson would make it easy to review the ones nothing has used in three months.
- **Retrieval.** The agent finds lessons via `index.md` and project folders. Past a few hundred lessons that will need ranking: by the edges first (lessons whose source tasks share `areas` with the current task), embeddings second.

## Moving off iCloud

The vault started under iCloud. That works for Obsidian on all my devices, but iCloud and `.git` don't mix, and version history is part of the pattern: being able to diff what the agent changed in a session is the best review tool I have. The plan is Obsidian Sync plus a git repo, and the move is one line in `vault_path`.
