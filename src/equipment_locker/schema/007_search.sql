-- SPDX-License-Identifier: MIT
-- Search documents, rebuilt from the catalog after each scan and edit (derived data, may be rewritten).
-- When SQLite has FTS5, search.py adds a trigram index over `norm` for fast, case- and typo-tolerant matching.
CREATE TABLE search_doc (
  id     INTEGER PRIMARY KEY,
  kind   TEXT NOT NULL,
  ref_id INTEGER NOT NULL,
  title  TEXT NOT NULL,
  body   TEXT,
  path   TEXT,
  tool   TEXT,
  tags   TEXT,
  norm   TEXT NOT NULL
);
CREATE INDEX search_doc_tool ON search_doc(tool);
