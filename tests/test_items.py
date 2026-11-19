# SPDX-License-Identifier: MIT
"""Items: names and standard descriptions only, capped reads, history without deletes."""
import json
import os
import tempfile
import unittest
from pathlib import Path

import helpers  # noqa: F401

from equipment_locker import db, itemread, places, scan
from equipment_locker.items import collect
from equipment_locker.probe import Budget

DOC = places.load()


def make(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


class TestReaders(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_frontmatter_only_body_never_read(self):
        make(self.tmp / "a.md", "---\nname: Alpha\ndescription: >\n  Does a\n  thing\n---\nSECRET BODY")
        self.assertEqual(itemread.frontmatter(self.tmp / "a.md"), {"name": "Alpha", "description": "Does a thing"})

    def test_frontmatter_cap(self):
        make(self.tmp / "big.md", "---\nname: x\n" + "pad: y\n" * 3000 + "description: late\n---\n")
        self.assertNotIn("description", itemread.frontmatter(self.tmp / "big.md"))

    def test_mcp_names_only(self):
        cfg = {"mcpServers": {"alpha": {"command": "run", "env": {"TOKEN": "s3cret"}},
                              "beta": {"url": "https://x", "description": "Beta server"}},
               "projects": {"/p": {"mcpServers": {"gamma": {"args": ["--key", "k"]}}}}}
        make(self.tmp / ".claude.json", json.dumps(cfg))
        found = itemread.mcp_servers(self.tmp / ".claude.json")
        self.assertEqual({(n, d) for n, d, _ in found}, {("alpha", None), ("beta", "Beta server"), ("gamma", None)})
        self.assertNotIn("s3cret", repr(found))

    def test_codex_toml_servers(self):
        make(self.tmp / "config.toml", '[mcp_servers.docs]\ncommand = "x"\n')
        self.assertEqual([n for n, _, _ in itemread.mcp_servers(self.tmp / "config.toml")], ["docs"])

    def test_malformed_files_do_not_raise(self):
        make(self.tmp / "bad.json", "{not json")
        make(self.tmp / "bad.md", "---\nname: [unclosed\n")
        self.assertEqual(itemread.mcp_servers(self.tmp / "bad.json"), [])
        self.assertEqual(itemread.frontmatter(self.tmp / "bad.md"), {})


class TestCollect(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_skills_plugins_agents(self):
        make(self.tmp / "skills" / "one" / "SKILL.md", "---\nname: one\ndescription: first\n---\n")
        make(self.tmp / "skills" / "loose.txt", "x")
        make(self.tmp / "plugins" / "cache" / "mk" / "p1" / ".claude-plugin" / "plugin.json",
             json.dumps({"name": "p1", "description": "plug"}))
        make(self.tmp / "agents" / "rev.md", "---\ndescription: reviews\n---\n")
        b = Budget(1000)
        self.assertEqual(collect(self.tmp / "skills", "skills", "dir", b), [("skill", "one", "first", "one/SKILL.md")])
        self.assertEqual([i[1:3] for i in collect(self.tmp / "plugins", "plugins", "dir", b)], [("p1", "plug")])
        self.assertEqual(collect(self.tmp / "agents", "agents", "dir", b), [("agent", "rev", "reviews", "rev.md")])

    @unittest.skipIf(not hasattr(os, "symlink"), "no symlinks")
    def test_symlinked_skill_file_not_read(self):
        make(self.tmp / "outside.md", "---\ndescription: outside\n---\n")
        (self.tmp / "skills" / "s").mkdir(parents=True)
        os.symlink(self.tmp / "outside.md", self.tmp / "skills" / "s" / "SKILL.md")
        found = collect(self.tmp / "skills", "skills", "dir", Budget(100))
        self.assertTrue(all(i[2] is None for i in found))


class TestItemHistory(unittest.TestCase):
    def test_items_appear_disappear_without_delete(self):
        root = Path(tempfile.mkdtemp())
        home = root / "home" / "alice"
        make(home / ".claude" / "skills" / "one" / "SKILL.md", "---\nname: one\n---\n")
        make(home / ".claude" / "skills" / "two" / "SKILL.md", "---\nname: two\n---\n")
        conn = db.open_db(":memory:")
        self.addCleanup(conn.close)
        opts = {"platform": "linux", "machine": "t", "env": {}, "current_home": home, "users": "me",
                "projects": False, "sweep": False, "limits": {"depth": 4, "max_entries": 50000, "size_max_files": 100}}
        self.assertEqual(scan.run(conn, DOC, opts)["items"], 2)
        (home / ".claude" / "skills" / "two" / "SKILL.md").unlink()
        (home / ".claude" / "skills" / "two").rmdir()
        self.assertEqual(scan.run(conn, DOC, opts)["items"], 1)
        self.assertEqual(conn.execute("SELECT COUNT(*) FROM item").fetchone()[0], 2)
        n = conn.execute("SELECT COUNT(*) FROM item_change ic JOIN ref_change c ON c.id = ic.change_id "
                         "WHERE c.code = 'disappeared'").fetchone()[0]
        self.assertEqual(n, 1)


if __name__ == "__main__":
    unittest.main()
