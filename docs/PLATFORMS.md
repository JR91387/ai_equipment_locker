# Platforms

What the scanner assumes on each operating system, where that comes from, and what has not been tested on a
real machine yet. Paths per tool are in `PLACES.md`.

## Shared
- Python reports the OS as `linux`, `darwin` (macOS) or `win32` (Windows); `places.json` uses the same codes.
- Tool folders that start with a dot (`.claude`, `.codex`, `.gemini`, `.cursor`, ...) sit in the user's home on
  every OS. On Windows the home is `%USERPROFILE%` (`C:\Users\<name>`). Source: each tool's docs (see `PLACES.md`).
- Tool environment variables (`CLAUDE_CONFIG_DIR`, `CODEX_HOME`, ...) are read only for the user running the
  scan. Other users' variables cannot be seen from outside their session.
- Nothing is opened, hashed or followed through a symbolic link. Folder sizes are counted up to a file limit.

## Windows (8, 10, 11)
- Per-user app data: `%APPDATA%` = `<home>\AppData\Roaming` (`{roaming}`, `{appconfig}`) and `%LOCALAPPDATA%` =
  `<home>\AppData\Local` (`{local}`, `{appdata}`, `{appcache}`). These folder names are the same on 8, 10 and 11.
  The scanner builds them from each user's home, so it works for users other than the one running it.
- Machine-wide: `%PROGRAMDATA%` (`C:\ProgramData`) and `%ProgramFiles%` (`C:\Program Files`).
- Users: `%SystemDrive%\Users\*`, skipping `Public`, `Default`, `Default User`, `All Users`.
- Microsoft Store (MSIX) apps keep a virtualised copy of their AppData under
  `%LOCALAPPDATA%\Packages\<package>\LocalCache\Roaming`. Known case: Claude Desktop (`Packages\Claude_*`).
- Reading other users' folders needs an administrator account; without it they are recorded as unreadable.
- Untested here: a real Windows run. Folder checks on a Windows 10 Pro machine matched `PLACES.md`.

## macOS
- Per-user app data: `~/Library/Application Support` (`{appconfig}`, `{appdata}`), `~/Library/Caches`
  (`{appcache}`), `~/Library/Logs` (`{applogs}`).
- Machine-wide: `/Library/Application Support/<Tool>` (Claude Code, Gemini CLI, Cursor, Qwen Code managed files).
- Users: `/Users/*`, skipping `Shared` and `Guest`.
- macOS privacy controls (TCC) can block reading parts of another user's home, or Desktop/Documents/Downloads
  even for your own, unless the terminal running the scan has Full Disk Access. Blocked folders are recorded as
  unreadable; the scan does not stop.
- Untested here: a real macOS run.

## Linux (Ubuntu, Debian)
- Per-user app data follows the XDG base directories: `$XDG_CONFIG_HOME` or `~/.config` (`{appconfig}`),
  `$XDG_DATA_HOME` or `~/.local/share` (`{appdata}`), `$XDG_STATE_HOME` or `~/.local/state` (`{appstate}`),
  `$XDG_CACHE_HOME` or `~/.cache` (`{appcache}`). The variables apply only to the user running the scan.
- Machine-wide: `/etc/<tool>` (Claude Code managed settings, Codex, Gemini CLI, Cursor, Qwen Code).
- Users: `/home/*` and `/root`. Other users' homes are usually mode 750 or 700, so a normal user sees them as
  unreadable; running the scan with more rights is the user's choice, never the tool's.
- Tested here: Ubuntu, as a normal user. Folder checks on Ubuntu 24.04 matched `PLACES.md`.

## Disk safety
- Defaults (in `places.json` under `limits`): project search depth 4; at most 50,000 folder entries listed per
  run, half for sizes and half for the project search and name sweep; folder sizes counted up to 10,000 files.
- Folders whose modified time has not changed since the last run are not listed again (cached in `walk_state`).
- When the entry budget runs out the run is marked partial, and the next run continues where it stopped.
- The scanner lowers its own priority (`nice 10`; idle IO class via `ionice` on Linux when available).
- Sizes are approximate, for at-a-glance use: a folder is re-counted when its own modified time changes. A file
  growing deep inside an unchanged folder is picked up when that folder next changes.

## Known limits
- Path identity is case-sensitive. On Windows and default macOS volumes, the same folder reached with
  different capitalisation (for example through an environment variable) could be catalogued twice.

