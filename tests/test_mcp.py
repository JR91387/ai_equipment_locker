# SPDX-License-Identifier: MIT
"""MCP server: protocol shape over a real subprocess, tools, errors, read-only mode."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import helpers

from equipment_locker import db, places, scan


def rpc(mid, method, params=None):
    msg = {"jsonrpc": "2.0", "id": mid, "method": method}
    if params is not None:
        msg["params"] = params
    return msg


class TestMcp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(tempfile.mkdtemp())
        home = root / "home" / "alice"
        (home / ".claude" / "skills" / "code-review").mkdir(parents=True)
        (home / ".claude" / "skills" / "code-review" / "SKILL.md").write_text(
            "---\nname: code-review\ndescription: Reviews diffs\n---\n")
        cls.db = root / "cat.db"
        conn = db.open_db(cls.db)
        opts = {"platform": "linux", "machine": "t", "env": {}, "current_home": home, "users": "me",
                "projects": False, "sweep": False, "limits": {"depth": 4, "max_entries": 50000, "size_max_files": 100}}
        scan.run(conn, places.load(), opts)
        conn.close()

    def session(self, messages, *flags):
        env = {**os.environ, "PYTHONPATH": str(helpers.ROOT / "src")}
        lines = "\n".join(json.dumps(m) for m in messages) + "\n"
        out = subprocess.run([sys.executable, "-m", "equipment_locker", "mcp", "--db", str(self.db), *flags],
                             input=lines, capture_output=True, text=True, env=env, timeout=60, check=True)
        return [json.loads(line) for line in out.stdout.splitlines()]

    def call(self, name, args, *flags):
        replies = self.session([rpc(1, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                                       "clientInfo": {"name": "t", "version": "0"}}),
                                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                                rpc(2, "tools/call", {"name": name, "arguments": args})], *flags)
        return replies[1]["result"]

    def test_handshake_and_tool_list(self):
        replies = self.session([rpc(1, "initialize", {"protocolVersion": "2025-06-18"}),
                                {"jsonrpc": "2.0", "method": "notifications/initialized"}, rpc(2, "tools/list"),
                                rpc(3, "ping")])
        self.assertEqual(len(replies), 3)  # the notification gets no reply
        self.assertEqual(replies[0]["result"]["protocolVersion"], "2025-06-18")
        self.assertIn("tools", replies[0]["result"]["capabilities"])
        names = {t["name"] for t in replies[1]["result"]["tools"]}
        self.assertEqual(names, {"search", "list_tools", "tool_detail", "item_detail", "recent_changes",
                                 "add_tag", "remove_tag", "set_note"})
        self.assertEqual(replies[2]["result"], {})

    def test_unknown_version_falls_back(self):
        reply = self.session([rpc(1, "initialize", {"protocolVersion": "1999-01-01"})])[0]
        self.assertEqual(reply["result"]["protocolVersion"], "2025-06-18")

    def test_search_and_note_round_trip(self):
        hits = json.loads(self.call("search", {"query": "Code_Review"})["content"][0]["text"])
        item = next(h for h in hits if h["kind"] == "item")
        self.call("set_note", {"target_kind": "item", "target_id": item["ref_id"], "note": "use before merge"})
        self.call("add_tag", {"target_kind": "item", "target_id": item["ref_id"], "tag": "daily"})
        detail = json.loads(self.call("item_detail", {"kind": "item", "id": item["ref_id"]})["content"][0]["text"])
        self.assertEqual((detail["annotation"]["note"], detail["tags"]), ("use before merge", ["daily"]))
        tools = json.loads(self.call("list_tools", {})["content"][0]["text"])
        self.assertEqual(tools["tools"][0]["items"], {"skill": 1})

    def test_errors(self):
        replies = self.session([rpc(1, "nope"), rpc(2, "tools/call", {"name": "missing"}), {"id": 3}])
        self.assertEqual([r["error"]["code"] for r in replies], [-32601, -32602, -32600])
        res = self.call("item_detail", {"kind": "item", "id": 99999})
        self.assertTrue(res["isError"])
        self.assertTrue(self.call("tool_detail", {})["isError"])

    def test_read_only_hides_writes(self):
        replies = self.session([rpc(1, "tools/list"), rpc(2, "tools/call", {"name": "set_note", "arguments": {}})],
                               "--read-only")
        self.assertEqual(len(replies[0]["result"]["tools"]), 5)
        self.assertEqual(replies[1]["error"]["code"], -32602)


if __name__ == "__main__":
    unittest.main()
