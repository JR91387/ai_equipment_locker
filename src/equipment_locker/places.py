# SPDX-License-Identifier: MIT
"""Built-in places: load places.json, sync it into the place table, resolve path templates per OS and user."""
import json
import os
import re
from pathlib import Path

from .db import now

PLACES_FILE = Path(__file__).resolve().parent / "places.json"
_TOKEN = re.compile(r"\{(\w+)\}")
GENERIC_ROOTS = {".local", ".config", ".cache"}  # env overrides never replace these shared folders


def load(path=PLACES_FILE):
    """The places document (envelope + places list)."""
    return json.loads(Path(path).read_text())


def _upsert_place(conn, p):
    ids = (conn.ref_id("ref_tool", p["tool"], p["tool"]), conn.ref_id("ref_scope", p["scope"]),
           conn.ref_id("ref_category", p["category"], p["category"]), conn.ref_id("ref_source", p["source"]))
    conn.execute(
        """INSERT INTO place (code, tool_id, scope_id, category_id, source_id, path_template, kind, env_var,
                              holds, ref_url, is_builtin, is_retired, updated)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 0, ?)
           ON CONFLICT(code) DO UPDATE SET tool_id = excluded.tool_id, scope_id = excluded.scope_id,
             category_id = excluded.category_id, source_id = excluded.source_id,
             path_template = excluded.path_template, kind = excluded.kind, env_var = excluded.env_var,
             holds = excluded.holds, ref_url = excluded.ref_url, is_retired = 0, updated = excluded.updated""",
        (p["code"], *ids, p["path"], p["kind"], p.get("env"), p.get("holds"), p.get("ref"), now()))
    place_id = conn.execute("SELECT id FROM place WHERE code = ?", (p["code"],)).fetchone()[0]
    conn.execute("DELETE FROM place_os WHERE place_id = ?", (place_id,))
    for os_code in p.get("os") or ():
        conn.execute("INSERT INTO place_os (place_id, os_id) VALUES (?, ?)",
                     (place_id, conn.ref_id("ref_os", os_code)))


def sync(conn, doc):
    """Upsert every built-in place; retire built-ins no longer in the file. Returns (active, retired) counts."""
    conn.execute("BEGIN")
    for code, display in doc.get("tool_names", {}).items():
        conn.execute("INSERT INTO ref_tool (code, display) VALUES (?, ?) ON CONFLICT(code) DO UPDATE SET "
                     "display = excluded.display", (code, display))
    conn._refs.clear()
    for p in doc["places"]:
        _upsert_place(conn, p)
    codes = [p["code"] for p in doc["places"]]
    marks = ",".join("?" * len(codes))
    cur = conn.execute(f"UPDATE place SET is_retired = 1, updated = ? WHERE is_builtin = 1 AND is_retired = 0 "
                       f"AND code NOT IN ({marks})", (now(), *codes))
    conn.execute("COMMIT")
    return len(codes), cur.rowcount


def token_roots(home, platform, env=None):
    """Token -> folder for one user on one OS. Tokens with no value on this OS are absent from the result.

    env is os.environ for the user running the scan (XDG overrides apply), None for other users.
    """
    env = env or {}
    h = Path(home)
    roots = {"home": h}
    if platform == "win32":
        roaming, local = h / "AppData" / "Roaming", h / "AppData" / "Local"
        roots.update(appconfig=roaming, appdata=local, appcache=local, roaming=roaming, local=local,
                     programdata=Path(os.environ.get("PROGRAMDATA", "C:/ProgramData")),
                     programfiles=Path(os.environ.get("ProgramFiles", "C:/Program Files")))
    elif platform == "darwin":
        support = h / "Library" / "Application Support"
        roots.update(appconfig=support, appdata=support, appsupport=support, appcache=h / "Library" / "Caches",
                     applogs=h / "Library" / "Logs")
    else:
        roots.update(appconfig=Path(env.get("XDG_CONFIG_HOME") or h / ".config"),
                     appdata=Path(env.get("XDG_DATA_HOME") or h / ".local" / "share"),
                     appcache=Path(env.get("XDG_CACHE_HOME") or h / ".cache"),
                     appstate=Path(env.get("XDG_STATE_HOME") or h / ".local" / "state"))
    return roots


def _env_override(template, kind, value):
    """Replace a tool's own root folder ({home}/.tool) with an env var's value; None if not applicable."""
    parts = template.split("/", 2)
    if parts[0] != "{home}" or len(parts) < 2 or not parts[1].startswith(".") or parts[1] in GENERIC_ROOTS:
        return None
    if len(parts) == 2:
        return Path(value) / parts[1] if kind == "file" else Path(value)
    return Path(value) / parts[2]


def resolve(template, kind, roots, env_value=None):
    """Concrete path for a template, or None if a token has no value here (entry skipped)."""
    if env_value:
        hit = _env_override(template, kind, env_value)
        if hit is not None:
            return hit
    missing = [t for t in _TOKEN.findall(template) if t not in roots]
    if missing:
        return None
    return Path(_TOKEN.sub(lambda m: str(roots[m.group(1)]), template))


def applies(place, platform):
    """True if a place (dict from places.json) applies on this OS."""
    return not place.get("os") or platform in place["os"]
