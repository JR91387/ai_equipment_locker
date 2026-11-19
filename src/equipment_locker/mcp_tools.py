# SPDX-License-Identifier: MIT
"""The tools Equipment Locker offers over MCP. Each serves what is already in the catalog; none reads tool files."""
from . import annotations as ann
from . import api, search

TARGET = {"type": "string", "enum": ["location", "item", "tool"],
          "description": "What the id refers to: a location (folder/file), an item (skill, agent...) or a tool"}
TARGET_ID = {"type": ["string", "integer"], "description": "Numeric id for location/item; tool code (e.g. 'codex') for tool"}


def _obj(props, required=()):
    return {"type": "object", "properties": props, "required": list(required), "additionalProperties": False}


def t_search(conn, a):
    rows = search.query(conn, a["query"], {"tool": a.get("tool"), "kind": a.get("kind")})
    return rows[: int(a.get("limit") or 25)]


def t_list_tools(conn, a):
    s = api.summary(conn)
    tools = [{k: t[k] for k in ("tool", "display", "present", "bytes", "items", "is_favorite", "label")} for t in s["tools"]]
    return {"tools": tools, "last_scan": s["last_scan"]}


def t_tool_detail(conn, a):
    d = api.tool_detail(conn, a["tool"])
    groups = [{"kind": g["kind"], "items": [{k: i[k] for k in ("id", "name", "description", "path")} for i in g["items"]]}
              for g in d["groups"]]
    locs = [{k: loc[k] for k in ("id", "category", "path", "size_bytes", "presence", "origin")} for loc in d["locations"]]
    return {"tool": a["tool"], "groups": groups, "locations": locs}


def t_item_detail(conn, a):
    found = api.detail(conn, a["kind"], a["id"])
    if found is None:
        raise LookupError(f"no {a['kind']} with id {a['id']}")
    return found


def t_recent_changes(conn, a):
    limit = min(int(a.get("limit") or 20), 200)
    return [dict(r) for r in conn.execute(
        """SELECT * FROM (
             SELECT lc.at, c.code AS change, 'location' AS kind, l.id, l.path AS name FROM location_change lc
             JOIN ref_change c ON c.id = lc.change_id JOIN location l ON l.id = lc.location_id
             UNION ALL
             SELECT ic.at, c.code, 'item', i.id, ic.name FROM item_change ic
             JOIN ref_change c ON c.id = ic.change_id JOIN item i ON i.id = ic.item_id)
           ORDER BY at DESC LIMIT ?""", (limit,))]


def _edit(conn, fn):
    result = fn()
    search.rebuild(conn)
    return result


def t_add_tag(conn, a):
    return {"tag_id": _edit(conn, lambda: ann.tag(conn, {"kind": a["target_kind"], "id": a["target_id"]}, a["tag"]))}


def t_remove_tag(conn, a):
    target = {"kind": a["target_kind"], "id": a["target_id"]}
    return {"tag_id": _edit(conn, lambda: ann.tag(conn, target, a["tag"], on=False))}


def t_set_note(conn, a):
    target = {"kind": a["target_kind"], "id": a["target_id"]}
    row = _edit(conn, lambda: ann.set_annotation(conn, target, {"note": a["note"]}))
    return {"note": row["note"], "updated": row["updated"]}


TAG_ARGS = _obj({"target_kind": TARGET, "target_id": TARGET_ID, "tag": {"type": "string"}},
                ("target_kind", "target_id", "tag"))
TOOLS = [
    ("search", ("Find tools, skills, agents, MCP servers, plugins and folders. Ignores case, dashes, dots and "
                "underscores; matches partial words, notes and tags."),
     _obj({"query": {"type": "string"}, "tool": {"type": "string", "description": "Tool code filter, e.g. 'cursor'"},
           "kind": {"type": "string", "enum": ["tool", "location", "item", "project"]},
           "limit": {"type": "integer", "minimum": 1, "maximum": 200}}, ("query",)), t_search, False),
    ("list_tools", ("The shelves: every AI tool found on this computer, with counts of its skills, agents, MCP "
                    "servers and plugins, and when the catalog was last scanned."), _obj({}), t_list_tools, False),
    ("tool_detail", "One tool's items (name, description, path) grouped by kind, and its folders and files.",
     _obj({"tool": {"type": "string", "description": "Tool code from list_tools, e.g. 'claude-code'"}}, ("tool",)),
     t_tool_detail, False),
    ("item_detail", "Everything known about one location, item or tool, including the person's note and tags.",
     _obj({"kind": TARGET, "id": TARGET_ID}, ("kind", "id")), t_item_detail, False),
    ("recent_changes", "What appeared, changed or disappeared most recently, newest first.",
     _obj({"limit": {"type": "integer", "minimum": 1, "maximum": 200}}), t_recent_changes, False),
    ("add_tag", "Add a tag to a location, item or tool (tags ignore case).", TAG_ARGS, t_add_tag, True),
    ("remove_tag", "Remove a tag from a location, item or tool (kept in history).", TAG_ARGS, t_remove_tag, True),
    ("set_note", "Set the note on a location, item or tool. Earlier notes are kept as versions.",
     _obj({"target_kind": TARGET, "target_id": TARGET_ID, "note": {"type": "string"}},
          ("target_kind", "target_id", "note")), t_set_note, True),
]
