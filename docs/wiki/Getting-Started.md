# Getting started

**You need:** Python 3.11 or newer. No other installs, no internet connection.

## Open the cabinet
```bash
pipx install .               # once, from the downloaded folder; adds the equipment-locker command
equipment-locker serve
```
Without pipx, run `PYTHONPATH=src python3 -m equipment_locker` instead of `equipment-locker`.
Open `http://127.0.0.1:8765`. The first scan starts right away; the shelves fill in as it finishes. After that
the cabinet takes stock every 6 hours while it is open, and whenever you press **Refresh**.

Options: `--port 9000`, `--db /path/to/locker.db`, `--no-scan` (no scan on start or every 6 hours; **Refresh**
still scans), `--users me` (only your own home folder), `--max-entries N` (see below), `--allow-host NAME` (see
[View from another machine](View-From-Another-Machine.md)). To keep it running, see
[Run on a schedule](Run-On-A-Schedule.md).

## Scan from the terminal
```bash
equipment-locker scan            # all users you can read
equipment-locker scan --dry-run  # look without saving anything
equipment-locker scan --json     # machine-readable summary
```

The summary lists each tool's **places** (folders and files it uses) and how many of them are **third-party**
(found inside other code, such as `node_modules` or `site-packages`). A size marked **not measured** was skipped
this run, not empty.

**`partial`** means the scan hit its limit of folder entries (1,000,000 by default: half for finding folders,
half for measuring sizes) and stopped early; the summary says which half ran out. Raise it with
`--max-entries 4000000`. Nothing is lost: the next run picks up again.

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
