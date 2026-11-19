# Design

Equipment Locker catalogs a person's AI "equipment" and shows it as a dashboard they curate. The person is the
primary audience: collection is a small helper, the visual work is the product. (Contrast: THE INDEX collects
large amounts of system data mainly for an LLM to read.)

## Scope
| In | Out (for now) |
|---|---|
| Claude Code, Claude Desktop, Codex, ChatGPT desktop, Antigravity, Gemini CLI | Editing any tool's files |
| AI coding tools: Cursor, Copilot, Windsurf, VS Code AI extensions, Continue, Aider, opencode, Goose, Kiro, Qwen Code, Amp | Reading the contents of history, cache, log or auth files |
| Local models and runtimes: Ollama, LM Studio, Hugging Face cache, Jan, GPT4All, npx/uv/pipx caches | Cloud-only state with no local file |
| Every user on the machine; project folders; user-pinned folders | Whole-system scans (that is THE INDEX) |
| User-added images, notes, tags, favourites | Multi-user sharing |

## Patterns reused from THE INDEX
Lookup tables (`id` + unique `code`), no-delete triggers (retire instead), `PRAGMA user_version`
migrations plus idempotent seeds/views, standalone stdlib scripts. Copied, never imported.

## Decisions
| Topic | Decision |
|---|---|
| Independence | Fully standalone. THE INDEX may not exist on the user's machine; neither app depends on the other. |
| Images | Stored as BLOBs in SQLite (one portable file), with a per-image size cap. |
| History | Full history: every change to a catalogued location is a change row; nothing is deleted. |
| Main view | Card grid with images, with a toggle to a sortable table; both share the same filters. |
| Frontend | A local server (`serve`, Python stdlib) is required: everything is viewed and edited in the browser. |
| Known places | Built-in list in `src/equipment_locker/places.json` (see `docs/PLACES.md`): tool, scope, category, path template, OS, source. Loaded into the `place` table on every start; removed entries are retired. Users pin their own folders as non-built-in rows of the same table. |
| Path templates | Tokens resolve per OS and per user: `{home}`, `{appconfig}` (Roaming / Application Support / `~/.config`), `{appdata}`, `{appcache}`, `{appstate}`, `{roaming}`, `{local}`, `{programdata}`, `{programfiles}`, `{project}`. A token with no value on an OS skips the entry there. Tool env vars (`CLAUDE_CONFIG_DIR`, `CODEX_HOME`, ...) apply to the user running the scan. |
| Users | Every home folder on the machine is scanned. Unreadable homes are recorded as unreadable; the tool never elevates privileges. |
| Data folders | History, cache, logs, install and model folders: existence and size only, never opened. Auth files: existence only. |
| Project folders | Searched under each home by marker files (`CLAUDE.md`, `.claude`, `AGENTS.md`, `.cursor`, ...). Nothing is skipped: hits inside third-party code (`node_modules`, `vendor`, `.cargo`, `site-packages`, ...) are tagged `vendored` so the dashboard can group or hide them. |
| Name sweep | One level deep under each user's app-data folders, matching tool names; hits are `discovered`. |
| Disk safety | Defaults: depth 4, 50,000 folder entries per run (the next run resumes), sizes counted up to 10,000 files then marked "over", only folders whose modified time changed are walked again, low CPU/IO priority. Files are never opened, hashed or followed through symlinks. |
| Self-maintaining | Each scan upserts. Things that vanish are marked absent with a change row; things that return are re-linked; new finds are added silently. The user is never asked. |

## What is catalogued
Equipment Locker is a catalogue, not an editor: it answers "what do I have, and where?" at a glance. It
records names, paths, presence, size and dates. File contents are never read; the one planned exception is the
`description` (and name) in a skill's or agent's frontmatter, so a card can say what it is.

## Data model (SQLite)
- Lookups `ref_*`: os, tool, scope, category, source, presence, origin, change, run_status, item_kind.
- `place` (+ `place_os`): what to look for. Built-ins come from `places.json`; pinned folders are rows with
  `is_builtin = 0` and scope `pinned`. `machine`, `os_user`: where.
- `location`: one real path on a machine, identified by (machine, `path_key`). `path_key` is the normalized path,
  lowercased on Windows and macOS, so different spellings of one folder share a row. `project` groups locations.
- `item`: one skill, agent, command, MCP server, plugin or model inside a location (name + standard description).
- `scan_run`; `location_change` and `item_change`: written only when something appears, changes, disappears or
  returns. `walk_state`: folder cache so unchanged folders are not listed again.
- Yours: `annotation` (one per location, item or tool: label, note, favourite) with `annotation_version` kept by a
  trigger; `tag` + `tag_link`; `image` (png/jpeg/gif/webp up to 2 MB). Nothing is deleted; removing retires.
- Search: `search_doc` rebuilt after each scan and edit; an FTS5 trigram index over its normalized text when SQLite
  has FTS5 (case, separators and partial words ignored), a normalized LIKE otherwise.

## Local page
- `python -m equipment_locker serve`: stdlib server on `127.0.0.1` only; JSON API + static page from `web/`.
- Scans on start, every 6 hours while running, and on Refresh; one scan at a time.
- Guards: non-local `Host` headers refused (DNS rebinding); writes need `X-Locker: 1` and a local or absent
  `Origin`; request bodies capped at 3 MB; uploads checked by magic bytes; static files confined to `web/`;
  `Content-Security-Policy: default-src 'self'`.
- Page: plain HTML/CSS/JS, no build, bundled fonts. Tool shelves, tool view, table, search, detail panel.

## MCP server
- `python -m equipment_locker mcp`: JSON-RPC 2.0 over stdin/stdout, standard library only (protocol versions
  2025-06-18, 2025-03-26, 2024-11-05). Tools: search, list_tools, tool_detail, item_detail, recent_changes, plus
  add_tag, remove_tag, set_note (hidden with `--read-only`). Serves only the catalogue; never scans or reads tool files.

## Look
- Tools without a picture get one of ten square palette gradients (`web/gradients/`), chosen by a stable hash of the
  tool code, with the tool's initials on top.
- Storage art (vector, `06_brand_and_media/01_current/`): foot locker for the social preview, wiki header and empty
  state; supply shelves for the README hero. The mascot illustration is no longer the lead.

## Open questions
None.
