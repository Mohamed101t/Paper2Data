from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT / "presentation" / "translations"
EXPECTED_CODES = ("ar", "fr", "ru", "zh")  # English is the source/base language.


def _find_lrelease() -> str | None:
    """Find pyside6-lrelease even when the Conda environment was not activated.

    When Paper2Data is launched with an explicit environment Python executable,
    that environment's Scripts directory may not be present in PATH. Resolve the
    Qt tool from sys.executable before giving up.
    """
    from_path = shutil.which("pyside6-lrelease")
    if from_path:
        return from_path

    python_dir = Path(sys.executable).resolve().parent
    executable_names = (
        "pyside6-lrelease.exe",
        "pyside6-lrelease",
    )
    candidate_dirs = (
        python_dir / "Scripts",  # Windows virtualenv/Conda environments
        python_dir,              # Unix-style environment bin directory
        python_dir.parent / "Scripts",
    )

    for directory in candidate_dirs:
        for executable_name in executable_names:
            candidate = directory / executable_name
            if candidate.is_file():
                return str(candidate)

    return None


def main() -> int:
    lrelease = _find_lrelease()
    if lrelease is None:
        print(
            "pyside6-lrelease was not found. Install PySide6 in the Python environment used to run this script.",
            file=sys.stderr,
        )
        return 1

    missing = [
        code
        for code in EXPECTED_CODES
        if not (TRANSLATIONS_DIR / f"paper2data_{code}.ts").is_file()
    ]
    if missing:
        print(
            "Missing translation source files: " + ", ".join(missing),
            file=sys.stderr,
        )
        return 1

    for code in EXPECTED_CODES:
        ts_file = TRANSLATIONS_DIR / f"paper2data_{code}.ts"
        qm_file = ts_file.with_suffix(".qm")
        subprocess.run(
            [lrelease, str(ts_file), "-qm", str(qm_file)],
            check=True,
        )
        print(f"Built: {qm_file.relative_to(ROOT)}")

    print("Ready languages: Arabic, English, French, Russian, Chinese")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
