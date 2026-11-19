# SPDX-License-Identifier: MIT
"""Read and write operations behind the local page. Each takes a connection and returns JSON-ready data."""
import base64
import re
import zlib
from functools import cache
from pathlib import Path

from . import annotations as ann
from . import search

TOOL_ICONS = Path(__file__).resolve().parent / "web" / "icons" / "tools"
GRADIENTS = 10
LIGHT_GRADIENTS = {2, 5, 9}  # pale blends: lettering on them is dark


@cache
def icon_for(code):
    """(url, dark_tile) for a bundled tool icon, or (None, False). Very light brand colours sit on a dark tile."""
    path = TOOL_ICONS / f"{code}.svg"
    if not path.is_file():
        return None, False
    m = re.search(r'fill="#([0-9A-Fa-f]{6})"', path.read_text())
    r, g, b = (int(m.group(1)[i:i + 2], 16) / 255 for i in (0, 2, 4)) if m else (0, 0, 0)
    return f"icons/tools/{code}.svg", 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.6


def gradient_for(code):
    """Stable gradient number 1..10 for a tool without its own picture."""
    return zlib.crc32(str(code).encode()) % GRADIENTS + 1


ITEM_ORDER = ("skill", "agent", "command", "mcp_server", "plugin", "extension", "rule", "workflow", "model")


def _rows(conn, sql, args=()):
    return [dict(r) for r in conn.execute(sql, args).fetchall()]


def summary(conn):
    """Tool shelves: one entry per tool with something present, plus the last scan."""
    tools = _rows(conn, """SELECT t.code AS tool, t.display, s.present, s.bytes, s.vendored,
                             a.is_favorite, a.label, (SELECT MAX(id) FROM image i WHERE i.tool_id = t.id
                             AND i.is_retired = 0) AS image_id
                           FROM v_tool_summary s JOIN ref_tool t ON t.code = s.tool
                           LEFT JOIN annotation a ON a.tool_id = t.id WHERE s.present > 0""")
    counts = {}
    for r in conn.execute("""SELECT t.code AS tool, k.code AS kind, COUNT(*) AS n FROM item i
                             JOIN location l ON l.id = i.location_id JOIN ref_tool t ON t.id = l.tool_id
                             JOIN ref_item_kind k ON k.id = i.kind_id JOIN ref_presence p ON p.id = i.presence_id
                             WHERE p.code = 'present' AND i.is_retired = 0 GROUP BY 1, 2"""):
        counts.setdefault(r["tool"], {})[r["kind"]] = r["n"]
    for t in tools:
        t["items"] = counts.get(t["tool"], {})
        t["gradient"] = gradient_for(t["tool"])
        t["gradient_light"] = t["gradient"] in LIGHT_GRADIENTS
        t["icon"], t["icon_dark"] = icon_for(t["tool"])
    last = conn.execute("""SELECT r.id, r.started, r.finished, s.code AS status FROM scan_run r
                           JOIN ref_run_status s ON s.id = r.status_id ORDER BY r.id DESC LIMIT 1""").fetchone()
    tools.sort(key=lambda t: (-(t["is_favorite"] or 0), -t["present"], t["tool"]))
    return {"tools": tools, "last_scan": dict(last) if last else None}


ITEMS_SQL = """SELECT i.id, k.code AS kind, i.name, i.description, l.path || '/' || i.rel_path AS path,
                      a.is_favorite, a.label FROM item i JOIN ref_item_kind k ON k.id = i.kind_id
               JOIN location l ON l.id = i.location_id JOIN ref_tool t ON t.id = l.tool_id
               JOIN ref_presence p ON p.id = i.presence_id LEFT JOIN annotation a ON a.item_id = i.id
               WHERE t.code = ? AND p.code = 'present' AND i.is_retired = 0 ORDER BY lower(i.name)"""
LOC_SQL = """SELECT v.id, v.category, v.kind, v.path, v.size_bytes, v.size_over, v.presence, v.origin, v.project_root,
                    a.is_favorite, a.label FROM v_location_current v LEFT JOIN annotation a ON a.location_id = v.id
             WHERE v.tool = ? ORDER BY v.origin, v.path"""


def tool_detail(conn, code):
    """One tool's shelf: items grouped by kind, then its folders and files."""
    groups = {}
    for it in _rows(conn, ITEMS_SQL, (code,)):
        groups.setdefault(it["kind"], []).append(it)
    ordered = [{"kind": k, "items": groups[k]} for k in sorted(groups, key=lambda k: (
        ITEM_ORDER.index(k) if k in ITEM_ORDER else 99, k))]
    return {"tool": code, "groups": ordered, "locations": _rows(conn, LOC_SQL, (code,))}


