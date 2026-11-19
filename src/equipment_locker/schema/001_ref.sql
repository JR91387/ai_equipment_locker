-- SPDX-License-Identifier: MIT
-- Lookup tables: id + unique code. Rows are retired, never deleted (see 003_guards.sql).
CREATE TABLE ref_os (
  id         INTEGER PRIMARY KEY,
  code       TEXT NOT NULL UNIQUE,
  display    TEXT NOT NULL,
  is_retired INTEGER NOT NULL DEFAULT 0 CHECK (is_retired IN (0, 1))
);
CREATE TABLE ref_tool (
  id         INTEGER PRIMARY KEY,
  code       TEXT NOT NULL UNIQUE,
  display    TEXT NOT NULL,
  is_retired INTEGER NOT NULL DEFAULT 0 CHECK (is_retired IN (0, 1))
);
CREATE TABLE ref_scope (
  id         INTEGER PRIMARY KEY,
  code       TEXT NOT NULL UNIQUE,
  display    TEXT NOT NULL,
  is_retired INTEGER NOT NULL DEFAULT 0 CHECK (is_retired IN (0, 1))
);
CREATE TABLE ref_category (
  id         INTEGER PRIMARY KEY,
  code       TEXT NOT NULL UNIQUE,
  display    TEXT NOT NULL,
  is_retired INTEGER NOT NULL DEFAULT 0 CHECK (is_retired IN (0, 1))
);
CREATE TABLE ref_source (
  id         INTEGER PRIMARY KEY,
  code       TEXT NOT NULL UNIQUE,
  display    TEXT NOT NULL,
  is_retired INTEGER NOT NULL DEFAULT 0 CHECK (is_retired IN (0, 1))
);
CREATE TABLE ref_presence (
  id         INTEGER PRIMARY KEY,
  code       TEXT NOT NULL UNIQUE,
  display    TEXT NOT NULL,
  is_retired INTEGER NOT NULL DEFAULT 0 CHECK (is_retired IN (0, 1))
);
CREATE TABLE ref_origin (
  id         INTEGER PRIMARY KEY,
  code       TEXT NOT NULL UNIQUE,
  display    TEXT NOT NULL,
  is_retired INTEGER NOT NULL DEFAULT 0 CHECK (is_retired IN (0, 1))
);
CREATE TABLE ref_change (
  id         INTEGER PRIMARY KEY,
  code       TEXT NOT NULL UNIQUE,
  display    TEXT NOT NULL,
  is_retired INTEGER NOT NULL DEFAULT 0 CHECK (is_retired IN (0, 1))
);
CREATE TABLE ref_run_status (
  id         INTEGER PRIMARY KEY,
  code       TEXT NOT NULL UNIQUE,
  display    TEXT NOT NULL,
  is_retired INTEGER NOT NULL DEFAULT 0 CHECK (is_retired IN (0, 1))
);
