# Getting started

**You need:** Python 3.11 or newer. No other installs, no internet connection.

## Open the cabinet
```bash
PYTHONPATH=src python3 -m equipment_locker serve
```
Open `http://127.0.0.1:8765`. The first scan starts right away; the shelves fill in as it finishes. After that
the cabinet takes stock every 6 hours while it is open, and whenever you press **Refresh**.

Options: `--port 9000`, `--db /path/to/locker.db`, `--no-scan` (just show what is already catalogued),
`--users me` (only your own home folder).

## Scan from the terminal
```bash
PYTHONPATH=src python3 -m equipment_locker scan            # all users you can read
PYTHONPATH=src python3 -m equipment_locker scan --dry-run  # look without saving anything
PYTHONPATH=src python3 -m equipment_locker scan --json     # machine-readable summary
```

## Where the catalogue lives
One SQLite file in your app-data folder: `~/.local/share/equipment-locker/locker.db` on Linux,
`~/Library/Application Support/equipment-locker/` on macOS, `%LOCALAPPDATA%\equipment-locker\` on Windows.
Delete it to start over; nothing else is written anywhere.

## Using the page
- **Shelves**: one card per tool. Click to open it.
- **Table**: everything in one sortable list.
- **Search**: type anything; case, dashes, dots and underscores do not matter.
- **Details**: click any card to see its path and size, and to add a note, tags, a favourite star or a picture.
- **Pin a folder**: the box under the shelves adds any folder to every future scan.
