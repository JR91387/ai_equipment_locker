# SPDX-License-Identifier: MIT
"""Annotations (history), tags, images, pinned folders."""
import sqlite3
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

import helpers  # noqa: F401

from equipment_locker import annotations as ann
from equipment_locker import db, places, scan

DOC = places.load()


def png(w=3, h=2):
    head = b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return head + struct.pack(">I", zlib.crc32(head[12:]))


class TestAnnotations(unittest.TestCase):
    def setUp(self):
        self.conn = db.open_db(":memory:")
        self.addCleanup(self.conn.close)
        self.tool = {"kind": "tool", "id": "other"}

    def test_edits_keep_versions(self):
        ann.set_annotation(self.conn, self.tool, {"note": "first"})
        ann.set_annotation(self.conn, self.tool, {"note": "second", "is_favorite": True})
        ann.set_annotation(self.conn, self.tool, {"note": "second", "is_favorite": True})
        row = self.conn.execute("SELECT note, is_favorite FROM annotation").fetchone()
        versions = self.conn.execute("SELECT note FROM annotation_version").fetchall()
        self.assertEqual((row["note"], row["is_favorite"], [v[0] for v in versions]), ("second", 1, ["first"]))

    def test_tags_case_insensitive_and_retired_not_deleted(self):
        a = ann.tag(self.conn, self.tool, "Daily")
        b = ann.tag(self.conn, self.tool, "daily")
        ann.tag(self.conn, self.tool, "DAILY", on=False)
        link = self.conn.execute("SELECT COUNT(*), MAX(is_retired) FROM tag_link").fetchone()
        self.assertEqual((a, tuple(link)), (b, (1, 1)))

    def test_images_checked(self):
        img = ann.add_image(self.conn, self.tool, png())
        row = self.conn.execute("SELECT mime, width, height FROM image WHERE id = ?", (img,)).fetchone()
        self.assertEqual(tuple(row), ("image/png", 3, 2))
        with self.assertRaises(ValueError):
            ann.add_image(self.conn, self.tool, b"<svg onload=x>")
        with self.assertRaises(OverflowError):
            ann.add_image(self.conn, self.tool, b"\x89PNG\r\n\x1a\n" + b"0" * ann.MAX_IMAGE)

    def test_one_target_only(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("INSERT INTO annotation (updated) VALUES ('x')")

    def test_bad_target_kind(self):
        with self.assertRaises(ValueError):
            ann.set_annotation(self.conn, {"kind": "user", "id": 1}, {"note": "x"})


class TestPins(unittest.TestCase):
    def test_pin_scanned_unpin_keeps_history(self):
        root = Path(tempfile.mkdtemp())
        home, extra = root / "home" / "alice", root / "elsewhere" / "kit"
        (home).mkdir(parents=True)
        (extra / "proj").mkdir(parents=True)
        (extra / "proj" / "AGENTS.md").write_text("x")
        conn = db.open_db(":memory:")
        self.addCleanup(conn.close)
        opts = {"platform": "linux", "machine": "t", "env": {}, "current_home": home, "users": "me",
                "projects": True, "sweep": False, "limits": {"depth": 4, "max_entries": 50000, "size_max_files": 100}}
        place_id = ann.pin(conn, extra)
        scan.run(conn, DOC, opts)
        paths = {r[0] for r in conn.execute("SELECT path FROM location")}
        self.assertIn(str(extra), paths)
        self.assertIn(str(extra / "proj" / "AGENTS.md"), paths)
        ann.unpin(conn, place_id)
        self.assertEqual(ann.pinned(conn), [])
        self.assertIsNotNone(conn.execute("SELECT id FROM location WHERE path = ?", (str(extra),)).fetchone())
        places.sync(conn, DOC)
        enabled = conn.execute("SELECT is_retired FROM place WHERE id = ?", (place_id,)).fetchone()[0]
        self.assertEqual(enabled, 0)

    def test_pin_missing_path(self):
        conn = db.open_db(":memory:")
        self.addCleanup(conn.close)
        with self.assertRaises(ValueError):
            ann.pin(conn, "/definitely/not/here")


if __name__ == "__main__":
    unittest.main()
