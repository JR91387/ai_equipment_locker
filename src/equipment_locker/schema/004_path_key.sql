-- SPDX-License-Identifier: MIT
-- Path identity that ignores case on Windows and macOS. Filled by paths.backfill() on open.
ALTER TABLE location ADD COLUMN path_key TEXT;
ALTER TABLE project ADD COLUMN path_key TEXT;
CREATE UNIQUE INDEX location_path_key ON location(machine_id, path_key) WHERE is_retired = 0 AND path_key IS NOT NULL;
CREATE UNIQUE INDEX project_path_key ON project(machine_id, path_key) WHERE is_retired = 0 AND path_key IS NOT NULL;
