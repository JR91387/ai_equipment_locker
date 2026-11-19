-- SPDX-License-Identifier: MIT
-- What the person adds: notes (with full history), favourites, tags, images. Each row points at exactly one
-- target: a location, an item or a tool. Removing means retiring.
CREATE TABLE annotation (
  id          INTEGER PRIMARY KEY,
  location_id INTEGER REFERENCES location(id),
  item_id     INTEGER REFERENCES item(id),
  tool_id     INTEGER REFERENCES ref_tool(id),
  label       TEXT,
  note        TEXT,
  is_favorite INTEGER NOT NULL DEFAULT 0 CHECK (is_favorite IN (0, 1)),
  updated     TEXT NOT NULL,
  CHECK ((location_id IS NOT NULL) + (item_id IS NOT NULL) + (tool_id IS NOT NULL) = 1)
);
CREATE UNIQUE INDEX annotation_location ON annotation(location_id) WHERE location_id IS NOT NULL;
CREATE UNIQUE INDEX annotation_item ON annotation(item_id) WHERE item_id IS NOT NULL;
CREATE UNIQUE INDEX annotation_tool ON annotation(tool_id) WHERE tool_id IS NOT NULL;
CREATE TABLE annotation_version (
  id            INTEGER PRIMARY KEY,
  annotation_id INTEGER NOT NULL REFERENCES annotation(id),
  label         TEXT,
  note          TEXT,
  is_favorite   INTEGER NOT NULL,
  at            TEXT NOT NULL
);
CREATE TRIGGER annotation_keep_version AFTER UPDATE ON annotation
  WHEN OLD.label IS NOT NEW.label OR OLD.note IS NOT NEW.note OR OLD.is_favorite IS NOT NEW.is_favorite
  BEGIN
    INSERT INTO annotation_version (annotation_id, label, note, is_favorite, at)
    VALUES (OLD.id, OLD.label, OLD.note, OLD.is_favorite, OLD.updated);
  END;
CREATE TABLE tag (
  id         INTEGER PRIMARY KEY,
  name       TEXT NOT NULL UNIQUE COLLATE NOCASE,
  color      TEXT,
  is_retired INTEGER NOT NULL DEFAULT 0 CHECK (is_retired IN (0, 1))
);
CREATE TABLE tag_link (
  id          INTEGER PRIMARY KEY,
  tag_id      INTEGER NOT NULL REFERENCES tag(id),
  location_id INTEGER REFERENCES location(id),
  item_id     INTEGER REFERENCES item(id),
  tool_id     INTEGER REFERENCES ref_tool(id),
  is_retired  INTEGER NOT NULL DEFAULT 0 CHECK (is_retired IN (0, 1)),
  created     TEXT NOT NULL,
  CHECK ((location_id IS NOT NULL) + (item_id IS NOT NULL) + (tool_id IS NOT NULL) = 1)
);
CREATE UNIQUE INDEX tag_link_target ON tag_link(tag_id, COALESCE(location_id, 0), COALESCE(item_id, 0),
  COALESCE(tool_id, 0));
CREATE TABLE image (
  id          INTEGER PRIMARY KEY,
  location_id INTEGER REFERENCES location(id),
  item_id     INTEGER REFERENCES item(id),
  tool_id     INTEGER REFERENCES ref_tool(id),
  mime        TEXT NOT NULL CHECK (mime IN ('image/png', 'image/jpeg', 'image/webp', 'image/gif')),
  bytes       BLOB NOT NULL,
  byte_size   INTEGER NOT NULL CHECK (byte_size > 0 AND byte_size <= 2097152),
  width       INTEGER,
  height      INTEGER,
  created     TEXT NOT NULL,
  is_retired  INTEGER NOT NULL DEFAULT 0 CHECK (is_retired IN (0, 1)),
  CHECK ((location_id IS NOT NULL) + (item_id IS NOT NULL) + (tool_id IS NOT NULL) = 1)
);
CREATE TRIGGER annotation_no_delete BEFORE DELETE ON annotation
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER annotation_version_no_delete BEFORE DELETE ON annotation_version
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER tag_no_delete BEFORE DELETE ON tag
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER tag_link_no_delete BEFORE DELETE ON tag_link
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER image_no_delete BEFORE DELETE ON image
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
