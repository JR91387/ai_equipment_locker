# SPDX-License-Identifier: MIT
"""Project search and name sweep: names only, never file contents, bounded by depth and an entry budget.

Unchanged folders (same mtime as last run) reuse their cached child list instead of being listed again.
"""
import os
import re
from pathlib import Path

_SPLIT = re.compile(r"[^a-z0-9]+")


def is_vendored(path, vendored_dirs):
    """True if any folder in the path is third-party code (node_modules, vendor, .cargo, ...)."""
    text = "/" + str(path).replace("\\", "/").strip("/").lower() + "/"
    return any(f"/{v.strip('/').lower()}/" in text for v in vendored_dirs)


def _listing(path, cache, budget):
    """(children dirs, entry names) for a folder, from cache when its mtime is unchanged. None if unreadable."""
    try:
        mtime = round(os.stat(path).st_mtime, 3)
    except OSError:
        return None
    hit = cache.get(str(path))
    if hit and hit["mtime"] == mtime:
        hit["used"] = True
        return hit["children"], hit["names"]
    if budget.spent:
        return None
    try:
        entries = list(os.scandir(path))
    except OSError:
        return None
    budget.spend(len(entries))
    children = sorted(e.name for e in entries if _is_dir(e))
    names = sorted(e.name for e in entries)
    cache[str(path)] = {"mtime": mtime, "children": children, "names": names, "used": True, "fresh": True}
    return children, names


def _is_dir(entry):
    try:
        return entry.is_dir(follow_symlinks=False)
    except OSError:
        return False


def _lexists(path):
    """Exists without following a symlink."""
    try:
        os.lstat(path)
        return True
    except OSError:
        return False


def _hits_in(folder, names, markers):
    found = []
    name_set = set(names)
    for m in markers:
        first, _, rest = m.partition("/")
        if first in name_set and (not rest or _lexists(folder / m)):
            found.append((folder, m))
    return found


def find_projects(root, opts, cache, budget):
    """[(folder, marker)] under root. opts: markers, depth, skip_roots. Returns (hits, complete)."""
    hits, complete, stack = [], True, [(Path(root), 0)]
    skip = {str(p) for p in opts.get("skip_roots", ())}
    marker_dirs = {m.split("/", 1)[0] for m in opts["markers"]}
    while stack:
        folder, depth = stack.pop()
        listing = _listing(folder, cache, budget)
        if listing is None:
            complete = complete and not budget.spent
            continue
        children, names = listing
        hits.extend(_hits_in(folder, names, opts["markers"]))
        if depth >= opts["depth"]:
            continue
        for child in children:
            path = folder / child
            if child not in marker_dirs and str(path) not in skip:
                stack.append((path, depth + 1))
    return hits, complete and not budget.spent


def _tokens(name):
    return [t for t in _SPLIT.split(name.lower()) if t]


def matches_tool(name, tool_names):
    """Tool keyword matched by a folder name: exact token, or token prefix for keywords of 5+ letters."""
    for tok in _tokens(name):
        for word in tool_names:
            if tok == word or (len(word) >= 5 and tok.startswith(word)):
                return word
    return None


def sweep(roots, tool_names, budget):
    """([(path, keyword)], complete) for entries one level under each root whose name matches a tool keyword.

    complete is False when a root could not be listed, so earlier finds there are not marked absent.
    """
    found, seen, complete = [], set(), True
    for root in roots:
        if budget.spent or str(root) in seen:
            continue
        seen.add(str(root))
        try:
            entries = list(os.scandir(root))
        except FileNotFoundError:
            continue
        except OSError:
            complete = False
            continue
        budget.spend(len(entries))
        found.extend((Path(e.path), w) for e in entries if (w := matches_tool(e.name, tool_names)))
    return found, complete and not budget.spent
