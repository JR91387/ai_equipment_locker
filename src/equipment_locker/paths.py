# SPDX-License-Identifier: MIT
"""Path identity: one key per real folder, case-insensitive where the OS is (Windows, macOS)."""
import posixpath
import sys

CASE_INSENSITIVE = ("win32", "darwin")
CHILDREN = (("item", "location_id"), ("annotation", "location_id"), ("tag_link", "location_id"),
            ("image", "location_id"))


def path_key(path, platform=sys.platform):
    """Normalized identity of a path: forward slashes, no trailing slash, lowercased on Windows and macOS."""
    text = str(path).replace("\\", "/")
    text = posixpath.normpath(text) if text else text
    text = text.rstrip("/") or "/"
    return text.lower() if platform in CASE_INSENSITIVE else text


def _tables(conn):
    return {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}


def _merge(conn, table, survivor, dup):
    """Retire a case duplicate and move what hangs off it to the survivor (never deletes)."""
    conn.execute(f"UPDATE {table} SET is_retired = 1 WHERE id = ?", (dup,))
    if table != "location":
        conn.execute("UPDATE location SET project_id = ? WHERE project_id = ?", (survivor, dup))
        return
    present = _tables(conn)
    for child, col in CHILDREN:
        if child in present:
            conn.execute(f"UPDATE OR IGNORE {child} SET {col} = ? WHERE {col} = ?", (survivor, dup))


def backfill(conn):
    """Fill missing path keys and merge live rows that share one. Idempotent. Returns rows merged."""
    merged = 0
    conn.execute("BEGIN")
    for table, col in (("location", "path"), ("project", "root")):
        rows = conn.execute(f"""SELECT t.id, t.machine_id, t.{col} AS p, o.code AS os FROM {table} t
                                JOIN machine m ON m.id = t.machine_id JOIN ref_os o ON o.id = m.os_id
                                WHERE t.path_key IS NULL ORDER BY t.id""").fetchall()
        for r in rows:
            key = path_key(r["p"], r["os"])
            hit = conn.execute(f"SELECT id FROM {table} WHERE machine_id = ? AND path_key = ? AND is_retired = 0",
                               (r["machine_id"], key)).fetchone()
            if hit:
                _merge(conn, table, hit[0], r["id"])
                merged += 1
            conn.execute(f"UPDATE {table} SET path_key = ? WHERE id = ?", (key, r["id"]))
    conn.execute("COMMIT")
    return merged
