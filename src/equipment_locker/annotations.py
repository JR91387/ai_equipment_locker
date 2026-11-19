# SPDX-License-Identifier: MIT
"""What the person adds: notes, labels, favourites, tags, images, pinned folders. Only the catalog DB is written."""
import os
import stat
import struct

from .db import now
from .paths import path_key

MAX_IMAGE = 2 * 1024 * 1024
TARGETS = {"location": "location_id", "item": "item_id", "tool": "tool_id"}
MAGIC = ((b"\x89PNG\r\n\x1a\n", "image/png"), (b"\xff\xd8\xff", "image/jpeg"), (b"GIF87a", "image/gif"),
         (b"GIF89a", "image/gif"))


def target_column(conn, target):
    """(column, id) for {'kind': 'location'|'item'|'tool', 'id': int or tool code}."""
    col = TARGETS.get(target.get("kind"))
    if col is None:
        raise ValueError("target kind must be location, item or tool")
    ident = target["id"]
    if col == "tool_id" and not str(ident).isdigit():
        ident = conn.ref_id("ref_tool", str(ident))
    return col, int(ident)


def set_annotation(conn, target, fields):
    """Create or update the one annotation of a target. fields: label, note, is_favorite (any subset)."""
    col, ident = target_column(conn, target)
    keep = {k: fields[k] for k in ("label", "note", "is_favorite") if k in fields}
    if "is_favorite" in keep:
        keep["is_favorite"] = int(bool(keep["is_favorite"]))
    row = conn.execute(f"SELECT id FROM annotation WHERE {col} = ?", (ident,)).fetchone()
    if row is None:
        conn.execute(f"INSERT INTO annotation ({col}, label, note, is_favorite, updated) VALUES (?, ?, ?, ?, ?)",
                     (ident, keep.get("label"), keep.get("note"), keep.get("is_favorite", 0), now()))
    elif keep:
        sets = ", ".join(f"{k} = ?" for k in keep)
        conn.execute(f"UPDATE annotation SET {sets}, updated = ? WHERE id = ?", (*keep.values(), now(), row[0]))
    return conn.execute(f"SELECT * FROM annotation WHERE {col} = ?", (ident,)).fetchone()


def tag(conn, target, name, on=True):
    """Add (on=True) or retire (on=False) a tag on a target. Tag names are case-insensitive."""
    col, ident = target_column(conn, target)
    name = " ".join(str(name).split())[:60]
    if not name:
        raise ValueError("empty tag")
    conn.execute("INSERT INTO tag (name) VALUES (?) ON CONFLICT(name) DO UPDATE SET is_retired = 0", (name,))
    tag_id = conn.execute("SELECT id FROM tag WHERE name = ?", (name,)).fetchone()[0]
    row = conn.execute(f"SELECT id FROM tag_link WHERE tag_id = ? AND {col} = ?", (tag_id, ident)).fetchone()
    if row:
        conn.execute("UPDATE tag_link SET is_retired = ? WHERE id = ?", (int(not on), row[0]))
    elif on:
        conn.execute(f"INSERT INTO tag_link (tag_id, {col}, created) VALUES (?, ?, ?)", (tag_id, ident, now()))
    return tag_id


def sniff(data):
    """(mime, width, height) from image bytes, or raises ValueError for anything not png/jpeg/gif/webp."""
    if len(data) > MAX_IMAGE:
        raise OverflowError("image larger than 2 MB")
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp", None, None
    mime = next((m for sig, m in MAGIC if data.startswith(sig)), None)
    if mime is None:
        raise ValueError("only png, jpeg, gif or webp images")
    if mime == "image/png" and len(data) >= 24:
        return mime, *struct.unpack(">II", data[16:24])
    if mime == "image/gif" and len(data) >= 10:
        return mime, *struct.unpack("<HH", data[6:10])
    return mime, None, None


def add_image(conn, target, data):
    """Store an image for a target; earlier images of that target are retired. Returns the image id."""
    col, ident = target_column(conn, target)
    mime, width, height = sniff(data)
    conn.execute(f"UPDATE image SET is_retired = 1 WHERE {col} = ? AND is_retired = 0", (ident,))
    cur = conn.execute(f"""INSERT INTO image ({col}, mime, bytes, byte_size, width, height, created)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""", (ident, mime, data, len(data), width, height, now()))
    return cur.lastrowid


def pin(conn, path, tool="other", category="pinned"):
    """Pin a folder or file so every scan includes it. Returns the place id. Re-pinning re-enables it."""
    try:
        st = os.lstat(path)
    except OSError as exc:
        raise ValueError(f"cannot pin {path}: not found or not readable") from exc
    kind = "dir" if stat.S_ISDIR(st.st_mode) else "file"
    code = "pin:" + path_key(path)
    ids = (conn.ref_id("ref_tool", tool, tool), conn.ref_id("ref_scope", "pinned"),
           conn.ref_id("ref_category", category, category), conn.ref_id("ref_source", "user"))
    conn.execute("""INSERT INTO place (code, tool_id, scope_id, category_id, source_id, path_template, kind,
                      is_builtin, is_enabled, updated) VALUES (?, ?, ?, ?, ?, ?, ?, 0, 1, ?)
                    ON CONFLICT(code) DO UPDATE SET is_enabled = 1, is_retired = 0, tool_id = excluded.tool_id,
                      category_id = excluded.category_id, updated = excluded.updated""",
                 (code, *ids, str(path), kind, now()))
    return conn.execute("SELECT id FROM place WHERE code = ?", (code,)).fetchone()[0]


def unpin(conn, place_id):
    """Stop scanning a pinned place; its history stays."""
    conn.execute("UPDATE place SET is_enabled = 0, updated = ? WHERE id = ? AND is_builtin = 0", (now(), place_id))


def pinned(conn):
    """Enabled pinned places as dicts shaped like places.json entries."""
    rows = conn.execute("""SELECT p.id, p.code, p.path_template AS path, p.kind, t.code AS tool, c.code AS category
                           FROM place p JOIN ref_tool t ON t.id = p.tool_id JOIN ref_category c ON c.id = p.category_id
                           JOIN ref_scope s ON s.id = p.scope_id
                           WHERE s.code = 'pinned' AND p.is_enabled = 1 AND p.is_retired = 0""").fetchall()
    return [{**dict(r), "scope": "pinned", "source": "user"} for r in rows]
