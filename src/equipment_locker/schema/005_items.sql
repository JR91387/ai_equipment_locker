-- SPDX-License-Identifier: MIT
-- Items inside a location: one skill, agent, command, MCP server, plugin, model... Names and standard
-- descriptions only; contents are never stored.
CREATE TABLE ref_item_kind (
  id         INTEGER PRIMARY KEY,
  code       TEXT NOT NULL UNIQUE,
  display    TEXT NOT NULL,
  is_retired INTEGER NOT NULL DEFAULT 0 CHECK (is_retired IN (0, 1))
);
CREATE TABLE item (
  id             INTEGER PRIMARY KEY,
  location_id    INTEGER NOT NULL REFERENCES location(id),
  kind_id        INTEGER NOT NULL REFERENCES ref_item_kind(id),
  name           TEXT NOT NULL,
  description    TEXT,
  rel_path       TEXT NOT NULL,
  presence_id    INTEGER NOT NULL REFERENCES ref_presence(id),
  first_seen_run INTEGER NOT NULL REFERENCES scan_run(id),
  last_seen_run  INTEGER NOT NULL REFERENCES scan_run(id),
  is_retired     INTEGER NOT NULL DEFAULT 0 CHECK (is_retired IN (0, 1)),
  updated        TEXT NOT NULL,
  UNIQUE (location_id, rel_path)
);
CREATE INDEX item_kind ON item(kind_id);
CREATE TABLE item_change (
  id          INTEGER PRIMARY KEY,
  item_id     INTEGER NOT NULL REFERENCES item(id),
  run_id      INTEGER NOT NULL REFERENCES scan_run(id),
  change_id   INTEGER NOT NULL REFERENCES ref_change(id),
  name        TEXT NOT NULL,
  description TEXT,
  at          TEXT NOT NULL
);
CREATE INDEX item_change_item ON item_change(item_id);
CREATE TRIGGER ref_item_kind_no_delete BEFORE DELETE ON ref_item_kind
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER item_no_delete BEFORE DELETE ON item
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER item_change_no_delete BEFORE DELETE ON item_change
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
