# SPDX-License-Identifier: MIT
"""Project folders and the name sweep for one user, plus the walk_state folder cache."""
import json

from . import record
from .paths import path_key
from .places import resolve
from .probe import expand_glob, probe
from .walk import find_projects, is_vendored, sweep

SWEEP_TOOL = {"anthropic": "claude", "chatgpt": "chatgpt-desktop", "gemini": "gemini-cli", "codeium": "windsurf",
              "devin": "windsurf", "qwen": "qwen-code", "roo": "roo-code"}
APP_ROOTS = ("appconfig", "appdata", "appcache", "appstate", "applogs", "roaming", "local")


def load_cache(conn, machine_id):
    rows = conn.execute("SELECT dir_path, dir_mtime, children, markers FROM walk_state WHERE machine_id = ?",
                        (machine_id,))
    return {r["dir_path"]: {"mtime": r["dir_mtime"], "children": json.loads(r["children"]),
                            "names": json.loads(r["markers"]), "used": False} for r in rows}


def save_cache(conn, ctx):
    for path, c in ctx["cache"].items():
        if c.get("fresh"):
            conn.execute("""INSERT INTO walk_state (machine_id, dir_path, dir_mtime, children, markers, last_run_id)
                            VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(machine_id, dir_path) DO UPDATE SET
                            dir_mtime = excluded.dir_mtime, children = excluded.children,
                            markers = excluded.markers, last_run_id = excluded.last_run_id""",
                         (ctx["machine_id"], path, c["mtime"], json.dumps(c["children"]), json.dumps(c["names"]),
                          ctx["run_id"]))


def _project_places(doc):
    """Project-scope places keyed by their first path segment after {project}/."""
    by_first = {}
    for p in doc["places"]:
        if p["scope"] == "project" and p["path"].startswith("{project}/"):
            first = p["path"].split("/", 2)[1]
            by_first.setdefault(first, []).append(p)
    return by_first


def _record_project(conn, ctx, folder, by_first):
    origin = "vendored" if is_vendored(folder, ctx["doc"]["project_search"]["vendored_dirs"]) else "own"
    project_id = record.upsert_project(conn, ctx, folder, origin)
    names = set(ctx["cache"].get(str(folder), {}).get("names", ()))
    for first in names & set(by_first):
        for place in by_first[first]:
            for path in expand_glob(resolve(place["path"], place["kind"], {"project": folder})):
                old = record.prior(conn, ctx, path)
                res = probe(path, place["kind"], place["category"], {**ctx["probe"], "prior": old})
                meta = {**place, "path": path, "place_id": ctx["place_ids"].get(place["code"]),
                        "project_id": project_id, "os_user_id": ctx["user_id"], "origin": origin}
                record.record_location(conn, ctx, meta, res)


def scan_projects(conn, ctx, home, roots_seen):
    """Find and record project folders under one home. True if the walk finished within the budget."""
    roots, seen = roots_seen
    search = ctx["doc"]["project_search"]
    opts = {"markers": search["markers"], "depth": ctx["opts"]["limits"]["depth"],
            "skip_roots": [roots[k] for k in APP_ROOTS if k in roots and roots[k] != home]}
    hits, complete = find_projects(home, opts, ctx["cache"], ctx["walk_budget"])
    by_first = _project_places(ctx["doc"])
    folders = {folder for folder, m in hits if str(folder / m) not in seen}
    for folder in sorted(folders):
        _record_project(conn, ctx, folder, by_first)
    return complete


def _covered(path, seen):
    """True if a sweep hit is already a known place, or contains one."""
    key = path_key(path)
    keys = [path_key(s) for s in seen]
    return key in keys or any(k.startswith(key + "/") for k in keys)


def scan_sweep(conn, ctx, roots, seen):
    """Record folders one level under the app-data roots whose names match a tool, unless already known.

    Returns True if every sweep root could be listed.
    """
    sweep_roots = [roots[t.strip("{}")] for t in ctx["doc"]["sweep"]["roots"] if t.strip("{}") in roots]
    hits, complete = sweep(sweep_roots, ctx["doc"]["sweep"]["names"], ctx["walk_budget"])
    for path, word in hits:
        if _covered(path, seen):
            continue
        kind = "dir" if path.is_dir() and not path.is_symlink() else "file"
        res = probe(path, kind, "discovered", {**ctx["probe"], "prior": record.prior(conn, ctx, path)})
        meta = {"tool": SWEEP_TOOL.get(word, word), "scope": "user", "category": "discovered", "source": "discovered",
                "kind": kind, "os_user_id": ctx["user_id"], "path": path}
        record.record_location(conn, ctx, meta, res)
    return complete
