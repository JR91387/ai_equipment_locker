# SPDX-License-Identifier: MIT
"""Schema: migrations, idempotent seeds, guards."""
import sqlite3
import unittest

import helpers  # noqa: F401

from equipment_locker import db


class TestSchema(unittest.TestCase):
    def setUp(self):
        self.conn = db.open_db(":memory:")
        self.addCleanup(self.conn.close)

    def count(self, table):
        return self.conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def test_user_version_matches_last_migration(self):
        self.assertEqual(self.conn.execute("PRAGMA user_version").fetchone()[0], db.migrations()[-1][0])

    def test_migrate_and_reapply_are_idempotent(self):
        before = {t: self.count(t) for t in ("ref_os", "ref_category", "ref_presence")}
        db.migrate(self.conn)
        db.reapply(self.conn)
        self.assertEqual(before, {t: self.count(t) for t in before})

    def test_nothing_can_be_deleted(self):
        for table in ("ref_os", "ref_category"):
            with self.assertRaises(sqlite3.DatabaseError, msg=table):
                self.conn.execute(f"DELETE FROM {table}")
        triggers = {r[0] for r in self.conn.execute("SELECT tbl_name FROM sqlite_master WHERE type = 'trigger'")}
        self.assertLessEqual({"location", "place", "location_change", "scan_run", "project", "os_user"}, triggers)

    def test_foreign_keys_enforced(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("INSERT INTO machine (name, os_id, first_seen, last_seen) VALUES ('x', 999, '', '')")

    def test_ref_id_adds_unknown_codes_only_with_display(self):
        with self.assertRaises(KeyError):
            self.conn.ref_id("ref_tool", "brand-new")
        new_id = self.conn.ref_id("ref_tool", "brand-new", "Brand new")
        self.assertEqual(new_id, self.conn.ref_id("ref_tool", "brand-new"))

    def test_ref_id_rejects_non_ref_tables(self):
        with self.assertRaises(ValueError):
            self.conn.ref_id("location; DROP TABLE x", "a")


if __name__ == "__main__":
    unittest.main()
