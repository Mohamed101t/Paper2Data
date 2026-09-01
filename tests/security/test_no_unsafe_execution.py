import ast
from pathlib import Path

import pytest


pytestmark = pytest.mark.security


FORBIDDEN_CALLS = {"eval", "exec", "compile"}
SOURCE_ROOTS = ("core", "data", "domain", "presentation")


def test_application_code_has_no_raw_dynamic_execution():
    project_root = Path(__file__).resolve().parents[2]
    violations = []

    for root_name in SOURCE_ROOTS:
        root = project_root / root_name
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            # utf-8-sig accepts normal UTF-8 and safely strips a UTF-8 BOM if one
            # exists. ast.parse() receives clean source text in both cases.
            source = path.read_text(encoding="utf-8-sig")
            tree = ast.parse(source, filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in FORBIDDEN_CALLS:
                        violations.append(
                            f"{path.relative_to(project_root)}:{node.lineno} -> {node.func.id}"
                        )

    assert not violations, "Unsafe dynamic execution found:\n" + "\n".join(violations)
