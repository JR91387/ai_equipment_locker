# SPDX-License-Identifier: MIT
"""MCP server over stdin/stdout (JSON-RPC 2.0, one message per line). Standard library only.

Run: python -m equipment_locker mcp [--db PATH] [--read-only]
Only JSON-RPC goes to stdout; anything else goes to stderr.
"""
import json
import sys

from . import __version__, db
from .mcp_tools import TOOLS

SUPPORTED = ("2025-06-18", "2025-03-26", "2024-11-05")
INSTRUCTIONS = ("Equipment Locker is a catalogue of the AI tools on this computer: their skills, agents, MCP "
                "servers, plugins and folders. Start with list_tools or search. It never reads tool files; notes and "
                "tags belong to the person, so change them only when asked.")


class Server:
    def __init__(self, conn, read_only=False):
        self.conn = conn
        self.tools = {t[0]: t for t in TOOLS if not (read_only and t[4])}

    def handle(self, msg):
        """Reply dict for a request, or None for a notification."""
        if not isinstance(msg, dict) or msg.get("jsonrpc") != "2.0" or "method" not in msg:
            return _error(msg.get("id") if isinstance(msg, dict) else None, -32600, "Invalid Request")
        method, mid = msg["method"], msg.get("id")
        if mid is None:
            return None  # notifications (initialized, cancelled) need no reply
        fn = {"initialize": self.initialize, "ping": lambda p: {}, "tools/list": self.list_tools,
              "tools/call": self.call_tool}.get(method)
        if fn is None:
            return _error(mid, -32601, f"Method not found: {method}")
        try:
            return {"jsonrpc": "2.0", "id": mid, "result": fn(msg.get("params") or {})}
        except (KeyError, TypeError, ValueError) as exc:
            return _error(mid, -32602, f"Invalid params: {exc}")

    def initialize(self, params):
        asked = params.get("protocolVersion")
        return {"protocolVersion": asked if asked in SUPPORTED else SUPPORTED[0],
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "equipment-locker", "version": __version__},
                "instructions": INSTRUCTIONS}

    def list_tools(self, params):
        return {"tools": [{"name": n, "description": d, "inputSchema": s} for n, d, s, _, _ in self.tools.values()]}

    def call_tool(self, params):
        name, args = params["name"], params.get("arguments") or {}
        if name not in self.tools:
            raise ValueError(f"unknown tool {name}")
        try:
            data = self.tools[name][3](self.conn, args)
        except KeyError as exc:
            return _tool_error(f"missing argument {exc}")
        except (LookupError, ValueError, OverflowError) as exc:
            return _tool_error(str(exc))
        return {"content": [{"type": "text", "text": json.dumps(data, default=str, ensure_ascii=False)}]}


def _error(mid, code, message):
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}


def _tool_error(text):
    return {"content": [{"type": "text", "text": text}], "isError": True}


def serve(db_path, read_only=False, stdin=None, stdout=None):
    """Read requests line by line until stdin closes."""
    stdin, stdout = stdin or sys.stdin, stdout or sys.stdout
    conn = db.open_db(db_path)
    server = Server(conn, read_only)
    try:
        for line in stdin:
            if not line.strip():
                continue
            try:
                reply = server.handle(json.loads(line))
            except json.JSONDecodeError:
                reply = _error(None, -32700, "Parse error")
            if reply is not None:
                stdout.write(json.dumps(reply, default=str, ensure_ascii=False) + "\n")
                stdout.flush()
    finally:
        conn.close()
