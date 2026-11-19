# SPDX-License-Identifier: MIT
"""Catalog writes: machines, users, runs, projects, locations and their change history. Nothing is deleted."""
import json

from .db import now
from .paths import path_key

FOUND = ("present", "link", "wrong_type", "unreadable")


def upsert_machine(conn, name, os_code):
    t = now()
    conn.execute("""INSERT INTO machine (name, os_id, first_seen, last_seen) VALUES (?, ?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET last_seen = excluded.last_seen, os_id = excluded.os_id""",
                 (name, conn.ref_id("ref_os", os_code), t, t))
    return conn.execute("SELECT id FROM machine WHERE name = ?", (name,)).fetchone()[0]


def upsert_user(conn, machine_id, home, readable):
    t, presence = now(), conn.ref_id("ref_presence", "present" if readable else "unreadable")
    conn.execute("""INSERT INTO os_user (machine_id, name, home, presence_id, first_seen, last_seen)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(machine_id, name) DO UPDATE SET home = excluded.home,
                      presence_id = excluded.presence_id, last_seen = excluded.last_seen, is_retired = 0""",
                 (machine_id, home.name, str(home), presence, t, t))
    return conn.execute("SELECT id FROM os_user WHERE machine_id = ? AND name = ?",
                        (machine_id, home.name)).fetchone()[0]


def start_run(conn, machine_id, options):
    cur = conn.execute("INSERT INTO scan_run (machine_id, started, status_id, options_json) VALUES (?, ?, ?, ?)",
                       (machine_id, now(), conn.ref_id("ref_run_status", "running"), json.dumps(options)))
    return cur.lastrowid


def finish_run(conn, run_id, status, usage):
    """usage: (entries listed, budget_hit)."""
    used, budget_hit = usage
    conn.execute("UPDATE scan_run SET finished = ?, status_id = ?, entries_seen = ?, budget_hit = ? WHERE id = ?",
                 (now(), conn.ref_id("ref_run_status", status), used, int(budget_hit), run_id))


def upsert_project(conn, ctx, root, origin):
    run, user_id, key = ctx["run_id"], ctx["user_id"], path_key(root, ctx["platform"])
    hit = conn.execute("SELECT id FROM project WHERE machine_id = ? AND path_key = ? AND is_retired = 0",
                       (ctx["machine_id"], key)).fetchone()
    if hit:
        conn.execute("UPDATE project SET last_seen_run = ?, root = ? WHERE id = ?", (run, str(root), hit[0]))
        return hit[0]
    cur = conn.execute("""INSERT INTO project (machine_id, os_user_id, root, path_key, origin_id, first_seen_run,
                            last_seen_run) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                       (ctx["machine_id"], user_id, str(root), key, conn.ref_id("ref_origin", origin), run, run))
    return cur.lastrowid


def prior(conn, ctx, path):
    """Last recorded live row for a path (matched by path_key), or None."""
    return conn.execute("""SELECT l.id, p.code AS presence, l.size_bytes, l.size_over, l.mtime
                           FROM location l JOIN ref_presence p ON p.id = l.presence_id
                           WHERE l.machine_id = ? AND l.path_key = ? AND l.is_retired = 0""",
                        (ctx["machine_id"], path_key(path, ctx["platform"]))).fetchone()


def _change(old, res):
    if old is None:
        return "appeared"
    if old["presence"] == "absent" and res["presence"] != "absent":
        return "reappeared"
    if res["presence"] == "absent":
        return "disappeared" if old["presence"] != "absent" else None
    if (old["presence"], old["size_bytes"], old["mtime"]) != (res["presence"], res["size_bytes"], res["mtime"]):
        return "changed"
    return None


def _ids(conn, meta):
    r = conn.ref_id
    return (meta.get("place_id"), meta.get("project_id"), meta.get("os_user_id"),
            r("ref_tool", meta["tool"], meta["tool"]), r("ref_scope", meta["scope"]),
            r("ref_category", meta["category"], meta["category"]), r("ref_origin", meta.get("origin", "own")),
            r("ref_source", meta["source"]))


def record_location(conn, ctx, meta, res):
    """Insert or update one location (meta["path"]); write a change row when something changed.

    Returns the change code or None.
    """
    path = meta["path"]
    recorded, key = ctx.setdefault("recorded", set()), path_key(path, ctx["platform"])
    if key in recorded:
        return None  # already recorded this run (a path listed under two tools keeps the first)
    old = prior(conn, ctx, path)
    if old is None and res["presence"] == "absent":
        return None
    recorded.add(key)
    change, run, t = _change(old, res), ctx["run_id"], now()
    vals = (conn.ref_id("ref_presence", res["presence"]), meta["kind"], res["size_bytes"], res["size_over"],
            res["entry_count"], res["mtime"])
    if old is None:
        cur = conn.execute(
            """INSERT INTO location (machine_id, path, path_key, place_id, project_id, os_user_id, tool_id, scope_id,
                 category_id, origin_id, source_id, presence_id, kind, size_bytes, size_over, entry_count, mtime,
                 first_seen_run, last_seen_run, updated)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (ctx["machine_id"], str(path), key, *_ids(conn, meta), *vals, run, run, t))
        loc_id = cur.lastrowid
    else:
        loc_id = old["id"]
        conn.execute("""UPDATE location SET presence_id = ?, kind = COALESCE(?, kind), size_bytes = ?, size_over = ?,
                          entry_count = ?, mtime = ?, last_seen_run = ?, updated = ?, path = ? WHERE id = ?""",
                     (*vals, run, t, str(path), loc_id))
    if change:
        conn.execute("""INSERT INTO location_change (location_id, run_id, change_id, presence_id, size_bytes,
                          mtime, at) VALUES (?, ?, ?, ?, ?, ?, ?)""",
                     (loc_id, run, conn.ref_id("ref_change", change), vals[0], res["size_bytes"], res["mtime"], t))
    return change


def mark_missing(conn, ctx, covered):
    """Locations not seen this run, inside areas this run fully covered, become absent. Returns how many.

    covered: {"users": user ids fully scanned, "projects": user ids whose project walk completed,
              "sweep_users": user ids whose name sweep completed, "system": bool}
    """
    rows = conn.execute("""SELECT l.id, l.path, l.os_user_id, l.place_id, l.project_id, s.code AS source
                           FROM location l JOIN ref_source s ON s.id = l.source_id
                           JOIN ref_presence p ON p.id = l.presence_id
                           WHERE l.machine_id = ? AND l.last_seen_run < ? AND p.code != 'absent'
                             AND l.is_retired = 0""", (ctx["machine_id"], ctx["run_id"])).fetchall()
    gone = [r for r in rows if _is_covered(r, covered)]
    absent = {"presence": "absent", "size_bytes": None, "size_over": 0, "entry_count": None, "mtime": None}
    for r in gone:
        record_location(conn, ctx, {"path": r["path"], "kind": None}, absent)
    return len(gone)


def _is_covered(row, covered):
    if row["project_id"] is not None:
        return row["os_user_id"] in covered["projects"]
    if row["source"] == "discovered":
        return row["os_user_id"] in covered["sweep_users"]
    if row["os_user_id"] is None:
        return covered["system"]
    return row["os_user_id"] in covered["users"]
