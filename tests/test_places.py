# SPDX-License-Identifier: MIT
"""places.json integrity, sync into the DB, token resolution per OS, env overrides."""
import re
import unittest
from pathlib import Path

import helpers  # noqa: F401

from equipment_locker import db
from equipment_locker import places as pl

DOC = pl.load()
FIELDS = {"tool", "scope", "category", "path", "kind", "source", "code"}


class TestPlacesFile(unittest.TestCase):
    def test_every_place_is_complete(self):
        bad = [p.get("code") for p in DOC["places"] if not FIELDS <= set(p)]
        self.assertEqual(bad, [])

    def test_codes_unique(self):
        codes = [p["code"] for p in DOC["places"]]
        self.assertEqual(len(codes), len(set(codes)))

    def test_every_token_is_defined(self):
        used = {t for p in DOC["places"] for t in re.findall(r"\{(\w+)\}", p["path"])}
        self.assertLessEqual(used, set(DOC["tokens"]))

    def test_values_are_known(self):
        self.assertTrue(all(p["kind"] in ("dir", "file", "glob") for p in DOC["places"]))
        self.assertTrue(all(p["scope"] in ("user", "system", "project") for p in DOC["places"]))
        self.assertTrue(all(p["source"] in DOC["sources"] for p in DOC["places"]))
        self.assertTrue(all(set(p.get("os") or ()) <= {"linux", "darwin", "win32"} for p in DOC["places"]))


class TestSync(unittest.TestCase):
    def test_sync_is_idempotent_and_retires_removed(self):
        conn = db.open_db(":memory:")
        self.addCleanup(conn.close)
        active, retired = pl.sync(conn, DOC)
        self.assertEqual((active, retired), (len(DOC["places"]), 0))
        self.assertEqual(pl.sync(conn, DOC), (active, 0))
        smaller = {**DOC, "places": DOC["places"][1:]}
        self.assertEqual(pl.sync(conn, smaller), (active - 1, 1))
        n = conn.execute("SELECT COUNT(*) FROM place WHERE is_retired = 1").fetchone()[0]
        self.assertEqual(n, 1)


class TestTokens(unittest.TestCase):
    home = Path("/h/alice")

    def test_windows_roots(self):
        r = pl.token_roots(self.home, "win32")
        self.assertEqual(r["appconfig"], self.home / "AppData" / "Roaming")
        self.assertEqual(r["local"], self.home / "AppData" / "Local")
        self.assertNotIn("appstate", r)

    def test_mac_roots(self):
        r = pl.token_roots(self.home, "darwin")
        self.assertEqual(r["appconfig"], self.home / "Library" / "Application Support")
        self.assertEqual(r["appcache"], self.home / "Library" / "Caches")
        self.assertNotIn("roaming", r)

    def test_linux_xdg_only_for_scanning_user(self):
        env = {"XDG_CONFIG_HOME": "/elsewhere/cfg"}
        self.assertEqual(pl.token_roots(self.home, "linux", env)["appconfig"], Path("/elsewhere/cfg"))
        self.assertEqual(pl.token_roots(self.home, "linux")["appconfig"], self.home / ".config")

    def test_missing_token_skips_entry(self):
        roots = pl.token_roots(self.home, "linux")
        self.assertIsNone(pl.resolve("{roaming}/Claude", "dir", roots))
        self.assertEqual(pl.resolve("{home}/.claude", "dir", roots), self.home / ".claude")

    def test_env_override_replaces_tool_root(self):
        roots = pl.token_roots(self.home, "linux")
        self.assertEqual(pl.resolve("{home}/.claude/skills", "dir", roots, "/cfg"), Path("/cfg/skills"))
        self.assertEqual(pl.resolve("{home}/.claude.json", "file", roots, "/cfg"), Path("/cfg/.claude.json"))
        self.assertEqual(pl.resolve("{home}/.codex", "dir", roots, "/cx"), Path("/cx"))

    def test_env_override_never_replaces_shared_folders(self):
        roots = pl.token_roots(self.home, "linux")
        self.assertEqual(pl.resolve("{home}/.local/bin/codex", "file", roots, "/bin2"),
                         self.home / ".local" / "bin" / "codex")

    def test_applies_by_os(self):
        self.assertTrue(pl.applies({"os": ["darwin"]}, "darwin"))
        self.assertFalse(pl.applies({"os": ["darwin"]}, "win32"))
        self.assertTrue(pl.applies({}, "linux"))


if __name__ == "__main__":
    unittest.main()
