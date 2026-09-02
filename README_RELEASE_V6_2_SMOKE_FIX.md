# Paper2Data V6.2 Smoke Test Fix

## Problem

The packaged EXE built successfully and all 124 pytest tests passed, but
`--smoke-test` exited with WinError 32 on Windows while Python's
`TemporaryDirectory` attempted to delete a smoke-test directory before all
SQLite/Qt file handles had fully disappeared.

## Fix

`main.py` no longer owns/deletes an internal TemporaryDirectory during the
packaged smoke test.

The existing PowerShell runner already creates an isolated directory and sets
`PAPER2DATA_DATA_DIR`. The application now places `smoke.db` there, exits, and
the PowerShell runner removes the directory only after the EXE process has
finished.

This keeps normal application data behavior unchanged.
