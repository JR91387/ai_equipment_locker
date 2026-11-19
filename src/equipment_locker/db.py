# SPDX-License-Identifier: MIT
"""Database access: connect, migrate, re-apply seeds and views, look up ref codes.

schema/NNN_*.sql are migrations, applied once each and tracked by PRAGMA user_version.
schema/seed_ref.sql and schema/views.sql are re-applied on every open (idempotent).
"""
import re
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

SCHEMA_DIR = Path(__file__).resolve().parent / "schema"
REAPPLY = ("seed_ref.sql", "views.sql")
_MIGRATION = re.compile(r"^(\d{3})_.*\.sql$")
_REF = re.compile(r"^ref_[a-z_]+$")


class LockerConnection(sqlite3.Connection):
    """A connection that caches ref code -> id lookups and can add new codes on the fly."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._refs = {}

    def ref_id(self, table, code, display=None):
        """Id of `code` in `table`. With `display`, an unknown code is added instead of raising."""
        if not _REF.match(table):
            raise ValueError(f"not a ref table: {table}")
        hit = self._refs.get((table, code))
        if hit is not None:
            return hit
        row = self.execute(f"SELECT id FROM {table} WHERE code = ?", (code,)).fetchone()
        if row is None and display is None:
            raise KeyError(f"{table} has no code {code!r}")
        if row is None:
            self.execute(f"INSERT INTO {table} (code, display) VALUES (?, ?)", (code, display))
            row = self.execute(f"SELECT id FROM {table} WHERE code = ?", (code,)).fetchone()
        self._refs[(table, code)] = row[0]
        return row[0]


def now():
    """Current UTC time in the schema's text format."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def connect(path):
    """Open (creating folders as needed) with the PRAGMAs every connection needs."""
    if str(path) != ":memory:":
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path), factory=LockerConnection, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 30000")
    return conn


def migrations():
    """(number, path) for every migration file, in order."""
    found = []
    for path in sorted(SCHEMA_DIR.glob("*.sql")):
        match = _MIGRATION.match(path.name)
        if match:
            found.append((int(match.group(1)), path))
    return found


def migrate(conn):
    """Apply pending migrations, each in its own transaction with its user_version bump."""
    current = conn.execute("PRAGMA user_version").fetchone()[0]
    for number, path in migrations():
        if number > current:
            conn.executescript(f"BEGIN;\n{path.read_text()}\nPRAGMA user_version = {number};\nCOMMIT;")
    return conn.execute("PRAGMA user_version").fetchone()[0]


def reapply(conn):
    """Seeds and views: safe to run any number of times."""
    for name in REAPPLY:
        conn.executescript(f"BEGIN;\n{(SCHEMA_DIR / name).read_text()}\nCOMMIT;")


def open_db(path):
    """Connect, migrate and re-apply seeds/views: the one call callers need."""
    from .paths import backfill
    conn = connect(path)
    migrate(conn)
    reapply(conn)
    backfill(conn)
    return conn
