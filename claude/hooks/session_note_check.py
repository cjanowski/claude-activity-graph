#!/usr/bin/env python3
"""Claude Code Stop hook: no real work ends without a session note.

If the transcript shows at least MIN_EDITS file edits outside the vault and tooling,
and no note in <vault>/sessions/ was written today, exit 2 with instructions on
stderr. Claude Code feeds that back to the model, which writes the note and stops.

Skips when: stop_hook_active (one nudge per stop, no loops), CLAUDE_SKIP_SESSION_NOTE=1,
the vault can't be found, or the work was trivial.
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path

MIN_EDITS = int(os.environ.get("CLAUDE_SESSION_NOTE_MIN_EDITS", "3"))
POINTER = Path.home() / ".claude/tools/vault_path"
# A shell command counts as an edit if it looks like it writes a file.
WRITE_BASH = re.compile(r"(cat\s*>|tee\s|sed\s+-i|>\s*[\"']?/|python3?\s+-\s*<<|\bmv\s|\bcp\s|git\s+(commit|apply)|ditto\s)")
ABS_PATH = re.compile(r"/(?:Users|home|private|tmp)[^\s'\"`;|)]*")


def find_vault() -> Path | None:
    if os.environ.get("CLAUDE_GRAPH_VAULT"):
        return Path(os.environ["CLAUDE_GRAPH_VAULT"]).expanduser()
    if POINTER.exists():
        return Path(POINTER.read_text().strip()).expanduser()
    return None


def count_edits(transcript: Path, ignore: tuple[str, ...]) -> int:
    edits = 0
    for line in transcript.read_text(errors="replace").splitlines():
        if '"tool_use"' not in line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        for block in (msg.get("message") or {}).get("content") or []:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            name, inp = block.get("name"), block.get("input") or {}
            if name in ("Write", "Edit", "NotebookEdit"):
                if not any(x in inp.get("file_path", "") for x in ignore):
                    edits += 1
            elif name == "Bash" and WRITE_BASH.search(inp.get("command", "")):
                paths = ABS_PATH.findall(inp.get("command", ""))
                # Bookkeeping commands that only touch ignored areas don't count.
                if not (paths and all(any(x in p for x in ignore) for p in paths)):
                    edits += 1
    return edits


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except ValueError:
        return 0
    if data.get("stop_hook_active") or os.environ.get("CLAUDE_SKIP_SESSION_NOTE") == "1":
        return 0
    vault = find_vault()
    tp = data.get("transcript_path")
    if vault is None or not tp or not Path(tp).exists():
        return 0
    ignore = ("/.claude/", str(vault), "/scratchpad/", "/tmp/")
    edits = count_edits(Path(tp), ignore)
    if edits < MIN_EDITS:
        return 0
    today = date.today()
    sessions = vault / "sessions"
    if sessions.exists():
        for f in sessions.glob("*.md"):
            if f.name.startswith(today.isoformat()) or datetime.fromtimestamp(f.stat().st_mtime).date() == today:
                return 0
    sys.stderr.write(
        f"This session made {edits} file edits but sessions/ has no note from today. "
        f"Write or update sessions/{today.isoformat()}-<project>.md from _templates/Session.md "
        "(Done / Decisions / Next, `touched` links to every task, decision and lesson), update any task "
        "status that changed, append a line to log.md, run vault_lint.py, then stop. "
        "If the edits were trivial, a two-line note is enough.\n")
    return 2


if __name__ == "__main__":
    sys.exit(main())
