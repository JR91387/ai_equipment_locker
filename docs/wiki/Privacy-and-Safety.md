# Privacy and safety

- **Local only.** The catalogue is one SQLite file on your computer. The page is served to `127.0.0.1` only and
  refuses requests from other hosts or other websites.
- **Read-only toward your tools.** Equipment Locker never writes, moves or deletes a tool file.
- **Contents are not read.** The exceptions are small and named: the first 8 KB of a skill/agent/command file (for
  its name and description), plugin manifests (name and description), and MCP config files, from which only server
  names are taken.
- **Login files** (`auth.json`, tokens, OAuth caches) are checked for existence only: never opened, never sized.
- **Symbolic links** are recorded as links and never followed.
- **Other users.** Folders you are not allowed to read are listed as unreadable. The tool never asks for more rights.
- **Disk friendly.** Each run lists at most 50,000 folder entries, skips folders that have not changed, and runs at
  low priority.
