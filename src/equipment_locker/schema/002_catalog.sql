-- SPDX-License-Identifier: MIT
-- Catalog: what to look for (place), where (machine, os_user), what was found (location) and its history.
CREATE TABLE machine (
  id         INTEGER PRIMARY KEY,
  name       TEXT NOT NULL UNIQUE,
  os_id      INTEGER NOT NULL REFERENCES ref_os(id),
  first_seen TEXT NOT NULL,
  last_seen  TEXT NOT NULL
);
CREATE TABLE os_user (
  id          INTEGER PRIMARY KEY,
  machine_id  INTEGER NOT NULL REFERENCES machine(id),
  name        TEXT NOT NULL,
  home        TEXT NOT NULL,
  presence_id INTEGER NOT NULL REFERENCES ref_presence(id),
  first_seen  TEXT NOT NULL,
  last_seen   TEXT NOT NULL,
  is_retired  INTEGER NOT NULL DEFAULT 0 CHECK (is_retired IN (0, 1)),
  UNIQUE (machine_id, name)
);
CREATE TABLE place (
  id            INTEGER PRIMARY KEY,
  code          TEXT NOT NULL UNIQUE,
  tool_id       INTEGER NOT NULL REFERENCES ref_tool(id),
  scope_id      INTEGER NOT NULL REFERENCES ref_scope(id),
  category_id   INTEGER NOT NULL REFERENCES ref_category(id),
  source_id     INTEGER NOT NULL REFERENCES ref_source(id),
  path_template TEXT NOT NULL,
  kind          TEXT NOT NULL CHECK (kind IN ('dir', 'file', 'glob')),
  env_var       TEXT,
  holds         TEXT,
  ref_url       TEXT,
  is_builtin    INTEGER NOT NULL DEFAULT 1 CHECK (is_builtin IN (0, 1)),
  is_enabled    INTEGER NOT NULL DEFAULT 1 CHECK (is_enabled IN (0, 1)),
  is_retired    INTEGER NOT NULL DEFAULT 0 CHECK (is_retired IN (0, 1)),
  updated       TEXT NOT NULL
);
-- No rows for a place = it applies on every OS.
CREATE TABLE place_os (
  place_id INTEGER NOT NULL REFERENCES place(id),
  os_id    INTEGER NOT NULL REFERENCES ref_os(id),
  PRIMARY KEY (place_id, os_id)
);
CREATE TABLE scan_run (
  id           INTEGER PRIMARY KEY,
  machine_id   INTEGER NOT NULL REFERENCES machine(id),
  started      TEXT NOT NULL,
  finished     TEXT,
  status_id    INTEGER NOT NULL REFERENCES ref_run_status(id),
  entries_seen INTEGER NOT NULL DEFAULT 0,
  budget_hit   INTEGER NOT NULL DEFAULT 0 CHECK (budget_hit IN (0, 1)),
  options_json TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE project (
  id             INTEGER PRIMARY KEY,
  machine_id     INTEGER NOT NULL REFERENCES machine(id),
  os_user_id     INTEGER REFERENCES os_user(id),
  root           TEXT NOT NULL,
  origin_id      INTEGER NOT NULL REFERENCES ref_origin(id),
  first_seen_run INTEGER NOT NULL REFERENCES scan_run(id),
  last_seen_run  INTEGER NOT NULL REFERENCES scan_run(id),
  is_retired     INTEGER NOT NULL DEFAULT 0 CHECK (is_retired IN (0, 1)),
  UNIQUE (machine_id, root)
);
-- One real path on one machine. (machine_id, path) is its stable identity: notes and images attach here later.
CREATE TABLE location (
  id             INTEGER PRIMARY KEY,
  machine_id     INTEGER NOT NULL REFERENCES machine(id),
  path           TEXT NOT NULL,
  place_id       INTEGER REFERENCES place(id),
  project_id     INTEGER REFERENCES project(id),
  os_user_id     INTEGER REFERENCES os_user(id),
  tool_id        INTEGER NOT NULL REFERENCES ref_tool(id),
  scope_id       INTEGER NOT NULL REFERENCES ref_scope(id),
  category_id    INTEGER NOT NULL REFERENCES ref_category(id),
  origin_id      INTEGER NOT NULL REFERENCES ref_origin(id),
  source_id      INTEGER NOT NULL REFERENCES ref_source(id),
  presence_id    INTEGER NOT NULL REFERENCES ref_presence(id),
  kind           TEXT NOT NULL,
  size_bytes     INTEGER,
  size_over      INTEGER NOT NULL DEFAULT 0 CHECK (size_over IN (0, 1)),
  entry_count    INTEGER,
  mtime          REAL,
  first_seen_run INTEGER NOT NULL REFERENCES scan_run(id),
  last_seen_run  INTEGER NOT NULL REFERENCES scan_run(id),
  is_retired     INTEGER NOT NULL DEFAULT 0 CHECK (is_retired IN (0, 1)),
  updated        TEXT NOT NULL,
  UNIQUE (machine_id, path)
);
CREATE INDEX location_tool ON location(tool_id);
CREATE INDEX location_project ON location(project_id);
-- Written only when a location appears, changes, disappears or returns.
CREATE TABLE location_change (
  id          INTEGER PRIMARY KEY,
  location_id INTEGER NOT NULL REFERENCES location(id),
  run_id      INTEGER NOT NULL REFERENCES scan_run(id),
  change_id   INTEGER NOT NULL REFERENCES ref_change(id),
  presence_id INTEGER NOT NULL REFERENCES ref_presence(id),
  size_bytes  INTEGER,
  mtime       REAL,
  at          TEXT NOT NULL
);
CREATE INDEX location_change_location ON location_change(location_id);
-- Folder cache for the project search: unchanged folders (same mtime) are not listed again.
CREATE TABLE walk_state (
  machine_id   INTEGER NOT NULL REFERENCES machine(id),
  dir_path     TEXT NOT NULL,
  dir_mtime    REAL NOT NULL,
  children     TEXT NOT NULL DEFAULT '[]',
  markers      TEXT NOT NULL DEFAULT '[]',
  last_run_id  INTEGER NOT NULL REFERENCES scan_run(id),
  PRIMARY KEY (machine_id, dir_path)
);
