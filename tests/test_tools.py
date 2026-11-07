"""Run with: python3 -m unittest discover -s tests"""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import vault_graph  # noqa: E402
import vault_lint  # noqa: E402
from vaultlib import frontmatter, load  # noqa: E402

EXAMPLE = ROOT / "example-vault"
HOOK = ROOT / "claude/hooks/session_note_check.py"


def make_vault(files: dict[str, str]) -> Path:
    root = Path(tempfile.mkdtemp())
    for rel, text in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(text).lstrip())
    return root


class Frontmatter(unittest.TestCase):
    def test_scalars_lists_and_inline_lists(self):
        fm, body = frontmatter('---\ntype: task\nstatus: "done"\nareas: [a.py, b.py]\ntouched:\n  - "[[x]]"\n  - "[[y]]"\n---\nbody\n')
        self.assertEqual(fm["type"], "task")
        self.assertEqual(fm["status"], "done")
        self.assertEqual(fm["areas"], ["a.py", "b.py"])
        self.assertEqual(fm["touched"], ["[[x]]", "[[y]]"])
        self.assertEqual(body, "body\n")

    def test_no_frontmatter(self):
        self.assertEqual(frontmatter("just text"), ({}, "just text"))


class Graph(unittest.TestCase):
    def test_edges_are_typed_by_frontmatter_key(self):
        v = make_vault({
            "p/tasks/t1.md": "---\ntype: task\nstatus: done\n---\nSee [[l1]].\n",
            "p/lessons/l1.md": '---\ntype: lesson\nsource: "[[t1]]"\n---\nrule\n',
        })
        g = load(v)
        labels = {(g.notes[s].name, g.notes[d].name, lbl) for s, d, lbl in g.edges}
        self.assertEqual(labels, {("l1", "t1", "source"), ("t1", "l1", "mentions")})

    def test_path_links_resolve_exactly(self):
        v = make_vault({
            "a/project.md": "---\ntype: project\n---\n",
            "b/project.md": "---\ntype: project\n---\n",
            "s.md": "---\ntype: session\n---\n[[a/project|a]]\n",
        })
        g = load(v)
        targets = [g.notes[d].rel for _, d, _ in g.edges]
        self.assertEqual(targets, ["a/project"])

    def test_example_vault_is_one_component(self):
        comps = vault_graph.components(load(EXAMPLE))
        self.assertEqual(len(comps), 1)

    def test_html_embeds_data(self):
        page = vault_graph.html(load(EXAMPLE))
        self.assertNotIn("/*DATA*/null", page)
        self.assertIn('"nodes"', page)


class Lint(unittest.TestCase):
    def run_lint(self, vault: Path, *args: str) -> tuple[int, str]:
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = vault_lint.main(["--vault", str(vault), *args])
        return code, buf.getvalue()

    def test_example_vault_is_clean(self):
        code, out = self.run_lint(EXAMPLE, "--check")
        self.assertEqual(code, 0, out)

    def test_reports_each_problem_kind(self):
        v = make_vault({
            "p/tasks/t.md": "---\ntype: task\n---\n[[missing-note]]\n",
            "p/lessons/l.md": "---\ntype: lesson\nsource: \n---\n",
            "p/decisions/d.md": "---\ntype: decision\n---\n",
            "x/dup.md": "---\ntype: reference\n---\n[[y/dup]]\n",
            "y/dup.md": "---\ntype: reference\n---\n[[x/dup]]\n",
            "untyped.md": "no frontmatter\n",
        })
        code, out = self.run_lint(v, "--check")
        self.assertEqual(code, 1)
        for kind in ("broken link", "task without status", "lesson without source",
                     "orphan (no inbound link)", "duplicate name", "missing type"):
            self.assertIn(kind, out)
        self.assertFalse((v / "index.md").exists(), "--check must not write")

    def test_default_mode_writes_index_log_and_stubs(self):
        v = make_vault({"a.md": "---\ntype: session\n---\n[[ghost]]\n"})
        self.run_lint(v, "--fix-stubs")
        self.assertIn("[[a|a]]", (v / "index.md").read_text())
        self.assertIn("lint | 1 notes, 1 problems", (v / "log.md").read_text())
        self.assertTrue((v / "stubs/ghost.md").exists())


class StopHook(unittest.TestCase):
    def run_hook(self, vault: Path, transcript_lines: list[dict], **extra) -> subprocess.CompletedProcess:
        tp = Path(tempfile.mkdtemp()) / "t.jsonl"
        tp.write_text("\n".join(json.dumps(x) for x in transcript_lines))
        env = {**os.environ, "CLAUDE_GRAPH_VAULT": str(vault)}
        env.pop("CLAUDE_SKIP_SESSION_NOTE", None)
        payload = json.dumps({"transcript_path": str(tp), **extra})
        return subprocess.run([sys.executable, str(HOOK)], input=payload, text=True, capture_output=True, env=env)

    @staticmethod
    def edit(path: str) -> dict:
        return {"message": {"content": [{"type": "tool_use", "name": "Edit", "input": {"file_path": path}}]}}

    def test_blocks_real_work_without_a_note(self):
        v = make_vault({"README.md": "x"})
        r = self.run_hook(v, [self.edit(f"/Users/me/code/app/f{i}.py") for i in range(3)])
        self.assertEqual(r.returncode, 2)
        self.assertIn("sessions/", r.stderr)

    def test_passes_when_todays_note_exists(self):
        v = make_vault({f"sessions/{date.today().isoformat()}-app.md": "---\ntype: session\n---\n"})
        r = self.run_hook(v, [self.edit(f"/Users/me/code/app/f{i}.py") for i in range(5)])
        self.assertEqual(r.returncode, 0)

    def test_ignores_vault_and_tooling_edits(self):
        v = make_vault({"README.md": "x"})
        lines = [self.edit(str(v / "a.md")), self.edit("/Users/me/.claude/tools/x.py"), self.edit(str(v / "b.md"))]
        self.assertEqual(self.run_hook(v, lines).returncode, 0)

    def test_never_loops(self):
        v = make_vault({"README.md": "x"})
        r = self.run_hook(v, [self.edit(f"/Users/me/code/f{i}.py") for i in range(9)], stop_hook_active=True)
        self.assertEqual(r.returncode, 0)

    def test_counts_writing_shell_commands(self):
        v = make_vault({"README.md": "x"})
        bash = {"message": {"content": [{"type": "tool_use", "name": "Bash",
                                         "input": {"command": "sed -i '' s/a/b/ /Users/me/code/app/x.py"}}]}}
        self.assertEqual(self.run_hook(v, [bash] * 3).returncode, 2)


if __name__ == "__main__":
    unittest.main()
