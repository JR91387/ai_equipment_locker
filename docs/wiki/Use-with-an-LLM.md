# Use with an LLM (MCP)

Equipment Locker ships a small [MCP](https://modelcontextprotocol.io) server. Any MCP client (Claude Code, Claude
Desktop, a local model runner) can ask it what AI gear you have. It answers from the catalogue only; it never opens
your tool files.

## Start it
```bash
PYTHONPATH=/path/to/equipment-locker/src python3 -m equipment_locker mcp            # read + tags/notes
PYTHONPATH=/path/to/equipment-locker/src python3 -m equipment_locker mcp --read-only
```
It talks over standard input/output, so a client starts it for you. Use `--db` to point at a different catalogue.

## Connect a client
**Claude Code**
```bash
claude mcp add equipment-locker -e PYTHONPATH=/path/to/equipment-locker/src -- python3 -m equipment_locker mcp
```

**Claude Desktop** (`claude_desktop_config.json`) and most other clients:
```json
{ "mcpServers": { "equipment-locker": {
    "command": "python3", "args": ["-m", "equipment_locker", "mcp"],
    "env": { "PYTHONPATH": "/path/to/equipment-locker/src" } } } }
```

## Tools
| Tool | Arguments | Returns |
|---|---|---|
| `search` | `query`, optional `tool`, `kind`, `limit` | matching tools, items, folders |
| `list_tools` | none | every tool with counts and the last scan |
| `tool_detail` | `tool` (e.g. `claude-code`) | items by kind, folders and files |
| `item_detail` | `kind` (`location`, `item`, `tool`), `id` | full record with note and tags |
| `recent_changes` | optional `limit` | newest appearances, changes, disappearances |
| `add_tag` / `remove_tag` | `target_kind`, `target_id`, `tag` | the tag id |
| `set_note` | `target_kind`, `target_id`, `note` | the saved note |

## Good to know
- The catalogue is filled by `scan` or `serve`; the MCP server does not scan.
- Notes keep every earlier version, and removed tags stay in history, so nothing an LLM does is lost.
- Try asking: *"Which MCP servers are configured on this machine?"*, *"Do I have a skill for release notes?"*,
  *"What changed in my Claude setup this week?"*
