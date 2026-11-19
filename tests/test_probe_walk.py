# SPDX-License-Identifier: MIT
"""probe (presence, bounded size, never follow links) and walk (projects, vendored, cache, budget, sweep)."""
import os
import tempfile
import unittest
from pathlib import Path

import helpers  # noqa: F401

from equipment_locker.probe import Budget, expand_glob, probe
from equipment_locker.walk import find_projects, is_vendored, matches_tool, sweep

LIMITS = {"size_max_files": 5, "depth": 4, "max_entries": 1000}


def opts(budget=None, prior=None):
    return {"limits": LIMITS, "budget": budget or Budget(1000), "prior": prior}


class TestProbe(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_absent_and_file(self):
        self.assertEqual(probe(self.tmp / "nope", "file", "config", opts())["presence"], "absent")
        (self.tmp / "a.json").write_text("{}")
        res = probe(self.tmp / "a.json", "file", "config", opts())
        self.assertEqual((res["presence"], res["size_bytes"]), ("present", 2))

    def test_wrong_type_and_symlink(self):
        (self.tmp / "f").write_text("x")
        self.assertEqual(probe(self.tmp / "f", "dir", "config", opts())["presence"], "wrong_type")
        os.symlink(self.tmp / "f", self.tmp / "link")
        self.assertEqual(probe(self.tmp / "link", "file", "config", opts())["presence"], "link")

    def test_size_capped(self):
        d = self.tmp / "cache"
        d.mkdir()
        for i in range(8):
            (d / f"{i}").write_text("12345")
        res = probe(d, "dir", "cache", opts())
        self.assertEqual((res["entry_count"], res["size_over"]), (8, 1))

    def test_budget_cut_size_is_unknown_not_zero(self):
        d = self.tmp / "big"
        d.mkdir()
        for i in range(4):
            (d / f"{i}").write_text("x")
        res = probe(d, "dir", "cache", opts(Budget(2)))
        self.assertEqual((res["presence"], res["size_bytes"], res["size_over"]), ("present", None, 0))

    def test_auth_existence_only(self):
        (self.tmp / "auth.json").write_text("secret")
        res = probe(self.tmp / "auth.json", "file", "auth", opts())
        self.assertEqual((res["presence"], res["size_bytes"]), ("present", None))

    def test_unchanged_folder_reuses_size(self):
        d = self.tmp / "s"
        d.mkdir()
        (d / "x").write_text("abc")
        first = probe(d, "dir", "skills", opts())
        reused = probe(d, "dir", "skills", opts(Budget(0), dict(first)))
        self.assertEqual(reused["size_bytes"], 3)

    @unittest.skipIf(hasattr(os, "geteuid") and os.geteuid() == 0, "root reads everything")
    def test_unreadable_folder(self):
        d = self.tmp / "locked"
        d.mkdir()
        d.chmod(0)
        try:
            self.assertEqual(probe(d, "dir", "config", opts())["presence"], "unreadable")
        finally:
            d.chmod(0o755)

    def test_glob(self):
        for n in ("Claude_abc", "Claude_def", "Other"):
            (self.tmp / n).mkdir()
        self.assertEqual(len(expand_glob(self.tmp / "Claude_*")), 2)


class TestWalk(unittest.TestCase):
    def setUp(self):
        self.home = Path(tempfile.mkdtemp())
        (self.home / "work" / "app").mkdir(parents=True)
        (self.home / "work" / "app" / "CLAUDE.md").write_text("x")
        (self.home / "work" / "app" / "node_modules" / "lib").mkdir(parents=True)
        (self.home / "work" / "app" / "node_modules" / "lib" / "AGENTS.md").write_text("x")
        (self.home / "a" / "b" / "c" / "d" / "e").mkdir(parents=True)
        (self.home / "a" / "b" / "c" / "d" / "e" / "CLAUDE.md").write_text("too deep")
        self.opts = {"markers": ["CLAUDE.md", "AGENTS.md", ".github/copilot-instructions.md"], "depth": 4}

    def test_finds_projects_and_vendored_within_depth(self):
        hits, complete = find_projects(self.home, self.opts, {}, Budget(1000))
        folders = {str(f.relative_to(self.home)) for f, _ in hits}
        self.assertEqual(folders, {"work/app", "work/app/node_modules/lib"})
        self.assertTrue(complete)
        self.assertTrue(is_vendored(self.home / "work/app/node_modules/lib", ["node_modules"]))
        self.assertFalse(is_vendored(self.home / "work/app", ["node_modules"]))

    def test_cache_skips_unchanged_folders(self):
        cache = {}
        find_projects(self.home, self.opts, cache, Budget(1000))
        second = Budget(1000)
        hits, _ = find_projects(self.home, self.opts, cache, second)
        self.assertEqual((second.used, len(hits)), (0, 2))

    def test_budget_stops_and_resumes(self):
        cache = {}
        _, complete = find_projects(self.home, self.opts, cache, Budget(3))
        self.assertFalse(complete)
        hits, complete = find_projects(self.home, self.opts, cache, Budget(1000))
        self.assertTrue(complete)
        self.assertEqual(len(hits), 2)

    def test_sweep_depth_one_token_match(self):
        for n in ("Claude-Data", "claude-cli-nodejs", "example", "January", "jan", "deep"):
            (self.home / "r" / n).mkdir(parents=True)
        (self.home / "r" / "deep" / "claude").mkdir()
        names = ["claude", "jan", "amp"]
        hits, complete = sweep([self.home / "r"], names, Budget(1000))
        found = {p.name for p, _ in hits}
        self.assertTrue(complete)
        self.assertEqual(found, {"Claude-Data", "claude-cli-nodejs", "jan"})
        self.assertEqual(matches_tool("com.google.antigravity", ["antigravity"]), "antigravity")


if __name__ == "__main__":
    unittest.main()
