# SPDX-License-Identifier: MIT
"""Command line: equipment-locker scan|serve|mcp [options] (or python -m equipment_locker)."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from . import db, mcp, places, scan, server


def default_db(opts):
    home = opts["current_home"] or Path.cwd()
    return places.token_roots(home, opts["platform"], opts["env"])["appdata"] / "equipment-locker" / "locker.db"


def lower_priority():
    """Be gentle on CPU and disk: nice 10, and idle IO class on Linux when ionice exists."""
    try:
        os.nice(10)
    except (AttributeError, OSError):
        pass
    if sys.platform == "linux" and shutil.which("ionice"):
        subprocess.run(["ionice", "-c3", "-p", str(os.getpid())], check=False, capture_output=True)


def _common(p, db_text, scan_options=True):
    p.add_argument("--db", help=f"catalog file (default: {db_text})")
    if scan_options:
        p.add_argument("--users", choices=["all", "me"], default="all")
        p.add_argument("--max-entries", type=int,
                       help="folder entries listed per scan, half for folders, half for sizes (default 1000000)")


def parse(argv, db_text="your app-data folder/equipment-locker/locker.db"):
    ap = argparse.ArgumentParser(prog="equipment-locker", description="Catalog your AI tooling (read-only).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan", help="scan this machine into the catalog")
    _common(s, db_text)
    s.add_argument("--depth", type=int, help="project search depth (default from places.json)")
    s.add_argument("--no-projects", action="store_true")
    s.add_argument("--no-sweep", action="store_true")
    s.add_argument("--dry-run", action="store_true", help="scan into memory; write nothing")
    s.add_argument("--json", action="store_true", help="print the summary as JSON")
    v = sub.add_parser("serve", help="open the cabinet page on http://127.0.0.1 (scans on start and every 6 h)")
    _common(v, db_text)
    v.add_argument("--port", type=int, default=8765)
    v.add_argument("--no-scan", action="store_true", help="no scan on start or every 6 h (Refresh still scans)")
    v.add_argument("--allow-host", action="append", default=[], metavar="NAME",
                   help="also answer requests for this host name, e.g. a tunnel or proxy in front (repeatable)")
    m = sub.add_parser("mcp", help="MCP server on stdin/stdout so an LLM can ask the catalog")
    _common(m, db_text, scan_options=False)
    m.add_argument("--read-only", action="store_true", help="hide the tag and note tools")
    return ap.parse_args(argv)


def options(args, doc):
    opts = scan.default_options(doc)
    opts.update(users=getattr(args, "users", "all"), projects=not getattr(args, "no_projects", False),
                sweep=not getattr(args, "no_sweep", False))
    if getattr(args, "max_entries", None):
        opts["limits"]["max_entries"] = args.max_entries
    if getattr(args, "depth", None) is not None:
        opts["limits"]["depth"] = args.depth
    return opts


def partial_note(budget):
    """Why a run stopped early, and what to do about it."""
    ran_out = [w for w, hit in (("listing folders", budget["walk_hit"]), ("measuring sizes", budget["size_hit"]))
               if hit]
    return (f"partial: the entry limit ({budget['limit']:,}) ran out while {' and '.join(ran_out)}. "
            f"Run again with a higher limit, e.g. --max-entries {budget['limit'] * 4}.")


def show(summary, as_json):
    if as_json:
        print(json.dumps(summary, indent=2, default=str))
        return
    print(f"run {summary['run_id']}: {summary['status']}, {summary['entries_seen']} entries listed, "
          f"{summary['seconds']} s")
    print(f"catalog: {summary['db']}")
    if summary["status"] == "partial":
        print(partial_note(summary["budget"]))
    print(f"users: {', '.join(summary['users']) or '-'}; unreadable: {', '.join(summary['unreadable_users']) or '-'}")
    print(f"changes: {summary['changes'] or 'none'}; marked absent: {summary['marked_absent']}")
    print("places: folders and files found for the tool; third-party: inside other code (node_modules, site-packages, ...)")
    for t in summary["tools"]:
        size = f"{t['bytes']:>14,} bytes" + (f" ({t['unsized']} not measured)" if t["unsized"] else "")
        print(f"  {t['tool']:<18} {t['present']:>5} places  {t['vendored'] or 0:>4} third-party  {size}")


def main(argv=None):
    doc = places.load()
    opts = scan.default_options(doc)
    args = parse(argv if argv is not None else sys.argv[1:], default_db(opts))
    opts = options(args, doc)
    db_path = args.db or default_db(opts)
    if args.cmd == "mcp":
        mcp.serve(db_path, args.read_only)
        return 0
    if args.cmd == "serve":
        lower_priority()
        server.serve(db_path, opts, {"port": args.port, "scan": not args.no_scan, "allow": args.allow_host})
        return 0
    path = ":memory:" if args.dry_run else db_path
    lower_priority()
    started = time.monotonic()
    conn = db.open_db(path)
    try:
        summary = scan.run(conn, doc, opts)
    finally:
        conn.close()
    summary["seconds"] = round(time.monotonic() - started, 1)
    summary["db"] = str(path)
    show(summary, args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
