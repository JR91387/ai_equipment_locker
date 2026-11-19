# SPDX-License-Identifier: MIT
"""Look at one path without opening it: lstat, a bounded size count, never follow symlinks."""
import os
import stat
from pathlib import Path

NO_SIZE = {"auth"}  # existence only


class Budget:
    """Counts directory entries listed during a run; once spent, walking stops (the next run resumes)."""

    def __init__(self, limit):
        self.limit, self.used = limit, 0

    def spend(self, n=1):
        self.used += n
        return self.used <= self.limit

    @property
    def spent(self):
        return self.used >= self.limit


def dir_size(path, max_files, budget):
    """(bytes, files_counted, over) for a folder, counting at most max_files files. Symlinks are not followed."""
    total, files, stack = 0, 0, [path]
    while stack:
        current = stack.pop()
        try:
            entries = list(os.scandir(current))
        except OSError:
            continue
        budget.spend(len(entries))
        for e in entries:
            if files >= max_files or budget.spent:
                return total, files, True
            try:
                if e.is_dir(follow_symlinks=False):
                    stack.append(e.path)
                elif e.is_file(follow_symlinks=False):
                    total += e.stat(follow_symlinks=False).st_size
                    files += 1
            except OSError:
                continue
    return total, files, False


def probe(path, kind, category, opts):
    """{presence, size_bytes, size_over, entry_count, mtime} for one path. Never raises.

    opts: limits, budget (sizing budget), prior (last run's row or None: an unchanged folder keeps its size).
    """
    path = Path(path)
    out = {"presence": "absent", "size_bytes": None, "size_over": 0, "entry_count": None, "mtime": None}
    try:
        st = os.lstat(path)
    except FileNotFoundError:
        return out
    except OSError:
        return {**out, "presence": "unreadable"}
    out["mtime"] = round(st.st_mtime, 3)
    if stat.S_ISLNK(st.st_mode):
        return {**out, "presence": "link"}
    want_dir = kind == "dir"
    if want_dir != stat.S_ISDIR(st.st_mode) and kind != "glob":
        return {**out, "presence": "wrong_type"}
    out["presence"] = "present"
    if category in NO_SIZE:
        return out
    if not stat.S_ISDIR(st.st_mode):
        return {**out, "size_bytes": st.st_size}
    return _fill_dir(out, path, opts)


def _fill_dir(out, path, opts):
    try:
        with os.scandir(path) as it:
            out["entry_count"] = sum(1 for _ in it)
        opts["budget"].spend(out["entry_count"])
    except OSError:
        return {**out, "presence": "unreadable"}
    prior = opts.get("prior")
    # Reuse a known size when the folder is unchanged, or when it already hit the file cap ("over"): re-counting
    # a huge, busy folder every run would spend the whole budget and starve folders not yet sized.
    if prior and prior["size_bytes"] is not None and (prior["mtime"] == out["mtime"] or prior["size_over"]):
        return {**out, "size_bytes": prior["size_bytes"], "size_over": prior["size_over"]}
    max_files = opts["limits"]["size_max_files"]
    size, files, over = dir_size(path, max_files, opts["budget"])
    if over and files < max_files:  # cut short by the run budget: unknown, retried next run
        return out
    return {**out, "size_bytes": size, "size_over": int(over)}


def expand_glob(path):
    """Matches for a path containing '*' (searched from the folder before the first '*').

    None when that folder exists but cannot be read, so callers do not mistake it for "no matches".
    """
    text = str(path)
    if "*" not in text:
        return [Path(text)]
    head, _, _ = text.partition("*")
    anchor = Path(head) if head.endswith(("/", os.sep)) else Path(head).parent
    try:
        pattern = os.path.relpath(text, anchor)
        os.scandir(anchor).close()
    except FileNotFoundError:
        return []
    except (OSError, ValueError):
        return None
    try:
        return sorted(anchor.glob(pattern))[:200]
    except (OSError, ValueError):
        return None
