from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
TRANSLATIONS_DIR = ROOT / "presentation" / "translations"
SOURCE_PATHS = [
    ROOT / "presentation" / "views",
    ROOT / "presentation" / "viewmodels",
    ROOT / "presentation" / "components",
]
LANGUAGE_CODES = ("ar", "fr", "ru", "zh")


def main() -> int:
    lupdate = shutil.which("pyside6-lupdate")
    if lupdate is None:
        print(
            "pyside6-lupdate was not found. Activate the same environment that contains PySide6, then run this script again.",
            file=sys.stderr,
        )
        return 1

    ts_files = [
        TRANSLATIONS_DIR / f"paper2data_{code}.ts" for code in LANGUAGE_CODES
    ]
    command = [lupdate, *map(str, SOURCE_PATHS), "-ts", *map(str, ts_files)]
    subprocess.run(command, check=True)
    for ts_file in ts_files:
        print(f"Updated: {ts_file.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
