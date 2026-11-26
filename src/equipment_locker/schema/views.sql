-- SPDX-License-Identifier: MIT
-- Re-applied on every start.
DROP VIEW IF EXISTS v_location_current;
CREATE VIEW v_location_current AS
SELECT l.id, m.name AS machine, u.name AS os_user, t.code AS tool, s.code AS scope, c.code AS category,
       o.code AS origin, src.code AS source, p.code AS presence, l.kind, l.path, l.size_bytes, l.size_over,
       l.entry_count, l.mtime, l.first_seen_run, l.last_seen_run, pr.root AS project_root
FROM location l
JOIN machine m ON m.id = l.machine_id
LEFT JOIN os_user u ON u.id = l.os_user_id
JOIN ref_tool t ON t.id = l.tool_id
JOIN ref_scope s ON s.id = l.scope_id
JOIN ref_category c ON c.id = l.category_id
JOIN ref_origin o ON o.id = l.origin_id
JOIN ref_source src ON src.id = l.source_id
JOIN ref_presence p ON p.id = l.presence_id
LEFT JOIN project pr ON pr.id = l.project_id
WHERE l.is_retired = 0;

DROP VIEW IF EXISTS v_tool_summary;
CREATE VIEW v_tool_summary AS
SELECT tool,
       SUM(presence = 'present') AS present,
       SUM(presence = 'absent') AS gone,
       SUM(origin = 'vendored') AS vendored,
       COALESCE(SUM(CASE WHEN presence = 'present' THEN size_bytes END), 0) AS bytes,
       SUM(presence = 'present' AND kind = 'dir' AND category <> 'auth' AND size_bytes IS NULL) AS unsized,
       MAX(size_over) AS any_size_over
FROM v_location_current
GROUP BY tool
ORDER BY present DESC, tool;
