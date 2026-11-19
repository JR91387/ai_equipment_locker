# SPDX-License-Identifier: MIT
"""Search: one document per tool, location, item and project. Matching ignores case and separators
("Claude-Code", "claude code" and ".claude" all match "claude"); FTS5 trigram when SQLite has it, LIKE otherwise."""
import re
import sqlite3

_SEP = re.compile(r"[\s\-_./\\:]+")
LIMIT = 200

DOCS = {
    "tool": """SELECT t.id, t.display, a.note, '', t.code FROM ref_tool t
               LEFT JOIN annotation a ON a.tool_id = t.id WHERE t.is_retired = 0""",
    "location": """SELECT l.id, l.path, COALESCE(pl.holds, '') || ' ' || COALESCE(a.note, ''), l.path, t.code
                   FROM location l JOIN ref_tool t ON t.id = l.tool_id LEFT JOIN place pl ON pl.id = l.place_id
                   LEFT JOIN annotation a ON a.location_id = l.id WHERE l.is_retired = 0""",
    "item": """SELECT i.id, i.name, COALESCE(i.description, '') || ' ' || COALESCE(a.note, ''),
                      l.path || '/' || i.rel_path, t.code
               FROM item i JOIN location l ON l.id = i.location_id JOIN ref_tool t ON t.id = l.tool_id
               JOIN ref_presence p ON p.id = i.presence_id LEFT JOIN annotation a ON a.item_id = i.id
               WHERE i.is_retired = 0 AND p.code = 'present'""",
    "project": "SELECT id, root, '', root, '' FROM project WHERE is_retired = 0",
}
TAGS = """SELECT COALESCE(location_id, item_id, tool_id) AS ref, location_id, item_id, tool_id,
                 group_concat(t.name, ' ') AS names FROM tag_link l JOIN tag t ON t.id = l.tag_id
          WHERE l.is_retired = 0 AND t.is_retired = 0 GROUP BY location_id, item_id, tool_id"""


def normalize(text):
    return _SEP.sub(" ", str(text or "").lower()).strip()


def has_fts(conn):
    try:
        conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS search_fts USING fts5(norm, content='', tokenize='trigram')")
        return True
    except sqlite3.OperationalError:
        return False


def _tag_map(conn):
    out = {}
    for r in conn.execute(TAGS):
        kind = "location" if r["location_id"] else "item" if r["item_id"] else "tool"
        out[(kind, r["ref"])] = r["names"]
    return out


def rebuild(conn):
    """Rewrite all search documents from the catalog. Returns how many."""
    tags = _tag_map(conn)
    fts = has_fts(conn)
    conn.execute("BEGIN")
    conn.execute("DELETE FROM search_doc")
    if fts:
        conn.execute("INSERT INTO search_fts(search_fts) VALUES ('delete-all')")
    for kind, sql in DOCS.items():
        for ref, title, body, path, tool in conn.execute(sql).fetchall():
            title = str(title).replace("\\", "/").rstrip("/").rsplit("/", 1)[-1] if kind != "item" else title
            tag = tags.get((kind, ref), "")
            norm = normalize(" ".join(str(x or "") for x in (title, body, path, tool, tag)))
            cur = conn.execute("INSERT INTO search_doc (kind, ref_id, title, body, path, tool, tags, norm) "
                               "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (kind, ref, title, body, path, tool, tag, norm))
            if fts:
                conn.execute("INSERT INTO search_fts(rowid, norm) VALUES (?, ?)", (cur.lastrowid, norm))
    conn.execute("COMMIT")
    return conn.execute("SELECT COUNT(*) FROM search_doc").fetchone()[0]


def _filters(filters):
    sql, args = "", []
    for col in ("kind", "tool"):
        if filters.get(col):
            sql += f" AND d.{col} = ?"
            args.append(filters[col])
    return sql, args


def query(conn, text, filters=None):
    """Matching documents, best first. Short or unindexable queries use a normalized LIKE."""
    q = normalize(text)
    if not q:
        return []
    extra, args = _filters(filters or {})
    cols = "d.kind, d.ref_id, d.title, d.body, d.path, d.tool, d.tags"
    if len(q) >= 3 and has_fts(conn):
        phrase = '"' + q.replace('"', '""') + '"'
        rows = conn.execute(f"SELECT {cols} FROM search_fts f JOIN search_doc d ON d.id = f.rowid "
                            f"WHERE search_fts MATCH ?{extra} ORDER BY bm25(search_fts) LIMIT ?",
                            (phrase, *args, LIMIT)).fetchall()
    else:
        like = "%" + q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        rows = conn.execute(f"SELECT {cols} FROM search_doc d WHERE d.norm LIKE ? ESCAPE '\\'{extra} "
                            f"ORDER BY d.kind, d.title LIMIT ?", (like, *args, LIMIT)).fetchall()
    return [dict(r) for r in rows]
