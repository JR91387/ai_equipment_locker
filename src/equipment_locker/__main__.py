# SPDX-License-Identifier: MIT
"""Command line: python -m equipment_locker scan [options]."""
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


def parse(argv):
    ap = argparse.ArgumentParser(prog="equipment_locker", description="Catalog your AI tooling (read-only).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan", help="scan this machine into the catalog")
    s.add_argument("--db", help="catalog file (default: your app-data folder/equipment-locker/locker.db)")
    s.add_argument("--users", choices=["all", "me"], default="all")
    s.add_argument("--max-entries", type=int, help="folder entries listed per run (default from places.json)")
    s.add_argument("--depth", type=int, help="project search depth (default from places.json)")
    s.add_argument("--no-projects", action="store_true")
    s.add_argument("--no-sweep", action="store_true")
    s.add_argument("--dry-run", action="store_true", help="scan into memory; write nothing")
    s.add_argument("--json", action="store_true", help="print the summary as JSON")
    v = sub.add_parser("serve", help="open the cabinet page on http://127.0.0.1 (scans on start and every 6 h)")
    v.add_argument("--db", help="catalog file (default as for scan)")
    v.add_argument("--port", type=int, default=8765)
    v.add_argument("--no-scan", action="store_true", help="show the catalog without scanning")
    v.add_argument("--users", choices=["all", "me"], default="all")
    m = sub.add_parser("mcp", help="MCP server on stdin/stdout so an LLM can ask the catalog")
    m.add_argument("--db", help="catalog file (default as for scan)")
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


def show(summary, as_json):
    if as_json:
        print(json.dumps(summary, indent=2, default=str))
        return
    print(f"run {summary['run_id']}: {summary['status']}, {summary['entries_seen']} entries listed, "
          f"{summary['seconds']} s")
    print(f"users: {', '.join(summary['users']) or '-'}; unreadable: {', '.join(summary['unreadable_users']) or '-'}")
    print(f"changes: {summary['changes'] or 'none'}; marked absent: {summary['marked_absent']}")
    for t in summary["tools"]:
        print(f"  {t['tool']:<18} {t['present']:>5} present  {t['vendored'] or 0:>4} vendored  {t['bytes']:>14,} bytes")


def main(argv=None):
    args = parse(argv if argv is not None else sys.argv[1:])
    doc = places.load()
    opts = options(args, doc)
    if args.cmd == "mcp":
        mcp.serve(args.db or default_db(opts), args.read_only)
        return 0
    if args.cmd == "serve":
        lower_priority()
        server.serve(args.db or default_db(opts), opts, args.port, not args.no_scan)
        return 0
    path = ":memory:" if args.dry_run else (args.db or default_db(opts))
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
