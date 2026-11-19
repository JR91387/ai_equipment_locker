# SPDX-License-Identifier: MIT
"""Path identity: case folds on Windows/macOS, stays exact on Linux; backfill merges duplicates without deleting."""
import unittest

import helpers  # noqa: F401

from equipment_locker import db, record
from equipment_locker.paths import backfill, path_key

PRESENT = {"presence": "present", "size_bytes": 1, "size_over": 0, "entry_count": None, "mtime": 1.0}


class TestPathKey(unittest.TestCase):
    def test_windows_and_mac_fold_case_and_separators(self):
        self.assertEqual(path_key("C:\\Users\\Bob\\.Claude\\", "win32"), "c:/users/bob/.claude")
        self.assertEqual(path_key("/Users/Bob/Library/../.Codex", "darwin"), "/users/bob/.codex")

    def test_linux_stays_exact(self):
        self.assertEqual(path_key("/home/Bob/.Claude/", "linux"), "/home/Bob/.Claude")
        self.assertNotEqual(path_key("/home/bob/.claude", "linux"), path_key("/home/Bob/.Claude", "linux"))


class TestIdentity(unittest.TestCase):
    def setUp(self):
        self.conn = db.open_db(":memory:")
        self.addCleanup(self.conn.close)

    def ctx(self, platform):
        m = record.upsert_machine(self.conn, f"box-{platform}", platform)
        run = record.start_run(self.conn, m, {})
        return {"machine_id": m, "run_id": run, "platform": platform, "user_id": None}

    def meta(self, path):
        return {"path": path, "tool": "claude-code", "scope": "user", "category": "config", "source": "official",
                "kind": "dir"}

    def live(self, machine_id):
        return self.conn.execute("SELECT path FROM location WHERE machine_id = ? AND is_retired = 0",
                                 (machine_id,)).fetchall()

    def test_two_spellings_one_row_on_windows(self):
        ctx = self.ctx("win32")
        record.record_location(self.conn, ctx, self.meta("C:/Users/Bob/.claude"), PRESENT)
        ctx2 = {**ctx, "recorded": set(), "run_id": record.start_run(self.conn, ctx["machine_id"], {})}
        record.record_location(self.conn, ctx2, self.meta("c:/users/bob/.Claude"), PRESENT)
        rows = self.live(ctx["machine_id"])
        self.assertEqual([r["path"] for r in rows], ["c:/users/bob/.Claude"])

    def test_two_spellings_two_rows_on_linux(self):
        ctx = self.ctx("linux")
        record.record_location(self.conn, ctx, self.meta("/home/bob/.claude"), PRESENT)
        record.record_location(self.conn, {**ctx, "recorded": set()}, self.meta("/home/bob/.Claude"), PRESENT)
        self.assertEqual(len(self.live(ctx["machine_id"])), 2)

    def test_backfill_merges_by_retiring(self):
        ctx = self.ctx("darwin")
        record.record_location(self.conn, ctx, self.meta("/Users/Bob/.claude"), PRESENT)
        cols = [r[1] for r in self.conn.execute("PRAGMA table_info(location)") if r[1] not in ("id", "path")]
        self.conn.execute("DROP INDEX location_path_key")
        self.conn.execute(f"INSERT INTO location (path, {', '.join(cols)}) "  # a pre-004 duplicate spelling
                          f"SELECT '/users/bob/.CLAUDE', {', '.join(cols)} FROM location")
        self.conn.execute("UPDATE location SET path_key = NULL")
        self.assertEqual(backfill(self.conn), 1)
        total = self.conn.execute("SELECT COUNT(*) FROM location").fetchone()[0]
        self.assertEqual((len(self.live(ctx["machine_id"])), total), (1, 2))
        self.assertEqual(backfill(self.conn), 0)


if __name__ == "__main__":
    unittest.main()
