# SPDX-License-Identifier: MIT
"""Search tolerates case, partial words and separators; FTS5 and the LIKE fallback agree."""
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import helpers  # noqa: F401

from equipment_locker import annotations as ann
from equipment_locker import db, places, scan, search

DOC = places.load()


def make(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


class TestSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(tempfile.mkdtemp())
        home = root / "home" / "alice"
        make(home / ".claude" / "skills" / "Code-Review" / "SKILL.md",
             "---\nname: Code-Review\ndescription: Reviews pull requests\n---\n")
        make(home / ".claude" / "settings.json", "{}")
        cls.conn = db.open_db(":memory:")
        opts = {"platform": "linux", "machine": "t", "env": {}, "current_home": home, "users": "me",
                "projects": False, "sweep": False, "limits": {"depth": 4, "max_entries": 50000, "size_max_files": 100}}
        scan.run(cls.conn, DOC, opts)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def titles(self, text, **filters):
        return {r["title"] for r in search.query(self.conn, text, filters)}

    def test_variations_find_the_same_skill(self):
        for q in ("code review", "Code-Review", "CODE_REVIEW", "code.review", "ode-rev", "pull REQUESTS"):
            self.assertIn("Code-Review", self.titles(q), q)

    def test_short_queries_use_fallback(self):
        self.assertIn("Code-Review", self.titles("co"))

    def test_filters(self):
        self.assertEqual({r["kind"] for r in search.query(self.conn, "claude", {"kind": "location"})}, {"location"})
        self.assertEqual(self.titles("review", tool="nope"), set())

    def test_tags_and_notes_are_searchable(self):
        item_id = self.conn.execute("SELECT id FROM item").fetchone()[0]
        ann.tag(self.conn, {"kind": "item", "id": item_id}, "Daily Driver")
        ann.set_annotation(self.conn, {"kind": "item", "id": item_id}, {"note": "use before merging"})
        search.rebuild(self.conn)
        self.assertIn("Code-Review", self.titles("daily-driver"))
        self.assertIn("Code-Review", self.titles("before merging"))

    def test_fallback_matches_fts(self):
        with_fts = self.titles("review")
        with mock.patch.object(search, "has_fts", return_value=False):
            self.assertEqual(self.titles("review"), with_fts)

    def test_quotes_and_wildcards_are_safe(self):
        self.assertEqual(search.query(self.conn, '"; DROP TABLE item; --'), [])
        self.assertEqual(search.query(self.conn, "%_%"), [])


if __name__ == "__main__":
    unittest.main()
