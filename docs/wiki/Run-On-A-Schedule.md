# Run on a schedule

`serve` already scans when it starts and every 6 hours while it runs, so keeping it running is often enough.
To keep it running after logout or a restart, or to scan without the page, use your system's scheduler.
These examples assume you installed with `pipx install .`, which puts the `equipment-locker` command in
`~/.local/bin` (`%USERPROFILE%\.local\bin` on Windows).

## Linux (systemd, per user)
Files in [`docs/examples/`](../examples/):

| File | What it does |
|---|---|
| `equipment-locker-web.service` | Keeps the page open on `127.0.0.1:8765`, without its own scans |
| `equipment-locker-scan.service` + `.timer` | A scan 10 minutes after start, then every 6 hours |

```bash
cp docs/examples/equipment-locker-*.service docs/examples/equipment-locker-scan.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now equipment-locker-web equipment-locker-scan.timer
loginctl enable-linger "$USER"     # optional: keep running after you log out
```

## macOS (launchd)
[`docs/examples/local.equipment-locker.plist`](../examples/local.equipment-locker.plist) keeps the page open
and restarts it if it stops. Change `/Users/alice` to your home folder first.

```bash
cp docs/examples/local.equipment-locker.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/local.equipment-locker.plist
```

## Windows (Task Scheduler)
In a Command Prompt, as yourself (not as administrator):

```bat
schtasks /Create /TN "Equipment Locker scan" /SC HOURLY /MO 6 /TR "%USERPROFILE%\.local\bin\equipment-locker.exe scan"
schtasks /Create /TN "Equipment Locker page" /SC ONLOGON /TR "%USERPROFILE%\.local\bin\equipment-locker.exe serve --no-scan"
```

## Large machines
A scan lists at most 1,000,000 folder entries (half for finding folders, half for measuring sizes). If the
summary says `partial`, add `--max-entries 4000000` (or higher) to the `scan` or `serve` line.
