# SPDX-License-Identifier: MIT
"""Local display server: static page + JSON API on 127.0.0.1, background scans on start and every 6 hours.

Refresh on the page scans even under --no-scan, with the same entry limit."""
import binascii
import json
import mimetypes
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from . import api, db, places, scan, search

WEB = Path(__file__).resolve().parent / "web"
MAX_BODY = 3 * 1024 * 1024
RESCAN_SECONDS = 6 * 3600
LOCAL = {"127.0.0.1", "localhost", "[::1]"}


class Scanner:
    """Runs one scan at a time in the background; remembers the last outcome."""

    def __init__(self, db_path, opts):
        self.db_path, self.opts, self.lock = db_path, opts, threading.Lock()
        self.state = {"running": False, "last": None, "error": None}

    def start(self):
        if self.lock.locked():
            return False
        threading.Thread(target=self._run, daemon=True).start()
        return True

    def _run(self):
        with self.lock:
            self.state.update(running=True, error=None)
            conn = db.open_db(self.db_path)
            try:
                s = scan.run(conn, places.load(), self.opts)
                self.state["last"] = {k: s[k] for k in ("run_id", "status", "entries_seen", "items")}
            except Exception as exc:  # noqa: BLE001 - a failed scan is reported on the page, never fatal
                self.state["error"] = f"{type(exc).__name__}: {exc}"
                traceback.print_exc()
            finally:
                conn.close()
                self.state["running"] = False

    def every(self, seconds):
        def loop():
            while True:
                time.sleep(seconds)
                self.start()
        threading.Thread(target=loop, daemon=True).start()


class Handler(BaseHTTPRequestHandler):
    server_version = "EquipmentLocker"

    def log_message(self, fmt, *args):  # quiet by default
        pass

    def _send(self, code, body, ctype="application/json"):
        data = body if isinstance(body, bytes) else json.dumps(body, default=str).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; style-src 'self'")
        self.end_headers()
        self.wfile.write(data)

    def _host(self):
        return (self.headers.get("Host") or "").rsplit(":", 1)[0].lower()

    def _local(self):
        return self._host() in LOCAL | self.server.allow_hosts

    def _refuse(self, what):
        host = self._host() or "(none)"
        return self._send(403, {"error": f"{what}: this server answers only on 127.0.0.1 and localhost, and this "
                                         f"request asked for '{host}'. To view it from another machine, use an SSH "
                                         f"tunnel, or restart with: serve --allow-host {host} "
                                         "(see docs/wiki/View-From-Another-Machine.md)"})

    def _conn(self):
        return db.connect(self.server.db_path)

    def do_GET(self):
        if not self._local():
            return self._refuse("local only")
        url = urlparse(self.path)
        if not url.path.startswith("/api/"):
            return self._static(url.path)
        conn = self._conn()
        try:
            self._get_api(conn, url.path.split("/")[2:], {k: v[0] for k, v in parse_qs(url.query).items()})
        finally:
            conn.close()

    def _get_api(self, conn, parts, qs):
        name = parts[0] if parts else ""
        if name == "summary":
            return self._send(200, api.summary(conn) | {"scan": self.server.scanner.state})
        if name == "tool" and len(parts) > 1:
            return self._send(200, api.tool_detail(conn, parts[1]))
        if name == "table":
            return self._send(200, api.table(conn))
        if name == "search":
            return self._send(200, {"results": search.query(conn, qs.get("q", ""), qs)})
        if name == "detail" and len(parts) > 2 and parts[1] in api.DETAIL_SQL:
            found = api.detail(conn, parts[1], parts[2])
            return self._send(200 if found else 404, found or {"error": "not found"})
        if name == "image" and len(parts) > 1 and parts[1].isdigit():
            found = api.image(conn, int(parts[1]))
            return self._send(200, found[1], found[0]) if found else self._send(404, {"error": "not found"})
        if name == "scan":
            return self._send(200, self.server.scanner.state)
        return self._send(404, {"error": "unknown"})

    def _static(self, path):
        rel = "index.html" if path in ("", "/") else path.lstrip("/")
        target = (WEB / rel).resolve()
        if WEB not in target.parents or not target.is_file():
            return self._send(404, b"not found", "text/plain")
        ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        return self._send(200, target.read_bytes(), ctype)

    def do_POST(self):
        origin = self.headers.get("Origin")
        same = origin is None or urlparse(origin).hostname in {"127.0.0.1", "localhost", "::1"} | self.server.allow_hosts
        if not self._local() or self.headers.get("X-Locker") != "1" or not same:
            return self._refuse("local page only")
        length = int(self.headers.get("Content-Length") or 0)
        if length > MAX_BODY:
            return self._send(413, {"error": "too large"})
        action = urlparse(self.path).path.split("/")[-1]
        if action == "scan":
            return self._send(202, {"started": self.server.scanner.start()})
        self._post(action, self.rfile.read(length))

    def _post(self, action, raw):
        conn = self._conn()
        try:
            self._send(200, api.write(conn, action, json.loads(raw or b"{}")))
        except OverflowError as exc:
            self._send(413, {"error": str(exc)})
        except (ValueError, KeyError, TypeError, binascii.Error) as exc:
            self._send(400, {"error": str(exc) or "bad request"})
        finally:
            conn.close()


def make_server(db_path, opts, port=8765, allow=()):
    """Build (not start) the server; migrations run once here. allow: extra Host names to accept (a proxy's)."""
    conn = db.open_db(db_path)
    places.sync(conn, places.load())
    search.rebuild(conn)
    conn.close()
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    httpd.db_path, httpd.scanner = str(db_path), Scanner(db_path, opts)
    httpd.allow_hosts = {h.lower() for h in allow}
    return httpd


def serve(db_path, opts, web):
    """web: port, scan (scan on start and every 6 h), allow (extra Host names)."""
    httpd = make_server(db_path, opts, web["port"], web["allow"])
    print(f"catalog: {db_path}", flush=True)
    if web["scan"]:
        httpd.scanner.start()
        httpd.scanner.every(RESCAN_SECONDS)
    print(f"Equipment Locker: http://127.0.0.1:{httpd.server_address[1]}/  (Ctrl+C to stop)", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
