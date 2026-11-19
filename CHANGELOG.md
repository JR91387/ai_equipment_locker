# Changelog

## 1.0.0 (2026-11-19)
First public release.

- **Catalog**: built-in list of 366 default locations for 28 AI tools (Claude Code, Claude Desktop, Codex,
  ChatGPT, Antigravity, Gemini CLI, Cursor, Copilot, Windsurf, local model runners and more) on macOS,
  Windows and Linux, each with its source.
- **Scanner**: every user on the computer, project folders (third-party code tagged, not skipped), a one-level
  name sweep, disk limits with resume, read-only (names, paths, sizes; never file contents).
- **Items**: skills, agents, commands, MCP servers, plugins and models, with their standard descriptions.
- **Catalogue database**: one SQLite file with full change history; nothing is ever deleted.
- **Cabinet page** (`serve`): tool shelves, tool view, table, search that ignores case and punctuation,
  notes with history, tags, favourites, pictures, pinned folders; scans on start, every 6 hours and on Refresh.
- **MCP server** (`mcp`): search and browse the catalogue from Claude or any MCP client; optional tags and notes.
- **Look**: storage-themed art, ten palette gradients for tools without a picture, bundled fonts.
