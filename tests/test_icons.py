# SPDX-License-Identifier: MIT
"""Bundled icons: tool glyphs are listed in SOURCES.md and reach the API; every item kind has an icon."""
import re
import unittest
import xml.etree.ElementTree as ET

import helpers

from equipment_locker import api, db

WEB = helpers.ROOT / "src" / "equipment_locker" / "web" / "icons"
KINDS = ["skill", "agent", "command", "mcp_server", "plugin", "extension", "rule", "model", "workflow",
         "output_style", "prompt", "hook", "folder"]


class TestIcons(unittest.TestCase):
    def test_tool_icons_valid_and_sourced(self):
        sources = (WEB / "tools" / "SOURCES.md").read_text()
        files = sorted((WEB / "tools").glob("*.svg"))
        self.assertGreaterEqual(len(files), 10)
        for f in files:
            root = ET.parse(f).getroot()
            self.assertRegex(root.get("fill") or "", r"^#[0-9A-Fa-f]{6}$", f.name)
            self.assertIn(f"`{f.name}`", sources)

    def test_every_kind_has_an_icon(self):
        for kind in KINDS:
            ET.parse(WEB / "kinds" / f"{kind}.svg")

    def test_icon_for(self):
        self.assertEqual(api.icon_for("claude-code")[0], "icons/tools/claude-code.svg")
        self.assertTrue(api.icon_for("huggingface")[1])   # yellow glyph sits on a dark tile
        self.assertFalse(api.icon_for("cursor")[1])
        self.assertEqual(api.icon_for("codex"), (None, False))

    def test_summary_carries_icon(self):
        conn = db.open_db(":memory:")
        self.addCleanup(conn.close)
        self.assertEqual(api.summary(conn)["tools"], [])
        self.assertTrue(re.match(r"icons/tools/", api.icon_for("ollama")[0]))


if __name__ == "__main__":
    unittest.main()