def table(conn, limit=2000):
    """Flat list for the table view: items and locations together."""
    rows = _rows(conn, """SELECT 'item' AS type, i.id, t.code AS tool, k.code AS kind, i.name, l.path || '/' ||
                            i.rel_path AS path, NULL AS size_bytes, i.updated FROM item i
                          JOIN ref_item_kind k ON k.id = i.kind_id JOIN location l ON l.id = i.location_id
                          JOIN ref_tool t ON t.id = l.tool_id JOIN ref_presence p ON p.id = i.presence_id
                          WHERE p.code = 'present' AND i.is_retired = 0 LIMIT ?""", (limit,))
    rows += _rows(conn, """SELECT 'location' AS type, id, tool, category AS kind, path AS name, path, size_bytes,
                             NULL AS updated FROM v_location_current WHERE presence = 'present' LIMIT ?""", (limit,))
    return {"rows": rows}


DETAIL_SQL = {
    "location": "SELECT v.*, pl.holds FROM v_location_current v LEFT JOIN place pl ON pl.id = "
                "(SELECT place_id FROM location WHERE id = v.id) WHERE v.id = ?",
    "item": """SELECT i.id, k.code AS kind, i.name, i.description, l.path || '/' || i.rel_path AS path, t.code AS tool,
                      i.first_seen_run, i.last_seen_run FROM item i JOIN ref_item_kind k ON k.id = i.kind_id
               JOIN location l ON l.id = i.location_id JOIN ref_tool t ON t.id = l.tool_id WHERE i.id = ?""",
    "tool": "SELECT t.id, t.code AS tool, t.display FROM ref_tool t WHERE t.code = ?",
}


def detail(conn, kind, ident):
    """Everything the detail panel shows for one location, item or tool."""
    row = conn.execute(DETAIL_SQL[kind], (ident,)).fetchone()
    if row is None:
        return None
    out = dict(row)
    col, tid = ann.target_column(conn, {"kind": kind, "id": ident})
    note = conn.execute(f"SELECT label, note, is_favorite FROM annotation WHERE {col} = ?", (tid,)).fetchone()
    out["annotation"] = dict(note) if note else {}
    out["tags"] = [r[0] for r in conn.execute(f"""SELECT t.name FROM tag_link l JOIN tag t ON t.id = l.tag_id
                                                 WHERE l.{col} = ? AND l.is_retired = 0 ORDER BY t.name""", (tid,))]
    img = conn.execute(f"SELECT MAX(id) FROM image WHERE {col} = ? AND is_retired = 0", (tid,)).fetchone()[0]
    out["image_id"] = img
    if kind == "tool":
        out["gradient"] = gradient_for(ident)
        out["gradient_light"] = out["gradient"] in LIGHT_GRADIENTS
        out["icon"], out["icon_dark"] = icon_for(out["tool"])
    if kind == "location":
        out["history"] = _rows(conn, """SELECT c.code AS change, lc.at, lc.size_bytes FROM location_change lc
                                        JOIN ref_change c ON c.id = lc.change_id WHERE lc.location_id = ?
                                        ORDER BY lc.id DESC LIMIT 10""", (ident,))
    return out


def image(conn, image_id):
    row = conn.execute("SELECT mime, bytes FROM image WHERE id = ?", (image_id,)).fetchone()
    return (row["mime"], row["bytes"]) if row else None


def write(conn, action, body):
    """POST actions from the page. Returns a small JSON result; search is refreshed after edits."""
    target = body.get("target") or {}
    if action == "annotation":
        result = dict(ann.set_annotation(conn, target, body.get("fields") or {}))
    elif action == "tag":
        result = {"tag_id": ann.tag(conn, target, body.get("name", ""), bool(body.get("on", True)))}
    elif action == "image":
        result = {"image_id": ann.add_image(conn, target, base64.b64decode(body.get("data", ""), validate=True))}
    elif action == "pin":
        result = {"place_id": ann.pin(conn, body.get("path", ""), body.get("tool") or "other")}
    elif action == "unpin":
        ann.unpin(conn, int(body.get("place_id", 0)))
        result = {"ok": True}
    else:
        raise KeyError(action)
    search.rebuild(conn)
    return result
