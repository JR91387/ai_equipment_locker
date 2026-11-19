# SPDX-License-Identifier: MIT
"""Items inside catalogued locations, collected after each scan for locations that changed or have none yet."""
import os
from pathlib import Path

from . import itemread
from .db import now

MCP_FILES = {".mcp.json", "mcp.json", "mcp_config.json", ".claude.json", "settings.json", "settings.local.json",
             "claude_desktop_config.json", "cline_mcp_settings.json", "mcp_settings.json", "config.toml"}
MAX_ITEMS = 500
DIR_KINDS = {"skills": "skill", "agents": "agent", "commands": "command", "instructions": "rule",
             "plugins": "plugin", "models": "model"}


def _entries(path, budget):
    try:
        entries = list(os.scandir(path))
    except OSError:
        return []
    budget.spend(len(entries))
    return sorted(entries, key=lambda e: e.name)[:MAX_ITEMS]


def _is_dir(e):
    try:
        return e.is_dir(follow_symlinks=False)
    except OSError:
        return False


def skills(path, budget):
    for e in _entries(path, budget):
        if _is_dir(e) and os.path.isfile(os.path.join(e.path, "SKILL.md")):
            fm = itemread.frontmatter(os.path.join(e.path, "SKILL.md"))
            yield "skill", fm.get("name") or e.name, fm.get("description"), f"{e.name}/SKILL.md"


def documents(path, kind, budget):
    """Markdown, TOML and JS definitions in a folder (agents, commands, rules, workflows, output styles)."""
    for e in _entries(path, budget):
        stem, ext = os.path.splitext(e.name)
        if _is_dir(e) or ext not in (".md", ".mdc", ".toml", ".js"):
            continue
        if ext in (".md", ".mdc"):
            fm = itemread.frontmatter(e.path)
            yield kind, fm.get("name") or stem, fm.get("description"), e.name
        elif ext == ".toml":
            yield kind, stem, itemread.toml_description(e.path).get("description"), e.name
        else:
            yield "workflow", stem, None, e.name


MANIFESTS = ("plugin.json", ".claude-plugin/plugin.json", "gemini-extension.json", "package.json")


def plugins(path, budget, depth=3):
    """Folders holding a plugin/extension manifest, up to `depth` levels down (marketplaces/cache layouts)."""
    seen = set()
    stack = [(Path(path), 0)]
    while stack and len(seen) < MAX_ITEMS:
        folder, level = stack.pop()
        for e in _entries(folder, budget):
            if not _is_dir(e):
                continue
            hit = next((m for m in MANIFESTS if os.path.isfile(os.path.join(e.path, m))), None)
            if hit:
                info = itemread.manifest(os.path.join(e.path, hit))
                name = info.get("name") or e.name
                rel = os.path.relpath(e.path, path)
                if (name, rel) not in seen:
                    seen.add((name, rel))
                    yield "extension" if hit == "gemini-extension.json" else "plugin", name, info.get("description"), rel
            elif level + 1 < depth:
                stack.append((Path(e.path), level + 1))


def models(path, budget):
    """Model folders by name only (Hugging Face models--org--name, Ollama library/<model>, LM Studio)."""
    library = os.path.join(path, "manifests", "registry.ollama.ai", "library")
    if os.path.isdir(library):
        path = library
    for e in _entries(path, budget):
        if _is_dir(e) and not e.name.startswith("."):
            name = e.name.removeprefix("models--").replace("--", "/")
            yield "model", name, None, e.name


def collect(path, category, kind, budget):
    """Items for one location. Yields (kind, name, description, rel_path)."""
    name = os.path.basename(str(path))
    if kind == "file":
        return [("mcp_server", *s) for s in itemread.mcp_servers(path)] if name in MCP_FILES else []
    if category == "skills":
        return list(skills(path, budget))
    if category == "plugins":
        return list(plugins(path, budget))
    if category == "models":
        return list(models(path, budget))
    if category in DIR_KINDS:
        return list(documents(path, DIR_KINDS[category], budget))
    return []


def _upsert(conn, ctx, loc_id, found):
    seen = set()
    for kind, name, desc, rel in found[:MAX_ITEMS]:
        if rel in seen:
            continue
        seen.add(rel)
        old = conn.execute("SELECT id, name, description FROM item WHERE location_id = ? AND rel_path = ?",
                           (loc_id, rel)).fetchone()
        args = (conn.ref_id("ref_item_kind", kind, kind), name, desc, conn.ref_id("ref_presence", "present"))
        if old is None:
            cur = conn.execute("""INSERT INTO item (location_id, kind_id, name, description, rel_path, presence_id,
                                    first_seen_run, last_seen_run, updated) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                               (loc_id, *args[:3], rel, args[3], ctx["run_id"], ctx["run_id"], now()))
            _change(conn, ctx, cur.lastrowid, ("appeared", name, desc))
            continue
        conn.execute("""UPDATE item SET kind_id = ?, name = ?, description = ?, presence_id = ?, last_seen_run = ?,
                          updated = ? WHERE id = ?""", (*args, ctx["run_id"], now(), old["id"]))
        if (old["name"], old["description"]) != (name, desc):
            _change(conn, ctx, old["id"], ("changed", name, desc))
    return seen


def _change(conn, ctx, item_id, what):
    """what: (change code, name, description)."""
    code, name, desc = what
    conn.execute("INSERT INTO item_change (item_id, run_id, change_id, name, description, at) VALUES (?, ?, ?, ?, ?, ?)",
                 (item_id, ctx["run_id"], conn.ref_id("ref_change", code), name, desc, now()))


def _mark_gone(conn, ctx, loc_id, seen):
    absent = conn.ref_id("ref_presence", "absent")
    rows = conn.execute("SELECT id, name, description, rel_path FROM item WHERE location_id = ? AND presence_id != ?",
                        (loc_id, absent)).fetchall()
    for r in rows:
        if r["rel_path"] not in seen:
            conn.execute("UPDATE item SET presence_id = ?, updated = ? WHERE id = ?", (absent, now(), r["id"]))
            _change(conn, ctx, r["id"], ("disappeared", r["name"], r["description"]))


def collect_run(conn, ctx, budget):
    """Collect items for this run's present locations that changed this run or have no items yet."""
    rows = conn.execute("""SELECT l.id, l.path, l.kind, c.code AS category FROM location l
                           JOIN ref_category c ON c.id = l.category_id JOIN ref_presence p ON p.id = l.presence_id
                           WHERE l.machine_id = ? AND l.last_seen_run = ? AND p.code = 'present' AND l.is_retired = 0
                             AND (EXISTS (SELECT 1 FROM location_change lc WHERE lc.location_id = l.id AND lc.run_id = ?)
                                  OR NOT EXISTS (SELECT 1 FROM item i WHERE i.location_id = l.id))""",
                        (ctx["machine_id"], ctx["run_id"], ctx["run_id"])).fetchall()
    total = 0
    for r in rows:
        found = collect(r["path"], r["category"], r["kind"], budget)
        if found or r["category"] in DIR_KINDS:
            _mark_gone(conn, ctx, r["id"], _upsert(conn, ctx, r["id"], list(found)))
            total += len(found)
    return total
