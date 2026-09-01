# Paper2Data GitHub V7.1 Fix

Fixes `prepare_github_repo.ps1` on Windows systems where `Get-Command python`
returns a broken launcher/path.

The script now prefers:

`%USERPROFILE%\.conda\envs\data_analysis\python.exe`

and only falls back to `python` on PATH when that executable path is valid.

Safe to apply after V7. The existing `.git` directory is preserved.
