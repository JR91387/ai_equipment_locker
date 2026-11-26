# SPDX-License-Identifier: MIT
"""End-to-end scans on fake machines: every user, each OS layout, history, idempotence, dry-run CLI."""
import contextlib
import io
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import helpers  # noqa: F401

from equipment_locker import __main__ as cli
from equipment_locker import db, places, scan

DOC = places.load()


def make(path, text="{}"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


class FakeMachine(unittest.TestCase):
    platform = "linux"

    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.alice = self.root / "home" / "alice"
        make(self.alice / ".claude" / "settings.json")
        make(self.alice / ".claude" / "skills" / "one" / "SKILL.md", "x")
        make(self.alice / ".codex" / "auth.json", "secret")
        make(self.alice / "work" / "app" / "CLAUDE.md", "x")
        make(self.alice / "work" / "app" / ".claude" / "settings.json")
        make(self.alice / "work" / "app" / "node_modules" / "pkg" / "AGENTS.md", "x")
        self.conn = db.open_db(":memory:")
        self.addCleanup(self.conn.close)

    def opts(self, **kw):
        o = {"platform": self.platform, "machine": "test-box", "env": {}, "current_home": self.alice,
             "users": "all", "projects": True, "sweep": True, "home_patterns": [str(self.root / "home" / "*")],
             "limits": {"depth": 4, "max_entries": 50000, "size_max_files": 10000}}
        return o | kw

    def rows(self, where="1"):
        return self.conn.execute(f"SELECT * FROM v_location_current WHERE {where}").fetchall()

    def tools(self):
        return {r["tool"] for r in self.rows("presence = 'present'")}


class TestLinuxScan(FakeMachine):
    def test_finds_places_projects_and_vendored(self):
        s = scan.run(self.conn, DOC, self.opts())
        self.assertEqual(s["status"], "ok")
        self.assertLessEqual({"claude-code", "codex"}, self.tools())
        roots = {r["project_root"] for r in self.rows("project_root IS NOT NULL")}
        self.assertIn(str(self.alice / "work" / "app"), roots)
        vendored = self.rows("origin = 'vendored'")
        self.assertTrue(vendored and all("node_modules" in r["path"] for r in vendored))

    def test_auth_never_sized(self):
        scan.run(self.conn, DOC, self.opts())
        auth = self.rows("category = 'auth'")
        self.assertTrue(auth and all(r["size_bytes"] is None for r in auth))

    def test_second_run_changes_nothing(self):
        scan.run(self.conn, DOC, self.opts())
        n = len(self.rows())
        s = scan.run(self.conn, DOC, self.opts())
        self.assertEqual((len(self.rows()), s["changes"]), (n, {}))

    def test_disappear_and_reappear_without_deleting(self):
        scan.run(self.conn, DOC, self.opts())
        shutil.rmtree(self.alice / ".codex")
        s = scan.run(self.conn, DOC, self.opts())
        self.assertGreater(s["changes"].get("disappeared", 0) + s["marked_absent"], 0)
        self.assertTrue(self.rows("path LIKE '%.codex%' AND presence = 'absent'"))
        make(self.alice / ".codex" / "auth.json", "again")
        s = scan.run(self.conn, DOC, self.opts())
        self.assertIn("reappeared", s["changes"])

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root reads everything")
    def test_unreadable_user_recorded_not_raised(self):
        bob = self.root / "home" / "bob"
        bob.mkdir()
        bob.chmod(0)
        try:
            s = scan.run(self.conn, DOC, self.opts())
        finally:
            bob.chmod(0o755)
        self.assertEqual((s["users"], s["unreadable_users"]), (["alice"], ["bob"]))

    def test_tiny_budget_is_partial_then_resumes(self):
        s = scan.run(self.conn, DOC, self.opts(limits={"depth": 4, "max_entries": 6, "size_max_files": 10}))
        self.assertEqual(s["status"], "partial")
        self.assertEqual(s["budget"]["limit"], 6)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            cli.show({**s, "seconds": 0, "db": "x.db"}, False)
        self.assertIn("partial: the entry limit (6) ran out while", out.getvalue())
        self.assertIn("--max-entries 24", out.getvalue())
        s = scan.run(self.conn, DOC, self.opts())
        self.assertEqual(s["status"], "ok")

    def test_sweep_finds_unlisted_tool_folder(self):
        make(self.alice / ".config" / "claude-extra" / "x")
        scan.run(self.conn, DOC, self.opts())
        self.assertTrue(self.rows("source = 'discovered' AND path LIKE '%claude-extra'"))

    def test_env_override_for_scanning_user(self):
        alt = self.root / "alt-claude"
        make(alt / "settings.json")
        scan.run(self.conn, DOC, self.opts(env={"CLAUDE_CONFIG_DIR": str(alt)}, users="me"))
        self.assertTrue(self.rows(f"path = '{alt / 'settings.json'}'"))


class TestWindowsLayout(FakeMachine):
    platform = "win32"

    def test_claude_desktop_in_roaming(self):
        make(self.alice / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json")
        scan.run(self.conn, DOC, self.opts())
        self.assertIn("claude-desktop", self.tools())


class TestMacLayout(FakeMachine):
    platform = "darwin"

    def test_claude_desktop_in_application_support(self):
        make(self.alice / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json")
        scan.run(self.conn, DOC, self.opts())
        self.assertIn("claude-desktop", self.tools())


class TestCli(unittest.TestCase):
    def test_dry_run_writes_nothing(self):
        home = Path(tempfile.mkdtemp())
        make(home / ".claude" / "settings.json")
        with mock.patch.dict(os.environ, {"HOME": str(home)}), mock.patch.object(cli, "lower_priority"), \
                mock.patch("sys.stdout"):
            self.assertEqual(cli.main(["scan", "--dry-run", "--users", "me", "--json"]), 0)
        self.assertEqual(sorted(p.name for p in home.iterdir()), [".claude"])


if __name__ == "__main__":
    unittest.main()
