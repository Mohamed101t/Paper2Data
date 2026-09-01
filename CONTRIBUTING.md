# Contributing to Paper2Data

Thanks for helping improve Paper2Data.

## Development principles

Changes should preserve the project's coding constitution:

- **SRP** — one responsibility per class/module/function.
- **DRY** — centralize repeated behavior.
- **KISS** — prefer the simplest maintainable solution.
- **YAGNI** — do not add speculative features.
- clear Python naming and readable control flow;
- layered architecture with presentation separated from domain/data concerns;
- repository abstractions for persistence boundaries;
- reusable UI components and centralized design tokens;
- business rules that can be tested without the GUI.

## Setup

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements_test.txt
python scripts\build_translations.py
```

## Branches

Use short, descriptive branch names, for example:

```text
feature/project-wizard
fix/csv-formula-safety
refactor/field-validation
```

## Before opening a pull request

Run:

```powershell
python scripts\repository_health_check.py
python scripts\run_tests.py quick
python scripts\run_tests.py security
python scripts\run_tests.py gui
```

Run performance tests when your change affects database access, record loading, export, or large datasets:

```powershell
python scripts\run_tests.py performance
```

## Pull request expectations

A pull request should:

- describe the user problem being solved;
- stay focused on one responsibility;
- include or update tests for changed behavior;
- update translations when visible strings change;
- avoid adding personal data, local database files, build artifacts, or credentials;
- avoid changing stable field IDs merely to rename a UI label;
- preserve Arabic RTL behavior and LTR handling for codes/numbers/URLs where relevant.

## Translation changes

When UI source strings change, update translation source files and verify all supported languages before merging.

## Scope

The current MVP intentionally excludes OCR, cloud synchronization, and AI extraction. Proposals in those areas should be discussed before implementation so the desktop MVP remains focused.
