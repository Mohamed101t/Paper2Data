# Paper2Data V5 — Quality & Testing System

V5 is cumulative over UI/UX V4 and adds a formal quality gate for the project.

## Test pyramid used by Paper2Data

1. **Unit Testing** — fastest and simplest. Validates one rule/class at a time.
2. **Integration Testing** — combines real SQLite repositories, codecs, viewmodels and exporters.
3. **E2E (End-to-End)** — follows the actual user journey: project → fields → record → records → Excel/CSV. An optional offscreen GUI smoke test also exercises the PySide6 screens.
4. **Performance Testing** — checks 10,000-record retrieval/CSV and 5,000-record XLSX export against explicit budgets.
5. **Security Testing** — SQL injection, spreadsheet formula injection, foreign-key/cascade integrity, no unsafe eval/exec, and no sensitive record values printed to console.

## Important fixes discovered by the tests

- Fixed Records screen first-load ordering: the view now connects to `records_loaded` before `set_project()` emits the first dataset.
- Added spreadsheet formula-injection protection for CSV and XLSX text cells.
- Added a shared locale-tolerant number parser. Values such as `$1,500.50`, `€1.500,50`, and `72,5` now validate/store/export consistently.

## Default quick gate

Run this after every meaningful change:

```powershell
python scripts\run_tests.py quick
```

The default profile intentionally excludes the slow performance suite and GUI E2E.

## Run one test layer

```powershell
python scripts\run_tests.py unit
python scripts\run_tests.py integration
python scripts\run_tests.py e2e
python scripts\run_tests.py gui
python scripts\run_tests.py security
python scripts\run_tests.py performance
```

## Release gates

Before a normal build:

```powershell
python scripts\run_tests.py all
```

Before a release candidate, including the offscreen GUI E2E:

```powershell
python scripts\run_tests.py full
```

`performance` tests are excluded from plain `python -m pytest -q` so daily development stays fast. Use the profile above when you deliberately want performance measurements.

## Performance budgets

Current V5 regression budgets (can be relaxed on slower CI using `P2D_PERF_MULTIPLIER`):

- Retrieve 10,000 records × 5 values: `< 12 s`
- Export 10,000 records to CSV: `< 12 s`
- Export 5,000 records to XLSX: `< 20 s`

Example for a slower CI machine:

```powershell
$env:P2D_PERF_MULTIPLIER = "1.5"
python scripts\run_tests.py performance
```

## Test configuration

`pytest.ini` limits discovery to the real `tests/` folder. This also prevents accidentally extracted patch folders inside the project from being collected as tests.

Markers:

- `unit`
- `integration`
- `e2e`
- `e2e_gui`
- `security`
- `performance`
- `slow`

## Test dependencies

```powershell
python -m pip install -r requirements_test.txt
```

The application already uses PySide6 and openpyxl, so the main new testing dependency is pytest if it is not already installed.
