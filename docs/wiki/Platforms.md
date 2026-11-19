# Platforms

Works on macOS, Windows (8, 10, 11) and Linux (Ubuntu, Debian) with Python 3.11+.

- **Windows:** per-user folders under `%USERPROFILE%`, `%APPDATA%` and `%LOCALAPPDATA%`, including Microsoft Store
  app copies. Paths are matched without regard to case.
- **macOS:** `~/Library/Application Support`, `~/Library/Caches`, `~/Library/Logs`. Grant your terminal Full Disk
  Access if you want other users' folders included. Paths are matched without regard to case.
- **Linux:** XDG folders (`~/.config`, `~/.local/share`, `~/.local/state`, `~/.cache`) and `/etc` for
  machine-wide settings.

Details and known limits: [PLATFORMS.md](../PLATFORMS.md).
