# SPDX-License-Identifier: MIT
"""One scan run: built-in places for every user and the system, then project folders and the name sweep."""
import os
import platform as _platform
import sys
from pathlib import Path

from . import annotations, items, projects, record, search
from . import places as pl
from .probe import Budget, expand_glob, probe
from .users import current_home, home_patterns, list_homes


def default_options(doc):
    limits = doc["limits"]
    return {"platform": sys.platform, "machine": _platform.node() or "this-machine", "env": dict(os.environ),
            "current_home": current_home(), "users": "all", "projects": True, "sweep": True,
            "limits": dict(limits)}


def _homes(doc, opts):
    if opts["users"] == "me":
        home = opts["current_home"]
        return [(home.name, home, os.access(home, os.R_OK))] if home else []
    patterns = opts.get("home_patterns") or home_patterns(opts["platform"], doc["users"])
    return list_homes(patterns, opts["current_home"])


def _place_ids(conn):
    return {r["code"]: r["id"] for r in conn.execute("SELECT id, code FROM place WHERE is_retired = 0")}


def _probe_place(conn, ctx, place, target):
    """Probe one resolved place (expanding globs) and record what exists. Returns the paths recorded."""
    seen, matches = [], expand_glob(target)
    if matches is None:  # unreadable: this user's (or the system's) coverage is incomplete this run
        ctx["incomplete"].add(ctx.get("user_id"))
        return seen
    for path in matches:
        old = record.prior(conn, ctx, path)
        res = probe(path, place["kind"], place["category"], {**ctx["probe"], "prior": old})
        meta = {**place, "place_id": ctx["place_ids"].get(place["code"]), "os_user_id": ctx.get("user_id"),
                "path": path, "kind": "dir" if place["kind"] == "glob" and res.get("entry_count") is not None else place["kind"]}
        if record.record_location(conn, ctx, meta, res) or old is not None or res["presence"] != "absent":
            seen.append(str(path))
    return seen


def scan_places(conn, ctx, scope, roots):
    """Every built-in place of one scope ('user' or 'system') for one user's token roots."""
    seen = []
    for place in ctx["doc"]["places"]:
        if place["scope"] != scope or not pl.applies(place, ctx["platform"]):
            continue
        env_value = ctx["env"].get(place["env"]) if place.get("env") and ctx.get("is_current") else None
        target = pl.resolve(place["path"], place["kind"], roots, env_value)
        if target is not None:
            seen.extend(_probe_place(conn, ctx, place, target))
    return seen


def _scan_user(conn, ctx, name_home_readable, covered):
    _, home, readable = name_home_readable
    user_id = record.upsert_user(conn, ctx["machine_id"], home, readable)
    if not readable:
        return
    is_current = ctx["current_home"] is not None and str(home) == str(ctx["current_home"])
    roots = pl.token_roots(home, ctx["platform"], ctx["env"] if is_current else None)
    uctx = {**ctx, "user_id": user_id, "is_current": is_current}
    seen = set(scan_places(conn, uctx, "user", roots))
    if user_id not in ctx["incomplete"]:
        covered["users"].add(user_id)
    if ctx["opts"]["projects"] and projects.scan_projects(conn, uctx, home, (roots, seen)):
        covered["projects"].add(user_id)
    if ctx["opts"]["sweep"] and projects.scan_sweep(conn, uctx, roots, seen) and user_id in covered["users"]:
        covered["sweep_users"].add(user_id)


def _scan_pins(conn, ctx):
    """Folders the person pinned: scanned once per run, and searched for projects like a home folder."""
    complete = True
    for place in annotations.pinned(conn):
        seen = _probe_place(conn, ctx, place, Path(place["path"]))
        if place["kind"] == "dir" and ctx["opts"]["projects"]:
            complete &= projects.scan_projects(conn, ctx, Path(place["path"]), ({}, set(seen)))
    return complete


def run(conn, doc, opts):
    """Scan this machine into conn. Returns a summary dict."""
    pl.sync(conn, doc)
    machine_id = record.upsert_machine(conn, opts["machine"], opts["platform"])
    limits = opts["limits"]
    conn.execute("BEGIN")
    run_id = record.start_run(conn, machine_id, {k: v for k, v in opts.items() if k not in ("env", "current_home")}
                              | {"current_home": None})
    size_budget, walk_budget = Budget(limits["max_entries"] // 2), Budget(limits["max_entries"] // 2)
    ctx = {"conn": conn, "doc": doc, "opts": opts, "machine_id": machine_id, "run_id": run_id,
           "platform": opts["platform"], "env": opts["env"], "current_home": opts["current_home"],
           "place_ids": _place_ids(conn), "walk_budget": walk_budget, "cache": projects.load_cache(conn, machine_id),
           "probe": {"limits": limits, "budget": size_budget}, "recorded": set(), "incomplete": set()}
    covered = {"users": set(), "projects": set(), "sweep_users": set(), "system": True}
    homes = _homes(doc, opts)
    for entry in homes:
        _scan_user(conn, ctx, entry, covered)
    system_roots = pl.token_roots(opts["current_home"] or "/", opts["platform"], opts["env"])
    sctx = {**ctx, "user_id": None, "is_current": True}
    scan_places(conn, sctx, "system", system_roots)
    if _scan_pins(conn, sctx):
        covered["projects"].add(None)
    covered["system"] = None not in ctx["incomplete"]
    gone = record.mark_missing(conn, ctx, covered)
    items.collect_run(conn, ctx, size_budget)
    projects.save_cache(conn, ctx)
    hit = walk_budget.spent or size_budget.spent
    used = size_budget.used + walk_budget.used
    record.finish_run(conn, run_id, "partial" if hit else "ok", (used, hit))
    conn.execute("COMMIT")
    search.rebuild(conn)
    return summary(conn, run_id, homes, gone)


def summary(conn, run_id, homes, gone):
    run = conn.execute("""SELECT r.*, s.code AS status FROM scan_run r JOIN ref_run_status s ON s.id = r.status_id
                          WHERE r.id = ?""", (run_id,)).fetchone()
    changes = dict(conn.execute("""SELECT c.code, COUNT(*) FROM location_change lc
                                   JOIN ref_change c ON c.id = lc.change_id WHERE lc.run_id = ? GROUP BY c.code""",
                                (run_id,)).fetchall())
    tools = [dict(r) for r in conn.execute("SELECT * FROM v_tool_summary WHERE present > 0")]
    item_count = conn.execute("SELECT COUNT(*) FROM item i JOIN ref_presence p ON p.id = i.presence_id "
                              "WHERE p.code = 'present' AND i.is_retired = 0").fetchone()[0]
    return {"run_id": run_id, "status": run["status"], "entries_seen": run["entries_seen"],
            "budget_hit": bool(run["budget_hit"]), "users": [h[0] for h in homes if h[2]],
            "unreadable_users": [h[0] for h in homes if not h[2]], "changes": changes, "marked_absent": gone,
            "items": item_count, "tools": tools}
