from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROFILES = {
    "quick": ["-q"],
    "unit": ["tests/unit", "-q"],
    "integration": ["tests/integration", "-q", "-m", "integration"],
    "e2e": ["tests/e2e", "-q", "-m", "e2e and not e2e_gui"],
    "gui": ["tests/e2e", "-q", "-m", "e2e_gui"],
    "security": ["tests/security", "-q", "-m", "security"],
    "performance": ["tests/performance", "-q", "-s", "-m", "performance"],
    "all": ["-o", "addopts=-ra --strict-markers", "-q", "-m", "not e2e_gui"],
    "full": ["-o", "addopts=-ra --strict-markers", "-q", "-s"],
}


def main() -> int:
    profile = sys.argv[1].lower() if len(sys.argv) > 1 else "quick"
    if profile not in PROFILES:
        print("Unknown profile:", profile)
        print("Available:", ", ".join(PROFILES))
        return 2

    command = [sys.executable, "-m", "pytest", *PROFILES[profile]]
    print(f"Paper2Data test profile: {profile}")
    print("Command:", " ".join(command))
    return subprocess.call(command, cwd=PROJECT_ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
