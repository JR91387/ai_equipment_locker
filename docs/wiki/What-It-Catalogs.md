# What it catalogs

**Tools:** Claude Code, Claude Desktop, Codex, ChatGPT Desktop, Antigravity, Gemini CLI, Cursor, GitHub Copilot,
Windsurf, VS Code AI extensions (Cline, Roo Code), Continue, Aider, opencode, Goose, Kiro, Qwen Code, Amp, Ollama,
LM Studio, Hugging Face, Jan, GPT4All, and the npx/uv/pipx caches MCP servers run from.

**Where it looks:** a built-in list of each tool's default folders on macOS, Windows and Linux, for every user on
the computer; project folders that contain tool files (`CLAUDE.md`, `.claude`, `AGENTS.md`, `.cursor`, ...);
one level of app-data folders for anything with a tool's name; and folders you pin. The full list, with the source
for every path, is in [PLACES.md](../PLACES.md).

**What it records:**

| Thing | Recorded |
|---|---|
| Folders and files | path, exists or not, size, last change |
| Skills, agents, commands, rules | name and the description in their frontmatter |
| Plugins and extensions | name and description from their manifest |
| MCP servers | name only (never command, arguments, URLs or keys) |
| Models | folder name |
| Third-party code | found and tagged, so it can be grouped away from your own work |

When something disappears it is marked gone, never deleted, so the history stays.
