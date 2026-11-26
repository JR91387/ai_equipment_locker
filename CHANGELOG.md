# Changelog

## Unreleased
- Scans list up to 1,000,000 folder entries by default (was 50,000), so big machines finish in one run.
- A `partial` scan says which limit ran out and suggests `--max-entries`; sizes it skipped show as
  "not measured" instead of 0 bytes.
- `serve` takes `--max-entries` too, and `--allow-host NAME` to accept a proxy's or tunnel's host name. A refused
  request now explains why and how to fix it.
- `pipx install .` adds an `equipment-locker` command; the installed package now includes the page's fonts,
  icons and gradients.
- `--help`, the scan summary and `serve` show where the catalogue file is.
- The terminal summary uses the page's words: places and third-party.
- New wiki pages: Run on a schedule (systemd, launchd, Task Scheduler examples in `docs/examples/`) and
  View from another machine.

## 1.0.1 (2026-11-19)
- The shelves now say **Your tools** (was "Your AI gear").
- Known tools show their own icon in brand colours (Claude, Gemini, Cursor, GitHub Copilot, Windsurf, Cline,
  OpenCode, Qwen, Ollama, LM Studio, Hugging Face, npm, uv, pipx); other tools keep their palette gradient.
- Item cards and section headings show a kind icon (wrench for skills, robot for agents, plug for MCP servers,
  puzzle for plugins, and more) on a colour picked from the item's name.

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
