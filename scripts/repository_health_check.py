from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAX_TRACKED_FILE_BYTES = 25 * 1024 * 1024

FORBIDDEN_TRACKED_PATTERNS = (
    re.compile(r"(^|/)__pycache__(/|$)"),
    re.compile(r"(^|/)\.pytest_cache(/|$)"),
    re.compile(r"(^|/)\.venv(/|$)"),
    re.compile(r"(^|/)build(/|$)"),
    re.compile(r"(^|/)dist(/|$)"),
    re.compile(r"(^|/)release_output(/|$)"),
    re.compile(r"\.pyc$", re.IGNORECASE),
    re.compile(r"\.qm$", re.IGNORECASE),
    re.compile(r"\.(db|sqlite|sqlite3)(-(wal|shm))?$", re.IGNORECASE),
    re.compile(r"\.(pfx|p12|pem|key)$", re.IGNORECASE),
    re.compile(r"(^|/)\.env(\.|$)"),
    re.compile(r"-UNVERIFIED\.zip$", re.IGNORECASE),
)

LOCAL_PATH_PATTERNS = (
    re.compile(r"[A-Za-z]:\\" + "Users" + r"\\[^\\\r\n]+", re.IGNORECASE),
    re.compile("/" + "Users" + r"/[^/\r\n]+"),
    re.compile("/" + "home" + r"/[^/\r\n]+"),
)

TEXT_EXTENSIONS = {
    ".py",
    ".md",
    ".txt",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".ps1",
    ".ts",
    ".json",
}

IGNORED_LOCAL_HISTORY = {
    "README_FIELD_SYSTEM_V3.md",
    "README_LOCALIZATION_FIX.md",
    "README_UIUX_V4.md",
    "README_V5_1_FIX.md",
    "README_RELEASE_V6.md",
    "README_RELEASE_V6_1_FIX.md",
}


def git_tracked_files() -> list[Path] | None:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=PROJECT_ROOT,
            check=True,
            capture_output=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None

    raw_paths = [part for part in result.stdout.split(b"\0") if part]
    return [PROJECT_ROOT / part.decode("utf-8", errors="surrogateescape") for part in raw_paths]


def candidate_files() -> list[Path]:
    tracked = git_tracked_files()
    if tracked is not None and tracked:
        return tracked

    # Before the first commit, scan files that are not obvious generated output.
    candidates: list[Path] = []
    skipped_dirs = {".git", ".pytest_cache", "__pycache__", "build", "dist", "release_output", ".venv"}
    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in skipped_dirs for part in path.relative_to(PROJECT_ROOT).parts):
            continue
        candidates.append(path)
    return candidates


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []

    files = candidate_files()
    for path in files:
        relative = path.relative_to(PROJECT_ROOT).as_posix()

        if path.name in IGNORED_LOCAL_HISTORY:
            # These development-history files contain machine-specific installation notes.
            warnings.append(f"Local history file present (should stay ignored): {relative}")
            continue

        for pattern in FORBIDDEN_TRACKED_PATTERNS:
            if pattern.search(relative):
                failures.append(f"Forbidden repository artifact: {relative}")
                break

        try:
            size = path.stat().st_size
        except OSError as exc:
            failures.append(f"Cannot stat {relative}: {exc}")
            continue

        if size > MAX_TRACKED_FILE_BYTES:
            failures.append(f"Tracked/candidate file exceeds 25 MiB: {relative} ({size} bytes)")

        if path.suffix.lower() not in TEXT_EXTENSIONS:
            continue

        try:
            content = path.read_text(encoding="utf-8-sig", errors="strict")
        except (UnicodeError, OSError):
            continue

        for pattern in LOCAL_PATH_PATTERNS:
            match = pattern.search(content)
            if match:
                failures.append(
                    f"Machine-specific absolute user path found in {relative}: {match.group(0)[:100]}"
                )
                break

    if warnings:
        print("Repository health warnings:")
        for warning in sorted(set(warnings)):
            print(f"  WARN  {warning}")

    if failures:
        print("Repository health check: FAILED")
        for failure in sorted(set(failures)):
            print(f"  FAIL  {failure}")
        return 1

    print(f"Repository health check: PASS ({len(files)} files inspected)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
