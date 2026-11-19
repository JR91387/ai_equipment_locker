-- SPDX-License-Identifier: MIT
-- Nothing is deleted: retire rows instead. walk_state and place_os are derived and may be rewritten.
CREATE TRIGGER ref_os_no_delete BEFORE DELETE ON ref_os
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER ref_tool_no_delete BEFORE DELETE ON ref_tool
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER ref_scope_no_delete BEFORE DELETE ON ref_scope
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER ref_category_no_delete BEFORE DELETE ON ref_category
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER ref_source_no_delete BEFORE DELETE ON ref_source
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER ref_presence_no_delete BEFORE DELETE ON ref_presence
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER ref_origin_no_delete BEFORE DELETE ON ref_origin
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER ref_change_no_delete BEFORE DELETE ON ref_change
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER ref_run_status_no_delete BEFORE DELETE ON ref_run_status
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER machine_no_delete BEFORE DELETE ON machine
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER os_user_no_delete BEFORE DELETE ON os_user
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER place_no_delete BEFORE DELETE ON place
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER scan_run_no_delete BEFORE DELETE ON scan_run
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER project_no_delete BEFORE DELETE ON project
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER location_no_delete BEFORE DELETE ON location
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
CREATE TRIGGER location_change_no_delete BEFORE DELETE ON location_change
  BEGIN SELECT RAISE(ABORT, 'Equipment Locker never deletes: retire the row instead'); END;
