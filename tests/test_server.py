# SPDX-License-Identifier: MIT
"""Local server: API round trips and the local-only guards."""
import base64
import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

import helpers  # noqa: F401
from test_annotations import png

from equipment_locker import server


class TestServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(tempfile.mkdtemp())
        home = root / "home" / "alice"
        (home / ".claude" / "skills" / "one").mkdir(parents=True)
        (home / ".claude" / "skills" / "one" / "SKILL.md").write_text("---\nname: one\ndescription: First\n---\n")
        opts = {"platform": "linux", "machine": "t", "env": {}, "current_home": home, "users": "me",
                "projects": False, "sweep": False, "limits": {"depth": 4, "max_entries": 50000, "size_max_files": 100}}
        cls.httpd = server.make_server(root / "cab.db", opts, port=0)
        cls.httpd.scanner._run()
        cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()

    def call(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=10)
        hdrs = {"Host": f"127.0.0.1:{self.port}", **(headers or {})}
        data = json.dumps(body).encode() if body is not None else None
        conn.request(method, path, data, hdrs)
        res = conn.getresponse()
        raw = res.read()
        conn.close()
        return res.status, raw

    def get(self, path):
        status, raw = self.call("GET", path)
        return status, json.loads(raw)

    def post(self, action, body):
        return self.call("POST", f"/api/{action}", body, {"X-Locker": "1", "Content-Type": "application/json"})

    def test_summary_tool_search(self):
        _, s = self.get("/api/summary")
        self.assertEqual(s["tools"][0]["tool"], "claude-code")
        self.assertEqual(s["tools"][0]["items"], {"skill": 1})
        _, t = self.get("/api/tool/claude-code")
        self.assertEqual(t["groups"][0]["items"][0]["name"], "one")
        _, r = self.get("/api/search?q=FIRST")
        self.assertTrue(any(x["title"] == "one" for x in r["results"]))

    def test_note_tag_image_round_trip(self):
        target = {"kind": "tool", "id": "claude-code"}
        self.assertEqual(self.post("annotation", {"target": target, "fields": {"note": "daily"}})[0], 200)
        self.assertEqual(self.post("tag", {"target": target, "name": "core"})[0], 200)
        status, raw = self.post("image", {"target": target, "data": base64.b64encode(png()).decode()})
        self.assertEqual(status, 200)
        _, d = self.get("/api/detail/tool/claude-code")
        self.assertEqual((d["annotation"]["note"], d["tags"]), ("daily", ["core"]))
        status, img = self.call("GET", f"/api/image/{json.loads(raw)['image_id']}")
        self.assertEqual((status, img[:4]), (200, b"\x89PNG"))

    def test_guards(self):
        self.assertEqual(self.call("GET", "/api/summary", headers={"Host": "evil.example"})[0], 403)
        self.assertEqual(self.call("POST", "/api/annotation", {})[0], 403)
        hdr = {"X-Locker": "1", "Origin": "http://evil.example"}
        self.assertEqual(self.call("POST", "/api/annotation", {}, hdr)[0], 403)
        self.assertEqual(self.post("image", {"target": {"kind": "tool", "id": "claude-code"},
                                             "data": base64.b64encode(b"GIF89a" + b"0" * 2_200_000).decode()})[0], 413)
        self.assertEqual(self.post("image", {"target": {"kind": "tool", "id": "claude-code"}, "data": "!!"})[0], 400)
        self.assertEqual(self.call("GET", "/../../etc/passwd")[0], 404)


if __name__ == "__main__":
    unittest.main()
