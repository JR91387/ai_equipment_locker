# SPDX-License-Identifier: MIT
"""Every user home on the machine. Unreadable homes are reported, never raised; nothing is elevated."""
import os
from pathlib import Path

SKIP = {"public", "default", "default user", "all users", "shared", "guest", "lost+found", "defaultapppool"}


def home_patterns(platform, doc_users):
    """Glob patterns for user homes on this OS, from the places document's 'users' block."""
    pats = doc_users.get(platform, doc_users.get("linux", []))
    drive = os.environ.get("SystemDrive", "C:")
    return [p.replace("%SystemDrive%", drive) for p in pats]


def _readable(path):
    try:
        with os.scandir(path):
            return True
    except OSError:
        return False


def _expand(pattern):
    if "*" not in pattern:
        return [Path(pattern)]
    base, _, glob = pattern.partition("*")
    try:
        return sorted(Path(base).glob("*" + glob))
    except OSError:
        return []


def list_homes(patterns, current_home=None):
    """[(name, Path, readable)] for every home folder; the current user's home is always included."""
    seen, out = set(), []
    candidates = [p for pat in patterns for p in _expand(pat)]
    if current_home:
        candidates.append(Path(current_home))
    for path in candidates:
        try:
            is_dir = path.is_dir() and not path.is_symlink()
        except OSError:
            is_dir = False
        key = str(path)
        if not is_dir or key in seen or path.name.lower() in SKIP:
            continue
        seen.add(key)
        out.append((path.name, path, _readable(path)))
    return out


def current_home():
    """The scanning user's home, or None if the OS cannot say."""
    try:
        return Path.home()
    except RuntimeError:
        return None
