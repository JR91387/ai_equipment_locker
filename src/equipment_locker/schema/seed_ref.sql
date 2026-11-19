-- SPDX-License-Identifier: MIT
-- Re-applied on every start. Tools and categories found in places.json are added by the loader as well.
INSERT INTO ref_os (code, display) VALUES ('linux', 'Linux'), ('darwin', 'macOS'), ('win32', 'Windows')
  ON CONFLICT(code) DO UPDATE SET display = excluded.display;
INSERT INTO ref_scope (code, display) VALUES ('user', 'User'), ('system', 'System'), ('project', 'Project')
  ON CONFLICT(code) DO UPDATE SET display = excluded.display;
INSERT INTO ref_source (code, display) VALUES ('official', 'Official docs'), ('community', 'Community'),
  ('observed', 'Seen on a machine'), ('unverified', 'Not yet checked'), ('discovered', 'Found by name'),
  ('user', 'Added by you')
  ON CONFLICT(code) DO UPDATE SET display = excluded.display;
INSERT INTO ref_presence (code, display) VALUES ('present', 'Present'), ('absent', 'Absent'),
  ('unreadable', 'Unreadable'), ('wrong_type', 'Wrong type'), ('link', 'Symbolic link')
  ON CONFLICT(code) DO UPDATE SET display = excluded.display;
INSERT INTO ref_origin (code, display) VALUES ('own', 'Yours'), ('vendored', 'Third-party code')
  ON CONFLICT(code) DO UPDATE SET display = excluded.display;
INSERT INTO ref_change (code, display) VALUES ('appeared', 'Appeared'), ('changed', 'Changed'),
  ('disappeared', 'Disappeared'), ('reappeared', 'Reappeared')
  ON CONFLICT(code) DO UPDATE SET display = excluded.display;
INSERT INTO ref_run_status (code, display) VALUES ('running', 'Running'), ('ok', 'Complete'),
  ('partial', 'Partial (entry budget reached)'), ('failed', 'Failed')
  ON CONFLICT(code) DO UPDATE SET display = excluded.display;
INSERT INTO ref_category (code, display) VALUES ('config', 'Settings'), ('instructions', 'Instructions'),
  ('skills', 'Skills'), ('agents', 'Agents'), ('commands', 'Commands'), ('plugins', 'Plugins'), ('mcp', 'MCP'),
  ('hooks', 'Hooks'), ('history', 'History'), ('cache', 'Cache'), ('logs', 'Logs'), ('install', 'Install'),
  ('models', 'Models'), ('state', 'State'), ('auth', 'Login'), ('project', 'Project marker'),
  ('discovered', 'Found by name')
  ON CONFLICT(code) DO UPDATE SET display = excluded.display;
INSERT INTO ref_tool (code, display) VALUES ('other', 'Other')
  ON CONFLICT(code) DO UPDATE SET display = excluded.display;
INSERT INTO ref_item_kind (code, display) VALUES ('skill', 'Skill'), ('agent', 'Agent'), ('command', 'Command'),
  ('mcp_server', 'MCP server'), ('plugin', 'Plugin'), ('extension', 'Extension'), ('rule', 'Rule'),
  ('prompt', 'Prompt'), ('hook', 'Hook'), ('model', 'Model'), ('workflow', 'Workflow'),
  ('output_style', 'Output style')
  ON CONFLICT(code) DO UPDATE SET display = excluded.display;
INSERT INTO ref_scope (code, display) VALUES ('pinned', 'Pinned by you')
  ON CONFLICT(code) DO UPDATE SET display = excluded.display;
INSERT INTO ref_category (code, display) VALUES ('pinned', 'Pinned folder')
  ON CONFLICT(code) DO UPDATE SET display = excluded.display;
