# SPDX-License-Identifier: MIT
"""Read only what a catalogue needs from a file: frontmatter name/description, manifest name/description,
MCP server names. Reads are capped; nothing else is kept."""
import json
import os
import tomllib

FRONTMATTER_BYTES = 8 * 1024
MANIFEST_BYTES = 64 * 1024
CONFIG_BYTES = 1024 * 1024
DESC_MAX = 500
MCP_KEYS = ("mcpServers", "servers", "mcp_servers", "amp.mcpServers")


def _head(path, limit):
    """First `limit` bytes of a file, or None if unreadable or not a regular file (links are not followed)."""
    try:
        if not os.path.isfile(path) or os.path.islink(path):
            return None
        with open(path, "rb") as f:
            return f.read(limit)
    except OSError:
        return None


def _clip(text):
    text = " ".join(str(text).split())
    return text[:DESC_MAX] or None


def _unquote(value):
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
        return value[1:-1]
    return value


def _yaml_fields(lines, wanted):
    """Top-level `key: value` pairs (incl. > / | blocks) for the wanted keys. Not a YAML parser; enough here."""
    out, key, block = {}, None, []
    for line in lines + ["__end__:"]:
        if key and (line.startswith((" ", "\t")) or not line.strip()):
            block.append(line.strip())
            continue
        if key:
            out[key] = " ".join(b for b in block if b)
            key, block = None, []
        name, sep, value = line.partition(":")
        if sep and name in wanted:
            if value.strip() in (">", "|", ">-", "|-", ""):
                key = name
            else:
                out[name] = _unquote(value)
    return out


def frontmatter(path):
    """{'name', 'description'} from a Markdown file's frontmatter (first 8 KB only); {} if none."""
    raw = _head(path, FRONTMATTER_BYTES)
    if not raw:
        return {}
    lines = raw.decode("utf-8", "replace").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
    if end is None:
        return {}
    fields = _yaml_fields(lines[1:end], ("name", "description"))
    return {k: _clip(v) for k, v in fields.items() if v}


def manifest(path):
    """{'name', 'description'} from a JSON manifest (plugin.json, gemini-extension.json, package.json)."""
    raw = _head(path, MANIFEST_BYTES)
    try:
        data = json.loads(raw) if raw else {}
    except ValueError:
        return {}
    if not isinstance(data, dict):
        return {}
    return {k: _clip(data[k]) for k in ("name", "description") if isinstance(data.get(k), str)}


def toml_description(path):
    """{'description'} from a TOML file that defines one (Gemini commands, Codex agents)."""
    raw = _head(path, MANIFEST_BYTES)
    try:
        data = tomllib.loads(raw.decode("utf-8", "replace")) if raw else {}
    except tomllib.TOMLDecodeError:
        return {}
    desc = data.get("description")
    return {"description": _clip(desc)} if isinstance(desc, str) else {}


def _servers(block, prefix):
    out = []
    for name, entry in (block or {}).items():
        desc = entry.get("description") if isinstance(entry, dict) else None
        out.append((name, _clip(desc) if isinstance(desc, str) else None, f"{prefix}{name}"))
    return out


def mcp_servers(path):
    """[(name, description or None, rel_path)] of MCP servers in a config file. Names only, never values."""
    raw = _head(path, CONFIG_BYTES)
    if not raw:
        return []
    try:
        data = tomllib.loads(raw.decode("utf-8", "replace")) if str(path).endswith(".toml") else json.loads(raw)
    except (ValueError, tomllib.TOMLDecodeError):
        return []
    if not isinstance(data, dict):
        return []
    found = []
    for key in MCP_KEYS:
        if isinstance(data.get(key), dict):
            found += _servers(data[key], f"{key}/")
    for proj, cfg in (data.get("projects") or {}).items() if isinstance(data.get("projects"), dict) else ():
        if isinstance(cfg, dict) and isinstance(cfg.get("mcpServers"), dict):
            found += _servers(cfg["mcpServers"], f"projects/{proj}/mcpServers/")
    return found
